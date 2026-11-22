"""
main.py - The FastAPI backend for LearnMate AI.

Run it from the learnmate-ai folder with:
    uvicorn backend.main:app --reload
(or from inside the backend folder with: uvicorn main:app --reload)

All API routes start with /api. The frontend folder is served at "/".
"""

import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from contextlib import closing
from typing import List, Optional

# Make sure sibling modules (database, security, seed_data) can be imported
# no matter which folder uvicorn is started from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import Depends, FastAPI, Header, HTTPException  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from database import get_connection, init_db  # noqa: E402
from security import hash_password, new_session_token, verify_password  # noqa: E402

# Read learnmate-ai/.env (if it exists) into environment variables.
# Variables already set in the terminal win over values in .env.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)

app = FastAPI(title="LearnMate AI")

# A topic counts as "completed" / "not weak" when its latest score is at least this.
PASS_PERCENT = 60


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup():
    """Create the tables and sample data when the server starts."""
    init_db()


# ---------------------------------------------------------------------------
# Request bodies (Pydantic checks the shape of the JSON for us)
# ---------------------------------------------------------------------------

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: str


class QuizBody(BaseModel):
    answers: List[int]


# ---------------------------------------------------------------------------
# Login helpers
# ---------------------------------------------------------------------------

def get_token(authorization):
    """Pull the token out of a header like 'Bearer abc123'."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please log in first")
    return authorization[len("Bearer "):].strip()


def get_current_user(authorization: Optional[str] = Header(default=None)):
    """Find the logged-in user for this request. Used as a dependency."""
    token = get_token(authorization)
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT users.id, users.name, users.email FROM sessions "
            "JOIN users ON users.id = sessions.user_id "
            "WHERE sessions.token = ?",
            (token,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Session is invalid or expired")
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


# ---------------------------------------------------------------------------
# Progress helpers (shared by several endpoints)
# ---------------------------------------------------------------------------

def latest_scores(conn, user_id):
    """Return {topic_id: percent} using the user's most recent attempt per topic."""
    rows = conn.execute(
        "SELECT topic_id, percent FROM quiz_attempts WHERE user_id = ? "
        "ORDER BY created_at DESC, id DESC",
        (user_id,),
    ).fetchall()
    latest = {}
    for row in rows:
        # Rows are newest first, so the first one we see for a topic is the latest.
        if row["topic_id"] not in latest:
            latest[row["topic_id"]] = row["percent"]
    return latest


def topic_status(conn, user_id):
    """Return one dict per topic with the user's latest percent and attempt count."""
    latest = latest_scores(conn, user_id)
    count_rows = conn.execute(
        "SELECT topic_id, COUNT(*) AS n FROM quiz_attempts WHERE user_id = ? "
        "GROUP BY topic_id",
        (user_id,),
    ).fetchall()
    attempts = {row["topic_id"]: row["n"] for row in count_rows}

    topic_rows = conn.execute(
        "SELECT t.id, t.title, t.subject_id, s.name AS subject_name "
        "FROM topics t JOIN subjects s ON s.id = t.subject_id ORDER BY t.id"
    ).fetchall()

    result = []
    for t in topic_rows:
        result.append({
            "topic_id": t["id"],
            "title": t["title"],
            "subject_id": t["subject_id"],
            "subject_name": t["subject_name"],
            "latest_percent": latest.get(t["id"]),
            "attempts": attempts.get(t["id"], 0),
        })
    return result


def average_of(values):
    """Average of a list of numbers, rounded to 1 decimal. None if the list is empty."""
    if not values:
        return None
    return round(sum(values) / len(values), 1)


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@app.post("/api/register")
def register(body: RegisterBody):
    """Create a new student account and log them in straight away."""
    name = body.name.strip()
    email = body.email.strip().lower()

    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a valid email")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    with closing(get_connection()) as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing is not None:
            raise HTTPException(status_code=400, detail="This email is already registered")

        try:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, hash_password(body.password)),
            )
        except sqlite3.IntegrityError:
            # Two sign-ups with the same email at the same moment.
            raise HTTPException(status_code=400, detail="This email is already registered")

        user_id = cur.lastrowid
        token = new_session_token()
        conn.execute(
            "INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id)
        )
        conn.commit()

    return {"token": token, "user": {"id": user_id, "name": name, "email": email}}


@app.post("/api/login")
def login(body: LoginBody):
    """Check email and password, then create a new session token."""
    email = body.email.strip().lower()

    with closing(get_connection()) as conn:
        user = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
        if user is None or not verify_password(body.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Wrong email or password")

        token = new_session_token()
        conn.execute(
            "INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"])
        )
        conn.commit()

    return {
        "token": token,
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
    }


@app.post("/api/logout")
def logout(
    authorization: Optional[str] = Header(default=None),
    user: dict = Depends(get_current_user),
):
    """Delete the current session so the token can no longer be used."""
    token = get_token(authorization)
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    return {"ok": True}


@app.get("/api/me")
def me(user: dict = Depends(get_current_user)):
    """Return the logged-in user's basic details."""
    return user


# ---------------------------------------------------------------------------
# Subjects and topics
# ---------------------------------------------------------------------------

@app.get("/api/subjects")
def list_subjects(user: dict = Depends(get_current_user)):
    """List all subjects with topic counts and the user's average score in each."""
    with closing(get_connection()) as conn:
        subjects = conn.execute(
            "SELECT id, name, description FROM subjects ORDER BY id"
        ).fetchall()
        status = topic_status(conn, user["id"])

    result = []
    for s in subjects:
        mine = [t for t in status if t["subject_id"] == s["id"]]
        scores = [t["latest_percent"] for t in mine if t["latest_percent"] is not None]
        result.append({
            "id": s["id"],
            "name": s["name"],
            "description": s["description"],
            "topic_count": len(mine),
            "average_percent": average_of(scores),
        })
    return result


@app.get("/api/subjects/{subject_id}")
def get_subject(subject_id: int, user: dict = Depends(get_current_user)):
    """Return one subject and the list of its topics."""
    with closing(get_connection()) as conn:
        subject = conn.execute(
            "SELECT id, name, description FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        if subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")

        status = topic_status(conn, user["id"])
        topic_rows = conn.execute(
            "SELECT id, title, content FROM topics WHERE subject_id = ? ORDER BY id",
            (subject_id,),
        ).fetchall()

    latest = {t["topic_id"]: t["latest_percent"] for t in status}
    topics = []
    for t in topic_rows:
        topics.append({
            "id": t["id"],
            "title": t["title"],
            "content_summary": t["content"][:120],
            "latest_percent": latest.get(t["id"]),
        })

    return {
        "id": subject["id"],
        "name": subject["name"],
        "description": subject["description"],
        "topics": topics,
    }


@app.get("/api/topics/{topic_id}")
def get_topic(topic_id: int, user: dict = Depends(get_current_user)):
    """Return one topic's learning content and its quiz questions (no answers)."""
    with closing(get_connection()) as conn:
        topic = conn.execute(
            "SELECT t.id, t.title, t.content, t.subject_id, s.name AS subject_name "
            "FROM topics t JOIN subjects s ON s.id = t.subject_id WHERE t.id = ?",
            (topic_id,),
        ).fetchone()
        if topic is None:
            raise HTTPException(status_code=404, detail="Topic not found")

        # The next topic in the same subject, by id. None if this is the last one.
        next_row = conn.execute(
            "SELECT id FROM topics WHERE subject_id = ? AND id > ? ORDER BY id LIMIT 1",
            (topic["subject_id"], topic_id),
        ).fetchone()

        question_rows = conn.execute(
            "SELECT id, question_text, option_a, option_b, option_c, option_d "
            "FROM questions WHERE topic_id = ? ORDER BY id",
            (topic_id,),
        ).fetchall()

    questions = []
    for q in question_rows:
        questions.append({
            "id": q["id"],
            "question_text": q["question_text"],
            # Correct answers are deliberately NOT sent to the browser.
            "options": [q["option_a"], q["option_b"], q["option_c"], q["option_d"]],
        })

    return {
        "id": topic["id"],
        "title": topic["title"],
        "content": topic["content"],
        "subject_id": topic["subject_id"],
        "subject_name": topic["subject_name"],
        "next_topic_id": next_row["id"] if next_row else None,
        "questions": questions,
    }


# ---------------------------------------------------------------------------
# Quiz
# ---------------------------------------------------------------------------

@app.post("/api/topics/{topic_id}/quiz")
def submit_quiz(topic_id: int, body: QuizBody, user: dict = Depends(get_current_user)):
    """Mark a quiz, save the attempt, and return the results question by question."""
    with closing(get_connection()) as conn:
        topic = conn.execute("SELECT id FROM topics WHERE id = ?", (topic_id,)).fetchone()
        if topic is None:
            raise HTTPException(status_code=404, detail="Topic not found")

        question_rows = conn.execute(
            "SELECT id, question_text, correct_option FROM questions "
            "WHERE topic_id = ? ORDER BY id",
            (topic_id,),
        ).fetchall()

        results = []
        score = 0
        for index, q in enumerate(question_rows):
            # A missing answer becomes None, which never matches, so it counts as wrong.
            your_answer = body.answers[index] if index < len(body.answers) else None
            is_correct = your_answer == q["correct_option"]
            if is_correct:
                score += 1
            results.append({
                "question_id": q["id"],
                "question_text": q["question_text"],
                "your_answer": your_answer,
                "correct_answer": q["correct_option"],
                "is_correct": is_correct,
            })

        total = len(question_rows)
        percent = round(score / total * 100, 1) if total else 0.0

        conn.execute(
            "INSERT INTO quiz_attempts (user_id, topic_id, score, total, percent) "
            "VALUES (?, ?, ?, ?, ?)",
            (user["id"], topic_id, score, total, percent),
        )
        conn.commit()

    return {"score": score, "total": total, "percent": percent, "results": results}


# ---------------------------------------------------------------------------
# Progress and recommendations
# ---------------------------------------------------------------------------

@app.get("/api/progress")
def progress(user: dict = Depends(get_current_user)):
    """Summarise how the user is doing overall, per subject and per topic."""
    with closing(get_connection()) as conn:
        taken = conn.execute(
            "SELECT COUNT(*) FROM quiz_attempts WHERE user_id = ?", (user["id"],)
        ).fetchone()[0]
        all_percents = [
            row["percent"] for row in conn.execute(
                "SELECT percent FROM quiz_attempts WHERE user_id = ?", (user["id"],)
            ).fetchall()
        ]
        subjects = conn.execute("SELECT id, name FROM subjects ORDER BY id").fetchall()
        status = topic_status(conn, user["id"])

    per_subject = []
    for s in subjects:
        mine = [t for t in status if t["subject_id"] == s["id"]]
        attempted = [t for t in mine if t["latest_percent"] is not None]
        total_here = len(mine)
        per_subject.append({
            "subject_id": s["id"],
            "subject_name": s["name"],
            "topics_total": total_here,
            "topics_attempted": len(attempted),
            "progress_percent": round(len(attempted) / total_here * 100, 1) if total_here else 0.0,
        })

    attempted_all = [t for t in status if t["latest_percent"] is not None]
    completed = [t for t in attempted_all if t["latest_percent"] >= PASS_PERCENT]
    weak = sorted(
        [t for t in attempted_all if t["latest_percent"] < PASS_PERCENT],
        key=lambda t: t["latest_percent"],
    )

    return {
        "quizzes_taken": taken,
        "average_percent": average_of(all_percents),
        "topics_completed": len(completed),
        "total_topics": len(status),
        "per_subject": per_subject,
        "topics": [
            {
                "topic_id": t["topic_id"],
                "title": t["title"],
                "subject_name": t["subject_name"],
                "latest_percent": t["latest_percent"],
                "attempts": t["attempts"],
            }
            for t in status
        ],
        "weak_topics": [
            {
                "topic_id": t["topic_id"],
                "title": t["title"],
                "subject_name": t["subject_name"],
                "latest_percent": t["latest_percent"],
            }
            for t in weak
        ],
    }


@app.get("/api/recommendations")
def recommendations(user: dict = Depends(get_current_user)):
    """Suggest up to 5 topics: weakest scores first, then topics not started yet."""
    with closing(get_connection()) as conn:
        status = topic_status(conn, user["id"])

    # Weak topics first (lowest score first).
    weak = sorted(
        [t for t in status if t["latest_percent"] is not None and t["latest_percent"] < PASS_PERCENT],
        key=lambda t: t["latest_percent"],
    )
    # Then topics the user has never tried.
    not_started = [t for t in status if t["latest_percent"] is None]

    items = []
    for t in weak:
        items.append({
            "topic_id": t["topic_id"],
            "title": t["title"],
            "subject_name": t["subject_name"],
            "reason": "You scored %s%% \u2013 revise this" % t["latest_percent"],
        })
    for t in not_started:
        items.append({
            "topic_id": t["topic_id"],
            "title": t["title"],
            "subject_name": t["subject_name"],
            "reason": "Not started yet",
        })

    return items[:5]


# ---------------------------------------------------------------------------
# AI tutor (calls an external AI service; questions are not saved)
# ---------------------------------------------------------------------------

class TutorRequest(BaseModel):
    question: str
    topic: str = ""


@app.post("/api/tutor/ask")
def ask_tutor(body: TutorRequest, user: dict = Depends(get_current_user)):
    """Send the student's question to the AI service and return the answer."""
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please type a question first.")
    if len(question) > 1000:
        raise HTTPException(status_code=400, detail="Question is too long (max 1000 characters).")

    # The key is read from the environment only. It is never printed or returned.
    api_key = os.environ.get("AI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI tutor is not configured yet. Ask your teacher or admin to set AI_API_KEY.",
        )
    api_url = os.environ.get("AI_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    model = os.environ.get("AI_MODEL", "openai/gpt-oss-20b")

    # Build the instructions for the AI, adding the topic if the student gave one.
    system = (
        "You are a friendly tutor for students. You help with C Programming, Java, Python "
        "and Mathematics. Explain step by step in simple English, for a beginner. Use short "
        "numbered steps and a small example when helpful. Keep answers under 250 words."
    )
    topic = body.topic.strip()[:100]
    if topic:
        system += " The student is studying: " + topic + "."

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        "temperature": 0.4,
    }
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
            "User-Agent": "LearnMate-AI/1.0",
        },
        method="POST",
    )

    # Send the request and read the raw reply.
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as err:
        # HTTPError must come before URLError, because it is a kind of URLError.
        if err.code == 429:
            raise HTTPException(status_code=429, detail="The AI tutor is busy right now. Please wait a minute and try again.")
        elif err.code in (401, 403):
            raise HTTPException(status_code=502, detail="The AI key was rejected. Ask your admin to check AI_API_KEY.")
        else:
            raise HTTPException(status_code=502, detail="The AI service returned an error. Please try again later.")
    except (urllib.error.URLError, TimeoutError):
        raise HTTPException(status_code=502, detail="Could not reach the AI service. Check your internet connection.")

    # Pull the answer text out of the JSON reply.
    try:
        data = json.loads(raw)
        answer = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError, TypeError):
        raise HTTPException(status_code=502, detail="Unexpected response from the AI service.")

    return {"answer": answer, "model": model}



# ---------------------------------------------------------------------------
# Frontend (served last so that /api routes always win)
# ---------------------------------------------------------------------------

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

# Only mount the website if the frontend folder exists.
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

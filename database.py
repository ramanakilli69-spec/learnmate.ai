"""
database.py - SQLite database setup.

- get_connection() opens the database file.
- init_db() creates the tables and loads sample data the first time.
"""

import os
import sqlite3

from seed_data import seed

# The database file lives next to this file: backend/learnmate.db
DB_PATH = os.path.join(os.path.dirname(__file__), "learnmate.db")

# All tables. "IF NOT EXISTS" means it is safe to run this many times.
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id),
    question_text TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option INTEGER NOT NULL CHECK(correct_option BETWEEN 0 AND 3)
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    topic_id INTEGER NOT NULL REFERENCES topics(id),
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    percent REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection():
    """Open a new connection. Rows can be read by column name, e.g. row['name']."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite does not check foreign keys unless we turn this on.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables, and add sample data if the subjects table is empty."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        if count == 0:
            seed(conn)
        conn.commit()
    finally:
        conn.close()

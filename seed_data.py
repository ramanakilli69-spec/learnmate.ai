"""
seed_data.py - Sample subjects, topics and quiz questions.

seed(conn) inserts all of this into the database. It only runs when the
subjects table is empty (see init_db in database.py).
"""

SUBJECTS = [
    {"name": "C Programming", "description": "Learn the basics of the C language, the parent of many languages."},
    {"name": "Java", "description": "Object-oriented programming with Java, used in apps and big companies."},
    {"name": "Python", "description": "A friendly, readable language for beginners and data science."},
    {"name": "Mathematics", "description": "Core maths skills: algebra, equations and percentages."},
]

# Each topic belongs to one subject (matched by subject name).
TOPICS = [
    {
        "subject": "C Programming",
        "title": "Introduction to C",
        "content": (
            "- C is a small, fast, general-purpose language.\n"
            "- Every C program starts running at main().\n"
            "- printf() is used to show output on the screen.\n"
            "- Save C code in files ending with .c\n"
        ),
    },
    {
        "subject": "C Programming",
        "title": "Variables and Data Types",
        "content": (
            "- A variable is a named box that stores a value.\n"
            "- int stores whole numbers, char stores one character.\n"
            "- Use %d in printf() to print an int.\n"
            "- & gives the address of a variable.\n"
        ),
    },
    {
        "subject": "C Programming",
        "title": "Loops in C",
        "content": (
            "- for loop: best when you know how many times to repeat.\n"
            "- while loop: checks the condition before each run.\n"
            "- do-while loop: runs the body at least once.\n"
            "- break exits a loop; continue skips to the next round.\n"
        ),
    },
    {
        "subject": "Java",
        "title": "Java Basics and JVM",
        "content": (
            "- Java code is compiled to bytecode (.class files).\n"
            "- The JVM (Java Virtual Machine) runs that bytecode.\n"
            "- Every Java program starts at the main method.\n"
            "- Each statement ends with a semicolon ;\n"
        ),
    },
    {
        "subject": "Java",
        "title": "Classes and Objects",
        "content": (
            "- A class is a blueprint; an object is one instance of it.\n"
            "- Create an object with the new keyword.\n"
            "- Fields store data; methods store behaviour.\n"
            "- this refers to the current object.\n"
        ),
    },
    {
        "subject": "Java",
        "title": "Inheritance",
        "content": (
            "- extends lets one class inherit from another.\n"
            "- Inheritance helps you reuse code.\n"
            "- super calls the parent class constructor or methods.\n"
            "- A Java class can extend only one class.\n"
        ),
    },
    {
        "subject": "Python",
        "title": "Python Basics",
        "content": (
            "- Python uses indentation (spaces) to group code.\n"
            "- # starts a comment.\n"
            "- print() shows output.\n"
            "- Variables are created just by assigning: x = 5\n"
        ),
    },
    {
        "subject": "Python",
        "title": "Lists and Tuples",
        "content": (
            "- A list [1, 2, 3] can be changed after creation.\n"
            "- A tuple (1, 2, 3) cannot be changed.\n"
            "- Indexing starts at 0.\n"
            "- len(x) gives the number of items.\n"
        ),
    },
    {
        "subject": "Python",
        "title": "Functions in Python",
        "content": (
            "- def defines a function.\n"
            "- Parameters receive values; return sends a value back.\n"
            "- A function with no return gives back None.\n"
            "- Functions help you avoid repeating code.\n"
        ),
    },
    {
        "subject": "Mathematics",
        "title": "Algebra Basics",
        "content": (
            "- A variable (like x) stands for an unknown number.\n"
            "- In 3x, the 3 is the coefficient.\n"
            "- Follow BODMAS: brackets, orders, division/multiplication, addition/subtraction.\n"
            "- Like terms have the same variable part.\n"
        ),
    },
    {
        "subject": "Mathematics",
        "title": "Linear Equations",
        "content": (
            "- A linear equation has x with power 1 only.\n"
            "- Move numbers to one side and x to the other.\n"
            "- Always do the same operation on both sides.\n"
            "- Check your answer by putting it back in.\n"
        ),
    },
    {
        "subject": "Mathematics",
        "title": "Percentages and Ratios",
        "content": (
            "- Percentage = (part / whole) x 100.\n"
            "- 20% of 50 means 20/100 x 50.\n"
            "- A ratio 2:3 splits a total into 5 equal shares.\n"
            "- 1/4 equals 25%.\n"
        ),
    },
]

# Each question belongs to one topic (matched by topic title).
# "correct" is the index of the right option: 0=A, 1=B, 2=C, 3=D.
QUESTIONS = [
    # Introduction to C
    {"topic": "Introduction to C", "question": "Who developed the C language?",
     "options": ["Dennis Ritchie", "James Gosling", "Guido van Rossum", "Bjarne Stroustrup"], "correct": 0},
    {"topic": "Introduction to C", "question": "Which file extension is used for C source files?",
     "options": [".txt", ".c", ".java", ".py"], "correct": 1},
    {"topic": "Introduction to C", "question": "Which function is the entry point of a C program?",
     "options": ["start()", "main()", "run()", "begin()"], "correct": 1},
    {"topic": "Introduction to C", "question": "Which header file is needed for printf()?",
     "options": ["<stdlib.h>", "<math.h>", "<stdio.h>", "<string.h>"], "correct": 2},

    # Variables and Data Types
    {"topic": "Variables and Data Types", "question": "Which keyword declares an integer variable?",
     "options": ["int", "integer", "num", "var"], "correct": 0},
    {"topic": "Variables and Data Types", "question": "Which format specifier prints an int with printf?",
     "options": ["%f", "%d", "%c", "%s"], "correct": 1},
    {"topic": "Variables and Data Types", "question": "How many bytes is a typical char?",
     "options": ["1", "2", "4", "8"], "correct": 0},
    {"topic": "Variables and Data Types", "question": "Which operator gives the address of a variable?",
     "options": ["*", "&", "%", "#"], "correct": 1},

    # Loops in C
    {"topic": "Loops in C", "question": "Which loop always runs its body at least once?",
     "options": ["for", "while", "do-while", "if"], "correct": 2},
    {"topic": "Loops in C", "question": "Which keyword skips to the next iteration of a loop?",
     "options": ["break", "continue", "skip", "next"], "correct": 1},
    {"topic": "Loops in C", "question": "Which loop is best when the count is known in advance?",
     "options": ["for", "do", "goto", "switch"], "correct": 0},
    {"topic": "Loops in C", "question": "What does break do inside a loop?",
     "options": ["Pauses it", "Exits the loop", "Restarts it", "Does nothing"], "correct": 1},

    # Java Basics and JVM
    {"topic": "Java Basics and JVM", "question": "What does JVM stand for?",
     "options": ["Java Virtual Machine", "Java Visual Mode", "Joint Variable Method", "Java Verified Module"], "correct": 0},
    {"topic": "Java Basics and JVM", "question": "Which method is the entry point of a Java program?",
     "options": ["main", "start", "run", "init"], "correct": 0},
    {"topic": "Java Basics and JVM", "question": "Java source code is compiled into what?",
     "options": ["Machine code", ".class bytecode", ".exe files", "Python code"], "correct": 1},
    {"topic": "Java Basics and JVM", "question": "Which symbol ends a Java statement?",
     "options": ["Colon", "Period", "Semicolon", "Comma"], "correct": 2},

    # Classes and Objects
    {"topic": "Classes and Objects", "question": "A class is best described as?",
     "options": ["A blueprint for objects", "A running program", "A variable", "A loop"], "correct": 0},
    {"topic": "Classes and Objects", "question": "Which keyword creates a new object in Java?",
     "options": ["make", "new", "create", "alloc"], "correct": 1},
    {"topic": "Classes and Objects", "question": "Which keyword refers to the current object?",
     "options": ["this", "self", "me", "super"], "correct": 0},
    {"topic": "Classes and Objects", "question": "Which of these is a method of a class?",
     "options": ["A variable", "A function inside a class", "A package", "An import"], "correct": 1},

    # Inheritance
    {"topic": "Inheritance", "question": "Which keyword makes a Java class inherit from another?",
     "options": ["implements", "extends", "inherits", "uses"], "correct": 1},
    {"topic": "Inheritance", "question": "Inheritance mainly helps you achieve?",
     "options": ["Code reuse", "Slower code", "Less memory always", "No classes"], "correct": 0},
    {"topic": "Inheritance", "question": "Which keyword calls the parent class constructor?",
     "options": ["this", "parent", "super", "base"], "correct": 2},
    {"topic": "Inheritance", "question": "Can a Java class extend two classes at once?",
     "options": ["Yes, always", "No, not with classes", "Only with threads", "Only in Java 17"], "correct": 1},

    # Python Basics
    {"topic": "Python Basics", "question": "Which symbol starts a comment in Python?",
     "options": ["//", "#", "/*", "--"], "correct": 1},
    {"topic": "Python Basics", "question": "Which function prints output in Python?",
     "options": ["print()", "echo()", "show()", "display()"], "correct": 0},
    {"topic": "Python Basics", "question": "How does Python group code into blocks?",
     "options": ["Curly braces", "Indentation", "Semicolons", "Keywords end"], "correct": 1},
    {"topic": "Python Basics", "question": "Which is a valid Python variable name?",
     "options": ["2value", "my_value", "my-value", "class"], "correct": 1},

    # Lists and Tuples
    {"topic": "Lists and Tuples", "question": "Which collection type can be changed after creation?",
     "options": ["tuple", "list", "string", "int"], "correct": 1},
    {"topic": "Lists and Tuples", "question": "How do you get the number of items in a list?",
     "options": ["size(x)", "len(x)", "count(x)", "length(x)"], "correct": 1},
    {"topic": "Lists and Tuples", "question": "Which brackets create a tuple?",
     "options": ["[]", "{}", "()", "<>"], "correct": 2},
    {"topic": "Lists and Tuples", "question": "What is the index of the first element in a list?",
     "options": ["1", "0", "-1", "First"], "correct": 1},

    # Functions in Python
    {"topic": "Functions in Python", "question": "Which keyword defines a function in Python?",
     "options": ["func", "def", "function", "fn"], "correct": 1},
    {"topic": "Functions in Python", "question": "Which keyword sends a value back from a function?",
     "options": ["give", "return", "output", "send"], "correct": 1},
    {"topic": "Functions in Python", "question": "What is a parameter?",
     "options": ["A variable passed into a function", "A loop", "A module", "An error"], "correct": 0},
    {"topic": "Functions in Python", "question": "What does a function with no return give back?",
     "options": ["0", "None", "False", "Error"], "correct": 1},

    # Algebra Basics
    {"topic": "Algebra Basics", "question": "In 3x + 2, what is the coefficient of x?",
     "options": ["2", "3", "x", "5"], "correct": 1},
    {"topic": "Algebra Basics", "question": "What is the value of 2 to the power 3?",
     "options": ["6", "8", "9", "5"], "correct": 1},
    {"topic": "Algebra Basics", "question": "Which term is a like term of 4a?",
     "options": ["4b", "5a", "a squared", "4"], "correct": 1},
    {"topic": "Algebra Basics", "question": "What is 5 + 3 x 2?",
     "options": ["16", "11", "10", "13"], "correct": 1},

    # Linear Equations
    {"topic": "Linear Equations", "question": "Solve x + 4 = 9. What is x?",
     "options": ["4", "5", "13", "9"], "correct": 1},
    {"topic": "Linear Equations", "question": "Solve 2x = 10. What is x?",
     "options": ["20", "5", "8", "12"], "correct": 1},
    {"topic": "Linear Equations", "question": "What is the highest power of x in a linear equation?",
     "options": ["2", "3", "1", "0"], "correct": 2},
    {"topic": "Linear Equations", "question": "Solve 3x - 6 = 0. What is x?",
     "options": ["3", "2", "-2", "6"], "correct": 1},

    # Percentages and Ratios
    {"topic": "Percentages and Ratios", "question": "What is 20% of 50?",
     "options": ["5", "10", "15", "25"], "correct": 1},
    {"topic": "Percentages and Ratios", "question": "A ratio 2:3 shares a total of 10. What is the first part?",
     "options": ["4", "6", "5", "3"], "correct": 0},
    {"topic": "Percentages and Ratios", "question": "What is 1/4 written as a percentage?",
     "options": ["25%", "4%", "14%", "40%"], "correct": 0},
    {"topic": "Percentages and Ratios", "question": "Percentage = (part / whole) x ?",
     "options": ["10", "100", "1000", "50"], "correct": 1},
]


def seed(conn):
    """Insert subjects, topics and questions. The caller commits."""
    # Subjects first, remembering each new id by name.
    subject_ids = {}
    for s in SUBJECTS:
        cur = conn.execute(
            "INSERT INTO subjects (name, description) VALUES (?, ?)",
            (s["name"], s["description"]),
        )
        subject_ids[s["name"]] = cur.lastrowid

    # Topics next, remembering each new id by title.
    topic_ids = {}
    for t in TOPICS:
        cur = conn.execute(
            "INSERT INTO topics (subject_id, title, content) VALUES (?, ?, ?)",
            (subject_ids[t["subject"]], t["title"], t["content"]),
        )
        topic_ids[t["title"]] = cur.lastrowid

    # Questions last. Options A-D fill the four option columns.
    for q in QUESTIONS:
        a, b, c, d = q["options"]
        conn.execute(
            "INSERT INTO questions (topic_id, question_text, option_a, option_b, "
            "option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (topic_ids[q["topic"]], q["question"], a, b, c, d, q["correct"]),
        )

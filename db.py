import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect("resume.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        extracted_text TEXT,
        jd TEXT,
        score INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT UNIQUE,
        ph_number TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_resume(filename, text):
    conn = sqlite3.connect("resume.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO resumes (filename, extracted_text) VALUES (?, ?)",
                (filename, text))

    conn.commit()
    conn.close()

def update_jd_score(jd, score):
    conn = sqlite3.connect("resume.db")
    cur = conn.cursor()

    cur.execute("""
    UPDATE resumes 
    SET jd=?, score=? 
    WHERE id = (SELECT MAX(id) FROM resumes)
    """, (jd, score))

    conn.commit()
    conn.close()

def create_user(full_name, email, ph_number, password):
    # Hash password for basic security
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect("resume.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (full_name, email, ph_number, password) VALUES (?, ?, ?, ?)",
                    (full_name, email, ph_number, hashed_pw))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Email exists
    conn.close()
    return success

def verify_user(email, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect("resume.db")
    cur = conn.cursor()
    cur.execute("SELECT id, full_name FROM users WHERE email=? AND password=?", (email, hashed_pw))
    user = cur.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "full_name": user[1]}
    return None
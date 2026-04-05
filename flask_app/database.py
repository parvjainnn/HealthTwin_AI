import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'healthtwin_flask.db')


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Health logs per user
    c.execute("""
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            weight REAL,
            height REAL,
            steps INTEGER,
            sleep REAL,
            water REAL,
            heart_rate INTEGER,
            bmi REAL,
            health_score REAL,
            obesity_risk TEXT,
            fatigue_risk TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS patient_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            title TEXT NOT NULL,
            notes TEXT,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            ocr_text TEXT,
            ocr_engine TEXT,
            ocr_status TEXT DEFAULT 'pending',
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    _ensure_column(c, 'patient_documents', 'ocr_text', 'TEXT')
    _ensure_column(c, 'patient_documents', 'ocr_engine', 'TEXT')
    _ensure_column(c, 'patient_documents', 'ocr_status', "TEXT DEFAULT 'pending'")
    conn.commit()
    conn.close()


def _ensure_column(cursor, table_name, column_name, column_definition):
    columns = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing = {column[1] for column in columns}
    if column_name not in existing:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


def save_health_log(user_id, data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO health_logs
        (user_id, timestamp, age, gender, weight, height, steps, sleep,
         water, heart_rate, bmi, health_score, obesity_risk, fatigue_risk)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id, data['timestamp'], data['age'], data['gender'],
        data['weight'], data['height'], data['steps'], data['sleep'],
        data['water'], data['heart_rate'], data['bmi'],
        data['health_score'], data['obesity_risk'], data['fatigue_risk']
    ))
    conn.commit()
    conn.close()


def get_health_history(user_id, limit=50):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM health_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_latest_log(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM health_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT 1",
        (user_id,)
    )
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_all_health_logs(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM health_logs WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def save_patient_document(
    user_id,
    document_type,
    title,
    notes,
    original_filename,
    stored_filename,
    ocr_text=None,
    ocr_engine=None,
    ocr_status='pending'
):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO patient_documents
        (
            user_id, document_type, title, notes, original_filename, stored_filename,
            ocr_text, ocr_engine, ocr_status, uploaded_at
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id,
        document_type,
        title,
        notes,
        original_filename,
        stored_filename,
        ocr_text,
        ocr_engine,
        ocr_status,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    conn.commit()
    document_id = c.lastrowid
    conn.close()
    return document_id


def get_patient_documents(user_id, limit=100):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM patient_documents
        WHERE user_id=?
        ORDER BY uploaded_at DESC, id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_patient_document_by_id(document_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM patient_documents
        WHERE id=? AND user_id=?
        LIMIT 1
    """, (document_id, user_id))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_username(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_email(email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username, email, password_hash):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",
        (username, email, password_hash)
    )
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id


def get_user_by_id(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

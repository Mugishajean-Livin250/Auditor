# database.py
import sqlite3
import os
from datetime import datetime

DB_PATH = "data/auditors.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS auditors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    );

    CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        department TEXT,
        status TEXT DEFAULT 'Open',
        flagged INTEGER DEFAULT 0,
        date_logged TEXT DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id INTEGER,
        auditor_id INTEGER,
        due_date TEXT,
        action_taken TEXT,
        status TEXT DEFAULT 'Not Started',
        FOREIGN KEY (finding_id) REFERENCES findings(id),
        FOREIGN KEY (auditor_id) REFERENCES auditors(id)
    );

    CREATE TABLE IF NOT EXISTS auditor_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auditor_id INTEGER,
        department TEXT,
        note TEXT,
        date_written TEXT DEFAULT CURRENT_DATE,
        FOREIGN KEY (auditor_id) REFERENCES auditors(id)
    );
    """)

    # Seed auditors
    cur.execute("SELECT COUNT(*) FROM auditors")
    if cur.fetchone()[0] == 0:
        cur.executescript("""
        INSERT INTO auditors (name, username, password, role) VALUES 
        ('SHEMA Jackson', 'shema', 'pass123', 'auditor'),
        ('KARENZI Paul', 'karenzi', 'audit2024', 'auditor'),
        ('ADMIN User', 'admin', 'admin123', 'admin');
        """)

    # Seed findings
    cur.execute("SELECT COUNT(*) FROM findings")
    if cur.fetchone()[0] == 0:
        cur.executescript("""
        INSERT INTO findings (title, description, department, status, flagged)
        VALUES 
        ('Irregular Budget Usage', 'Spending over budget without approval', 'Finance', 'Open', 1),
        ('Unregistered Equipment', 'Missing inventory in records', 'Logistics', 'In Progress', 0);
        """)

    conn.commit()
    conn.close()

def fetch_assignments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.title, a.name, s.due_date, s.status, s.action_taken
        FROM assignments s
        JOIN auditors a ON s.auditor_id = a.id
        JOIN findings f ON s.finding_id = f.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def add_auditor_note(auditor_id, department, note):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO auditor_notes (auditor_id, department, note, date_written)
        VALUES (?, ?, ?, ?)
    """, (auditor_id, department, note, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_notes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.name, n.department, n.note, n.date_written
        FROM auditor_notes n
        JOIN auditors a ON n.auditor_id = a.id
        ORDER BY n.date_written DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# ✅ New function: Allow admin to add a finding
def add_finding(title, description, department, status="Open", flagged=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO findings (title, description, department, status, flagged, date_logged)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, department, status, flagged, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

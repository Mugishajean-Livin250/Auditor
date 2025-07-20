# logic.py
from database import get_connection
from datetime import datetime

def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, role 
        FROM auditors 
        WHERE username = ? AND password = ?
    """, (username, password))
    user = cur.fetchone()
    conn.close()
    return user

def fetch_auditors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, username, role 
        FROM auditors
    """)
    data = cur.fetchall()
    conn.close()
    return data

def fetch_findings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, department, status, flagged, date_logged 
        FROM findings
    """)
    data = cur.fetchall()
    conn.close()
    return data

def fetch_assignments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.title, a.name, assign.due_date, assign.status, assign.action_taken
        FROM assignments assign
        JOIN auditors a ON a.id = assign.auditor_id
        JOIN findings f ON f.id = assign.finding_id
    """)
    data = cur.fetchall()
    conn.close()
    return data

def create_auditor(name, username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO auditors (name, username, password, role) 
        VALUES (?, ?, ?, ?)
    """, (name, username, password, role))
    conn.commit()
    conn.close()

def assign_finding(finding_id, auditor_id, due_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO assignments (finding_id, auditor_id, due_date, status) 
        VALUES (?, ?, ?, ?)
    """, (finding_id, auditor_id, due_date, "Not Started"))
    conn.commit()
    conn.close()
    
def add_auditor_note(auditor_id, department, note):
    conn = get_connection()
    cur = conn.cursor()
    date_written = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO auditor_notes (auditor_id, department, note, date_written)
        VALUES (?, ?, ?, ?)
    """, (auditor_id, department, note, date_written))
    conn.commit()
    conn.close()
    
def fetch_all_notes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT an.department, a.name, an.note, an.date_written
        FROM auditor_notes an
        JOIN auditors a ON an.auditor_id = a.id
        ORDER BY an.date_written DESC
    """)
    data = cur.fetchall()
    conn.close()
    return data

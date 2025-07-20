# app.py
import streamlit as st
from logic import (
    authenticate_user,
    fetch_auditors,
    fetch_findings,
    fetch_assignments,
    create_auditor,
    assign_finding,
    add_auditor_note,
    fetch_all_notes
)
from database import init_db
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize DB and Streamlit config
st.set_page_config(page_title="Auditors Tracker", layout="wide")
init_db()

if "user" not in st.session_state:
    st.session_state.user = None

# ------------------------- LOGIN SCREEN -------------------------
def login_screen():
    st.title("Auditors Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.user = {
                "id": user[0],
                "name": user[1],
                "role": user[2],
            }
            st.success(f"Welcome {user[1]}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ------------------------- DASHBOARD -------------------------
def dashboard():
    st.subheader("📊 Dashboard Overview")
    findings = fetch_findings()

    if not findings:
        st.info("No findings available.")
        return

    df = pd.DataFrame(findings, columns=["ID", "Title", "Department", "Status", "Flagged", "Date Logged"])
    st.dataframe(df)

    chart_data = df["Status"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(chart_data, labels=chart_data.index, autopct="%1.1f%%")
    ax.set_title("Audit Status Distribution")
    st.pyplot(fig)

# ------------------------- AUDITORS TAB -------------------------
def auditors_tab():
    st.subheader("👥 Registered Auditors")
    auditors = fetch_auditors()

    if not auditors:
        st.info("No auditors found.")
        return

    df = pd.DataFrame(auditors, columns=["ID", "Name", "Username", "Role"])
    st.dataframe(df)

# ------------------------- ASSIGNMENTS TAB -------------------------
def assignments_tab():
    st.subheader("🗂️ Audit Assignments")
    assignments = fetch_assignments()

    if not assignments:
        st.info("No assignments found.")
        return

    df = pd.DataFrame(assignments, columns=["Finding", "Auditor", "Due Date", "Status", "Action Taken"])
    st.dataframe(df)

    # Show note writing only to auditors
    if st.session_state.user and st.session_state.user["role"] == "auditor":
        st.subheader("📝 Write a Note About Audited Department")
        dept = st.text_input("Department Name")
        note = st.text_area("Note")
        if st.button("Submit Note"):
            if dept and note:
                add_auditor_note(st.session_state.user["id"], dept, note)
                st.success("Note submitted successfully.")
                st.rerun()
            else:
                st.warning("Please fill all fields.")

# ------------------------- AUDITOR NOTES TAB -------------------------
def auditor_notes_tab():
    st.subheader("📝 Auditor Notes (Admin Only)")
    notes = fetch_all_notes()

    if not notes:
        st.info("No auditor notes available.")
        return

    df = pd.DataFrame(notes, columns=["Department", "Auditor", "Note", "Date Written"])
    st.dataframe(df)

# ------------------------- ADD AUDITOR -------------------------
def add_auditor_form():
    st.subheader("➕ Add New Auditor (Admin Only)")
    with st.form("add_auditor_form"):
        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password")
        role = st.selectbox("Role", ["auditor", "admin"])
        submitted = st.form_submit_button("Add Auditor")
        if submitted:
            if name and username and password:
                create_auditor(name, username, password, role)
                st.success(f"Auditor '{name}' added.")
                st.rerun()
            else:
                st.warning("Please fill all fields.")

# ------------------------- ASSIGN FINDING -------------------------
def assign_finding_form():
    st.subheader("📝 Assign Audit Finding")

    findings = fetch_findings()
    auditors = fetch_auditors()

    if not findings:
        st.warning("No findings available to assign.")
        return
    if not auditors:
        st.warning("No auditors available to assign.")
        return

    # Create mapping for dropdowns
    finding_map = {f"{f[0]} - {f[1]}": f[0] for f in findings}
    auditor_map = {f"{a[0]} - {a[1]}": a[0] for a in auditors}

    selected_finding = st.selectbox("Select Finding", list(finding_map.keys()))
    selected_auditor = st.selectbox("Assign To", list(auditor_map.keys()))
    due_date = st.date_input("Due Date")

    if st.button("Assign"):
        try:
            assign_finding(
                finding_map[selected_finding],
                auditor_map[selected_auditor],
                due_date.isoformat()
            )
            st.success("Finding assigned successfully.")
            st.rerun()
        except KeyError as e:
            st.error(f"Assignment failed. KeyError: {e}")

# ------------------------- MAIN APP FLOW -------------------------
if st.session_state.user:
    st.sidebar.title("Navigation")

    # Dynamically build menu based on user role
    menu_options = ["Dashboard", "Auditors", "Assignments"]
    if st.session_state.user["role"] == "admin":
        menu_options += ["Add Auditor", "Assign Task", "Auditor Notes"]
    menu_options += ["Logout"]

    choice = st.sidebar.selectbox("Menu", menu_options)

    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user['name']} ({st.session_state.user['role']})")

    if choice == "Dashboard":
        dashboard()
    elif choice == "Auditors":
        auditors_tab()
    elif choice == "Assignments":
        assignments_tab()
    elif choice == "Add Auditor" and st.session_state.user["role"] == "admin":
        add_auditor_form()
    elif choice == "Assign Task" and st.session_state.user["role"] == "admin":
        assign_finding_form()
    elif choice == "Auditor Notes" and st.session_state.user["role"] == "admin":
        auditor_notes_tab()
    elif choice == "Logout":
        st.session_state.user = None
        st.rerun()

else:
    login_screen()

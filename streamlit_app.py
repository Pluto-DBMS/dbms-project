import streamlit as st
import sqlite3
import json
import urllib.request
import plotly.graph_objects as go

st.set_page_config(page_title="Academic Progression & Portfolio Tracker", layout="wide")

DB_FILE = "student_progression.db"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwWyPgMGbI7w8oEBQJj38l1W2NEAYOHQV1bAp8yt6sW22cm2-k9h9j_6A3I5NJFrT8d/exec"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def sync_to_google_sheets(payload):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(WEBHOOK_URL, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print("Webhook Error:", e)

st.title("🎓 Student Academic Progression & Portfolio Registry")

# Sidebar: Search & Discovery
st.sidebar.header("🔍 Student Discovery")
search_term = st.sidebar.text_input("Search Student by Name")

conn = get_connection()
c = conn.cursor()

if search_term.strip():
    c.execute("SELECT student_id, full_name, admission_year, ssc_score, hsc_score FROM student_profiles WHERE full_name LIKE ? ORDER BY full_name", (f"%{search_term.strip()}%",))
else:
    c.execute("SELECT student_id, full_name, admission_year, ssc_score, hsc_score FROM student_profiles ORDER BY full_name")

students = c.fetchall()

if students:
    student_dict = {f"{row[1]} [{row[0]}]": row for row in students}
    chosen_label = st.sidebar.selectbox("Select Student Profile", list(student_dict.keys()))
    selected_row = student_dict[chosen_label]
    sid, sname, adm_year, ssc_val, hsc_val = selected_row
else:
    st.sidebar.warning("No student records found.")
    selected_row = None

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Progression Curve & Drop Years",
    "📑 Subject Theory & Lab Marks",
    "🏆 Segregated Portfolios",
    "➕ Data Entry & Cloud Sync"
])

# 1. Progression Visuals
with tab1:
    if selected_row:
        st.subheader(f"Academic Overview: {sname} ({sid})")
        col1, col2, col3 = st.columns(3)
        col1.metric("Admission Year", adm_year)
        col2.metric("SSC Metric", f"{ssc_val}%")
        col3.metric("HSC Metric", f"{hsc_val}%")

        c.execute("""
            SELECT sem_id, semester_number, academic_year, sgpa, cgpa, is_drop_year 
            FROM academic_semesters 
            WHERE student_id = ? 
            ORDER BY semester_number ASC
        """, (sid,))
        sem_records = c.fetchall()

        if sem_records:
            sems = [r[1] for r in sem_records]
            sgpas = [r[3] for r in sem_records]
            drops = [r[5] for r in sem_records]

            fig = go.Figure()
            # Standard Line
            fig.add_trace(go.Scatter(
                x=sems, y=sgpas,
                mode="lines+markers",
                name="Regular Semester",
                line=dict(color="#1f77b4", width=3),
                marker=dict(size=8)
            ))

            # Drop Year Highlight
            drop_x = [sems[i] for i in range(len(sems)) if drops[i] == 1]
            drop_y = [sgpas[i] for i in range(len(sems)) if drops[i] == 1]
            if drop_x:
                fig.add_trace(go.Scatter(
                    x=drop_x, y=drop_y,
                    mode="markers",
                    name="Drop / Gap Year",
                    marker=dict(color="#d90429", size=14, symbol="square-x")
                ))

            fig.update_layout(
                title="SGPA Progression Curve with Academic Gap Detection",
                xaxis=dict(title="Semester Sequence", tickmode="linear", dtick=1),
                yaxis=dict(title="SGPA (0 - 10 Scale)", range=[0, 10.5]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

            table_data = [{
                "Sem ID": r[0], "Semester": r[1], "Academic Year": r[2], 
                "SGPA": r[3], "CGPA": r[4], 
                "Status": "DROP / GAP YEAR" if r[5] == 1 else "REGULAR"
            } for r in sem_records]
            st.dataframe(table_data, use_container_width=True)
        else:
            st.info("No semester progression logged for this student.")

# 2. Subject Marks
with tab2:
    if selected_row:
        st.subheader("Curricular Performance Breakdown")
        f_type = st.radio("Filter Format", ["All", "Theory", "Laboratory"], horizontal=True)

        if f_type == "All":
            c.execute("""
                SELECT s.semester_number, e.course_code, e.course_name, e.course_type, e.internal_score, e.endsem_score, e.status
                FROM subject_evaluations e
                JOIN academic_semesters s ON e.sem_id = s.sem_id
                WHERE s.student_id = ?
                ORDER BY s.semester_number
            """, (sid,))
        else:
            c.execute("""
                SELECT s.semester_number, e.course_code, e.course_name, e.course_type, e.internal_score, e.endsem_score, e.status
                FROM subject_evaluations e
                JOIN academic_semesters s ON e.sem_id = s.sem_id
                WHERE s.student_id = ? AND e.course_type = ?
                ORDER BY s.semester_number
            """, (sid, f_type))

        marks = c.fetchall()
        if marks:
            marks_data = [{
                "Sem": m[0], "Code": m[1], "Subject Name": m[2], 
                "Type": m[3], "Internal (20)": m[4], "Endsem (80)": m[5], "Result": m[6]
            } for m in marks]
            st.dataframe(marks_data, use_container_width=True)
        else:
            st.info("No subject marks found under this filter.")

# 3. Segregated Portfolios
with tab3:
    if selected_row:
        p1, p2 = st.columns(2)
        with p1:
            st.markdown("#### Seminars Portfolio")
            sem_filter = st.radio("Seminar Tier", ["All", "Internal", "External"], horizontal=True)
            if sem_filter == "All":
                c.execute("SELECT seminar_title, tier, host_institution FROM seminar_records WHERE student_id = ?", (sid,))
            else:
                c.execute("SELECT seminar_title, tier, host_institution FROM seminar_records WHERE student_id = ? AND tier = ?", (sid, sem_filter))
            sems_list = c.fetchall()
            st.dataframe([{"Title": r[0], "Tier": r[1], "Host": r[2]} for r in sems_list], use_container_width=True)

        with p2:
            st.markdown("#### Activities Portfolio")
            act_filter = st.radio("Domain", ["All", "Technical", "Co-curricular", "Extracurricular"], horizontal=True)
            if act_filter == "All":
                c.execute("SELECT activity_name, domain, position_attained FROM activity_records WHERE student_id = ?", (sid,))
            else:
                c.execute("SELECT activity_name, domain, position_attained FROM activity_records WHERE student_id = ? AND domain = ?", (sid, act_filter))
            acts_list = c.fetchall()
            st.dataframe([{"Activity Name": r[0], "Domain": r[1], "Achievement": r[2]} for r in acts_list], use_container_width=True)

# 4. Data Entry & Live Sync
with tab4:
    st.subheader("Manage Database & Cloud Sync")
    if selected_row:
        with st.form("add_sem_form"):
            st.write(f"Appending Record for: **{sname}** ({sid})")
            f_sem = st.selectbox("Semester", list(range(1, 9)))
            f_ay = st.text_input("Academic Year (e.g. 2024-2025)", "2024-2025")
            f_drop = st.checkbox("Mark as Drop / Gap Year")
            f_sgpa = st.number_input("SGPA (0 - 10)", min_value=0.0, max_value=10.0, value=8.50)
            f_cgpa = st.number_input("CGPA (0 - 10)", min_value=0.0, max_value=10.0, value=8.60)

            st.markdown("---")
            st.write("**Subject Marks (Theory / Lab)**")
            f_code = st.text_input("Subject Code", "ECC501")
            f_sname = st.text_input("Subject Name", "Digital Communication")
            f_type = st.selectbox("Format", ["Theory", "Laboratory"])
            f_int = st.number_input("Internal Score (0-20)", 0, 20, 18)
            f_end = st.number_input("Endsem Score (0-80)", 0, 80, 68)

            submitted = st.form_submit_button("Commit & Sync to Google Sheets")
            if submitted:
                try:
                    c.execute("""
                        INSERT INTO academic_semesters (student_id, semester_number, academic_year, is_drop_year, sgpa, cgpa)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (sid, f_sem, f_ay, 1 if f_drop else 0, f_sgpa, f_cgpa))
                    new_id = c.lastrowid
                    status = "PASS" if (f_int + f_end) >= 40 else "FAIL"
                    c.execute("""
                        INSERT INTO subject_evaluations (sem_id, course_code, course_name, course_type, internal_score, endsem_score, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (new_id, f_code, f_sname, f_type, f_int, f_end, status))
                    conn.commit()

                    payload = {
                        "action": "SEMESTER_COMMITTED",
                        "student_id": sid,
                        "name": sname,
                        "academic_year": f_ay,
                        "semester_number": f_sem,
                        "sgpa": f_sgpa,
                        "cgpa": f_cgpa,
                        "is_drop_year": 1 if f_drop else 0
                    }
                    sync_to_google_sheets(payload)
                    st.success("Record saved and synced to Google Spreadsheet!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Error: {err}")

conn.close()

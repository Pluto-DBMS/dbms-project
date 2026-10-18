import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
import urllib.request

DB_FILE = "student_progression.db"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwWyPgMGbI7w8oEBQJj38l1W2NEAYOHQV1bAp8yt6sW22cm2-k9h9j_6A3I5NJFrT8d/exec"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def sync_to_google_sheets(payload):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            WEBHOOK_URL, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print("Webhook Dispatch Note:", e)

class StudentTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Academic Progression & Portfolio Registry")
        self.root.geometry("1100x750")

        self.current_student_id = None
        self.current_student_name = ""
        self.build_ui()
        self.load_students()

    def build_ui(self):
        # Top Discovery Panel
        search_frame = ttk.LabelFrame(self.root, text=" Student Discovery & Search ", padding=10)
        search_frame.pack(fill="x", padx=12, pady=6)

        ttk.Label(search_frame, text="Search Name:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.load_students())
        ttk.Entry(search_frame, textvariable=self.search_var, width=22).pack(side="left", padx=5)

        ttk.Label(search_frame, text="Select Profile:").pack(side="left", padx=10)
        self.student_combobox = ttk.Combobox(search_frame, state="readonly", width=38)
        self.student_combobox.pack(side="left", padx=5)
        self.student_combobox.bind("<<ComboboxSelected>>", self.on_student_selected)

        ttk.Button(search_frame, text="Refresh All", command=self.refresh_current_view).pack(side="right", padx=5)

        # Tabbed Panes
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=6)

        # Tab 1: Progression Curve
        self.tab_progression = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_progression, text="Progression Curve & Drop Years")
        self.setup_progression_tab()

        # Tab 2: Subject Breakdown
        self.tab_marks = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_marks, text="Subject Theory & Lab Marks")
        self.setup_marks_tab()

        # Tab 3: Portfolios
        self.tab_portfolios = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_portfolios, text="Segregated Portfolios")
        self.setup_portfolios_tab()

        # Tab 4: Data Entry
        self.tab_entry = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_entry, text="Data Entry Management")
        self.setup_entry_tab()

    def setup_progression_tab(self):
        self.metrics_label = ttk.Label(self.tab_progression, text="Select a student to inspect records.", font=("Arial", 10, "bold"))
        self.metrics_label.pack(anchor="w", pady=4)

        self.canvas = tk.Canvas(self.tab_progression, bg="#ffffff", height=300, relief="solid", bd=1)
        self.canvas.pack(fill="both", expand=True, pady=6)

        table_frame = ttk.Frame(self.tab_progression)
        table_frame.pack(fill="x", pady=4)
        
        cols = ("Sem ID", "Semester", "Academic Year", "SGPA", "CGPA", "Academic Status")
        self.prog_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=5)
        for col in cols:
            self.prog_tree.heading(col, text=col)
            self.prog_tree.column(col, width=120, anchor="center")
        self.prog_tree.pack(side="left", fill="x", expand=True)

        btn_box = ttk.Frame(table_frame)
        btn_box.pack(side="right", padx=6)
        ttk.Button(btn_box, text="Delete Selected Sem", command=self.delete_selected_semester).pack(pady=4)

    def setup_marks_tab(self):
        filter_bar = ttk.Frame(self.tab_marks)
        filter_bar.pack(fill="x", pady=4)
        ttk.Label(filter_bar, text="Filter Evaluation Type:").pack(side="left", padx=5)
        self.marks_filter_var = tk.StringVar(value="All")
        for f in ["All", "Theory", "Laboratory"]:
            ttk.Radiobutton(filter_bar, text=f, variable=self.marks_filter_var, value=f, command=self.load_marks).pack(side="left", padx=5)

        cols = ("Sem", "Course Code", "Course Name", "Type", "Internal (20)", "Endsem (80)", "Status")
        self.marks_tree = ttk.Treeview(self.tab_marks, columns=cols, show="headings", height=14)
        for col in cols:
            self.marks_tree.heading(col, text=col)
            self.marks_tree.column(col, width=120, anchor="center")
        self.marks_tree.pack(fill="both", expand=True, pady=4)

    def setup_portfolios_tab(self):
        paned = ttk.PanedWindow(self.tab_portfolios, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Seminars Frame
        f_sem = ttk.LabelFrame(paned, text=" Seminars Portfolio ", padding=6)
        paned.add(f_sem, weight=1)
        sem_bar = ttk.Frame(f_sem)
        sem_bar.pack(fill="x", pady=2)
        ttk.Label(sem_bar, text="Filter Tier:").pack(side="left", padx=4)
        self.sem_filter_var = tk.StringVar(value="All")
        for val in ["All", "Internal", "External"]:
            ttk.Radiobutton(sem_bar, text=val, variable=self.sem_filter_var, value=val, command=self.load_portfolios).pack(side="left", padx=4)

        self.sem_tree = ttk.Treeview(f_sem, columns=("Title", "Tier", "Host"), show="headings")
        for c in ("Title", "Tier", "Host"):
            self.sem_tree.heading(c, text=c)
            self.sem_tree.column(c, width=120, anchor="w")
        self.sem_tree.pack(fill="both", expand=True)

        # Activities Frame
        f_act = ttk.LabelFrame(paned, text=" Activities & Extracurriculars ", padding=6)
        paned.add(f_act, weight=1)
        act_bar = ttk.Frame(f_act)
        act_bar.pack(fill="x", pady=2)
        ttk.Label(act_bar, text="Filter Domain:").pack(side="left", padx=4)
        self.act_filter_var = tk.StringVar(value="All")
        for val in ["All", "Technical", "Co-curricular", "Extracurricular"]:
            ttk.Radiobutton(act_bar, text=val, variable=self.act_filter_var, value=val, command=self.load_portfolios).pack(side="left", padx=2)

        self.act_tree = ttk.Treeview(f_act, columns=("Name", "Domain", "Standing"), show="headings")
        for c in ("Name", "Domain", "Standing"):
            self.act_tree.heading(c, text=c)
            self.act_tree.column(c, width=120, anchor="w")
        self.act_tree.pack(fill="both", expand=True)

    def setup_entry_tab(self):
        container = ttk.Notebook(self.tab_entry)
        container.pack(fill="both", expand=True)

        # Register Student
        sub_student = ttk.Frame(container, padding=12)
        container.add(sub_student, text="Register Student")

        ttk.Label(sub_student, text="Student ID:").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_sid = ttk.Entry(sub_student, width=28)
        self.ent_sid.grid(row=0, column=1, pady=4)

        ttk.Label(sub_student, text="Full Name:").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_sname = ttk.Entry(sub_student, width=28)
        self.ent_sname.grid(row=1, column=1, pady=4)

        ttk.Label(sub_student, text="Email:").grid(row=2, column=0, sticky="w", pady=4)
        self.ent_semail = ttk.Entry(sub_student, width=28)
        self.ent_semail.grid(row=2, column=1, pady=4)

        ttk.Label(sub_student, text="Admission Year:").grid(row=3, column=0, sticky="w", pady=4)
        self.ent_syear = ttk.Entry(sub_student, width=28)
        self.ent_syear.insert(0, "2024")
        self.ent_syear.grid(row=3, column=1, pady=4)

        ttk.Label(sub_student, text="SSC %:").grid(row=4, column=0, sticky="w", pady=4)
        self.ent_sssc = ttk.Entry(sub_student, width=28)
        self.ent_sssc.insert(0, "85.0")
        self.ent_sssc.grid(row=4, column=1, pady=4)

        ttk.Label(sub_student, text="HSC %:").grid(row=5, column=0, sticky="w", pady=4)
        self.ent_shsc = ttk.Entry(sub_student, width=28)
        self.ent_shsc.insert(0, "80.0")
        self.ent_shsc.grid(row=5, column=1, pady=4)

        ttk.Button(sub_student, text="Save Student", command=self.save_student).grid(row=6, column=1, sticky="e", pady=8)

        # Add Semester & Sync
        sub_sem = ttk.Frame(container, padding=12)
        container.add(sub_sem, text="Add Semester & Sync to Sheets")

        ttk.Label(sub_sem, text="Semester (1-8):").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_semnum = ttk.Spinbox(sub_sem, from_=1, to=8, width=26)
        self.ent_semnum.grid(row=0, column=1, pady=4)

        ttk.Label(sub_sem, text="Academic Year:").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_ayear = ttk.Entry(sub_sem, width=28)
        self.ent_ayear.insert(0, "2024-2025")
        self.ent_ayear.grid(row=1, column=1, pady=4)

        self.var_drop = tk.IntVar(value=0)
        ttk.Checkbutton(sub_sem, text="Mark as Drop / Gap Year", variable=self.var_drop).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(sub_sem, text="SGPA (0-10):").grid(row=3, column=0, sticky="w", pady=4)
        self.ent_sgpa = ttk.Entry(sub_sem, width=28)
        self.ent_sgpa.insert(0, "8.25")
        self.ent_sgpa.grid(row=3, column=1, pady=4)

        ttk.Label(sub_sem, text="CGPA (0-10):").grid(row=4, column=0, sticky="w", pady=4)
        self.ent_cgpa = ttk.Entry(sub_sem, width=28)
        self.ent_cgpa.insert(0, "8.30")
        self.ent_cgpa.grid(row=4, column=1, pady=4)

        ttk.Label(sub_sem, text="Subject Code:").grid(row=5, column=0, sticky="w", pady=4)
        self.ent_ccode = ttk.Entry(sub_sem, width=28)
        self.ent_ccode.insert(0, "CS401")
        self.ent_ccode.grid(row=5, column=1, pady=4)

        ttk.Label(sub_sem, text="Subject Name:").grid(row=6, column=0, sticky="w", pady=4)
        self.ent_cname = ttk.Entry(sub_sem, width=28)
        self.ent_cname.insert(0, "Database Management Systems")
        self.ent_cname.grid(row=6, column=1, pady=4)

        ttk.Label(sub_sem, text="Course Format:").grid(row=7, column=0, sticky="w", pady=4)
        self.combo_ctype = ttk.Combobox(sub_sem, values=["Theory", "Laboratory"], state="readonly", width=26)
        self.combo_ctype.current(0)
        self.combo_ctype.grid(row=7, column=1, pady=4)

        ttk.Label(sub_sem, text="Internal Marks (0-20):").grid(row=8, column=0, sticky="w", pady=4)
        self.ent_cint = ttk.Entry(sub_sem, width=28)
        self.ent_cint.insert(0, "18")
        self.ent_cint.grid(row=8, column=1, pady=4)

        ttk.Label(sub_sem, text="Endsem Marks (0-80):").grid(row=9, column=0, sticky="w", pady=4)
        self.ent_cend = ttk.Entry(sub_sem, width=28)
        self.ent_cend.insert(0, "68")
        self.ent_cend.grid(row=9, column=1, pady=4)

        ttk.Button(sub_sem, text="Commit & Sync to Google Sheets", command=self.save_semester_and_sync).grid(row=10, column=1, sticky="e", pady=8)

    def load_students(self):
        conn = get_connection()
        cur = conn.cursor()
        q = self.search_var.get().strip()
        if q:
            cur.execute("SELECT student_id, full_name FROM student_profiles WHERE full_name LIKE ? ORDER BY full_name", (f"%{q}%",))
        else:
            cur.execute("SELECT student_id, full_name FROM student_profiles ORDER BY full_name")
        rows = cur.fetchall()
        conn.close()

        self.student_map = {f"{name} [{sid}]": sid for sid, name in rows}
        options = list(self.student_map.keys())
        self.student_combobox["values"] = options

        if options:
            # Auto-select the top matching result on every keystroke
            self.student_combobox.set(options[0])
            self.current_student_id = self.student_map[options[0]]
            self.refresh_current_view()
        else:
            self.student_combobox.set("No match found")
            self.canvas.delete("all")
            self.canvas.create_text(400, 150, text="No matching student profile found", font=("Arial", 11, "italic"), fill="#888888")
            self.metrics_label.config(text="No matching student profile found.")
            for item in self.prog_tree.get_children():
                self.prog_tree.delete(item)
            for item in self.marks_tree.get_children():
                self.marks_tree.delete(item)
            for item in self.sem_tree.get_children():
                self.sem_tree.delete(item)
            for item in self.act_tree.get_children():
                self.act_tree.delete(item)

    def on_student_selected(self, event):
        sel = self.student_combobox.get()
        if sel in self.student_map:
            self.current_student_id = self.student_map[sel]
            self.refresh_current_view()

    def refresh_current_view(self):
        if self.current_student_id:
            self.load_student_details()
            self.draw_progression_canvas()
            self.load_marks()
            self.load_portfolios()

    def load_student_details(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT full_name, admission_year, ssc_score, hsc_score FROM student_profiles WHERE student_id = ?", (self.current_student_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            self.current_student_name = row[0]
            self.metrics_label.config(text=f"Student: {row[0]} | ID: {self.current_student_id} | Admission: {row[1]} | SSC: {row[2]}% | HSC: {row[3]}%")

    def draw_progression_canvas(self):
        self.canvas.delete("all")
        for item in self.prog_tree.get_children():
            self.prog_tree.delete(item)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT sem_id, semester_number, academic_year, sgpa, cgpa, is_drop_year FROM academic_semesters WHERE student_id = ? ORDER BY semester_number", (self.current_student_id,))
        records = cur.fetchall()
        conn.close()

        if not records:
            self.canvas.create_text(450, 150, text="No progression logged for this student", font=("Arial", 12, "italic"), fill="#666666")
            return

        for r in records:
            status_text = "DROP / GAP YEAR" if r[5] == 1 else "REGULAR"
            self.prog_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], status_text))

        # Canvas boundaries
        c_w, c_h = 800, 290
        x_start, x_end = 80, 750
        y_bottom, y_top = 240, 40

        self.canvas.create_line(x_start, y_bottom, x_end, y_bottom, width=2, fill="#333333")
        self.canvas.create_line(x_start, y_top, x_start, y_bottom, width=2, fill="#333333")

        for tick in range(0, 11, 2):
            y = y_bottom - (tick / 10.0) * (y_bottom - y_top)
            self.canvas.create_line(x_start - 5, y, x_start, y, fill="#333333")
            self.canvas.create_line(x_start, y, x_end, y, fill="#f0f0f0", dash=(2, 2))
            self.canvas.create_text(x_start - 18, y, text=str(tick), font=("Arial", 8))

        self.canvas.create_text(400, 20, text="Semester Progression Curve (SGPA) & Drop Year Marker", font=("Arial", 11, "bold"), fill="#1a1a1a")
        
        self.canvas.create_oval(600, 15, 608, 23, fill="#1f77b4", outline="#1f77b4")
        self.canvas.create_text(645, 19, text="Regular Sem", font=("Arial", 8))
        self.canvas.create_rectangle(690, 14, 700, 24, fill="#d90429", outline="#000000")
        self.canvas.create_text(745, 19, text="Drop/Gap Year", font=("Arial", 8, "bold"), fill="#d90429")

        points = []
        step_x = (x_end - x_start) / 8.0

        for r in records:
            _, sem_num, _, sgpa, _, is_drop = r
            px = x_start + (sem_num) * step_x - (step_x / 2.0)
            py = y_bottom - (sgpa / 10.0) * (y_bottom - y_top)
            points.append((px, py, sem_num, sgpa, is_drop))
            self.canvas.create_text(px, y_bottom + 15, text=f"Sem {sem_num}", font=("Arial", 8, "bold"))

        for i in range(len(points) - 1):
            self.canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill="#1f77b4", width=3)

        for p in points:
            px, py, sem_num, sgpa, is_drop = p
            if is_drop == 1:
                self.canvas.create_rectangle(px - 9, py - 9, px + 9, py + 9, fill="#d90429", outline="#000000", width=2)
                self.canvas.create_line(px - 5, py - 5, px + 5, py + 5, fill="#ffffff", width=2)
                self.canvas.create_line(px - 5, py + 5, px + 5, py - 5, fill="#ffffff", width=2)
                self.canvas.create_text(px, py - 18, text=f"{sgpa} (DROP)", font=("Arial", 8, "bold"), fill="#d90429")
            else:
                self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6, fill="#1f77b4", outline="#ffffff", width=2)
                self.canvas.create_text(px, py - 15, text=f"{sgpa}", font=("Arial", 8, "bold"), fill="#1f77b4")

    def load_marks(self):
        for item in self.marks_tree.get_children():
            self.marks_tree.delete(item)
        conn = get_connection()
        cur = conn.cursor()
        f_type = self.marks_filter_var.get()
        if f_type == "All":
            cur.execute("""
                SELECT s.semester_number, e.course_code, e.course_name, e.course_type, e.internal_score, e.endsem_score, e.status
                FROM subject_evaluations e
                JOIN academic_semesters s ON e.sem_id = s.sem_id
                WHERE s.student_id = ?
                ORDER BY s.semester_number
            """, (self.current_student_id,))
        else:
            cur.execute("""
                SELECT s.semester_number, e.course_code, e.course_name, e.course_type, e.internal_score, e.endsem_score, e.status
                FROM subject_evaluations e
                JOIN academic_semesters s ON e.sem_id = s.sem_id
                WHERE s.student_id = ? AND e.course_type = ?
                ORDER BY s.semester_number
            """, (self.current_student_id, f_type))
            
        for row in cur.fetchall():
            self.marks_tree.insert("", "end", values=row)
        conn.close()

    def load_portfolios(self):
        for item in self.sem_tree.get_children():
            self.sem_tree.delete(item)
        for item in self.act_tree.get_children():
            self.act_tree.delete(item)

        conn = get_connection()
        cur = conn.cursor()

        sem_t = self.sem_filter_var.get()
        if sem_t == "All":
            cur.execute("SELECT seminar_title, tier, host_institution FROM seminar_records WHERE student_id = ?", (self.current_student_id,))
        else:
            cur.execute("SELECT seminar_title, tier, host_institution FROM seminar_records WHERE student_id = ? AND tier = ?", (self.current_student_id, sem_t))
        for row in cur.fetchall():
            self.sem_tree.insert("", "end", values=row)

        act_t = self.act_filter_var.get()
        if act_t == "All":
            cur.execute("SELECT activity_name, domain, position_attained FROM activity_records WHERE student_id = ?", (self.current_student_id,))
        else:
            cur.execute("SELECT activity_name, domain, position_attained FROM activity_records WHERE student_id = ? AND domain = ?", (self.current_student_id, act_t))
        for row in cur.fetchall():
            self.act_tree.insert("", "end", values=row)

        conn.close()

    def delete_selected_semester(self):
        selected_item = self.prog_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please click on a semester row in the table first.")
            return

        item_values = self.prog_tree.item(selected_item[0])['values']
        sem_id = item_values[0]
        sem_num = item_values[1]

        confirm = messagebox.askyesno("Confirm Deletion", f"Delete Semester {sem_num} record? All linked subject marks will cascade delete.")
        if not confirm:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM academic_semesters WHERE sem_id = ?", (sem_id,))
        conn.commit()
        conn.close()

        # Log deletion to Google Sheet
        payload = {
            "action": "RECORD_DELETED",
            "student_id": self.current_student_id,
            "name": self.current_student_name,
            "academic_year": str(item_values[2]),
            "semester_number": int(sem_num),
            "sgpa": float(item_values[3]),
            "cgpa": float(item_values[4]),
            "is_drop_year": 1 if "DROP" in str(item_values[5]) else 0
        }
        sync_to_google_sheets(payload)

        messagebox.showinfo("Deleted", f"Semester {sem_num} deleted and sync dispatch sent.")
        self.refresh_current_view()

    def save_student(self):
        sid = self.ent_sid.get().strip()
        sname = self.ent_sname.get().strip()
        semail = self.ent_semail.get().strip()
        try:
            year = int(self.ent_syear.get().strip())
            ssc = float(self.ent_sssc.get().strip())
            hsc = float(self.ent_shsc.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "Admission Year, SSC, and HSC must be valid numeric values.")
            return

        if not sid or not sname or not semail:
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO student_profiles VALUES (?,?,?,?,?,?)", (sid, sname, semail, year, ssc, hsc))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Student {sname} registered successfully.")
            self.load_students()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Constraint Error", str(e))

    def save_semester_and_sync(self):
        if not self.current_student_id:
            messagebox.showerror("Error", "Please select a student from discovery first.")
            return

        try:
            sem_num = int(self.ent_semnum.get())
            ayear = self.ent_ayear.get().strip()
            is_drop = self.var_drop.get()
            sgpa = float(self.ent_sgpa.get())
            cgpa = float(self.ent_cgpa.get())
            ccode = self.ent_ccode.get().strip()
            cname = self.ent_cname.get().strip()
            ctype = self.combo_ctype.get()
            cint = int(self.ent_cint.get())
            cend = int(self.ent_cend.get())
            cstatus = "PASS" if (cint + cend) >= 40 else "FAIL"
        except ValueError:
            messagebox.showerror("Validation Error", "Please verify numerical ranges for marks and SGPA.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO academic_semesters (student_id, semester_number, academic_year, is_drop_year, sgpa, cgpa)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.current_student_id, sem_num, ayear, is_drop, sgpa, cgpa))
            new_sem_id = cur.lastrowid

            cur.execute("""
                INSERT INTO subject_evaluations (sem_id, course_code, course_name, course_type, internal_score, endsem_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (new_sem_id, ccode, cname, ctype, cint, cend, cstatus))
            conn.commit()
            conn.close()

            payload = {
                "action": "SEMESTER_COMMITTED",
                "student_id": self.current_student_id,
                "name": self.current_student_name,
                "academic_year": ayear,
                "semester_number": sem_num,
                "sgpa": sgpa,
                "cgpa": cgpa,
                "is_drop_year": is_drop
            }
            sync_to_google_sheets(payload)

            messagebox.showinfo("Success", "Semester recorded in database and synced to Google Spreadsheet.")
            self.refresh_current_view()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Constraint Error", str(e))

if __name__ == "__main__":
    app_root = tk.Tk()
    app = StudentTrackerApp(app_root)
    app_root.mainloop()
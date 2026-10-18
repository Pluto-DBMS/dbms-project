import sqlite3

DB_FILE = "student_progression.db"

def build_mu_ece_database():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()

    # Clear existing tables to reset clean foreign key mapping
    c.execute("DELETE FROM activity_records;")
    c.execute("DELETE FROM seminar_records;")
    c.execute("DELETE FROM subject_evaluations;")
    c.execute("DELETE FROM academic_semesters;")
    c.execute("DELETE FROM student_profiles;")

    # 1. 10 Representative Student Profiles
    students = [
        ("TE01A", "Aarav Sharma", "aarav.sharma@ece.mu.edu", 2022, 92.4, 89.2),
        ("TE02B", "Rohan Patil", "rohan.patil@ece.mu.edu", 2021, 78.5, 71.0),
        ("TE03C", "Ananya Iyer", "ananya.iyer@ece.mu.edu", 2022, 95.8, 94.6),
        ("TE04D", "Siddharth Verma", "siddharth.v@ece.mu.edu", 2020, 81.2, 74.0),
        ("TE05E", "Pooja Deshmukh", "pooja.d@ece.mu.edu", 2022, 87.5, 84.8),
        ("TE06F", "Aditya Kulkarni", "aditya.k@ece.mu.edu", 2021, 74.0, 68.5),
        ("TE07G", "Neha Nair", "neha.nair@ece.mu.edu", 2022, 89.6, 88.0),
        ("TE08H", "Varun Mehta", "varun.m@ece.mu.edu", 2022, 83.4, 80.5),
        ("TE09I", "Tanvi Joshi", "tanvi.j@ece.mu.edu", 2021, 80.2, 77.4),
        ("TE10J", "Kunal Shah", "kunal.shah@ece.mu.edu", 2022, 88.0, 85.5)
    ]
    c.executemany("INSERT INTO student_profiles VALUES (?,?,?,?,?,?)", students)

    # 2. Semester Progressions
    semesters = [
        # Aarav Sharma: High consistent performance (Sem 1 to 6)
        ("TE01A", 1, "2022-2023", 0, 8.85, 8.85),
        ("TE01A", 2, "2022-2023", 0, 9.10, 8.97),
        ("TE01A", 3, "2023-2024", 0, 9.25, 9.06),
        ("TE01A", 4, "2023-2024", 0, 9.40, 9.15),
        ("TE01A", 5, "2024-2025", 0, 9.55, 9.23),
        ("TE01A", 6, "2024-2025", 0, 9.70, 9.31),

        # Rohan Patil: Marked Drop/Gap at Sem 3
        ("TE02B", 1, "2021-2022", 0, 7.20, 7.20),
        ("TE02B", 2, "2021-2022", 0, 6.75, 6.98),
        ("TE02B", 3, "2023-2024", 1, 6.30, 6.75),  # Gap year marked
        ("TE02B", 4, "2023-2024", 0, 7.15, 6.85),
        ("TE02B", 5, "2024-2025", 0, 7.60, 7.00),
        ("TE02B", 6, "2024-2025", 0, 7.90, 7.15),

        # Ananya Iyer: Department Top Ranker (Sem 1 to 6)
        ("TE03C", 1, "2022-2023", 0, 9.55, 9.55),
        ("TE03C", 2, "2022-2023", 0, 9.68, 9.61),
        ("TE03C", 3, "2023-2024", 0, 9.80, 9.67),
        ("TE03C", 4, "2023-2024", 0, 9.85, 9.72),
        ("TE03C", 5, "2024-2025", 0, 9.90, 9.76),
        ("TE03C", 6, "2024-2025", 0, 9.95, 9.79),

        # Siddharth Verma: Gap at Sem 4
        ("TE04D", 1, "2020-2021", 0, 6.80, 6.80),
        ("TE04D", 2, "2020-2021", 0, 7.00, 6.90),
        ("TE04D", 3, "2021-2022", 0, 6.50, 6.76),
        ("TE04D", 4, "2023-2024", 1, 6.10, 6.59),  # Gap year marked
        ("TE04D", 5, "2023-2024", 0, 6.90, 6.65),
        ("TE04D", 6, "2024-2025", 0, 7.30, 6.76),

        # Pooja Deshmukh
        ("TE05E", 1, "2022-2023", 0, 7.80, 7.80),
        ("TE05E", 2, "2022-2023", 0, 8.10, 7.95),
        ("TE05E", 3, "2023-2024", 0, 8.45, 8.12),
        ("TE05E", 4, "2023-2024", 0, 8.70, 8.26),

        # Aditya Kulkarni: Gap at Sem 2
        ("TE06F", 1, "2021-2022", 0, 6.60, 6.60),
        ("TE06F", 2, "2023-2024", 1, 5.90, 6.25),  # Gap year marked
        ("TE06F", 3, "2023-2024", 0, 6.70, 6.40),

        # Neha Nair
        ("TE07G", 1, "2022-2023", 0, 8.60, 8.60),
        ("TE07G", 2, "2022-2023", 0, 8.80, 8.70),
        ("TE07G", 3, "2023-2024", 0, 8.95, 8.78),

        # Varun Mehta
        ("TE08H", 1, "2022-2023", 0, 7.90, 7.90),
        ("TE08H", 2, "2022-2023", 0, 8.10, 8.00),

        # Tanvi Joshi: Gap at Sem 3
        ("TE09I", 1, "2021-2022", 0, 7.50, 7.50),
        ("TE09I", 2, "2021-2022", 0, 7.60, 7.55),
        ("TE09I", 3, "2023-2024", 1, 6.85, 7.31),

        # Kunal Shah
        ("TE10J", 1, "2022-2023", 0, 8.30, 8.30),
        ("TE10J", 2, "2022-2023", 0, 8.50, 8.40)
    ]
    c.executemany("INSERT INTO academic_semesters (student_id, semester_number, academic_year, is_drop_year, sgpa, cgpa) VALUES (?,?,?,?,?,?)", semesters)

    # Dynamic foreign key mapper helper
    def insert_sub(student_id, sem_no, code, name, stype, internal, endsem, status):
        c.execute("SELECT sem_id FROM academic_semesters WHERE student_id = ? AND semester_number = ?", (student_id, sem_no))
        row = c.fetchone()
        if row:
            c.execute("""
                INSERT INTO subject_evaluations (sem_id, course_code, course_name, course_type, internal_score, endsem_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (row[0], code, name, stype, internal, endsem, status))

    # 3. Authentic Mumbai University ECE Curriculum (Rev-2019 'C' Scheme)
    
    # --- FE Sem 1 (Aarav, TE01A) ---
    insert_sub("TE01A", 1, "FEC101", "Applied Mathematics - I", "Theory", 19, 72, "PASS")
    insert_sub("TE01A", 1, "FEC102", "Applied Physics - I", "Theory", 18, 66, "PASS")
    insert_sub("TE01A", 1, "FEC105", "Basic Electrical Engineering", "Theory", 19, 74, "PASS")
    insert_sub("TE01A", 1, "FEL104", "Basic Electrical Engg Lab", "Laboratory", 20, 78, "PASS")

    # --- FE Sem 2 (Aarav, TE01A) ---
    insert_sub("TE01A", 2, "FEC201", "Applied Mathematics - II", "Theory", 18, 70, "PASS")
    insert_sub("TE01A", 2, "FEC205", "C Programming", "Theory", 19, 73, "PASS")
    insert_sub("TE01A", 2, "FEL204", "C Programming Laboratory", "Laboratory", 20, 77, "PASS")

    # --- SE Sem 3 (Aarav, TE01A) ---
    insert_sub("TE01A", 3, "ECC301", "Engineering Mathematics - III", "Theory", 19, 75, "PASS")
    insert_sub("TE01A", 3, "ECC302", "Electronic Devices & Circuits", "Theory", 18, 71, "PASS")
    insert_sub("TE01A", 3, "ECC303", "Digital System Design", "Theory", 20, 76, "PASS")
    insert_sub("TE01A", 3, "ECC304", "Network Theory", "Theory", 18, 69, "PASS")
    insert_sub("TE01A", 3, "ECL301", "Electronic Devices & Circuits Lab", "Laboratory", 19, 78, "PASS")
    insert_sub("TE01A", 3, "ECL302", "Digital System Design Lab", "Laboratory", 20, 79, "PASS")

    # --- SE Sem 4 (Aarav, TE01A) ---
    insert_sub("TE01A", 4, "ECC401", "Engineering Mathematics - IV", "Theory", 20, 76, "PASS")
    insert_sub("TE01A", 4, "ECC402", "Microcontrollers & Embedded Systems", "Theory", 20, 78, "PASS")
    insert_sub("TE01A", 4, "ECC403", "Analog Communication Systems", "Theory", 18, 70, "PASS")
    insert_sub("TE01A", 4, "ECC404", "Signals and Systems", "Theory", 19, 74, "PASS")
    insert_sub("TE01A", 4, "ECL401", "Microcontrollers Lab", "Laboratory", 20, 80, "PASS")
    insert_sub("TE01A", 4, "ECM401", "Mini Project 1B: Hardware Interfacing", "Laboratory", 20, 79, "PASS")

    # --- TE Sem 5 (Aarav, TE01A) ---
    insert_sub("TE01A", 5, "ECC501", "Digital Communication & Coding", "Theory", 19, 75, "PASS")
    insert_sub("TE01A", 5, "ECC502", "Discrete-Time Signal Processing", "Theory", 19, 74, "PASS")
    insert_sub("TE01A", 5, "ECC503", "Computer Organization & Architecture", "Theory", 20, 77, "PASS")
    insert_sub("TE01A", 5, "ECL501", "Digital Communication Lab", "Laboratory", 20, 80, "PASS")
    insert_sub("TE01A", 5, "ECL503", "Computer Architecture & Simulation Lab", "Laboratory", 19, 78, "PASS")

    # --- TE Sem 6 (Aarav, TE01A) ---
    insert_sub("TE01A", 6, "ECC601", "Electromagnetics & Antenna Theory", "Theory", 19, 73, "PASS")
    insert_sub("TE01A", 6, "ECC602", "Computer Networks & Protocol Suite", "Theory", 20, 77, "PASS")
    insert_sub("TE01A", 6, "ECC603", "VLSI Design & System on Chip", "Theory", 20, 78, "PASS")
    insert_sub("TE01A", 6, "ECL601", "Computer Networks Lab", "Laboratory", 20, 80, "PASS")
    insert_sub("TE01A", 6, "ECL602", "VLSI Design Lab", "Laboratory", 20, 79, "PASS")

    # --- Rohan Patil (TE02B) - Sem 1 and Sem 3 (Drop Recovery) ---
    insert_sub("TE02B", 1, "FEC105", "Basic Electrical Engineering", "Theory", 15, 52, "PASS")
    insert_sub("TE02B", 1, "FEL104", "Basic Electrical Engg Lab", "Laboratory", 17, 60, "PASS")
    insert_sub("TE02B", 3, "ECC302", "Electronic Devices & Circuits", "Theory", 13, 44, "PASS")
    insert_sub("TE02B", 3, "ECC303", "Digital System Design", "Theory", 14, 46, "PASS")
    insert_sub("TE02B", 3, "ECL302", "Digital System Design Lab", "Laboratory", 16, 55, "PASS")

    # --- Ananya Iyer (TE03C) - Sem 4 & Sem 5 (Top Ranker) ---
    insert_sub("TE03C", 4, "ECC402", "Microcontrollers & Embedded Systems", "Theory", 20, 79, "PASS")
    insert_sub("TE03C", 4, "ECC404", "Signals and Systems", "Theory", 20, 80, "PASS")
    insert_sub("TE03C", 4, "ECL401", "Microcontrollers Lab", "Laboratory", 20, 80, "PASS")
    insert_sub("TE03C", 5, "ECC501", "Digital Communication & Coding", "Theory", 20, 79, "PASS")
    insert_sub("TE03C", 5, "ECC503", "Computer Organization & Architecture", "Theory", 20, 80, "PASS")
    insert_sub("TE03C", 5, "ECL503", "Computer Architecture & Simulation Lab", "Laboratory", 20, 80, "PASS")

    # 4. Realistic ECE Seminars (Internal vs External)
    seminars = [
        ("TE01A", "Edge-AI Deployments on ESP32 Microcontrollers", "Internal", "Department Research Forum"),
        ("TE01A", "IEEE International VLSI & Embedded Systems Conclave", "External", "IIT Bombay"),
        ("TE02B", "Automotive CAN-Bus Telemetry & In-Vehicle Networks", "Internal", "College Technical Guild"),
        ("TE02B", "Industrial PLC & SCADA Automation Workshop", "External", "L&T Institute of Technology"),
        ("TE03C", "RISC-V Core Optimization & Verilog Verification", "External", "IISc Bangalore"),
        ("TE03C", "FPGA Hardware Acceleration for DSP Algorithms", "Internal", "IEEE Student Branch"),
        ("TE04D", "Low-Power Firmware & RTOS Task Schedulers", "External", "VJTI Mumbai"),
        ("TE05E", "Modern High-Speed PCB Layout & Signal Integrity", "Internal", "Department Technical Cell"),
        ("TE06F", "Component Reverse Engineering & Hardware Salvaging", "Internal", "College Maker Lab"),
        ("TE07G", "Satellite SDR Communication & Cadastral Mapping", "External", "ISRO Outreach Cell"),
        ("TE08H", "Predictive Diagnostics in Electric Vehicle Powertrains", "Internal", "ISTE Chapter"),
        ("TE09I", "RF Antenna Array Design for 5G Millimeter Wave", "Internal", "Department Technical Cell"),
        ("TE10J", "ASIC Design Flows and Modern CMOS Scaling", "External", "COEP Technological University")
    ]
    c.executemany("INSERT INTO seminar_records (student_id, seminar_title, tier, host_institution) VALUES (?,?,?,?)", seminars)

    # 5. ECE Activities Portfolio (Technical vs Co-curricular vs Extracurricular)
    activities = [
        ("TE01A", "Smart India Hackathon (Hardware Edition)", "Technical", "Winner (1st Place)"),
        ("TE01A", "Inter-Department Football Tournament", "Extracurricular", "Captain / Winners"),
        ("TE02B", "Robotics Autonomous Line Tracer Challenge", "Technical", "2nd Runner Up"),
        ("TE02B", "Annual Blood Donation & Community Drive", "Co-curricular", "Lead Volunteer"),
        ("TE03C", "Texas Instruments India Innovation Challenge", "Technical", "National Finalist"),
        ("TE03C", "University Parliamentary Debate Championship", "Extracurricular", "Best Speaker Award"),
        ("TE03C", "Technical Paper on Sensor Fusion Architectures", "Technical", "1st Prize"),
        ("TE04D", "Micro-Mouse Maze Solver Competition", "Technical", "Runner-Up"),
        ("TE05E", "State-Level IoT Hackathon 36-Hr Sprint", "Technical", "Winner"),
        ("TE05E", "Inter-College Badminton Open", "Extracurricular", "Quarter-Finalist"),
        ("TE06F", "College Annual Technical Symposium Lead", "Co-curricular", "Technical Secretary"),
        ("TE07G", "Drone Geospatial Navigation Challenge", "Technical", "1st Runner Up"),
        ("TE08H", "Formula Student EV Powertrain Telemetry Team", "Technical", "Lead Electronics Engineer"),
        ("TE09I", "Inter-College Street Play Festival", "Extracurricular", "Best Direction"),
        ("TE10J", "FPGA Game Emulator Hackathon", "Technical", "Top 5 Finalist")
    ]
    c.executemany("INSERT INTO activity_records (student_id, activity_name, domain, position_attained) VALUES (?,?,?,?)", activities)

    conn.commit()
    conn.close()
    print("MU_ECE_DATABASE_SEEDED_SUCCESSFULLY")

if __name__ == "__main__":
    build_mu_ece_database()
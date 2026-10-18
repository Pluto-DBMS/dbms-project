import sqlite3
import json
import urllib.request
import time

DB_FILE = "student_progression.db"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwWyPgMGbI7w8oEBQJj38l1W2NEAYOHQV1bAp8yt6sW22cm2-k9h9j_6A3I5NJFrT8d/exec"

def sync_entire_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Fetch all student semester records along with their profile names
    query = """
    SELECT s.student_id, p.full_name, s.academic_year, s.semester_number, s.sgpa, s.cgpa, s.is_drop_year
    FROM academic_semesters s
    JOIN student_profiles p ON s.student_id = p.student_id
    ORDER BY s.student_id, s.semester_number
    """
    c.execute(query)
    rows = c.fetchall()
    conn.close()

    print(f"Found {len(rows)} semester records. Pushing to Google Sheets...")

    for row in rows:
        sid, name, ayear, sem_num, sgpa, cgpa, is_drop = row
        payload = {
            "action": "SEMESTER_COMMITTED",
            "student_id": sid,
            "name": name,
            "academic_year": ayear,
            "semester_number": sem_num,
            "sgpa": sgpa,
            "cgpa": cgpa,
            "is_drop_year": is_drop
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(WEBHOOK_URL, data=data, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            print(f"Synced: {name} (Sem {sem_num})")
            time.sleep(0.4)  # Small delay so Google Sheets doesn't throttle requests
        except Exception as e:
            print(f"Sync error for {name}: {e}")

    print("\nAll database records pushed to Google Sheets successfully!")

if __name__ == "__main__":
    sync_entire_database()
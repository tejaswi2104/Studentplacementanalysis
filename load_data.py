
import mysql.connector
import random

random.seed(42)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=input("Enter your MySQL root password: "),
    database="placement_db"
)
cur = conn.cursor()

departments = ["CSE", "ECE", "EEE", "MECH", "CIVIL"]
skills_list = ["Java", "Python", "SQL", "DSA", "Web Development",
               "Machine Learning", "Communication", "C++"]

# Synthetic test records only — NOT actual college data.
students = []
for i in range(1, 101):
    dept = departments[(i - 1) % len(departments)]
    eligible = 1 if i % 10 != 0 else 0
    placed = 1 if eligible and i % 3 != 0 else 0

    students.append((
        f"TEST{i:03}",
        f"Test Student {i}",
        dept,
        2026,
        eligible,
        "Placed" if placed else "Not Placed"
    ))

cur.execute("SET FOREIGN_KEY_CHECKS = 0")
for table in ["student_skills", "placements", "skills", "students"]:
    cur.execute(f"DELETE FROM {table}")
cur.execute("SET FOREIGN_KEY_CHECKS = 1")

cur.executemany("""
    INSERT INTO students
    (roll_no, student_name, department, graduation_year,
     eligible, placement_status)
    VALUES (%s, %s, %s, %s, %s, %s)
""", students)

for skill in skills_list:
    cur.execute(
        "INSERT INTO skills (skill_name) VALUES (%s)",
        (skill,)
    )

cur.execute("SELECT student_id FROM students ORDER BY student_id")
student_ids = [row[0] for row in cur.fetchall()]

cur.execute("SELECT skill_id FROM skills")
skill_ids = [row[0] for row in cur.fetchall()]

for sid in student_ids:
    for skill_id in random.sample(skill_ids, 3):
        cur.execute("""
            INSERT INTO student_skills (student_id, skill_id)
            VALUES (%s, %s)
        """, (sid, skill_id))

for student in students:
    if student[5] == "Placed":
        cur.execute(
            "SELECT student_id FROM students WHERE roll_no = %s",
            (student[0],)
        )
        sid = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO placements
            (student_id, company, role, package_lpa, placement_year)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            sid,
            random.choice(["Example Tech A", "Example Tech B",
                           "Example Analytics C"]),
            random.choice(["Software Developer", "Analyst", "Junior Engineer"]),
            round(random.uniform(3.0, 12.0), 2),
            2026
        ))

conn.commit()
cur.close()
conn.close()

print("Synthetic test dataset loaded successfully.")
print("These records are fictional, not actual college placement data.")

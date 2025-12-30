import csv
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="student_support"
)

cursor = db.cursor()

CSV_PATH = "../data/subject_list.csv"

with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("""
            INSERT INTO subjects
            (id, subject_name, category, career_group, level,
             prerequisite, study_hours, description,
             resource_type, resource_link, image)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                subject_name=VALUES(subject_name),
                category=VALUES(category),
                career_group=VALUES(career_group),
                level=VALUES(level),
                prerequisite=VALUES(prerequisite),
                study_hours=VALUES(study_hours),
                description=VALUES(description),
                resource_type=VALUES(resource_type),
                resource_link=VALUES(resource_link),
                image=VALUES(image)
        """, (
            row["id"],
            row["subject_name"],
            row["category"],
            row["career_group"],
            row["level"],
            row["prerequisite"],
            row["study_hours"],
            row["description"],
            row["resource_type"],
            row["resource_link"],
            row["image"]
        ))

db.commit()
db.close()

print("✅ Import subjects thành công")

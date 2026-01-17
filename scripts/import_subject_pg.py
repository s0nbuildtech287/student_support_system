import csv
import psycopg2

conn = psycopg2.connect(
    host="nozomi.proxy.rlwy.net",
    port=32309,
    user="postgres",
    password="fLfMZDOUjpUimkqucnUrhNZZpztKcZkw",
    dbname="student_support"
)

cursor = conn.cursor()

CSV_PATH = "../data/subject_list.csv"

with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("""
            INSERT INTO subjects (
                id, subject_name, category, career_group, level,
                prerequisite, study_hours, description,
                resource_type, resource_link, image
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET
                subject_name = EXCLUDED.subject_name,
                category = EXCLUDED.category,
                career_group = EXCLUDED.career_group,
                level = EXCLUDED.level,
                prerequisite = EXCLUDED.prerequisite,
                study_hours = EXCLUDED.study_hours,
                description = EXCLUDED.description,
                resource_type = EXCLUDED.resource_type,
                resource_link = EXCLUDED.resource_link,
                image = EXCLUDED.image
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

conn.commit()
cursor.close()
conn.close()

print("✅ Import subjects lên PostgreSQL thành công")

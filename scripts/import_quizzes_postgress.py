"""
Script import quizzes từ CSV vào PostgreSQL
Chạy: python import_quizzes_postgres.py
"""

import csv
import psycopg2


# ======================
# DB CONFIG (POSTGRES)
# ======================
conn = psycopg2.connect(
    host="nozomi.proxy.rlwy.net",
    port=32309,
    user="postgres",
    password="fLfMZDOUjpUimkqucnUrhNZZpztKcZkw",
    dbname="student_support"
)

cursor = conn.cursor()


# ======================
# CSV PATH
# ======================
CSV_PATH = "../data/quiz.csv"


def import_quizzes():
    print("🚀 Bắt đầu import quizzes (PostgreSQL)...")

    try:
        cursor.execute("TRUNCATE TABLE quizzes RESTART IDENTITY CASCADE")
        print("✓ Đã xóa dữ liệu quiz cũ")

        with open(CSV_PATH, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            quizzes = list(reader)

        print(f"✓ Đọc được {len(quizzes)} câu hỏi từ CSV")

        sql = """
            INSERT INTO quizzes
            (subject_id, question, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        count = 0
        for quiz in quizzes:
            cursor.execute(sql, (
                int(quiz["subject_uid"]),
                quiz["question"],
                quiz["option_a"],
                quiz["option_b"],
                quiz["option_c"],
                quiz["option_d"],
                quiz["correct_answer"].strip().lower()
            ))
            count += 1

        conn.commit()
        print(f"✅ Đã import {count} câu hỏi vào PostgreSQL")

        print("\n🎉 Hoàn thành import quiz!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi import quiz: {e}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import_quizzes()

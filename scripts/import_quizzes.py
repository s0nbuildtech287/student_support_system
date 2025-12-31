"""
Script import quizzes từ CSV vào MySQL
Chạy: python import_quizzes.py
"""

import csv
import mysql.connector


# ======================
# DB CONFIG
# ======================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="student_support"
)

cursor = db.cursor()


# ======================
# CSV PATH (GIỐNG IMPORT SUBJECTS)
# ======================
CSV_PATH = "../data/quiz.csv"


def import_quizzes():
    print("🚀 Bắt đầu import quizzes...")

    try:
        cursor.execute("DELETE FROM quizzes")
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

        db.commit()
        print(f"✅ Đã import {count} câu hỏi vào database")

        print("\n🎉 Hoàn thành import quiz!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi import quiz: {e}")

    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    import_quizzes()

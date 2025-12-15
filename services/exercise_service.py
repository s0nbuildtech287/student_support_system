import csv
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CSV_PATH = os.path.join(BASE_DIR, "data", "workout_list_exercise.csv")


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# hiển thị tất cả các bài tập
def load_all_exercises_paginated(page=1, per_page=9):
    all_exercises = load_csv(CSV_PATH)

    # gán uid toàn cục (rất nên có)
    for i, ex in enumerate(all_exercises, start=1):
        ex["uid"] = i

    total = len(all_exercises)
    total_pages = math.ceil(total / per_page)

    # chống page out of range
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "exercises": all_exercises[start:end],
        "total": total,
        "total_pages": total_pages,
        "page": page
    }

# chi tiết bài tập
def get_exercise_by_uid(uid):
    all_exercises = load_csv(CSV_PATH)

    for i, ex in enumerate(all_exercises, start=1):
        if i == uid:
            ex["uid"] = i
            return ex

    return None
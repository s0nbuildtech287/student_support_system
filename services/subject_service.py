import csv
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "subject_list.csv")
OUTLINE_CSV_PATH = os.path.join(BASE_DIR, "data", "subject_outline.csv")


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_all_subject_paginated(page=1, per_page=9, category="", level=""):
    subjects = load_csv(CSV_PATH)

    # danh sách category để render select
    categories = sorted(set(s["category"] for s in subjects))

    # FILTER
    if category:
        subjects = [s for s in subjects if s["category"] == category]

    if level:
        subjects = [s for s in subjects if s["level"] == level]

    # gán uid sau khi filter
    for i, s in enumerate(subjects, start=1):
        s["uid"] = i

    total = len(subjects)
    total_pages = max(1, math.ceil(total / per_page))

    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "subjects": subjects[start:end],
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "categories": categories
    }


def get_subject_by_uid(uid):
    subjects = load_csv(CSV_PATH)

    for i, s in enumerate(subjects, start=1):
        if i == uid:
            s["uid"] = i
            s["outline"] = get_subject_outline(i)
            return s
            
    return None


def get_subject_outline(subject_id):
    outlines = load_csv(OUTLINE_CSV_PATH)

    # lọc theo subject_id
    result = [
        o for o in outlines
        if int(o["subject_id"]) == subject_id
    ]

    # sắp xếp theo thứ tự học
    result.sort(key=lambda x: int(x["order"]))

    return result

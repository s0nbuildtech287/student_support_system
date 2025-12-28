# services/roadmap_service.py
import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _safe_read_csv(filename: str):
    """
    Đọc CSV theo kiểu chịu lỗi:
    - Nếu có dòng bị lệch cột do dấu phẩy trong text -> bỏ dòng lỗi
    - Trả về list[dict]
    """
    path = os.path.join(DATA_DIR, filename)
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return []

        n = len(header)
        for line in reader:
            if len(line) != n:
                # bỏ dòng lỗi (tránh app crash)
                continue
            rows.append(dict(zip(header, line)))
    return rows


def get_all_roadmaps():
    roadmaps = _safe_read_csv("roadmap_list.csv")
    for r in roadmaps:
        r["roadmap_id"] = int(r["roadmap_id"])
    return roadmaps


def get_roadmap_by_id(roadmap_id: int):
    for r in get_all_roadmaps():
        if r["roadmap_id"] == roadmap_id:
            return r
    return None


def _get_subject_map():
    subjects = _safe_read_csv("subject_list.csv")
    # subject_list.csv của bạn dùng cột "id"
    m = {}
    for s in subjects:
        sid = str(s.get("id", "")).strip()
        if sid:
            m[sid] = s
    return m


def get_roadmap_steps(roadmap_id: int):
    mapping = _safe_read_csv("roadmap_subject.csv")
    subject_map = _get_subject_map()

    steps = []
    for row in mapping:
        if int(row["roadmap_id"]) != roadmap_id:
            continue

        sid = str(row["subject_id"]).strip()
        steps.append({
            "roadmap_id": roadmap_id,
            "subject_id": sid,
            "step_order": int(row["step_order"]),
            "note": row.get("note", ""),
            "subject": subject_map.get(sid),  # dict hoặc None
        })

    steps.sort(key=lambda x: x["step_order"])
    return steps

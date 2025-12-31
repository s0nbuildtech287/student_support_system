# services/roadmap_service.py
import os
import csv
from datetime import datetime
from database import fetch_one, fetch_all, execute_query, get_db_connection

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
    """
    Tạo map: subject_id (từ CSV) -> subject info + uid
    UID = vị trí trong CSV (index + 1)
    """
    subjects = _safe_read_csv("subject_list.csv")
    subject_map = {}
    
    for i, s in enumerate(subjects, start=1):
        # Lấy id từ CSV (có thể là cột 'id' hoặc 'subject_id')
        subject_id = s.get("id") or s.get("subject_id")
        
        if subject_id:
            subject_id = str(subject_id).strip()
            s['uid'] = i  # uid = index + 1 (để dùng trong YourPlan)
            subject_map[subject_id] = s
    
    return subject_map


def get_roadmap_steps(roadmap_id: int):
    mapping = _safe_read_csv("roadmap_subject.csv")
    subject_map = _get_subject_map()

    steps = []
    for row in mapping:
        if int(row["roadmap_id"]) != roadmap_id:
            continue

        sid = str(row["subject_id"]).strip()
        subject_info = subject_map.get(sid)
        
        steps.append({
            "roadmap_id": roadmap_id,
            "subject_id": sid,
            "step_order": int(row["step_order"]),
            "note": row.get("note", ""),
            "subject": subject_info,  # dict hoặc None
        })

    steps.sort(key=lambda x: x["step_order"])
    return steps


def apply_roadmap_to_user_plan(user_id: int, roadmap_id: int):
    """
    Áp dụng lộ trình có sẵn từ Roadmap vào YourPlan
    
    Logic:
    1. Kiểm tra user có đủ slot (max 3 plans)
    2. Tạo plan mới với tên từ roadmap
    3. Thêm các subject theo đúng thứ tự từ roadmap_subject.csv
    4. Trả về plan_id để redirect
    """
    
    # Kiểm tra giới hạn 3 lộ trình
    query_count = "SELECT COUNT(*) as count FROM study_plans WHERE user_id = %s"
    result = fetch_one(query_count, (user_id,))
    
    if result and result['count'] >= 3:
        return {
            'success': False, 
            'message': 'Bạn đã đạt giới hạn 3 lộ trình. Vui lòng xóa lộ trình cũ trước khi thêm mới.'
        }
    
    # Lấy thông tin roadmap
    roadmap = get_roadmap_by_id(roadmap_id)
    if not roadmap:
        return {'success': False, 'message': 'Lộ trình không tồn tại'}
    
    # Lấy các bước/môn học trong roadmap
    steps = get_roadmap_steps(roadmap_id)
    
    if not steps:
        return {'success': False, 'message': 'Lộ trình này chưa có môn học nào'}
    
    # DEBUG: In ra để kiểm tra
    print(f"[DEBUG] Roadmap {roadmap_id} has {len(steps)} steps")
    for step in steps:
        print(f"[DEBUG] Step {step['step_order']}: subject_id={step['subject_id']}, subject={step['subject']}")
    
    # Tạo plan mới
    plan_name = f"🎯 {roadmap.get('roadmap_name', 'Lộ trình')}"
    plan_description = roadmap.get('description', 'Lộ trình được áp dụng từ Roadmap gợi ý')
    
    query_create = """
        INSERT INTO study_plans (user_id, name, description, is_started, created_at)
        VALUES (%s, %s, %s, 0, %s)
    """
    
    if not execute_query(query_create, (user_id, plan_name, plan_description, datetime.now())):
        return {'success': False, 'message': 'Lỗi khi tạo lộ trình'}
    
    # Lấy plan_id vừa tạo
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT LAST_INSERT_ID() as id")
    plan_result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not plan_result:
        return {'success': False, 'message': 'Không thể lấy ID lộ trình vừa tạo'}
    
    plan_id = plan_result[0]
    
    # Thêm các môn học vào plan theo thứ tự
    added_count = 0
    failed_subjects = []
    
    for step in steps:
        subject_info = step.get('subject')
        
        if not subject_info:
            failed_subjects.append(f"Subject ID {step['subject_id']} (không tìm thấy)")
            continue
        
        # Lấy uid của subject
        subject_uid = subject_info.get('uid')
        
        if not subject_uid:
            failed_subjects.append(f"{subject_info.get('subject_name', 'Unknown')} (không có UID)")
            continue
        
        print(f"[DEBUG] Adding subject UID {subject_uid} to plan {plan_id}")
        
        # Thêm vào plan_subjects
        query_add = """
            INSERT INTO plan_subjects (plan_id, subject_id, progress, status)
            VALUES (%s, %s, 0, 'not_started')
        """
        
        try:
            if execute_query(query_add, (plan_id, subject_uid)):
                added_count += 1
                print(f"[DEBUG] Successfully added subject {subject_uid}")
            else:
                failed_subjects.append(f"{subject_info.get('subject_name', 'Unknown')} (lỗi DB)")
        except Exception as e:
            print(f"[DEBUG] Error adding subject {subject_uid}: {e}")
            failed_subjects.append(f"{subject_info.get('subject_name', 'Unknown')} ({str(e)})")
    
    # Log kết quả
    print(f"[DEBUG] Added {added_count}/{len(steps)} subjects")
    if failed_subjects:
        print(f"[DEBUG] Failed subjects: {failed_subjects}")
    
    if added_count == 0:
        # Nếu không thêm được môn nào thì xóa plan
        execute_query("DELETE FROM study_plans WHERE id = %s", (plan_id,))
        error_msg = f'Không thể thêm môn học vào lộ trình.'
        if failed_subjects:
            error_msg += f' Lỗi: {", ".join(failed_subjects[:3])}'
        return {'success': False, 'message': error_msg}
    
    success_msg = f'Đã áp dụng lộ trình thành công với {added_count} môn học!'
    if failed_subjects:
        success_msg += f' ({len(failed_subjects)} môn bị bỏ qua)'
    
    return {
        'success': True,
        'message': success_msg,
        'plan_id': plan_id
    }
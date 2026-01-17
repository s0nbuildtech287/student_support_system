# services/roadmap_service.py - FULL FIXED VERSION
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
        subject_id = s.get("id") or s.get("subject_id")
        
        if subject_id:
            subject_id = str(subject_id).strip()
            s['uid'] = i
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
            "subject": subject_info,
        })

    steps.sort(key=lambda x: x["step_order"])
    return steps


def apply_roadmap_to_user_plan(user_id: int, roadmap_id: int):
    """
    Áp dụng lộ trình có sẵn từ Roadmap vào YourPlan
    
    FINAL FIX: Sử dụng connection trực tiếp để lấy LAST_INSERT_ID
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
    
    print(f"[DEBUG] Roadmap {roadmap_id} has {len(steps)} steps")
    
    # Tạo plan mới
    plan_name = f"🎯 {roadmap.get('roadmap_name', 'Lộ trình')}"
    plan_description = roadmap.get('description', 'Lộ trình được áp dụng từ Roadmap gợi ý')
    
    # FIX: Dùng RETURNING để lấy ID (PostgreSQL way)
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        query_create = """
            INSERT INTO study_plans (user_id, name, description, is_started, created_at)
            VALUES (%s, %s, %s, FALSE, %s)
            RETURNING id
        """
        
        cursor.execute(query_create, (user_id, plan_name, plan_description, datetime.now()))
        plan_id = cursor.fetchone()[0]  # Get ID from RETURNING
        connection.commit()
        
        print(f"[DEBUG] Created plan with ID: {plan_id}")
        
        if not plan_id:
            cursor.close()
            connection.close()
            return {'success': False, 'message': 'Không thể lấy ID lộ trình vừa tạo'}
        
    except Exception as e:
        print(f"[DEBUG] Error creating plan: {e}")
        connection.rollback()
        cursor.close()
        connection.close()
        return {'success': False, 'message': f'Lỗi khi tạo lộ trình: {str(e)}'}
    
    # OPTIMIZATION: Batch verify và batch insert để giảm queries
    added_count = 0
    failed_subjects = []
    
    # Collect all subject IDs
    subject_ids = []
    for step in steps:
        subject_id_from_csv = step.get('subject_id')
        if subject_id_from_csv:
            try:
                subject_ids.append(int(subject_id_from_csv))
            except (ValueError, TypeError):
                failed_subjects.append(f"Subject ID {subject_id_from_csv} không hợp lệ")
    
    if not subject_ids:
        cursor.close()
        connection.close()
        return {'success': False, 'message': 'Không có môn học hợp lệ trong lộ trình'}
    
    print(f"[DEBUG] Processing {len(subject_ids)} subjects")
    
    try:
        # BATCH QUERY 1: Verify tất cả subjects exist cùng lúc
        placeholders = ','.join(['%s'] * len(subject_ids))
        cursor.execute(
            f"SELECT id FROM subjects WHERE id IN ({placeholders})",
            tuple(subject_ids)
        )
        existing_subjects = set(row[0] for row in cursor.fetchall())
        print(f"[DEBUG] ✓ Found {len(existing_subjects)} valid subjects")
        
        # BATCH QUERY 2: Check existing plan_subjects để tránh duplicate
        cursor.execute(
            f"SELECT subject_id FROM plan_subjects WHERE plan_id = %s AND subject_id IN ({placeholders})",
            (plan_id,) + tuple(subject_ids)
        )
        already_added = set(row[0] for row in cursor.fetchall())
        
        # Filter: chỉ giữ subjects exist và chưa có trong plan
        valid_subjects = [
            sid for sid in subject_ids 
            if sid in existing_subjects and sid not in already_added
        ]
        
        if not valid_subjects:
            cursor.close()
            connection.close()
            return {'success': False, 'message': 'Tất cả môn học đã có trong lộ trình hoặc không tồn tại'}
        
        # BATCH INSERT: Thêm tất cả subjects cùng lúc
        values = ','.join(
            cursor.mogrify("(%s, %s, 0, 'not_started')", (plan_id, sid)).decode('utf-8')
            for sid in valid_subjects
        )
        
        cursor.execute(
            f"INSERT INTO plan_subjects (plan_id, subject_id, progress, status) VALUES {values}"
        )
        connection.commit()
        added_count = cursor.rowcount
        
        print(f"[DEBUG] ✓ Batch inserted {added_count} subjects")
        
        # Track failed subjects
        for sid in subject_ids:
            if sid not in existing_subjects:
                failed_subjects.append(f"Subject ID {sid} không tồn tại")
            elif sid in already_added:
                failed_subjects.append(f"Subject ID {sid} đã có trong plan")
                
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"[DEBUG] ❌ Batch insert error: {error_msg}")
        connection.rollback()
        cursor.close()
        connection.close()
        return {'success': False, 'message': f'Lỗi khi thêm môn học: {error_msg}'}
    
    cursor.close()
    connection.close()
    
    # Log kết quả
    print(f"\n[DEBUG] ========== SUMMARY ==========")
    print(f"[DEBUG] Added {added_count}/{len(steps)} subjects to plan {plan_id}")
    
    if failed_subjects:
        print(f"[DEBUG] Failed: {len(failed_subjects)} subjects")
        for fs in failed_subjects[:5]:
            print(f"  - {fs}")
    
    if added_count == 0:
        execute_query("DELETE FROM study_plans WHERE id = %s", (plan_id,))
        error_msg = 'Không thể thêm môn học vào lộ trình.'
        if failed_subjects:
            error_msg += f' Lỗi: {failed_subjects[0]}'
        return {'success': False, 'message': error_msg}
    
    success_msg = f'✅ Đã áp dụng lộ trình thành công với {added_count} môn học!'
    if failed_subjects:
        success_msg += f' ({len(failed_subjects)} môn bị bỏ qua)'
    
    return {
        'success': True,
        'message': success_msg,
        'plan_id': plan_id
    }
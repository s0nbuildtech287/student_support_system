import csv
import os
from datetime import datetime
from database import fetch_one, fetch_all, execute_query, get_db_connection

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUBJECT_CSV = os.path.join(DATA_DIR, "subject_list.csv")

# Cache for subjects
_subjects_cache = None

def load_csv(path):
    """Load CSV file"""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_cached_subjects():
    """Get cached subjects list"""
    global _subjects_cache
    if _subjects_cache is None:
        _subjects_cache = load_csv(SUBJECT_CSV)
    return _subjects_cache


def get_user_plans(user_id):
    """Lấy tất cả plans của user (optimized with batch queries)"""
    query = """
        SELECT id, user_id, name, description, is_started, created_at
        FROM study_plans
        WHERE user_id = %s
        ORDER BY created_at DESC
    """
    plans = fetch_all(query, (user_id,))
    
    if not plans:
        return []
    
    # Dùng cached subjects
    subjects_data = get_cached_subjects()
    
    # Batch query: Lấy tất cả plan_subjects cho tất cả plans cùng lúc
    plan_ids = [p['id'] for p in plans]
    placeholders = ','.join(['%s'] * len(plan_ids))
    
    query_all_subjects = f"""
        SELECT plan_id, subject_id, progress, status
        FROM plan_subjects
        WHERE plan_id IN ({placeholders})
        ORDER BY plan_id, id
    """
    all_plan_subjects = fetch_all(query_all_subjects, tuple(plan_ids))
    
    # Group by plan_id
    plan_subjects_map = {}
    for ps in all_plan_subjects:
        plan_id = ps['plan_id']
        if plan_id not in plan_subjects_map:
            plan_subjects_map[plan_id] = []
        plan_subjects_map[plan_id].append(ps)
    
    # Gắn subjects vào mỗi plan
    for plan in plans:
        plan_subjects_data = plan_subjects_map.get(plan['id'], [])
        
        plan_subjects = []
        for ps in plan_subjects_data:
            subject_id = ps['subject_id']
            # Tìm subject trong CSV (uid = index + 1)
            for i, s in enumerate(subjects_data, start=1):
                if i == subject_id:
                    s_copy = s.copy()
                    s_copy['uid'] = i
                    s_copy['progress'] = ps['progress']
                    s_copy['status'] = ps['status']
                    plan_subjects.append(s_copy)
                    break
        
        plan['subjects'] = plan_subjects
        plan['total_hours'] = sum(int(s.get('study_hours', 0)) for s in plan_subjects)
    
    # Tính progress cho tất cả plans cùng lúc (batch query)
    if plans:
        plan_ids = [p['id'] for p in plans]
        placeholders = ','.join(['%s'] * len(plan_ids))
        
        query_progress = f"""
            SELECT 
                plan_id,
                COUNT(*) as total_subjects,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_subjects,
                SUM(CASE WHEN status = 'studying' THEN 1 ELSE 0 END) as studying_subjects,
                SUM(CASE WHEN status = 'not_started' THEN 1 ELSE 0 END) as not_started_subjects,
                AVG(progress) as overall_progress
            FROM plan_subjects
            WHERE plan_id IN ({placeholders})
            GROUP BY plan_id
        """
        
        progress_data = fetch_all(query_progress, tuple(plan_ids))
        progress_map = {p['plan_id']: p for p in progress_data}
        
        for plan in plans:
            progress = progress_map.get(plan['id'])
            if progress:
                plan['progress_info'] = {
                    'total_subjects': progress['total_subjects'] or 0,
                    'completed_subjects': progress['completed_subjects'] or 0,
                    'studying_subjects': progress['studying_subjects'] or 0,
                    'not_started_subjects': progress['not_started_subjects'] or 0,
                    'overall_progress': round(float(progress['overall_progress']) if progress['overall_progress'] else 0, 1)
                }
            else:
                plan['progress_info'] = {
                    'total_subjects': 0,
                    'completed_subjects': 0,
                    'studying_subjects': 0,
                    'not_started_subjects': 0,
                    'overall_progress': 0
                }
    
    return plans


def get_plan_by_id(plan_id, user_id):
    """Lấy plan theo ID"""
    plans = get_user_plans(user_id)
    for plan in plans:
        if plan['id'] == plan_id:
            return plan
    return None


def create_user_plan(user_id, name, description):
    """Tạo lộ trình mới"""
    if not name:
        return {'success': False, 'message': 'Vui lòng nhập tên lộ trình'}
    
    # Kiểm tra giới hạn 3 lộ trình
    query_count = "SELECT COUNT(*) as count FROM study_plans WHERE user_id = %s"
    result = fetch_one(query_count, (user_id,))
    
    if result and result['count'] >= 3:
        return {'success': False, 'message': 'Đã đạt giới hạn 3 lộ trình'}
    
    # Insert plan mới
    query = """
        INSERT INTO study_plans (user_id, name, description, is_started, created_at)
        VALUES (%s, %s, %s, FALSE, %s)
    """
    
    if execute_query(query, (user_id, name, description, datetime.now())):
        # Lấy ID vừa tạo - PostgreSQL compatible
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM study_plans WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            return {'success': True, 'message': 'Tạo lộ trình thành công', 'plan_id': result[0]}
    
    return {'success': False, 'message': 'Lỗi khi tạo lộ trình'}


def update_plan_name(plan_id, user_id, new_name):
    """Cập nhật tên lộ trình"""
    if not new_name:
        return {'success': False, 'message': 'Tên không được để trống'}
    
    query = """
        UPDATE study_plans
        SET name = %s
        WHERE id = %s AND user_id = %s
    """
    
    if execute_query(query, (new_name, plan_id, user_id)):
        return {'success': True, 'message': 'Cập nhật thành công'}
    
    return {'success': False, 'message': 'Không tìm thấy lộ trình'}


def delete_user_plan(plan_id, user_id):
    """Xóa lộ trình"""
    query = """
        DELETE FROM study_plans
        WHERE id = %s AND user_id = %s
    """
    
    if execute_query(query, (plan_id, user_id)):
        return {'success': True, 'message': 'Xóa thành công'}
    
    return {'success': False, 'message': 'Không tìm thấy lộ trình'}


def start_user_plan(plan_id, user_id):
    """Bắt đầu lộ trình (lock để không sửa được nữa)"""
    # Kiểm tra plan có tồn tại không
    query_check = """
        SELECT is_started FROM study_plans
        WHERE id = %s AND user_id = %s
    """
    plan = fetch_one(query_check, (plan_id, user_id))
    
    if not plan:
        return {'success': False, 'message': 'Không tìm thấy lộ trình'}
    
    if plan['is_started']:
        return {'success': False, 'message': 'Lộ trình đã được bắt đầu'}
    
    # Update is_started
    query = """
        UPDATE study_plans
        SET is_started = TRUE
        WHERE id = %s AND user_id = %s
    """
    
    if execute_query(query, (plan_id, user_id)):
        return {'success': True, 'message': 'Bắt đầu lộ trình thành công'}
    
    return {'success': False, 'message': 'Lỗi khi bắt đầu lộ trình'}


def add_subject_to_plan(plan_id, user_id, subject_uid, allow_edit=False):
    """Thêm môn học vào lộ trình (optimized)"""
    # OPTIMIZATION: Gộp plan check và insert thành 1 query duy nhất
    
    # Query 1: Check plan và insert nếu valid (dùng WITH để atomic)
    query = """
        WITH plan_check AS (
            SELECT id, is_started 
            FROM study_plans 
            WHERE id = %s AND user_id = %s
        )
        INSERT INTO plan_subjects (plan_id, subject_id, progress, status)
        SELECT %s, %s, 0, 'not_started'
        FROM plan_check
        WHERE EXISTS (SELECT 1 FROM plan_check)
          AND (plan_check.is_started = FALSE OR %s = TRUE)
          AND NOT EXISTS (
              SELECT 1 FROM plan_subjects 
              WHERE plan_id = %s AND subject_id = %s
          )
        RETURNING plan_id
    """
    
    result = fetch_one(query, (plan_id, user_id, plan_id, subject_uid, allow_edit, plan_id, subject_uid))
    
    if result:
        return {'success': True, 'message': 'Đã thêm môn học'}
    
    # Nếu không insert được, kiểm tra lý do (fallback check)
    plan = fetch_one("SELECT is_started FROM study_plans WHERE id = %s AND user_id = %s", (plan_id, user_id))
    
    if not plan:
        return {'success': False, 'message': 'Không tìm thấy lộ trình'}
    
    if plan['is_started'] and not allow_edit:
        return {'success': False, 'message': 'Không thể thêm môn khi lộ trình đang học. Dùng nút Chỉnh sửa lộ trình'}
    
    # Nếu đến đây thì likely là duplicate
    return {'success': False, 'message': 'Môn học đã có trong lộ trình'}


def remove_subject_from_plan(plan_id, user_id, subject_uid, allow_edit=False):
    """Xóa môn học khỏi lộ trình (optimized)"""
    # OPTIMIZATION: Gộp check và delete thành 1 query
    query = """
        WITH plan_check AS (
            SELECT id, is_started 
            FROM study_plans 
            WHERE id = %s AND user_id = %s
        )
        DELETE FROM plan_subjects
        WHERE plan_id = %s 
          AND subject_id = %s
          AND EXISTS (SELECT 1 FROM plan_check)
          AND (
              (SELECT is_started FROM plan_check) = FALSE 
              OR %s = TRUE
          )
        RETURNING plan_id
    """
    
    result = fetch_one(query, (plan_id, user_id, plan_id, subject_uid, allow_edit))
    
    if result:
        return {'success': True, 'message': 'Đã xóa môn học'}
    
    # Fallback check để return error message chính xác
    plan = fetch_one("SELECT is_started FROM study_plans WHERE id = %s AND user_id = %s", (plan_id, user_id))
    
    if not plan:
        return {'success': False, 'message': 'Không tìm thấy lộ trình'}
    
    if plan['is_started'] and not allow_edit:
        return {'success': False, 'message': 'Không thể xóa môn khi lộ trình đang học. Dùng nút Chỉnh sửa lộ trình'}
    
    return {'success': False, 'message': 'Môn học không có trong lộ trình'}


# Cache for subjects to avoid loading CSV every time
_subjects_cache = None

def get_all_subjects_for_modal():
    """Lấy tất cả subjects để hiển thị trong modal thêm môn (cached)"""
    subjects = get_cached_subjects()
    
    # Gắn uid cho mỗi subject (nếu chưa có)
    result = []
    for i, s in enumerate(subjects, start=1):
        s_copy = s.copy()
        s_copy['uid'] = i
        result.append(s_copy)
    
    return result
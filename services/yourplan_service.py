import csv
import os
from datetime import datetime
from database import fetch_one, fetch_all, execute_query, get_db_connection

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUBJECT_CSV = os.path.join(DATA_DIR, "subject_list.csv")


def load_csv(path):
    """Load CSV file"""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_user_plans(user_id):
    """Lấy tất cả plans của user"""
    query = """
        SELECT id, user_id, name, description, is_started, created_at
        FROM study_plans
        WHERE user_id = %s
        ORDER BY created_at DESC
    """
    plans = fetch_all(query, (user_id,))
    
    # Gắn thông tin subjects vào mỗi plan
    subjects_data = load_csv(SUBJECT_CSV)
    
    for plan in plans:
        # Lấy subject_ids và thông tin progress từ plan_subjects
        query_subjects = """
            SELECT subject_id, progress, status
            FROM plan_subjects
            WHERE plan_id = %s
            ORDER BY id
        """
        plan_subjects_data = fetch_all(query_subjects, (plan['id'],))
        
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
        
        # Tính progress info
        from services.progress_service import get_plan_overall_progress
        plan['progress_info'] = get_plan_overall_progress(plan['id'], user_id)
    
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
    """Thêm môn học vào lộ trình"""
    # Kiểm tra plan
    query_plan = """
        SELECT is_started FROM study_plans
        WHERE id = %s AND user_id = %s
    """
    plan = fetch_one(query_plan, (plan_id, user_id))
    
    if not plan:
        return {'success': False, 'message': 'Không tìm thấy lộ trình'}
    
    if plan['is_started'] and not allow_edit:
        return {'success': False, 'message': 'Không thể thêm môn khi lộ trình đang học. Dùng nút Chỉnh sửa lộ trình'}
    
    # Kiểm tra môn đã có chưa
    query_check = """
        SELECT id FROM plan_subjects
        WHERE plan_id = %s AND subject_id = %s
    """
    existing = fetch_one(query_check, (plan_id, subject_uid))
    
    if existing:
        return {'success': False, 'message': 'Môn học đã có trong lộ trình'}
    
    # Thêm môn
    query = """
        INSERT INTO plan_subjects (plan_id, subject_id, progress, status)
        VALUES (%s, %s, 0, 'not_started')
    """
    
    if execute_query(query, (plan_id, subject_uid)):
        return {'success': True, 'message': 'Đã thêm môn học'}
    
    return {'success': False, 'message': 'Lỗi khi thêm môn học'}


def remove_subject_from_plan(plan_id, user_id, subject_uid, allow_edit=False):
    """Xóa môn học khỏi lộ trình"""
    # Kiểm tra plan
    query_plan = """
        SELECT is_started FROM study_plans
        WHERE id = %s AND user_id = %s
    """
    plan = fetch_one(query_plan, (plan_id, user_id))
    
    if not plan:
        return {'success': False, 'message': 'Không tìm thấy lộ trình'}
    
    if plan['is_started'] and not allow_edit:
        return {'success': False, 'message': 'Không thể xóa môn khi lộ trình đang học. Dùng nút Chỉnh sửa lộ trình'}
    
    # Xóa môn
    query = """
        DELETE FROM plan_subjects
        WHERE plan_id = %s AND subject_id = %s
    """
    
    if execute_query(query, (plan_id, subject_uid)):
        return {'success': True, 'message': 'Đã xóa môn học'}
    
    return {'success': False, 'message': 'Môn học không có trong lộ trình'}


def get_all_subjects_for_modal():
    """Lấy tất cả subjects để hiển thị trong modal thêm môn"""
    subjects = load_csv(SUBJECT_CSV)
    
    # Gắn uid cho mỗi subject
    for i, s in enumerate(subjects, start=1):
        s['uid'] = i
    
    return subjects
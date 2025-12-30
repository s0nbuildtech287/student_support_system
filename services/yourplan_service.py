# services/yourplan_service.py

import csv
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUBJECT_CSV = os.path.join(DATA_DIR, "subject_list.csv")
PLANS_JSON = os.path.join(DATA_DIR, "user_plans.json")


def load_csv(path):
    """Load CSV file"""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_plans():
    """Load user plans từ JSON"""
    if not os.path.exists(PLANS_JSON):
        return []
    
    with open(PLANS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_plans(plans):
    """Save user plans vào JSON"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PLANS_JSON, 'w', encoding='utf-8') as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)


def get_user_plans(user_id):
    """Lấy tất cả plans của user"""
    all_plans = load_plans()
    user_plans = [p for p in all_plans if p['user_id'] == user_id]
    
    # Gắn thông tin subjects vào mỗi plan
    subjects = load_csv(SUBJECT_CSV)
    
    for plan in user_plans:
        plan_subjects = []
        for subject_uid in plan.get('subject_uids', []):
            # Tìm subject theo uid
            for i, s in enumerate(subjects, start=1):
                if i == subject_uid:
                    s_copy = s.copy()
                    s_copy['uid'] = i
                    plan_subjects.append(s_copy)
                    break
        
        plan['subjects'] = plan_subjects
        # Tính tổng giờ học
        plan['total_hours'] = sum(int(s.get('study_hours', 0)) for s in plan_subjects)
    
    return user_plans


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
    
    plans = load_plans()
    
    # Kiểm tra giới hạn 3 lộ trình
    user_plans = [p for p in plans if p['user_id'] == user_id]
    if len(user_plans) >= 3:
        return {'success': False, 'message': 'Đã đạt giới hạn 3 lộ trình'}
    
    # Tạo ID mới
    new_id = max([p['id'] for p in plans], default=0) + 1
    
    new_plan = {
        'id': new_id,
        'user_id': user_id,
        'name': name,
        'description': description,
        'is_started': False,
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'subject_uids': []  # Danh sách UID của subjects
    }
    
    plans.append(new_plan)
    save_plans(plans)
    
    return {'success': True, 'message': 'Tạo lộ trình thành công', 'plan_id': new_id}


def update_plan_name(plan_id, user_id, new_name):
    """Cập nhật tên lộ trình"""
    if not new_name:
        return {'success': False, 'message': 'Tên không được để trống'}
    
    plans = load_plans()
    
    for plan in plans:
        if plan['id'] == plan_id and plan['user_id'] == user_id:
            plan['name'] = new_name
            save_plans(plans)
            return {'success': True, 'message': 'Cập nhật thành công'}
    
    return {'success': False, 'message': 'Không tìm thấy lộ trình'}


def delete_user_plan(plan_id, user_id):
    """Xóa lộ trình"""
    plans = load_plans()
    
    # Tìm và xóa
    new_plans = [p for p in plans if not (p['id'] == plan_id and p['user_id'] == user_id)]
    
    if len(new_plans) == len(plans):
        return {'success': False, 'message': 'Không tìm thấy lộ trình'}
    
    save_plans(new_plans)
    return {'success': True, 'message': 'Xóa thành công'}


def start_user_plan(plan_id, user_id):
    """Bắt đầu lộ trình (lock để không sửa được nữa)"""
    plans = load_plans()
    
    for plan in plans:
        if plan['id'] == plan_id and plan['user_id'] == user_id:
            if plan['is_started']:
                return {'success': False, 'message': 'Lộ trình đã được bắt đầu'}
            
            plan['is_started'] = True
            plan['started_at'] = datetime.now().isoformat()
            save_plans(plans)
            return {'success': True, 'message': 'Bắt đầu lộ trình thành công'}
    
    return {'success': False, 'message': 'Không tìm thấy lộ trình'}


def add_subject_to_plan(plan_id, user_id, subject_uid):
    """Thêm môn học vào lộ trình"""
    plans = load_plans()
    
    for plan in plans:
        if plan['id'] == plan_id and plan['user_id'] == user_id:
            # Kiểm tra môn đã có chưa
            if subject_uid in plan.get('subject_uids', []):
                return {'success': False, 'message': 'Môn học đã có trong lộ trình'}
            
            # Thêm môn
            if 'subject_uids' not in plan:
                plan['subject_uids'] = []
            
            plan['subject_uids'].append(subject_uid)
            save_plans(plans)
            return {'success': True, 'message': 'Đã thêm môn học'}
    
    return {'success': False, 'message': 'Không tìm thấy lộ trình'}


def remove_subject_from_plan(plan_id, user_id, subject_uid):
    """Xóa môn học khỏi lộ trình"""
    plans = load_plans()
    
    for plan in plans:
        if plan['id'] == plan_id and plan['user_id'] == user_id:
            # Xóa môn
            if subject_uid in plan.get('subject_uids', []):
                plan['subject_uids'].remove(subject_uid)
                save_plans(plans)
                return {'success': True, 'message': 'Đã xóa môn học'}
            
            return {'success': False, 'message': 'Môn học không có trong lộ trình'}
    
    return {'success': False, 'message': 'Không tìm thấy lộ trình'}


def get_all_subjects_for_modal():
    """Lấy tất cả subjects để hiển thị trong modal thêm môn"""
    subjects = load_csv(SUBJECT_CSV)
    
    # Gắn uid cho mỗi subject
    for i, s in enumerate(subjects, start=1):
        s['uid'] = i
    
    return subjects
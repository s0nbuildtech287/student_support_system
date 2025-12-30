# routes/yourplan.py

from flask import Blueprint, render_template, request, jsonify, redirect, session
from services.yourplan_service import (
    get_user_plans,
    create_user_plan,
    update_plan_name,
    delete_user_plan,
    start_user_plan,
    add_subject_to_plan,
    remove_subject_from_plan,
    get_plan_by_id,
    get_all_subjects_for_modal
)
from routes.user import get_current_user, login_required

yourplan_bp = Blueprint('yourplan', __name__)


@yourplan_bp.route('/yourplan')
@login_required
def yourplan():
    """Hiển thị trang YourPlan"""
    user = get_current_user()
    user_id = session.get('user_id')
    
    # Lấy tất cả plans của user
    plans = get_user_plans(user_id)
    
    # Lấy plan được chọn
    selected_plan_id = request.args.get('plan_id', type=int)
    selected_plan = None
    
    if selected_plan_id:
        selected_plan = get_plan_by_id(selected_plan_id, user_id)
    elif plans:
        selected_plan = plans[0]
    
    # Lấy tất cả subjects để hiển thị trong modal
    all_subjects = get_all_subjects_for_modal()
    
    return render_template(
        'yourplan.html',
        plans=plans,
        selected_plan=selected_plan,
        all_subjects=all_subjects,
        user=user
    )


@yourplan_bp.route('/yourplan/create', methods=['POST'])
@login_required
def create_plan():
    """Tạo lộ trình mới"""
    user_id = session.get('user_id')
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    result = create_user_plan(user_id, name, description)
    
    if not result['success']:
        return jsonify(result), 400
    
    return redirect('/yourplan')


@yourplan_bp.route('/yourplan/edit/<int:plan_id>', methods=['POST'])
@login_required
def edit_plan(plan_id):
    """Sửa tên lộ trình"""
    user_id = session.get('user_id')
    data = request.get_json()
    new_name = data.get('name', '').strip()
    
    result = update_plan_name(plan_id, user_id, new_name)
    return jsonify(result)


@yourplan_bp.route('/yourplan/delete/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    """Xóa lộ trình"""
    user_id = session.get('user_id')
    
    result = delete_user_plan(plan_id, user_id)
    return jsonify(result)


@yourplan_bp.route('/yourplan/start/<int:plan_id>', methods=['POST'])
@login_required
def start_plan(plan_id):
    """Bắt đầu lộ trình"""
    user_id = session.get('user_id')
    
    result = start_user_plan(plan_id, user_id)
    return jsonify(result)


@yourplan_bp.route('/yourplan/add-subject', methods=['POST'])
@login_required
def add_subject():
    """Thêm môn học vào lộ trình"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    plan_id = data.get('plan_id')
    subject_uid = data.get('subject_id')  # Đây là uid từ CSV
    
    result = add_subject_to_plan(plan_id, user_id, subject_uid)
    return jsonify(result)


@yourplan_bp.route('/yourplan/remove-subject', methods=['POST'])
@login_required
def remove_subject():
    """Xóa môn học khỏi lộ trình"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    plan_id = data.get('plan_id')
    subject_uid = data.get('subject_id')
    
    result = remove_subject_from_plan(plan_id, user_id, subject_uid)
    return jsonify(result)
from flask import Blueprint, render_template, request, abort, jsonify, session
import logging
from services.subject_service import (
    load_all_subject_paginated,
    get_subject_by_uid
)
from services.progress_service import (
    get_subject_learning_progress,
    mark_subject_completed,
    get_subject_progress_in_plan
)
from services.quiz_service import (
    get_random_quiz_questions,
    submit_quiz,
    has_passed_quiz_in_plan,
    get_best_attempt
)
from routes.user import get_current_user, login_required
# SỬ DỤNG N8N
from n8n.n8n_subject_service import load_subjects_from_n8n

subject_bp = Blueprint("subject", __name__)

@subject_bp.route("/subject")
def subject():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 9, type=int)
    category = request.args.get("category", "").strip()
    level = request.args.get("level", "").strip()
    keyword = request.args.get("keyword", "").strip()

    # Thử n8n trước (có fast-fail)
    data = load_subjects_from_n8n(
        page=page,
        per_page=per_page,
        category=category,
        level=level
    )
    
    # Nếu n8n trả về None (down hoặc error), dùng CSV
    if data is None:
        logging.info("⚡ Using CSV fallback for subjects")
        data = load_all_subject_paginated(
            page=page,
            per_page=per_page,
            category=category,
            level=level
        )
        source = "csv"
    else:
        source = "n8n"

    # Validate data
    if not data or "subjects" not in data:
        return "DATA ERROR", 500

    user = get_current_user()

    return render_template(
        "subject.html",
        subjects=data["subjects"],
        page=data["page"],
        total_pages=data["total_pages"],
        categories=data["categories"],
        selected_category=category,
        selected_level=level,
        keyword=keyword,
        per_page=per_page,
        user=user,
        source=source
    )


# Chi tiết môn học
@subject_bp.route("/subject/<int:uid>")
def subject_detail(uid):
    subject = get_subject_by_uid(uid)

    if not subject:
        abort(404)

    user = get_current_user()
    
    # Lấy thông tin tiến độ học tập (nếu user đã đăng nhập)
    learning_progress = None
    quiz_passed = False
    best_attempt = None
    plan_id = None
    can_do_quiz = False 
    
    if user:
        user_id = session.get('user_id')
        plan_id = request.args.get('plan_id', type=int)
        
        if plan_id:
            can_do_quiz = True
        
            learning_progress = get_subject_progress_in_plan(plan_id, uid)
            if learning_progress:
                learning_progress['plan_id'] = plan_id
                quiz_passed = has_passed_quiz_in_plan(user_id, uid, plan_id)
                best_attempt = get_best_attempt(user_id, uid, plan_id)
            else:
                can_do_quiz = False


    return render_template(
        "subject_detail.html",
        subject=subject,
        user=user,
        learning_progress=learning_progress,
        quiz_passed=quiz_passed,
        best_attempt=best_attempt,
        plan_id=plan_id,
        can_do_quiz=can_do_quiz  # THÊM biến này
    )


# Lấy câu hỏi quiz
@subject_bp.route("/subject/<int:uid>/quiz", methods=["GET"])
@login_required
def get_quiz(uid):
    """Lấy 10 câu hỏi ngẫu nhiên cho bài test"""
    # KIỂM TRA plan_id - BẮT BUỘC phải có
    plan_id = request.args.get('plan_id', type=int)
    
    if not plan_id:
        return jsonify({
            'success': False,
            'message': 'Vui lòng làm bài từ lộ trình của bạn'
        }), 403
    
    # Kiểm tra môn này có trong plan của user không
    user_id = session.get('user_id')
    from services.progress_service import get_subject_progress_in_plan
    
    progress = get_subject_progress_in_plan(plan_id, uid)
    if not progress:
        return jsonify({
            'success': False,
            'message': 'Môn học này không có trong lộ trình của bạn'
        }), 403
    
    questions = get_random_quiz_questions(uid, limit=10)
    
    if not questions:
        return jsonify({
            'success': False,
            'message': 'Môn học này chưa có câu hỏi'
        }), 404
    
    # Loại bỏ correct_answer khỏi response
    for q in questions:
        q.pop('correct_answer', None)
    
    return jsonify({
        'success': True,
        'questions': questions
    })


# Nộp bài quiz
@subject_bp.route("/subject/<int:uid>/quiz/submit", methods=["POST"])
@login_required
def submit_quiz_route(uid):
    """Nộp bài quiz và chấm điểm"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    answers = data.get('answers', {})
    plan_id = data.get('plan_id')
    
    # KIỂM TRA plan_id - BẮT BUỘC
    if not plan_id:
        return jsonify({
            'success': False,
            'message': 'Vui lòng làm bài từ lộ trình của bạn'
        }), 403
    
    # Kiểm tra môn này có trong plan của user không
    from services.progress_service import get_subject_progress_in_plan
    from database import fetch_one
    
    # Verify plan thuộc về user
    query_check = """
        SELECT id FROM study_plans 
        WHERE id = %s AND user_id = %s
    """
    if not fetch_one(query_check, (plan_id, user_id)):
        return jsonify({
            'success': False,
            'message': 'Lộ trình không hợp lệ'
        }), 403
    
    progress = get_subject_progress_in_plan(plan_id, uid)
    if not progress:
        return jsonify({
            'success': False,
            'message': 'Môn học này không có trong lộ trình của bạn'
        }), 403
    
    # Convert string keys to int
    answers = {int(k): v for k, v in answers.items()}
    
    result = submit_quiz(user_id, uid, answers, plan_id)
    
    return jsonify(result)


# Đánh dấu hoàn thành
@subject_bp.route("/subject/<int:uid>/mark-completed", methods=["POST"])
@login_required
def mark_completed(uid):
    user_id = session.get('user_id')
    data = request.get_json()
    plan_id = data.get('plan_id')
    
    # KIỂM TRA plan_id - BẮT BUỘC
    if not plan_id:
        return jsonify({
            'success': False,
            'message': 'Vui lòng hoàn thành môn học từ lộ trình của bạn'
        }), 403
    
    # Verify plan thuộc về user
    from database import fetch_one
    query_check = """
        SELECT id FROM study_plans 
        WHERE id = %s AND user_id = %s
    """
    if not fetch_one(query_check, (plan_id, user_id)):
        return jsonify({
            'success': False,
            'message': 'Lộ trình không hợp lệ'
        }), 403
    
    # Kiểm tra môn này có trong plan không
    from services.progress_service import get_subject_progress_in_plan
    progress = get_subject_progress_in_plan(plan_id, uid)
    if not progress:
        return jsonify({
            'success': False,
            'message': 'Môn học này không có trong lộ trình của bạn'
        }), 403
    
    result = mark_subject_completed(user_id, uid, plan_id)
    return jsonify(result)
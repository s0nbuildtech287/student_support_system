from flask import Blueprint, render_template, request, abort, jsonify, session
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

subject_bp = Blueprint("subject", __name__)

# Danh sách môn học
@subject_bp.route("/subject")
def subject_list():
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "").strip()
    level = request.args.get("level", "").strip()

    data = load_all_subject_paginated(
        page=page,
        per_page=9,
        category=category,
        level=level
    )

    user = get_current_user()

    return render_template(
        "subject.html",
        subjects=data["subjects"],
        page=data["page"],
        total_pages=data["total_pages"],
        categories=data["categories"],
        selected_category=category,
        selected_level=level,
        keyword="",
        user=user
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
    
    if user:
        user_id = session.get('user_id')
        
        # LẤY plan_id từ URL nếu có (khi click từ yourplan)
        plan_id = request.args.get('plan_id', type=int)
        
        if plan_id:
            # Kiểm tra môn này có trong plan không
            learning_progress = get_subject_progress_in_plan(plan_id, uid)
            if learning_progress:
                learning_progress['plan_id'] = plan_id
                quiz_passed = has_passed_quiz_in_plan(user_id, uid, plan_id)
                best_attempt = get_best_attempt(user_id, uid, plan_id)
        else:
            # Nếu không có plan_id, lấy từ plan đang học đầu tiên
            learning_progress = get_subject_learning_progress(user_id, uid)
            if learning_progress:
                plan_id = learning_progress.get('plan_id')
                quiz_passed = has_passed_quiz_in_plan(user_id, uid, plan_id)
                best_attempt = get_best_attempt(user_id, uid, plan_id)

    return render_template(
        "subject_detail.html",
        subject=subject,
        user=user,
        learning_progress=learning_progress,
        quiz_passed=quiz_passed,
        best_attempt=best_attempt,
        plan_id=plan_id
    )


# Lấy câu hỏi quiz
@subject_bp.route("/subject/<int:uid>/quiz", methods=["GET"])
@login_required
def get_quiz(uid):
    """Lấy 10 câu hỏi ngẫu nhiên cho bài test"""
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
    plan_id = data.get('plan_id')  # THÊM plan_id từ client
    
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
    plan_id = data.get('plan_id')  # THÊM plan_id từ client
    
    result = mark_subject_completed(user_id, uid, plan_id)
    return jsonify(result)
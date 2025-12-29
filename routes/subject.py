from flask import Blueprint, render_template, request, abort, session, redirect, url_for, jsonify
from models import db, Subject, Enrollment, User
from sqlalchemy import func

subject_bp = Blueprint("subject", __name__)

def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@subject_bp.route("/subject")
def subject_list():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "").strip()
    level = request.args.get("level", "").strip()
    
    # Build query
    query = Subject.query
    
    if category:
        query = query.filter_by(category=category)
    
    if level:
        query = query.filter_by(level=level)
    
    # Get categories for filter dropdown
    categories = db.session.query(Subject.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Pagination
    per_page = 9
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        "subject.html",
        subjects=paginated.items,
        page=page,
        total_pages=paginated.pages,
        categories=categories,
        selected_category=category,
        selected_level=level,
        user=user
    )

@subject_bp.route("/subject/<int:subject_id>")
def subject_detail(subject_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        user_id=user.id,
        subject_id=subject_id
    ).first()
    
    return render_template(
        "subject_detail.html",
        subject=subject,
        enrollment=enrollment,
        user=user
    )

@subject_bp.route("/subject/<int:subject_id>/enroll", methods=["POST"])
def enroll_subject(subject_id):
    """Enroll user in a subject"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401
    
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Check if already enrolled
        existing = Enrollment.query.filter_by(
            user_id=user.id,
            subject_id=subject_id
        ).first()
        
        if existing:
            return jsonify({"success": False, "message": "Bạn đã ghi danh khóa học này"}), 400
        
        # Create enrollment
        enrollment = Enrollment(
            user_id=user.id,
            subject_id=subject_id,
            status="In Progress"
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Ghi danh khóa học thành công"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500

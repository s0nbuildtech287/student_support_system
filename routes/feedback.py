from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import db, Feedback, User

feedback_bp = Blueprint("feedback", __name__)

def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@feedback_bp.route("/feedback")
def feedback():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    return render_template("feedback.html", user=user)

@feedback_bp.route("/feedback/submit", methods=["POST"])
def submit_feedback():
    """Submit feedback"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401
    
    try:
        subject = request.form.get("subject")
        message = request.form.get("message")
        rating = request.form.get("rating", type=int)
        
        if not subject or not message:
            return jsonify({"success": False, "message": "Tiêu đề và nội dung không được để trống"}), 400
        
        feedback = Feedback(
            user_id=user.id,
            subject=subject,
            message=message,
            rating=rating,
            status="New"
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Gửi phản hồi thành công. Cảm ơn bạn!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500
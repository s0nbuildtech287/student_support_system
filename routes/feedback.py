from flask import Blueprint, render_template, request, jsonify
from routes.user import get_current_user, login_required
from services.feedback_service import FeedbackService

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/feedback", methods=["GET", "POST"])
def feedback():
    user = get_current_user()
    # Save new feedback
    if request.method == "POST":
        data = request.get_json() or request.form
        comment = (data.get("comment") or "").strip()
        try:
            stars = int(data.get("stars", 5))
        except Exception:
            stars = 5

        if not comment:
            return jsonify({"success": False, "message": "Comment is required"}), 400

        user_id = user['id'] if user else None
        name = user['name'] if user else "Guest"
        avatar = user.get('avatar') if user and user.get('avatar') else '/static/images/avatar.jpg'

        FeedbackService.add_feedback(user_id, name, avatar, comment, stars)
        return jsonify({"success": True})

    # GET -> render page with existing feedbacks
    feedbacks = FeedbackService.get_feedbacks()
    return render_template("feedback.html", user=user, feedbacks=feedbacks)
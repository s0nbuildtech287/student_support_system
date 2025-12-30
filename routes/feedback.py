from flask import Blueprint, render_template
from routes.user import get_current_user, login_required

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/feedback")
def feedback():
    user = get_current_user()
    return render_template("feedback.html", user=user)
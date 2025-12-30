from flask import Blueprint, render_template
from routes.user import CURRENT_USER

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/feedback")
def feedback():
    return render_template("feedback.html", user=CURRENT_USER)
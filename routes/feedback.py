from flask import Blueprint, render_template

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/feedback")
def feedback():
    return render_template("feedback.html")
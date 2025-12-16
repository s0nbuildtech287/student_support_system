from flask import Blueprint, render_template

user_bp = Blueprint("user", __name__)

# Hardcoded user data
CURRENT_USER = {
    "id": 1,
    "name": "Khang Nguyen",
    "email": "khang@example.com",
    "age": 25,
    "height": 175,
    "weight": 75,
    "goal": "Build Muscle",
    "experience": "Intermediate",
    "avatar": "https://i.pravatar.cc/150?img=1",
    "joined_date": "2024-01-15",
    "total_workouts": 45
}

@user_bp.route("/profile")
def profile():
    return render_template("profile.html", user=CURRENT_USER)

@user_bp.route("/settings")
def settings():
    return render_template("settings.html", user=CURRENT_USER)

@user_bp.route("/statistics")
def statistics():
    return render_template("statistics.html", user=CURRENT_USER)

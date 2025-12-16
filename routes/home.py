from flask import Blueprint, render_template, session

home_bp = Blueprint("home", __name__)

@home_bp.route("/home")
def home():
    # Lấy thông tin user từ session nếu đã đăng nhập
    user_info = {
        "user_id": session.get("user_id"),
        "user_name": session.get("user_name"),
        "user_email": session.get("user_email")
    }
    return render_template("home.html", user=user_info)
from flask import Blueprint, render_template, redirect, url_for, session
from routes.user import get_current_user

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def index():
    # Nếu chưa đăng nhập thì redirect sang login
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user = get_current_user()
    return render_template("home.html", user=user)

@home_bp.route("/home")
def home():
    user = get_current_user()
    return render_template("home.html", user=user)
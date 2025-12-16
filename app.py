from flask import Flask, redirect, request, session, url_for
from routes.exercise import exercise_bp
from routes.home import home_bp
from routes.login import login_bp
from routes.register import register_bp
from utils.db import init_database

app = Flask(__name__)
app.secret_key = "workout_ai_secret_key_2024"  # Secret key cho session

# Khởi tạo database
init_database()

# Đăng ký route
app.register_blueprint(home_bp) 
app.register_blueprint(exercise_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)

@app.before_request
def require_login():
    """
    Bắt buộc đăng nhập cho mọi route trừ login/register/static.
    Nếu chưa có session user_id thì chuyển tới trang login.
    """
    allowed_endpoints = {"login.login", "register.register", "static"}
    if request.endpoint in allowed_endpoints or request.endpoint is None:
        return
    if not session.get("user_id"):
        return redirect(url_for("login.login"))

# Trang mặc định → Login
@app.route("/")
def index():
    return redirect("/login")

if __name__ == "__main__":
    # Disable reloader to avoid permission issues on Windows environments
    app.run(debug=True, use_reloader=False)

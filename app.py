from flask import Flask, redirect
from routes.subject import subject_bp
from routes.home import home_bp
from routes.ranking import ranking_bp
from routes.user import user_bp
from routes.roadmap import roadmap_bp
from routes.feedback import feedback_bp
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Đăng ký route (Blueprint)
app.register_blueprint(home_bp)
app.register_blueprint(subject_bp)
app.register_blueprint(ranking_bp)       
app.register_blueprint(user_bp)
app.register_blueprint(roadmap_bp)
app.register_blueprint(feedback_bp)

from flask import session, request, redirect, url_for, g
from services.user_service import UserService

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id:
        g.user = UserService.get_user_by_id(user_id)
    else:
        g.user = None

@app.before_request
def require_login():
    allowed_routes = ['user.login', 'user.register', 'static']
    if not g.user and request.endpoint not in allowed_routes:
        return redirect(url_for('user.login'))

@app.context_processor
def inject_user():
    return dict(user=g.user)

# Trang mặc định → Home (handles redirect if not logged in)
@app.route("/")
def index():
    return redirect(url_for('home.home'))

if __name__ == "__main__":
    app.run(debug=True)

# BÙI XUÂN SƠN
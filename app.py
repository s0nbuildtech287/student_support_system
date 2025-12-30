from flask import Flask, redirect, url_for
from routes.subject import subject_bp
from routes.home import home_bp
from routes.ranking import ranking_bp
from routes.user import user_bp
from routes.roadmap import roadmap_bp
from routes.feedback import feedback_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Đăng ký route (Blueprint)
app.register_blueprint(user_bp)       
app.register_blueprint(home_bp)
app.register_blueprint(subject_bp)
app.register_blueprint(ranking_bp)       
app.register_blueprint(roadmap_bp)
app.register_blueprint(feedback_bp)

# Route mặc định
@app.route("/")
def index():
    return redirect(url_for('user.login'))

if __name__ == "__main__":
    app.run(debug=True)
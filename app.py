from flask import Flask, redirect
from routes.subject import subject_bp
from routes.home import home_bp
from routes.ranking import ranking_bp
from routes.user import user_bp
from routes.roadmap import roadmap_bp
from routes.feedback import feedback_bp
app = Flask(__name__)

# Đăng ký route (Blueprint)
app.register_blueprint(home_bp)
app.register_blueprint(subject_bp)
app.register_blueprint(ranking_bp)       
app.register_blueprint(user_bp)
app.register_blueprint(roadmap_bp)
app.register_blueprint(feedback_bp)

# Trang mặc định → Exercise
@app.route("/")
def index():
    return redirect("/home")

if __name__ == "__main__":
    app.run(debug=True)

# BÙI XUÂN SƠN
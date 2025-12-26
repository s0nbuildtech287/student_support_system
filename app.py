from flask import Flask, redirect
from routes.exercise import exercise_bp
from routes.home import home_bp
from routes.ranking import ranking_bp  
from routes.user import user_bp
app = Flask(__name__)

# Đăng ký route (Blueprint)
app.register_blueprint(home_bp)
app.register_blueprint(exercise_bp)
app.register_blueprint(ranking_bp)       
app.register_blueprint(user_bp)

# Trang mặc định → Exercise
@app.route("/")
def index():
    return redirect("/exercise")

if __name__ == "__main__":
    app.run(debug=True)

# BÙI XUÂN SƠN
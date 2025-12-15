from flask import Flask, redirect
from routes.exercise import exercise_bp
from routes.home import home_bp 

app = Flask(__name__)

# Đăng ký route
app.register_blueprint(home_bp) 
app.register_blueprint(exercise_bp)

# Trang mặc định → Exercise
@app.route("/")
def index():
    return redirect("/exercise")

if __name__ == "__main__":
    app.run(debug=True)

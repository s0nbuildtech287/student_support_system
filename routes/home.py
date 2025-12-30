from flask import Blueprint, render_template
from routes.user import CURRENT_USER

home_bp = Blueprint("home", __name__)

@home_bp.route("/home")
def home():
    return render_template("home.html", user=CURRENT_USER)

@home_bp.route("/")
def index():
    return render_template("home.html", user=CURRENT_USER)

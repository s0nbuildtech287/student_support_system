from flask import Blueprint, render_template
from services.ranking_service import get_top_exercises

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/ranking")
def ranking_page():
    top_exercises = get_top_exercises()

    max_uses = max(item["uses"] for item in top_exercises) if top_exercises else 1
    return render_template("ranking.html", top_exercises=top_exercises, max_uses=max_uses)

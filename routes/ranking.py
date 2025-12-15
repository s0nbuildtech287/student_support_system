from flask import Blueprint, render_template
from services.ranking_service import get_top_exercises

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/ranking")
def ranking_page():
    # Lấy top bài tập (demo hardcode lượt dùng)
    top_exercises = get_top_exercises(limit=9)

    # Dùng cho progress bar
    max_uses = max(ex["uses"] for ex in top_exercises) if top_exercises else 1

    return render_template(
        "ranking.html",
        top_exercises=top_exercises,
        max_uses=max_uses
    )

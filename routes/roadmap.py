from flask import Blueprint, render_template, abort
from services.roadmap_service import get_all_roadmaps, get_roadmap_by_id, get_roadmap_steps
from routes.user import get_current_user, login_required

roadmap_bp = Blueprint("roadmap", __name__)

@roadmap_bp.route("/roadmap")
def roadmap_page():
    roadmaps = get_all_roadmaps()
    user = get_current_user()
    return render_template("roadmap.html", roadmaps=roadmaps, user=user)

@roadmap_bp.route("/roadmap/<int:roadmap_id>")
def roadmap_detail_page(roadmap_id):
    roadmap = get_roadmap_by_id(roadmap_id)
    if not roadmap:
        abort(404)
    steps = get_roadmap_steps(roadmap_id)
    user = get_current_user()
    return render_template("roadmap_detail.html", roadmap=roadmap, steps=steps, user=user)
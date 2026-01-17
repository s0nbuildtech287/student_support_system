from flask import Blueprint, render_template, abort, jsonify, session, redirect
from services.roadmap_service import get_all_roadmaps, get_roadmap_by_id, get_roadmap_steps, apply_roadmap_to_user_plan
from routes.user import get_current_user, login_required
from GGCloud.services.analytics_service import AnalyticsService

roadmap_bp = Blueprint("roadmap", __name__)

@roadmap_bp.route("/roadmap")
def roadmap_page():
    user = get_current_user()

    try:
        roadmaps = load_roadmaps_from_n8n()
        source = "n8n"
    except Exception as e:
        print("⚠️ N8N DOWN → FALLBACK CSV:", e) 
        roadmaps = get_all_roadmaps()
        source = "csv"

    return render_template(
        "roadmap.html",
        roadmaps=roadmaps,
        user=user,
        source=source
    )

@roadmap_bp.route("/roadmap/<int:roadmap_id>")
def roadmap_detail_page(roadmap_id):
    roadmap = get_roadmap_by_id(roadmap_id)
    if not roadmap:
        abort(404)
    steps = get_roadmap_steps(roadmap_id)
    user = get_current_user()
        # Track activity
    user_id = session.get('user_id')
    AnalyticsService.track_activity(
        user_id=user_id,
        activity_type='view_roadmap',
        target_name=roadmap.get('roadmap_name', 'Unknown'),
        target_id=roadmap_id
    )
    return render_template("roadmap_detail.html", roadmap=roadmap, steps=steps, user=user)


@roadmap_bp.route("/roadmap/<int:roadmap_id>/apply", methods=["POST"])
@login_required
def apply_roadmap(roadmap_id):
    """
    Áp dụng lộ trình có sẵn từ Roadmap vào YourPlan của user
    """
    user_id = session.get('user_id')
    
    # Kiểm tra roadmap có tồn tại không
    roadmap = get_roadmap_by_id(roadmap_id)
    if not roadmap:
        return jsonify({
            'success': False,
            'message': 'Lộ trình không tồn tại'
        }), 404
    
    # Áp dụng lộ trình
    result = apply_roadmap_to_user_plan(user_id, roadmap_id)
    
    if result['success']:
        # Redirect về YourPlan với plan vừa tạo
        return jsonify({
            'success': True,
            'message': result['message'],
            'plan_id': result.get('plan_id'),
            'redirect_url': f"/yourplan?plan_id={result.get('plan_id')}"
        })
    else:
        return jsonify(result), 400
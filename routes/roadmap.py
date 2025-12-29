from flask import Blueprint, render_template, abort, session, redirect, url_for, jsonify
from models import db, Roadmap, RoadmapSubject, RoadmapProgress, User

roadmap_bp = Blueprint("roadmap", __name__)

def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@roadmap_bp.route("/roadmap")
def roadmap_page():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    roadmaps = Roadmap.query.all()
    
    # Get user's roadmap progress
    user_roadmaps = {}
    for roadmap in roadmaps:
        progress = RoadmapProgress.query.filter_by(
            user_id=user.id,
            roadmap_id=roadmap.id
        ).first()
        user_roadmaps[roadmap.id] = progress
    
    return render_template("roadmap.html", roadmaps=roadmaps, user=user, user_roadmaps=user_roadmaps)

@roadmap_bp.route("/roadmap/<int:roadmap_id>")
def roadmap_detail_page(roadmap_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    roadmap = Roadmap.query.get_or_404(roadmap_id)
    
    # Get subjects in roadmap
    subjects = db.session.query(RoadmapSubject).filter_by(roadmap_id=roadmap_id).order_by(RoadmapSubject.order).all()
    
    # Get user's progress
    progress = RoadmapProgress.query.filter_by(
        user_id=user.id,
        roadmap_id=roadmap_id
    ).first()
    
    return render_template(
        "roadmap_detail.html",
        roadmap=roadmap,
        subjects=subjects,
        progress=progress,
        user=user
    )

@roadmap_bp.route("/roadmap/<int:roadmap_id>/start", methods=["POST"])
def start_roadmap(roadmap_id):
    """Start a roadmap"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401
    
    try:
        roadmap = Roadmap.query.get_or_404(roadmap_id)
        
        # Check if already started
        existing = RoadmapProgress.query.filter_by(
            user_id=user.id,
            roadmap_id=roadmap_id
        ).first()
        
        if existing:
            return jsonify({"success": False, "message": "Bạn đã bắt đầu roadmap này"}), 400
        
        # Create progress
        progress = RoadmapProgress(
            user_id=user.id,
            roadmap_id=roadmap_id,
            status="In Progress"
        )
        
        db.session.add(progress)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Bắt đầu roadmap thành công"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500

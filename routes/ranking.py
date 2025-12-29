from flask import Blueprint, render_template, session, redirect, url_for
from models import db, User, Enrollment, Subject
from sqlalchemy import func, desc

ranking_bp = Blueprint("ranking", __name__)

def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@ranking_bp.route("/ranking")
def ranking():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    # Get top users by completed courses
    top_users = db.session.query(
        User.name,
        func.count(Enrollment.id).label('completed_count')
    ).join(
        Enrollment, Enrollment.user_id == User.id
    ).filter(
        Enrollment.status == "Completed"
    ).group_by(
        User.id, User.name
    ).order_by(
        desc('completed_count')
    ).limit(10).all()
    
    top_completed = [{"name": user[0], "completed": user[1]} for user in top_users]
    
    # Get top subjects
    top_subjects = db.session.query(
        Subject.name,
        func.count(Enrollment.id).label('enrollment_count')
    ).join(
        Enrollment, Enrollment.subject_id == Subject.id
    ).group_by(
        Subject.id, Subject.name
    ).order_by(
        desc('enrollment_count')
    ).limit(10).all()
    
    subject_labels = [subject[0] for subject in top_subjects]
    subject_values = [subject[1] for subject in top_subjects]
    
    # Prepare roadmap data (popularity by career goal)
    roadmap_labels = [
        "Full Stack Developer", "Data Scientist", "AI Engineer", "DevOps Engineer",
        "Mobile Developer", "Cloud Architect", "Backend Developer", "Frontend Developer",
        "Machine Learning Engineer", "Security Engineer"
    ]
    roadmap_values = [i for i in range(100, 0, -10)]
    
    return render_template(
        "ranking.html",
        top_completed=top_completed,
        subject_labels=subject_labels,
        subject_values=subject_values,
        roadmap_labels=roadmap_labels,
        roadmap_values=roadmap_values,
        user=user
    )

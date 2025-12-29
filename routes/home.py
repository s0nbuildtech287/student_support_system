from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import db, User, Enrollment
from services.groq_service import get_ai_recommendation, chat_about_roadmap, chat_directly

home_bp = Blueprint("home", __name__)

def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@home_bp.route("/")
@home_bp.route("/index")
def index():
    """Home page - redirect to login if not authenticated"""
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    return redirect(url_for('home.home'))

@home_bp.route("/home")
def home():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    # Get user statistics
    total_enrollments = Enrollment.query.filter_by(user_id=user.id).count()
    completed_courses = Enrollment.query.filter_by(user_id=user.id, status="Completed").count()
    in_progress = Enrollment.query.filter_by(user_id=user.id, status="In Progress").count()
    
    stats = {
        "total_courses": total_enrollments,
        "completed": completed_courses,
        "in_progress": in_progress,
        "completion_rate": round((completed_courses / total_enrollments * 100) if total_enrollments > 0 else 0, 1)
    }
    
    return render_template("home.html", user=user, stats=stats, roadmap="")

@home_bp.route("/recommend", methods=["POST"])
def recommend():
    """Get course recommendations based on user input using Groq AI"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        # Get form data
        year = request.form.get("year", type=int)
        gpa = request.form.get("gpa", type=float)
        hours_per_week = request.form.get("hours_per_week", type=int) or request.form.get("study_time", type=int)
        career_goal = request.form.get("goal")
        custom_goal = request.form.get("custom_goal")
        learning_mode = request.form.get("learning_mode")
        resource = request.form.get("resource")
        level = request.form.get("level")
        
        # Update user info in database
        user.year = year
        user.gpa = gpa
        user.career_goal = custom_goal or career_goal
        db.session.commit()
        
        # Prepare user info for Groq
        user_info = {
            "year": year,
            "gpa": gpa,
            "hours_per_week": hours_per_week,
            "career_goal": career_goal,
            "custom_goal": custom_goal,
            "learning_mode": learning_mode,
            "resource": resource,
            "level": level
        }
        
        # Get AI recommendation from Groq
        recommendation = get_ai_recommendation(user_info)
        
        return jsonify({
            "success": True,
            "message": "Đã tạo đề xuất lộ trình học tập thành công",
            "recommendation": recommendation
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500


@home_bp.route("/chat", methods=["POST"])
def chat():
    """Chat about the recommended roadmap"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        user_question = request.json.get("message")
        current_recommendation = request.json.get("recommendation")
        conversation_history = request.json.get("history", [])
        
        # Get user info from session/database
        user_info = {
            "year": user.year or 1,
            "gpa": user.gpa or 0,
            "career_goal": user.career_goal or "unknown"
        }
        
        # Get chat response from Groq
        response = chat_about_roadmap(
            user_question, 
            current_recommendation, 
            user_info,
            conversation_history
        )
        
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500


@home_bp.route("/chat-direct", methods=["POST"])
def chat_direct():
    """Direct chat about courses without user profile"""
    try:
        user_question = request.json.get("message")
        
        if not user_question or not user_question.strip():
            return jsonify({"success": False, "message": "Vui lòng nhập câu hỏi"}), 400
        
        # Get direct chat response from Groq
        response = chat_directly(user_question)
        
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        print(f"Direct chat error: {str(e)}")
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500

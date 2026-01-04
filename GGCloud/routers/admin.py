# GGCloud/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from functools import wraps
import sys
import os

# Thêm đường dẫn để import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GGCloud.services.analytics_service import AnalyticsService
from GGCloud.services.auth_service import AdminAuthService

admin_bp = Blueprint('admin', __name__, 
                     template_folder='../templates',
                     static_folder='../static',
                     url_prefix='/admin')

# Decorator kiểm tra quyền admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            return redirect(url_for('user.login'))
        
        if not AdminAuthService.is_admin(user_id):
            return "Access Denied: Admin only", 403
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Trang dashboard admin"""
    
    # Lấy thống kê tổng quan
    overview = AnalyticsService.get_overview_stats()
    
    # Môn học được xem nhiều nhất
    top_subjects = AnalyticsService.get_most_viewed_subjects(days=30, limit=10)
    
    # Lộ trình được xem nhiều nhất
    top_roadmaps = AnalyticsService.get_most_viewed_roadmaps(days=30, limit=10)
    
    # Người dùng hoạt động theo ngày
    daily_users = AnalyticsService.get_daily_active_users(days=30)
    
    return render_template('admin_dashboard.html',
                          overview=overview,
                          top_subjects=top_subjects,
                          top_roadmaps=top_roadmaps,
                          daily_users=daily_users)

@admin_bp.route('/api/subjects')
@admin_required
def api_subjects():
    """API lấy dữ liệu môn học"""
    days = request.args.get('days', 30, type=int)
    subjects = AnalyticsService.get_most_viewed_subjects(days=days, limit=20)
    return jsonify(subjects)

@admin_bp.route('/api/roadmaps')
@admin_required
def api_roadmaps():
    """API lấy dữ liệu lộ trình"""
    days = request.args.get('days', 30, type=int)
    roadmaps = AnalyticsService.get_most_viewed_roadmaps(days=days, limit=20)
    return jsonify(roadmaps)

@admin_bp.route('/api/user-journey/<int:user_id>')
@admin_required
def api_user_journey(user_id):
    """API lấy hành trình người dùng"""
    journey = AnalyticsService.get_user_journey(user_id, days=7)
    return jsonify(journey)
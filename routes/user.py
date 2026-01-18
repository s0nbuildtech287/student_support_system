from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
import os
import json
import logging
from datetime import datetime
from services.user_service import UserService
from services.statistics_service import StatisticsService
from services.superset_service import superset_service
from n8n.n8n_infouser_service import load_user_from_n8n
user_bp = Blueprint("user", __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    """
    Lấy thông tin user từ session
    Ưu tiên: n8n (MySQL) -> fallback UserService (MySQL trực tiếp)
    """
    if 'user_id' not in session:
        return None
    
    user_id = session['user_id']
    
    # Thử lấy từ n8n trước
    user = load_user_from_n8n(user_id)
    if user:
        logging.info(f"✅ Loaded user {user_id} from n8n->MySQL")
        # Convert created_at string to datetime object if needed
        if isinstance(user.get('created_at'), str):
            try:
                user['created_at'] = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
            except:
                user['created_at'] = datetime.now()
        return user
    
    # Fallback: query MySQL trực tiếp qua UserService
    user = UserService.get_user_by_id(user_id)
    return user

def login_required(f):
    """Decorator để yêu cầu đăng nhập"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Vui lòng đăng nhập", "warning")
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """Đăng nhập"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Try n8n authentication (với fake success logging)
        from n8n.n8n_login_service import authenticate_via_n8n
        user = authenticate_via_n8n(email, password)
        
        if user:
            # Lưu user_id vào session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('home.home'))
        else:
            flash("Email hoặc mật khẩu không đúng", "danger")
            return render_template("login.html")
    
    # Nếu đã đăng nhập rồi thì redirect về home
    if 'user_id' in session:
        return redirect(url_for('home.home'))
    
    return render_template("login.html")

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    """Đăng ký tài khoản"""
    if request.method == "POST":
        name = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        phone = request.form.get("phone")
        
        # Validation
        if not name or not email or not password:
            flash("Vui lòng điền đầy đủ thông tin", "danger")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Mật khẩu không khớp", "danger")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự", "danger")
            return render_template("register.html")
        
        # Đăng ký qua n8n (với fake success logging)
        from n8n.n8n_register_service import register_via_n8n
        result = register_via_n8n(name, email, password, phone)
        
        if result:
            flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
            return redirect(url_for('user.login'))
        else:
            flash("Email đã tồn tại hoặc có lỗi xảy ra", "danger")
            return render_template("register.html")
    
    # Nếu đã đăng nhập rồi thì redirect về home
    if 'user_id' in session:
        return redirect(url_for('home.home'))
    
    return render_template("register.html")

@user_bp.route("/google_login", methods=["POST"])
def google_login():
    """Xử lý đăng nhập bằng Google"""
    try:
        email = request.form.get("email")
        name = request.form.get("name")
        avatar = request.form.get("avatar")
        
        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400
            
        # Kiểm tra user đã tồn tại chưa
        user = UserService.get_user_by_email(email)
        
        if not user:
            # Nếu chưa tồn tại thì tạo mới với password ngẫu nhiên
            import string
            import random
            
            # Tạo password ngẫu nhiên 12 ký tự
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = ''.join(random.choice(chars) for _ in range(12))
            
            # Tạo user
            result = UserService.create_user(name, email, password)
            
            if not result['success']:
                return jsonify(result), 400
                
            # Lấy user vừa tạo
            user = UserService.get_user_by_email(email)
            
            # Cập nhật avatar nếu có
            if avatar and user:
                UserService.update_avatar(user['id'], avatar)
                # Cập nhật lại user info sau khi update avatar
                user = UserService.get_user_by_email(email)
        
        # Đăng nhập (lưu session)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"success": False, "message": "Login failed"}), 401
            
    except Exception as e:
        print(f"Google login error: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500

@user_bp.route("/logout")
def logout():
    """Đăng xuất"""
    session.clear()
    flash("Đã đăng xuất", "info")
    return redirect(url_for('user.login'))

@user_bp.route("/profile")
@login_required
def profile():
    """Trang profile"""
    user = get_current_user()
    return render_template("profile.html", user=user)

@user_bp.route("/settings")
@login_required
def settings():
    """Trang settings"""
    user = get_current_user()
    return render_template("settings.html", user=user)

@user_bp.route("/statistics")
@login_required
def statistics():
    """Trang thống kê - lấy dữ liệu từ database"""
    user = get_current_user()
    user_id = session.get('user_id')
    
    # Lấy tất cả thống kê từ service
    stats = StatisticsService.get_all_statistics(user_id)
    
    return render_template("statistics.html", user=user, stats=stats)

@user_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    """Cập nhật thông tin profile"""
    try:
        data = {
            'name': request.form.get("name"),
            'age': request.form.get("age"),
            'year': request.form.get("year"),
            'major': request.form.get("major"),
            'career_goal': request.form.get("career_goal"),
            'status': request.form.get("status")
        }
        
        # Validate
        if not data['name'] or len(data['name'].strip()) == 0:
            flash("Tên không được để trống", "danger")
            return redirect(url_for('user.settings'))
        
        # Update
        if UserService.update_user(session['user_id'], data):
            session['user_name'] = data['name']
            flash("Cập nhật thông tin thành công!", "success")
        else:
            flash("Lỗi khi cập nhật thông tin", "danger")
        
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/profile/update-avatar", methods=["POST"])
@login_required
def update_avatar():
    """Cập nhật avatar"""
    try:
        if 'avatar' not in request.files:
            return jsonify({"success": False, "message": "Không có file được chọn"}), 400
        
        file = request.files['avatar']
        
        if file.filename == '':
            return jsonify({"success": False, "message": "Không có file được chọn"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": "Chỉ chấp nhận file ảnh"}), 400
        
        # Tạo filename với timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"avatar_{timestamp}.{ext}"
        
        # Đảm bảo folder tồn tại
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Lưu file
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        # Update database
        avatar_path = f"/static/images/{filename}"
        UserService.update_avatar(session['user_id'], avatar_path)
        
        return jsonify({
            "success": True,
            "message": "Cập nhật avatar thành công",
            "avatar": avatar_path
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500

@user_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """Đổi mật khẩu"""
    try:
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validate
        if not new_password or len(new_password) < 6:
            flash("Mật khẩu mới phải có ít nhất 6 ký tự", "danger")
            return redirect(url_for('user.settings'))
        
        if new_password != confirm_password:
            flash("Mật khẩu mới không khớp", "danger")
            return redirect(url_for('user.settings'))
        
        # Đổi password
        result = UserService.change_password(session['user_id'], current_password, new_password)
        
        if result['success']:
            flash(result['message'], "success")
        else:
            flash(result['message'], "danger")
        
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/update-preferences", methods=["POST"])
@login_required
def update_preferences():
    """Cập nhật sở thích học tập"""
    try:
        data = {
            'study_level': request.form.get("study_level"),
            'study_goal': request.form.get("study_goal"),
            'study_style': request.form.get("study_style"),
            'preferred_language': request.form.get("preferred_language")
        }
        
        if UserService.update_user(session['user_id'], data):
            flash("Sở thích học tập đã được lưu thành công!", "success")
        else:
            flash("Lỗi khi cập nhật sở thích", "danger")
        
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))


# ==================== API ENDPOINTS CHO THỐNG KÊ ====================

@user_bp.route("/api/statistics")
@login_required
def api_statistics():
    """API endpoint lấy tất cả thống kê của user"""
    user_id = session.get('user_id')
    stats = StatisticsService.get_all_statistics(user_id)
    return jsonify(stats)


@user_bp.route("/api/statistics/overview")
@login_required
def api_statistics_overview():
    """API endpoint lấy tổng quan thống kê"""
    user_id = session.get('user_id')
    overview = StatisticsService.get_user_overview(user_id)
    return jsonify(overview)


@user_bp.route("/api/statistics/weekly")
@login_required
def api_statistics_weekly():
    """API endpoint lấy tiến độ theo tuần"""
    user_id = session.get('user_id')
    weekly = StatisticsService.get_weekly_progress(user_id)
    return jsonify(weekly)


@user_bp.route("/api/statistics/favorite-subjects")
@login_required
def api_statistics_favorite():
    """API endpoint lấy môn học yêu thích"""
    user_id = session.get('user_id')
    favorite = StatisticsService.get_favorite_subjects(user_id)
    return jsonify(favorite)


@user_bp.route("/api/statistics/monthly")
@login_required
def api_statistics_monthly():
    """API endpoint lấy xu hướng hàng tháng"""
    user_id = session.get('user_id')
    monthly = StatisticsService.get_monthly_trend(user_id)
    return jsonify(monthly)


@user_bp.route("/api/statistics/quiz")
@login_required
def api_statistics_quiz():
    """API endpoint lấy thống kê quiz"""
    user_id = session.get('user_id')
    quiz = StatisticsService.get_quiz_statistics(user_id)
    return jsonify(quiz)


@user_bp.route("/api/statistics/study-plans")
@login_required
def api_statistics_study_plans():
    """API endpoint lấy tiến độ lộ trình"""
    user_id = session.get('user_id')
    plans = StatisticsService.get_study_plans_progress(user_id)
    return jsonify(plans)


@user_bp.route("/api/statistics/achievements")
@login_required
def api_statistics_achievements():
    """API endpoint lấy thành tích"""
    user_id = session.get('user_id')
    achievements = StatisticsService.get_achievements(user_id)
    return jsonify(achievements)


# ==================== SUPERSET API ENDPOINTS ====================

@user_bp.route("/api/superset/login")
@login_required
def api_superset_login():
    """Test đăng nhập vào Superset"""
    success = superset_service.login()
    return jsonify({
        "success": success,
        "message": "Superset login successful" if success else "Superset login failed"
    })


@user_bp.route("/api/superset/databases")
@login_required
def api_superset_databases():
    """Lấy danh sách databases từ Superset"""
    databases = superset_service.get_databases()
    return jsonify({"databases": databases})


@user_bp.route("/api/superset/datasets")
@login_required
def api_superset_datasets():
    """Lấy danh sách datasets từ Superset"""
    datasets = superset_service.get_datasets()
    return jsonify({"datasets": datasets})


@user_bp.route("/api/superset/charts")
@login_required
def api_superset_charts():
    """Lấy danh sách charts từ Superset"""
    charts = superset_service.get_charts()
    return jsonify({"charts": charts})


@user_bp.route("/api/superset/dashboards")
@login_required
def api_superset_dashboards():
    """Lấy danh sách dashboards từ Superset"""
    dashboards = superset_service.get_dashboards()
    return jsonify({"dashboards": dashboards})


@user_bp.route("/api/superset/chart/<int:chart_id>/data")
@login_required
def api_superset_chart_data(chart_id):
    """Lấy dữ liệu của chart từ Superset"""
    try:
        data = superset_service.get_chart_data(chart_id)
        if data:
            return jsonify({"success": True, "data": data})
        return jsonify({"success": False, "error": "Chart not found or no data"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@user_bp.route("/api/superset/chart/<int:chart_id>/info")
@login_required
def api_superset_chart_info(chart_id):
    """Lấy thông tin chi tiết của chart"""
    try:
        info = superset_service.get_chart_by_id(chart_id)
        if info:
            return jsonify({"success": True, "data": info})
        return jsonify({"success": False, "error": "Chart not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@user_bp.route("/api/superset/chart/<int:chart_id>/render-data")
@login_required
def api_superset_chart_render_data(chart_id):
    """Lấy dữ liệu đã format để render chart trên web"""
    try:
        info = superset_service.get_chart_by_id(chart_id)
        if not info:
            return jsonify({"success": False, "error": "Chart not found"})
        
        # Parse params
        params = {}
        try:
            params = json.loads(info.get("params", "{}")) if isinstance(info.get("params"), str) else info.get("params", {})
        except:
            params = {}
        
        # Get datasource info
        datasource_id = info.get("datasource_id")
        
        # Try to get actual data via SQL
        # Get the SQL from query_context or build from params
        sql = None
        if "adhoc_filters" in params or "groupby" in params:
            # Build simple SQL based on chart config
            table_name = info.get("datasource_name_text", "").split(".")[-1] if info.get("datasource_name_text") else None
            if table_name:
                groupby = params.get("groupby", [])
                metrics = params.get("metrics", [])
                
                if groupby:
                    group_col = groupby[0] if isinstance(groupby[0], str) else groupby[0].get("column", {}).get("column_name", "")
                    sql = f"SELECT {group_col}, COUNT(*) as count FROM {table_name} GROUP BY {group_col} LIMIT 10"
        
        # Execute SQL if we have one
        chart_data = {"labels": [], "values": []}
        if sql:
            result = superset_service.execute_query(1, sql)  # database_id = 1
            if result and "data" in result:
                rows = result["data"]
                if rows:
                    # Extract labels and values from first two columns
                    for row in rows:
                        values = list(row.values())
                        if len(values) >= 2:
                            chart_data["labels"].append(str(values[0]))
                            chart_data["values"].append(values[1])
        
        return jsonify({
            "success": True,
            "chart_name": info.get("slice_name", "Unknown"),
            "viz_type": info.get("viz_type", "bar"),
            "data": chart_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@user_bp.route("/api/superset/query", methods=["POST"])
@login_required
def api_superset_query():
    """Thực thi SQL query qua Superset SQL Lab"""
    try:
        data = request.get_json()
        database_id = data.get("database_id", 1)
        sql = data.get("sql", "")
        
        if not sql:
            return jsonify({"success": False, "error": "SQL query is required"})
        
        result = superset_service.execute_query(database_id, sql)
        if result and "error" not in result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": result.get("error", "Query failed")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@user_bp.route("/api/superset/statistics")
@login_required
def api_superset_statistics():
    """Lấy thống kê user qua Superset API"""
    try:
        user_id = session.get('user_id')
        database_id = request.args.get('database_id', 1, type=int)
        
        stats = superset_service.get_user_statistics_via_superset(user_id, database_id)
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@user_bp.route("/api/superset/all-charts")
@login_required
def api_superset_all_charts():
    """Lấy tất cả dữ liệu charts từ Superset"""
    try:
        result = superset_service.get_all_chart_data_for_web()
        return jsonify(result)
    except Exception as e:
        return jsonify({"charts": [], "error": str(e)})
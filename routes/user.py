from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
import os
import logging
from datetime import datetime
from services.user_service import UserService
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
    logging.warning(f"⚠️ N8N failed, using direct MySQL fallback")
    user = UserService.get_user_by_id(user_id)
    if user:
        logging.info(f"✅ Loaded user {user_id} from direct MySQL (fallback)")
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
        
        # Xác thực user
        user = UserService.authenticate_user(email, password)
        
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
        
        # Tạo user mới
        result = UserService.create_user(name, email, password, phone)
        
        if result['success']:
            flash(result['message'], "success")
            return redirect(url_for('user.login'))
        else:
            flash(result['message'], "danger")
            return render_template("register.html")
    
    # Nếu đã đăng nhập rồi thì redirect về home
    if 'user_id' in session:
        return redirect(url_for('home.home'))
    
    return render_template("register.html")

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
    """Trang thống kê"""
    user = get_current_user()
    return render_template("statistics.html", user=user)

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
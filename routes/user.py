from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from models import db, User

user_bp = Blueprint("user", __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@user_bp.route("/profile")
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    return render_template("profile.html", user=user)

@user_bp.route("/settings")
def settings():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    return render_template("settings.html", user=user)

@user_bp.route("/statistics")
def statistics():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    return render_template("statistics.html", user=user)

@user_bp.route("/profile/update", methods=["POST"])
def update_profile():
    """Update user profile information"""
    try:
        user = get_current_user()
        if not user:
            flash("Chưa đăng nhập", "danger")
            return redirect(url_for('user.login'))
        
        name = request.form.get("name")
        email = request.form.get("email")
        age = request.form.get("age")
        year = request.form.get("year")
        major = request.form.get("major")
        career_goal = request.form.get("career_goal")
        status = request.form.get("status")
        
        # Validate email format
        if not email or "@" not in email:
            flash("Email không hợp lệ", "danger")
            return redirect(url_for('user.settings'))
        
        # Check if email already exists
        if email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash("Email đã được sử dụng", "danger")
                return redirect(url_for('user.settings'))
        
        # Validate name
        if not name or len(name.strip()) == 0:
            flash("Tên không được để trống", "danger")
            return redirect(url_for('user.settings'))
        
        # Update user
        user.name = name
        user.email = email
        if age:
            user.age = int(age)
        if year:
            user.year = int(year)
        if major:
            user.major = major
        if career_goal:
            user.career_goal = career_goal
        if status:
            user.status = status
        
        db.session.commit()
        flash("Cập nhật thông tin thành công!", "success")
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/profile/update-avatar", methods=["POST"])
def update_avatar():
    """Update user avatar"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401
        
        if 'avatar' not in request.files:
            return jsonify({"success": False, "message": "Không có file được chọn"}), 400
        
        file = request.files['avatar']
        
        if file.filename == '':
            return jsonify({"success": False, "message": "Không có file được chọn"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": "Chỉ chấp nhận file ảnh (png, jpg, jpeg, gif, avif, webp)"}), 400
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"avatar_{user.id}_{timestamp}.{ext}"
        
        # Ensure upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        # Update user avatar
        avatar_path = f"/static/images/{filename}"
        user.avatar = avatar_path
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Cập nhật avatar thành công",
            "avatar": avatar_path
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home.home'))
        else:
            return render_template("login.html", error="Email hoặc mật khẩu không đúng")
    
    return render_template("login.html")

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not name or not email or not password:
            return render_template("register.html", error="Tất cả trường bắt buộc")
        
        if password != confirm_password:
            return render_template("register.html", error="Mật khẩu không khớp")
        
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Email đã tồn tại")
        
        # Create new user
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            avatar="/static/images/avatar.jpg"
        )
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        return redirect(url_for('home.home'))
    
    return render_template("register.html")

@user_bp.route("/change-password", methods=["POST"])
def change_password():
    """Change user password"""
    try:
        user = get_current_user()
        if not user:
            flash("Chưa đăng nhập", "danger")
            return redirect(url_for('user.login'))
        
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validate current password
        if not check_password_hash(user.password, current_password):
            flash("Mật khẩu hiện tại không đúng", "danger")
            return redirect(url_for('user.settings'))
        
        # Validate new password
        if not new_password or len(new_password) < 6:
            flash("Mật khẩu mới phải có ít nhất 6 ký tự", "danger")
            return redirect(url_for('user.settings'))
        
        # Check if passwords match
        if new_password != confirm_password:
            flash("Mật khẩu mới không khớp", "danger")
            return redirect(url_for('user.settings'))
        
        # Update password
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash("Đổi mật khẩu thành công!", "success")
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/update-preferences", methods=["POST"])
def update_preferences():
    """Update user study preferences"""
    try:
        user = get_current_user()
        if not user:
            flash("Chưa đăng nhập", "danger")
            return redirect(url_for('user.login'))
        
        # Get form data
        study_level = request.form.get("study_level")
        study_goal = request.form.get("study_goal")
        study_style = request.form.get("study_style")
        preferred_language = request.form.get("preferred_language")
        
        # Update user preferences
        if study_level:
            user.study_level = study_level
        if study_goal:
            user.study_goal = study_goal
        if study_style:
            user.study_style = study_style
        if preferred_language:
            user.preferred_language = preferred_language
        
        db.session.commit()
        
        flash("Sở thích học tập đã được lưu thành công!", "success")
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/logout")
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('user.login'))



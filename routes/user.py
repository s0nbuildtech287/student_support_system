from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import os
from datetime import datetime

user_bp = Blueprint("user", __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp'}

# Hardcoded user data
CURRENT_USER = {
    "id": 1,
    "name": "Kevin Dev",
    "email": "khang@example.com",
    "age": 25,
    "year": 2,
    "major": "Công nghệ thông tin",
    "status": "Đang học",
    "career_goal": "Software Engineer",
    "avatar": "/static/images/avatar.jpg",
    "joined_date": "2024-01-15",
    "total_courses": 8,
    "study_level": "Trung cấp",
    "study_goal": "Nâng cao kỹ năng",
    "study_style": "Video & Bài tập",
    "preferred_language": "Tiếng Việt",
    "enrollments": [
        {"id": 1, "name": "Python Cơ bản"},
        {"id": 2, "name": "Web Development"},
        {"id": 3, "name": "Database Design"},
        {"id": 4, "name": "API Development"}
    ],
    "progress": [
        {"id": 1, "name": "Bài 1: Biến và kiểu dữ liệu", "completed": True},
        {"id": 2, "name": "Bài 2: Vòng lặp", "completed": True},
        {"id": 3, "name": "Bài 3: Hàm", "completed": True},
        {"id": 4, "name": "Bài 4: Xử lý file", "completed": False},
        {"id": 5, "name": "Bài 5: OOP", "completed": False}
    ]
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    """Get current hardcoded user"""
    return CURRENT_USER

@user_bp.route("/profile")
def profile():
    return render_template("profile.html", user=CURRENT_USER)

@user_bp.route("/settings")
def settings():
    return render_template("settings.html", user=CURRENT_USER)

@user_bp.route("/statistics")
def statistics():
    return render_template("statistics.html", user=CURRENT_USER)

@user_bp.route("/profile/update", methods=["POST"])
def update_profile():
    """Update user profile information"""
    try:
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
        
        # Validate name
        if not name or len(name.strip()) == 0:
            flash("Tên không được để trống", "danger")
            return redirect(url_for('user.settings'))
        
        # Update user
        CURRENT_USER["name"] = name
        CURRENT_USER["email"] = email
        if age:
            CURRENT_USER["age"] = int(age)
        if year:
            CURRENT_USER["year"] = int(year)
        if major:
            CURRENT_USER["major"] = major
        if career_goal:
            CURRENT_USER["career_goal"] = career_goal
        if status:
            CURRENT_USER["status"] = status
        
        flash("Cập nhật thông tin thành công!", "success")
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/profile/update-avatar", methods=["POST"])
def update_avatar():
    """Update user avatar"""
    try:
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
        filename = f"avatar_{timestamp}.{ext}"
        
        # Ensure upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        # Update user avatar
        avatar_path = f"/static/images/{filename}"
        CURRENT_USER["avatar"] = avatar_path
        
        return jsonify({
            "success": True,
            "message": "Cập nhật avatar thành công",
            "avatar": avatar_path
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Hardcoded login check
        if email == "khang@example.com" and password == "123456":
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
        
        # For hardcoded version, just update current user
        CURRENT_USER["name"] = name
        CURRENT_USER["email"] = email
        
        return redirect(url_for('home.home'))
    
    return render_template("register.html")

@user_bp.route("/change-password", methods=["POST"])
def change_password():
    """Change user password"""
    try:
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Hardcoded password check
        if current_password != "123456":
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
        
        flash("Đổi mật khẩu thành công!", "success")
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/update-preferences", methods=["POST"])
def update_preferences():
    """Update user study preferences"""
    try:
        # Get form data
        study_level = request.form.get("study_level")
        study_goal = request.form.get("study_goal")
        study_style = request.form.get("study_style")
        preferred_language = request.form.get("preferred_language")
        
        # Update user preferences
        if study_level:
            CURRENT_USER["study_level"] = study_level
        if study_goal:
            CURRENT_USER["study_goal"] = study_goal
        if study_style:
            CURRENT_USER["study_style"] = study_style
        if preferred_language:
            CURRENT_USER["preferred_language"] = preferred_language
        
        flash("Sở thích học tập đã được lưu thành công!", "success")
        return redirect(url_for('user.settings'))
        
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect(url_for('user.settings'))

@user_bp.route("/logout")
def logout():
    """User logout"""
    return redirect(url_for('user.login'))
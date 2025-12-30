from flask import Blueprint, render_template, redirect, url_for, request, jsonify

user_bp = Blueprint("user", __name__)

# Hardcoded user data
CURRENT_USER = {
    "id": 1,
    "name": "Khang Nguyen",
    "email": "khang@example.com",
    "age": 25,
    "year": 2,
    "major": "Công nghệ thông tin",
    "status": "Đang học",
    "career_goal": "Software Engineer",
    "avatar": "./static/images/avatar.jpg",
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

@user_bp.route("/profile")
def profile():
    return render_template("profile.html", user=CURRENT_USER)

@user_bp.route("/settings")
def settings():
    return render_template("settings.html", user=CURRENT_USER)

@user_bp.route("/statistics")
def statistics():
    return render_template("statistics.html", user=CURRENT_USER)

@user_bp.route("/logout")
def logout():
    return redirect(url_for('home.home'))

@user_bp.route("/update-profile", methods=["POST"])
def update_profile():
    data = request.get_json()
    if data:
        CURRENT_USER["name"] = data.get("name", CURRENT_USER["name"])
        CURRENT_USER["email"] = data.get("email", CURRENT_USER["email"])
        CURRENT_USER["age"] = data.get("age", CURRENT_USER["age"])
        CURRENT_USER["year"] = data.get("year", CURRENT_USER["year"])
        CURRENT_USER["major"] = data.get("major", CURRENT_USER["major"])
        CURRENT_USER["career_goal"] = data.get("career_goal", CURRENT_USER["career_goal"])
        CURRENT_USER["status"] = data.get("status", CURRENT_USER["status"])
    return jsonify({"success": True, "message": "Cập nhật thành công", "user": CURRENT_USER})

@user_bp.route("/change-password", methods=["POST"])
def change_password():
    return jsonify({"success": True, "message": "Đổi mật khẩu thành công"})

@user_bp.route("/update-preferences", methods=["POST"])
def update_preferences():
    data = request.form
    if data:
        CURRENT_USER["study_level"] = data.get("study_level", CURRENT_USER["study_level"])
        CURRENT_USER["study_goal"] = data.get("study_goal", CURRENT_USER["study_goal"])
        CURRENT_USER["study_style"] = data.get("study_style", CURRENT_USER["study_style"])
        CURRENT_USER["preferred_language"] = data.get("preferred_language", CURRENT_USER["preferred_language"])
    return redirect(url_for('user.settings'))

@user_bp.route("/profile/update-avatar", methods=["POST"])
def update_avatar():
    if "avatar" in request.files:
        file = request.files["avatar"]
        if file:
            CURRENT_USER["avatar"] = "./static/images/avatar.jpg"
            return jsonify({"success": True, "message": "Cập nhật ảnh đại diện thành công", "avatar": CURRENT_USER["avatar"]})
    return jsonify({"success": False, "message": "Không có file được chọn"})

@user_bp.route("/profile/update", methods=["POST"])
def update_profile_api():
    data = request.get_json()
    if data:
        CURRENT_USER["name"] = data.get("name", CURRENT_USER["name"])
        CURRENT_USER["email"] = data.get("email", CURRENT_USER["email"])
    return jsonify({"success": True, "message": "Cập nhật thành công", "user": CURRENT_USER})

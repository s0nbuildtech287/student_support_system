from flask import Blueprint, render_template, request, redirect, url_for, session, flash

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            flash("Vui lòng điền đầy đủ thông tin", "error")
            return render_template("login.html")
        
        from services.account_service import login_user
        success, message, user = login_user(email, password)
        
        if success:
            # Lưu thông tin user vào session
            session["user_id"] = user["id"]
            session["user_name"] = user["fullname"]
            session["user_email"] = user["email"]
            return redirect(url_for("home.home"))
        else:
            flash(message, "error")
            return render_template("login.html")
    
    return render_template("login.html")

@login_bp.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất thành công", "success")
    return redirect(url_for("login.login"))


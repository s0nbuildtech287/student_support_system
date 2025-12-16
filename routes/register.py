from flask import Blueprint, render_template, request, redirect, url_for, flash

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not fullname or not email or not password or not confirm_password:
            flash("Vui lòng điền đầy đủ thông tin", "error")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp", "error")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự", "error")
            return render_template("register.html")
        
        from services.account_service import register_user
        success, message, user_id = register_user(fullname, email, password)
        
        if success:
            flash(message, "success")
            return redirect(url_for("login.login"))
        else:
            flash(message, "error")
            return render_template("register.html")
    
    return render_template("register.html")


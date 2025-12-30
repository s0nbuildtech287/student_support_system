from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.user_service import UserService

user_bp = Blueprint("user", __name__)

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = UserService.login_user(email, password)
        if user:
            session['user_id'] = user['id']
            # Store essential user info in session/g if needed, or fetch on demand
            return redirect(url_for('home.home'))
        else:
            flash("Invalid email or password", "error")
            
    return render_template("login.html")

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        phone = request.form.get("phone")
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")
            
        success, message = UserService.register_user(fullname, email, password, phone)
        if success:
            flash(message, "success")
            return redirect(url_for('user.login'))
        else:
            flash(message, "error")
            
    return render_template("register.html")

@user_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('user.login'))

@user_bp.route("/profile")
def profile():
    user_id = session.get('user_id')
    user = UserService.get_user_by_id(user_id)
    return render_template("profile.html", user=user)

@user_bp.route("/settings")
def settings():
    user_id = session.get('user_id')
    user = UserService.get_user_by_id(user_id)
    return render_template("settings.html", user=user)

@user_bp.route("/statistics")
def statistics():
    user_id = session.get('user_id')
    user = UserService.get_user_by_id(user_id)
    return render_template("statistics.html", user=user)

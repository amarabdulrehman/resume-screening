"""routes/auth.py — Authentication Routes (Login / Register / Logout)"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash)
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


# ── Register ──────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # ── Validation ──────────────────────────────────
        if not all([name, email, password, confirm]):
            flash("All fields are required.", "warning")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("auth/register.html")

        if db.session.query(User).filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html")

        # ── Create user ──────────────────────────────────
        # First ever user becomes admin automatically
        is_first = db.session.query(User).count() == 0
        user = User(name=name, email=email, is_admin=is_first)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        flash(f"Welcome to RecruitAI, {name}! Your account has been created.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/register.html")


# ── Login ─────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = db.session.query(User).filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(next_page or url_for("main.index"))

    return render_template("auth/login.html")


# ── Logout ────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

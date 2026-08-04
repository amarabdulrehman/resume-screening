"""routes/admin.py — Super-Admin Dashboard"""

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.candidate import Candidate
from models.job import Job
from models.result import ScreeningResult

admin_bp = Blueprint("admin", __name__)


def require_admin():
    """Abort with 403 if the current user is not an admin."""
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


@admin_bp.route("/")
@login_required
def dashboard():
    """Super-admin overview of all users and platform stats."""
    require_admin()

    users       = db.session.query(User).order_by(User.created_at.desc()).all()
    total_users = len(users)
    total_cands = db.session.query(Candidate).count()
    total_jobs  = db.session.query(Job).count()
    total_res   = db.session.query(ScreeningResult).count()

    # Per-user stats
    user_stats = []
    for u in users:
        cands = db.session.query(Candidate).filter_by(owner_id=u.id).count()
        jobs  = db.session.query(Job).filter_by(owner_id=u.id).count()
        res   = db.session.query(ScreeningResult).filter_by(owner_id=u.id).count()
        user_stats.append({
            "user":       u,
            "candidates": cands,
            "jobs":       jobs,
            "results":    res,
        })

    return render_template(
        "admin/dashboard.html",
        user_stats    = user_stats,
        total_users   = total_users,
        total_cands   = total_cands,
        total_jobs    = total_jobs,
        total_results = total_res,
    )


@admin_bp.route("/user/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
def toggle_admin(user_id):
    """Promote or demote a user's admin status."""
    require_admin()
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.dashboard"))
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "warning")
        return redirect(url_for("admin.dashboard"))
    user.is_admin = not user.is_admin
    db.session.commit()
    status = "promoted to admin" if user.is_admin else "demoted from admin"
    flash(f"{user.name} has been {status}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    """Delete a user and all their data."""
    require_admin()
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.dashboard"))
    if user.id == current_user.id:
        flash("You cannot delete your own account from here.", "warning")
        return redirect(url_for("admin.dashboard"))
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.email} and all their data have been deleted.", "info")
    return redirect(url_for("admin.dashboard"))

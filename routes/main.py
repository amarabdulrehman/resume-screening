"""routes/main.py — Dashboard & Home Routes"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Candidate, Job, ScreeningResult
from extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """Main dashboard with statistics scoped to the current user."""
    uid = current_user.id

    total_candidates = db.session.query(Candidate).filter_by(owner_id=uid).count()
    total_jobs       = db.session.query(Job).filter_by(owner_id=uid).count()
    total_results    = db.session.query(ScreeningResult).filter_by(owner_id=uid).count()

    recent_candidates = (
        db.session.query(Candidate)
        .filter_by(owner_id=uid)
        .order_by(Candidate.uploaded_at.desc())
        .limit(5).all()
    )
    recent_jobs = (
        db.session.query(Job)
        .filter_by(owner_id=uid)
        .order_by(Job.created_at.desc())
        .limit(5).all()
    )

    # Top result by score for this user
    top_result = (
        db.session.query(ScreeningResult)
        .filter_by(owner_id=uid)
        .order_by(ScreeningResult.match_score.desc())
        .first()
    )

    return render_template(
        "index.html",
        total_candidates  = total_candidates,
        total_jobs        = total_jobs,
        total_results     = total_results,
        recent_candidates = recent_candidates,
        recent_jobs       = recent_jobs,
        top_result        = top_result,
    )


@main_bp.route("/candidates")
@login_required
def all_candidates():
    """List all candidates belonging to the current user."""
    candidates = (
        db.session.query(Candidate)
        .filter_by(owner_id=current_user.id)
        .order_by(Candidate.uploaded_at.desc())
        .all()
    )
    return render_template("candidates.html", candidates=candidates)

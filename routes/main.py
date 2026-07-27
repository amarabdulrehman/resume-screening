"""routes/main.py — Dashboard & Home Routes"""

from flask import Blueprint, render_template
from models import Candidate, Job, ScreeningResult
from extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Main dashboard with system statistics."""
    total_candidates = db.session.query(Candidate).count()
    total_jobs       = db.session.query(Job).count()
    total_results    = db.session.query(ScreeningResult).count()
    recent_candidates= db.session.query(Candidate).order_by(
                          Candidate.uploaded_at.desc()).limit(5).all()
    recent_jobs      = db.session.query(Job).order_by(
                          Job.created_at.desc()).limit(5).all()

    # Top result by score
    top_result = (
        db.session.query(ScreeningResult)
        .order_by(ScreeningResult.match_score.desc())
        .first()
    )

    return render_template(
        "index.html",
        total_candidates = total_candidates,
        total_jobs       = total_jobs,
        total_results    = total_results,
        recent_candidates= recent_candidates,
        recent_jobs      = recent_jobs,
        top_result       = top_result,
    )


@main_bp.route("/candidates")
def all_candidates():
    """List all candidates."""
    candidates = db.session.query(Candidate).order_by(
        Candidate.uploaded_at.desc()).all()
    return render_template("candidates.html", candidates=candidates)

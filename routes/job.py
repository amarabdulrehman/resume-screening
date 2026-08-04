"""routes/job.py — Job Description & Screening Routes"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, jsonify, abort)
from flask_login import login_required, current_user
from extensions import db
from models import Job, Candidate, ScreeningResult
from services.matcher import rank_candidates

job_bp = Blueprint("job", __name__)


def _get_owned_job(job_id: int) -> Job:
    """Fetch a job and abort 403 if it doesn't belong to current user."""
    job = db.session.get(Job, job_id)
    if not job or job.owner_id != current_user.id:
        abort(403)
    return job


@job_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_job():
    """Create a new job description."""
    if request.method == "POST":
        title       = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        skills_raw  = request.form.get("required_skills", "").strip()

        if not title or not description:
            flash("Job title and description are required.", "warning")
            return redirect(request.url)

        required_skills = [
            s.strip().lower()
            for s in skills_raw.split(",")
            if s.strip()
        ]

        job = Job(title=title, description=description, owner_id=current_user.id)
        job.required_skills = required_skills
        db.session.add(job)
        db.session.commit()

        flash(f'Job "{title}" created successfully!', "success")
        return redirect(url_for("job.job_detail", job_id=job.id))

    return render_template("job_form.html")


@job_bp.route("/<int:job_id>")
@login_required
def job_detail(job_id):
    """Single job detail page."""
    job = _get_owned_job(job_id)
    return render_template("job_detail.html", job=job)


@job_bp.route("/<int:job_id>/screen", methods=["POST"])
@login_required
def screen(job_id):
    """Run NLP screening for current user's candidates against this job."""
    job = _get_owned_job(job_id)
    uid = current_user.id

    candidates = db.session.query(Candidate).filter_by(owner_id=uid).all()
    if not candidates:
        flash("No candidates uploaded yet.", "warning")
        return redirect(url_for("job.job_detail", job_id=job_id))

    # Delete previous results for this job (owned by this user)
    db.session.query(ScreeningResult).filter_by(
        job_id=job_id, owner_id=uid
    ).delete()

    # Run matching engine
    ranked = rank_candidates(candidates, job)

    # Persist results
    for rank_pos, (candidate, scores) in enumerate(ranked, start=1):
        result = ScreeningResult(
            owner_id      = uid,
            candidate_id  = candidate.id,
            job_id        = job_id,
            match_score   = scores["match_score"],
            tfidf_score   = scores["tfidf_score"],
            skill_overlap = scores["skill_overlap"],
            exp_bonus     = scores["exp_bonus"],
            rank          = rank_pos,
        )
        db.session.add(result)

    db.session.commit()
    flash(f"Screening complete! Ranked {len(ranked)} candidates.", "success")
    return redirect(url_for("job.results", job_id=job_id))


@job_bp.route("/<int:job_id>/results")
@login_required
def results(job_id):
    """Ranked candidates table for a specific job."""
    job = _get_owned_job(job_id)

    ranked_results = (
        db.session.query(ScreeningResult)
        .filter_by(job_id=job_id, owner_id=current_user.id)
        .order_by(ScreeningResult.rank)
        .all()
    )
    return render_template("results.html", job=job, results=ranked_results)


@job_bp.route("/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    """Delete a job posting."""
    job = _get_owned_job(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted.", "info")
    return redirect(url_for("main.index"))


@job_bp.route("/list")
@login_required
def job_list():
    """All job postings belonging to the current user."""
    jobs = (
        db.session.query(Job)
        .filter_by(owner_id=current_user.id)
        .order_by(Job.created_at.desc())
        .all()
    )
    return render_template("job_list.html", jobs=jobs)


# ── JSON API endpoint ────────────────────────────────────
@job_bp.route("/api/screen", methods=["POST"])
@login_required
def api_screen():
    """
    JSON API: POST { job_id: int } → returns ranked candidates as JSON.
    Only screens candidates owned by the current user.
    """
    data   = request.get_json(force=True)
    job_id = data.get("job_id")
    job    = db.session.get(Job, job_id)
    if not job or job.owner_id != current_user.id:
        return jsonify({"error": "Job not found"}), 404

    candidates = db.session.query(Candidate).filter_by(owner_id=current_user.id).all()
    ranked     = rank_candidates(candidates, job)

    return jsonify([
        {
            "rank":      i + 1,
            "candidate": c.to_dict(),
            "scores":    s,
        }
        for i, (c, s) in enumerate(ranked)
    ])

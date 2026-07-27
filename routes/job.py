"""routes/job.py — Job Description & Screening Routes"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, jsonify)
from extensions import db
from models import Job, Candidate, ScreeningResult
from services.matcher import rank_candidates

job_bp = Blueprint("job", __name__)


@job_bp.route("/new", methods=["GET", "POST"])
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

        job = Job(title=title, description=description)
        job.required_skills = required_skills
        db.session.add(job)
        db.session.commit()

        flash(f'Job "{title}" created successfully!', "success")
        return redirect(url_for("job.job_detail", job_id=job.id))

    return render_template("job_form.html")


@job_bp.route("/<int:job_id>")
def job_detail(job_id):
    """Single job detail page."""
    job = db.session.get(Job, job_id)
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("main.index"))
    return render_template("job_detail.html", job=job)


@job_bp.route("/<int:job_id>/screen", methods=["POST"])
def screen(job_id):
    """Run NLP screening for all candidates against this job."""
    job = db.session.get(Job, job_id)
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("main.index"))

    candidates = db.session.query(Candidate).all()
    if not candidates:
        flash("No candidates uploaded yet.", "warning")
        return redirect(url_for("job.job_detail", job_id=job_id))

    # Delete previous results for this job
    db.session.query(ScreeningResult).filter_by(job_id=job_id).delete()

    # Run matching engine
    ranked = rank_candidates(candidates, job)

    # Persist results
    for rank_pos, (candidate, scores) in enumerate(ranked, start=1):
        result = ScreeningResult(
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
def results(job_id):
    """Ranked candidates table for a specific job."""
    job = db.session.get(Job, job_id)
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("main.index"))

    ranked_results = (
        db.session.query(ScreeningResult)
        .filter_by(job_id=job_id)
        .order_by(ScreeningResult.rank)
        .all()
    )
    return render_template("results.html", job=job, results=ranked_results)


@job_bp.route("/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    """Delete a job posting."""
    job = db.session.get(Job, job_id)
    if job:
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted.", "info")
    return redirect(url_for("main.index"))


@job_bp.route("/list")
def job_list():
    """All job postings."""
    jobs = db.session.query(Job).order_by(Job.created_at.desc()).all()
    return render_template("job_list.html", jobs=jobs)


# ── JSON API endpoint ────────────────────────────────────
@job_bp.route("/api/screen", methods=["POST"])
def api_screen():
    """
    JSON API: POST { job_id: int } → returns ranked candidates as JSON.
    """
    data   = request.get_json(force=True)
    job_id = data.get("job_id")
    job    = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    candidates = db.session.query(Candidate).all()
    ranked     = rank_candidates(candidates, job)

    return jsonify([
        {
            "rank":      i + 1,
            "candidate": c.to_dict(),
            "scores":    s,
        }
        for i, (c, s) in enumerate(ranked)
    ])

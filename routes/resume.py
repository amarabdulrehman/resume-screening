"""routes/resume.py — Resume Upload & Candidate Routes"""

import os
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, current_app, jsonify, abort)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Candidate
from services.file_parser import parse_resume
from services.extractor import extract_candidate_info

resume_bp = Blueprint("resume", __name__)


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def user_upload_dir() -> str:
    """Return and create a per-user upload subdirectory."""
    base = os.path.join(current_app.config["UPLOAD_FOLDER"], str(current_user.id))
    os.makedirs(base, exist_ok=True)
    return base


@resume_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload one or multiple resume files (scoped to current user)."""
    if request.method == "POST":
        files = request.files.getlist("resumes")
        if not files or all(f.filename == "" for f in files):
            flash("No files selected.", "warning")
            return redirect(request.url)

        added = []
        errors = []
        upload_dir = user_upload_dir()

        for file in files:
            if file and allowed_file(file.filename):
                filename  = secure_filename(file.filename)
                save_path = os.path.join(upload_dir, filename)
                file.save(save_path)

                try:
                    raw_text = parse_resume(save_path)
                    info = extract_candidate_info(
                        raw_text,
                        current_app.config["SKILLS_DB_PATH"]
                    )

                    candidate = Candidate(
                        owner_id         = current_user.id,
                        name             = info.get("name"),
                        email            = info.get("email"),
                        phone            = info.get("phone"),
                        education        = info.get("education"),
                        experience_years = info.get("experience_years", 0.0),
                        experience_text  = info.get("experience_text"),
                        resume_filename  = filename,
                        raw_text         = raw_text,
                    )
                    candidate.skills = info.get("skills", [])
                    db.session.add(candidate)
                    added.append(filename)

                except Exception as e:
                    errors.append(f"{filename}: {str(e)}")

        db.session.commit()

        if added:
            flash(f"Successfully processed {len(added)} resume(s).", "success")
        if errors:
            for err in errors:
                flash(f"Error — {err}", "danger")

        return redirect(url_for("main.all_candidates"))

    return render_template("upload.html")


@resume_bp.route("/candidate/<int:candidate_id>")
@login_required
def candidate_detail(candidate_id):
    """Full candidate profile page — only accessible by owner."""
    candidate = db.session.get(Candidate, candidate_id)
    if not candidate or candidate.owner_id != current_user.id:
        abort(403)

    results = sorted(
        candidate.results,
        key=lambda r: r.match_score,
        reverse=True
    )
    return render_template(
        "candidate_detail.html",
        candidate=candidate,
        results=results
    )


@resume_bp.route("/candidate/<int:candidate_id>/delete", methods=["POST"])
@login_required
def delete_candidate(candidate_id):
    """Delete a candidate and their resume file — only accessible by owner."""
    candidate = db.session.get(Candidate, candidate_id)
    if not candidate or candidate.owner_id != current_user.id:
        abort(403)

    # Remove uploaded file
    file_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        str(current_user.id),
        candidate.resume_filename
    )
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(candidate)
    db.session.commit()
    flash("Candidate deleted.", "info")
    return redirect(url_for("main.all_candidates"))

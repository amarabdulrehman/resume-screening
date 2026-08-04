"""
models/result.py — Screening Result Model
==========================================
Stores the NLP matching score between a Candidate and a Job.
Each result is owned by a specific user (tenant).
"""

from datetime import datetime, timezone
from extensions import db


class ScreeningResult(db.Model):
    __tablename__ = "screening_results"

    id            = db.Column(db.Integer, primary_key=True)
    owner_id      = db.Column(db.Integer, db.ForeignKey("users.id"),
                              nullable=False, index=True)
    candidate_id  = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    job_id        = db.Column(db.Integer, db.ForeignKey("jobs.id"),        nullable=False)
    match_score   = db.Column(db.Float,   default=0.0)   # composite 0-100
    tfidf_score   = db.Column(db.Float,   default=0.0)   # cosine similarity 0-1
    skill_overlap = db.Column(db.Float,   default=0.0)   # 0-1
    exp_bonus     = db.Column(db.Float,   default=0.0)   # 0-1
    rank          = db.Column(db.Integer, nullable=True)
    screened_at   = db.Column(db.DateTime,
                              default=lambda: datetime.now(timezone.utc))

    candidate = db.relationship("Candidate", back_populates="results")
    job       = db.relationship("Job",       back_populates="results")

    def to_dict(self):
        return {
            "id":            self.id,
            "candidate_id":  self.candidate_id,
            "job_id":        self.job_id,
            "match_score":   round(self.match_score, 2),
            "tfidf_score":   round(self.tfidf_score, 4),
            "skill_overlap": round(self.skill_overlap, 4),
            "exp_bonus":     round(self.exp_bonus, 4),
            "rank":          self.rank,
            "screened_at":   self.screened_at.isoformat() if self.screened_at else None,
        }

    def __repr__(self):
        return f"<Result candidate={self.candidate_id} job={self.job_id} score={self.match_score:.1f}>"

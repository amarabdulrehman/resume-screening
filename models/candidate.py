"""
models/candidate.py — Candidate Model
=======================================
Stores extracted candidate information from a resume.
Each candidate is owned by a specific user (tenant).
"""

import json
from datetime import datetime, timezone
from extensions import db


class Candidate(db.Model):
    __tablename__ = "candidates"

    id                = db.Column(db.Integer, primary_key=True)
    owner_id          = db.Column(db.Integer, db.ForeignKey("users.id"),
                                  nullable=False, index=True)
    name              = db.Column(db.String(200), nullable=True)
    email             = db.Column(db.String(200), nullable=True)
    phone             = db.Column(db.String(50),  nullable=True)
    _skills           = db.Column("skills",      db.Text, default="[]")
    education         = db.Column(db.Text,        nullable=True)
    experience_years  = db.Column(db.Float,       default=0.0)
    experience_text   = db.Column(db.Text,        nullable=True)
    resume_filename   = db.Column(db.String(500), nullable=False)
    raw_text          = db.Column(db.Text,        nullable=True)
    uploaded_at       = db.Column(db.DateTime,
                                  default=lambda: datetime.now(timezone.utc))

    # Relationships
    owner   = db.relationship("User",            back_populates="candidates")
    results = db.relationship(
        "ScreeningResult", back_populates="candidate",
        cascade="all, delete-orphan"
    )

    # ── Skills: stored as JSON string ───────────────────
    @property
    def skills(self):
        try:
            return json.loads(self._skills or "[]")
        except (ValueError, TypeError):
            return []

    @skills.setter
    def skills(self, value):
        self._skills = json.dumps(value if value else [])

    @property
    def skills_display(self):
        """Comma-separated skills string for templates."""
        return ", ".join(self.skills) if self.skills else "N/A"

    def to_dict(self):
        return {
            "id":               self.id,
            "name":             self.name or "Unknown",
            "email":            self.email or "N/A",
            "phone":            self.phone or "N/A",
            "skills":           self.skills,
            "education":        self.education or "N/A",
            "experience_years": self.experience_years,
            "resume_filename":  self.resume_filename,
            "uploaded_at":      self.uploaded_at.isoformat() if self.uploaded_at else None,
        }

    def __repr__(self):
        return f"<Candidate {self.id}: {self.name}>"

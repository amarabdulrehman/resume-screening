"""
models/job.py — Job Description Model
=======================================
Stores a job posting and its required skills/description.
"""

import json
from datetime import datetime, timezone
from extensions import db


class Job(db.Model):
    __tablename__ = "jobs"

    id              = db.Column(db.Integer, primary_key=True)
    title           = db.Column(db.String(300), nullable=False)
    description     = db.Column(db.Text,         nullable=False)
    _required_skills= db.Column("required_skills", db.Text, default="[]")
    created_at      = db.Column(db.DateTime,
                                default=lambda: datetime.now(timezone.utc))

    # Relationship to screening results
    results = db.relationship(
        "ScreeningResult", back_populates="job",
        cascade="all, delete-orphan"
    )

    @property
    def required_skills(self):
        try:
            return json.loads(self._required_skills or "[]")
        except (ValueError, TypeError):
            return []

    @required_skills.setter
    def required_skills(self, value):
        self._required_skills = json.dumps(value if value else [])

    @property
    def required_skills_display(self):
        return ", ".join(self.required_skills) if self.required_skills else "N/A"

    def to_dict(self):
        return {
            "id":              self.id,
            "title":           self.title,
            "description":     self.description,
            "required_skills": self.required_skills,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Job {self.id}: {self.title}>"

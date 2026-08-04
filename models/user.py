"""
models/user.py — User / Tenant Model
======================================
Each registered account is a tenant. All data (jobs, candidates, results)
is scoped to the user via owner_id foreign keys.
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(200), nullable=False)
    email         = db.Column(db.String(200), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False, nullable=False)
    plan          = db.Column(db.String(20), default="free")   # stub — no restrictions
    created_at    = db.Column(db.DateTime,
                              default=lambda: datetime.now(timezone.utc))

    # Relationships (cascade delete when user is removed)
    jobs       = db.relationship("Job",       back_populates="owner",
                                 cascade="all, delete-orphan", lazy="dynamic")
    candidates = db.relationship("Candidate", back_populates="owner",
                                 cascade="all, delete-orphan", lazy="dynamic")

    # ── Password helpers ─────────────────────────────────
    def set_password(self, plaintext: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(plaintext).decode("utf-8")

    def check_password(self, plaintext: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, plaintext)

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "is_admin":   self.is_admin,
            "plan":       self.plan,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"

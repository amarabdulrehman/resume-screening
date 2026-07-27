"""
extensions.py — Shared Flask Extensions
=========================================
Instantiated here to avoid circular imports between app.py and models.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db      = SQLAlchemy()
migrate = Migrate()

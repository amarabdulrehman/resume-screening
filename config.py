"""
config.py — Application Configuration
======================================
Switch DATABASE_URL to a MySQL/PostgreSQL URI for production:
  MySQL:      mysql+pymysql://user:pass@localhost/resume_db
  PostgreSQL: postgresql://user:pass@localhost/resume_db
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ai-resume-screening-secret-2026")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'resume_screening.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024          # 10 MB max upload
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    SKILLS_DB_PATH = os.path.join(BASE_DIR, "nlp_data", "skills_db.json")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}

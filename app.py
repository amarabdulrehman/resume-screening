"""
app.py — Flask Application Factory
=====================================
Entry point. Creates and configures the Flask app,
registers all blueprints, and initialises extensions.
"""

import os
from flask import Flask
from config import config
from extensions import db, migrate


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ── Ensure upload directory exists ──────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Initialise extensions ────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    # ── Import models so SQLAlchemy sees them ────────────
    from models import candidate, job, result   # noqa: F401

    # ── Register blueprints ──────────────────────────────
    from routes.main   import main_bp
    from routes.resume import resume_bp
    from routes.job    import job_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp, url_prefix="/resume")
    app.register_blueprint(job_bp,    url_prefix="/job")

    # ── Create all tables on first run ───────────────────
    with app.app_context():
        db.create_all()

    return app


# ── Development entry point ──────────────────────────────
app = create_app("development")

if __name__ == "__main__":
    app.run(debug=True, port=5000)

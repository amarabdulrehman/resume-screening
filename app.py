"""
app.py — Flask Application Factory
=====================================
Entry point. Creates and configures the Flask app,
registers all blueprints, and initialises extensions.
"""

import os
from flask import Flask
from config import config
from extensions import db, migrate, login_manager, bcrypt


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ── Ensure upload directory exists ──────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Initialise extensions ────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view       = "auth.login"
    login_manager.login_message    = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # ── User loader for Flask-Login ──────────────────────
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # ── Import models so SQLAlchemy sees them ────────────
    from models import candidate, job, result   # noqa: F401

    # ── Register blueprints ──────────────────────────────
    from routes.auth  import auth_bp
    from routes.main  import main_bp
    from routes.resume import resume_bp
    from routes.job   import job_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp,   url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp, url_prefix="/resume")
    app.register_blueprint(job_bp,    url_prefix="/job")
    app.register_blueprint(admin_bp,  url_prefix="/admin")

    # ── Create all tables on first run ───────────────────
    with app.app_context():
        db.create_all()

    return app


# ── Development entry point ──────────────────────────────
app = create_app("development")

if __name__ == "__main__":
    app.run(debug=True, port=5000)

import os
from datetime import datetime

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    secret = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["SECRET_KEY"] = secret

    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url.startswith("postgres://"):
        # SQLAlchemy expects postgresql://
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if not database_url:
        # Local default
        instance = os.path.join(app.root_path, "..", "instance")
        os.makedirs(instance, exist_ok=True)
        database_url = "sqlite:///" + os.path.abspath(os.path.join(instance, "filaqora.db"))

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User  # noqa: F401
    from .routes import main_bp, api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow}

    with app.app_context():
        db.create_all()
        _ensure_seed_admin()

    return app


def _ensure_seed_admin():
    """Create a default admin if no users exist (first deploy)."""
    from .models import User
    from werkzeug.security import generate_password_hash

    if User.query.first() is not None:
        return

    email = os.environ.get("ADMIN_EMAIL", "admin@filaqora.com")
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    name = os.environ.get("ADMIN_NAME", "Admin")

    user = User(
        name=name,
        email=email.lower().strip(),
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    print(f"[FilaQora] Seeded admin user: {email} (change password after login)")

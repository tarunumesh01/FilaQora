import os
from datetime import datetime
from inspect import getmembers, isclass

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import inspect, text

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

    # -----------------------------------------------------------------------
    # Configuration
    # -----------------------------------------------------------------------

    secret = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-me",
    )

    app.config["SECRET_KEY"] = secret

    database_url = os.environ.get(
        "DATABASE_URL",
        "",
    ).strip()

    # Render/PostgreSQL may provide postgres://
    # SQLAlchemy expects postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1,
        )

    # Local development fallback
    if not database_url:
        instance = os.path.join(
            app.root_path,
            "..",
            "instance",
        )

        os.makedirs(
            instance,
            exist_ok=True,
        )

        database_url = (
            "sqlite:///"
            + os.path.abspath(
                os.path.join(
                    instance,
                    "filaqora.db",
                )
            )
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

    # -----------------------------------------------------------------------
    # Extensions
    # -----------------------------------------------------------------------

    db.init_app(app)
    login_manager.init_app(app)

    # Import models before create_all()
    from .models import User, Customer  # noqa: F401

    # Import routes
    from .routes import main_bp, api_bp

    app.register_blueprint(main_bp)

    app.register_blueprint(
        api_bp,
        url_prefix="/api",
    )

    # -----------------------------------------------------------------------
    # Template helpers
    # -----------------------------------------------------------------------

    @app.context_processor
    def inject_now():
        return {
            "now": datetime.utcnow,
        }

    # -----------------------------------------------------------------------
    # Database initialization
    # -----------------------------------------------------------------------

    with app.app_context():

        # Creates tables that do not exist yet.
        #
        # IMPORTANT:
        # db.create_all() does NOT modify existing tables.
        # Therefore _ensure_admin_column() is also required.
        db.create_all()

        # Add users.is_admin to an existing production database
        # if the column doesn't already exist.
        _ensure_admin_column()

        # Create/promote the configured administrator.
        _ensure_seed_admin()

    return app


# ===========================================================================
# ADMIN DATABASE MIGRATION
# ===========================================================================

def _ensure_admin_column():
    """
    Ensure the users table contains the is_admin column.

    This is needed because db.create_all() does not modify an existing
    database table when the SQLAlchemy model changes.
    """

    inspector = inspect(db.engine)

    # If the users table does not exist yet, create_all() should have
    # created it before this function is called.
    if not inspector.has_table("users"):
        return

    columns = inspector.get_columns("users")

    column_names = {
        column["name"]
        for column in columns
    }

    if "is_admin" in column_names:
        return

    print(
        "[FilaQora] Adding missing users.is_admin column..."
    )

    with db.engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN is_admin BOOLEAN
                NOT NULL
                DEFAULT FALSE
                """
            )
        )

    print(
        "[FilaQora] users.is_admin column added successfully."
    )


# ===========================================================================
# ADMIN ACCOUNT
# ===========================================================================

def _ensure_seed_admin():
    """
    Create or promote the configured FilaQora administrator.

    ADMIN_EMAIL, ADMIN_PASSWORD and ADMIN_NAME should be configured
    through Render environment variables in production.

    The password is only used when creating a new admin account.
    Existing admin passwords are NOT overwritten on every deployment.
    """

    from .models import User
    from werkzeug.security import generate_password_hash

    # -----------------------------------------------------------------------
    # Environment variables
    # -----------------------------------------------------------------------

    email = os.environ.get(
        "ADMIN_EMAIL",
        "admin@filaqora.com",
    ).strip().lower()

    password = os.environ.get(
        "ADMIN_PASSWORD",
    )

    name = os.environ.get(
        "ADMIN_NAME",
        "FilaQora Administrator",
    ).strip()

    # Never silently create an admin with a known default password.
    if not password:
        raise RuntimeError(
            "ADMIN_PASSWORD environment variable is required."
        )

    if not email:
        raise RuntimeError(
            "ADMIN_EMAIL environment variable is required."
        )

    # -----------------------------------------------------------------------
    # Find existing user
    # -----------------------------------------------------------------------

    user = User.query.filter_by(
        email=email,
    ).first()

    # -----------------------------------------------------------------------
    # Create admin if account doesn't exist
    # -----------------------------------------------------------------------

    if user is None:

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(
                password,
            ),
            is_admin=True,
        )

        db.session.add(user)
        db.session.commit()

        print(
            f"[FilaQora] Created admin account: {email}"
        )

        return

    # -----------------------------------------------------------------------
    # Existing account
    # -----------------------------------------------------------------------

    changed = False

    # Promote the configured account if necessary.
    if not user.is_admin:
        user.is_admin = True
        changed = True

    # Update the configured admin display name if needed.
    if name and user.name != name:
        user.name = name
        changed = True

    if changed:
        db.session.commit()

        print(
            f"[FilaQora] Admin access updated: {email}"
        )

    else:
        print(
            f"[FilaQora] Admin account already exists: {email}"
        )
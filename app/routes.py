import csv
import io
import secrets
from collections import Counter
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    abort,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from werkzeug.security import generate_password_hash

from . import db
from .models import Customer, User

main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _customer_query_for_user(user_id, q=None):
    query = Customer.query.filter_by(user_id=user_id)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Customer.name.ilike(like),
                Customer.email.ilike(like),
                Customer.company.ilike(like),
                Customer.tags.ilike(like),
            )
        )
    return query.order_by(Customer.created_at.desc())


def _dashboard_stats(user_id):
    customers = Customer.query.filter_by(user_id=user_id).all()

    # Month buckets (last 12 months labels)
    month_counter = Counter()
    for c in customers:
        if c.created_at:
            key = c.created_at.strftime("%Y-%m")
            month_counter[key] += 1

    # Build last 12 month labels
    now = datetime.utcnow()
    month_labels = []
    month_counts = []
    for i in range(11, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        label = f"{y}-{m:02d}"
        month_labels.append(label)
        month_counts.append(month_counter.get(label, 0))

    company_counter = Counter(
        (c.company or "—").strip() or "—" for c in customers if (c.company or "").strip()
    )
    top = company_counter.most_common(5)
    company_labels = [t[0] for t in top] or ["No data"]
    company_counts = [t[1] for t in top] or [0]

    tag_counter = Counter()
    for c in customers:
        if not c.tags:
            continue
        for tag in c.tags.split(","):
            tag = tag.strip()
            if tag:
                tag_counter[tag] += 1
    top_tags = tag_counter.most_common(6)
    tag_labels = [t[0] for t in top_tags] or ["No tags"]
    tag_counts = [t[1] for t in top_tags] or [0]

    return {
        "month_labels": month_labels,
        "month_counts": month_counts,
        "company_labels": company_labels,
        "company_counts": company_counts,
        "tag_labels": tag_labels,
        "tag_counts": tag_counts,
    }


def _sample_demo_data():
    """Static sample for public demo page."""
    sample_customers = [
        {"name": "Jane Doe", "email": "jane@acme.com", "phone": "555-0101", "company": "Acme Corp", "tags": "vip,enterprise", "created_at": "2025-11-02"},
        {"name": "Alex Smith", "email": "alex@northstar.io", "phone": "555-0102", "company": "Northstar Labs", "tags": "lead", "created_at": "2025-12-14"},
        {"name": "Priya Patel", "email": "priya@orbit.dev", "phone": "555-0103", "company": "Orbit Soft", "tags": "vip", "created_at": "2026-01-08"},
        {"name": "Marcus Chen", "email": "marcus@bluepeak.co", "phone": "555-0104", "company": "Bluepeak", "tags": "enterprise", "created_at": "2026-02-21"},
        {"name": "Sofia Rossi", "email": "sofia@lumen.tech", "phone": "555-0105", "company": "Lumen Tech", "tags": "lead,vip", "created_at": "2026-03-05"},
    ]
    stats = {
        "month_labels": ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"],
        "month_counts": [4, 7, 6, 9, 11, 10, 14, 12, 15, 18, 16, 20],
        "company_labels": ["Acme Corp", "Northstar Labs", "Orbit Soft", "Bluepeak", "Lumen Tech"],
        "company_counts": [28, 22, 18, 14, 11],
        "tag_labels": ["lead", "vip", "enterprise"],
        "tag_counts": [42, 31, 19],
    }
    return sample_customers, stats


def _require_api_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = None
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
        if not token:
            token = request.args.get("token")
        if not token:
            return jsonify({"error": "Missing Bearer token"}), 401
        user = User.query.filter_by(api_token=token).first()
        if not user:
            return jsonify({"error": "Invalid token"}), 401
        request.api_user = user
        return f(*args, **kwargs)

    return wrapped


def _ensure_api_token(user: User) -> str:
    if user.api_token:
        return user.api_token
    user.api_token = secrets.token_hex(24)
    db.session.commit()
    return user.api_token

def admin_required(f):
    @wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/demo")
def demo():
    sample_customers, stats = _sample_demo_data()
    return render_template("demo.html", sample_customers=sample_customers, **stats)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form_data = {}
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        remember = bool(request.form.get("remember"))
        form_data["email"] = email

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Welcome back.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form_data=form_data)


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# Authenticated app
# ---------------------------------------------------------------------------

@main_bp.route("/dashboard")
@login_required
def dashboard():
    stats = _dashboard_stats(current_user.id)
    return render_template("dashboard.html", **stats)


@main_bp.route("/customers")
@login_required
def customers():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 15
    pagination = _customer_query_for_user(current_user.id, q).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("customers.html", pagination=pagination, q=q)


@main_bp.route("/customers/new", methods=["GET", "POST"])
@login_required
def customer_new():
    form_data = {}
    if request.method == "POST":
        form_data = {k: (request.form.get(k) or "").strip() for k in ("name", "email", "phone", "company", "tags")}
        if not form_data["name"] or not form_data["email"]:
            flash("Name and email are required.", "danger")
            return render_template("customer_form.html", title="Add Customer", form_data=form_data)

        c = Customer(
            user_id=current_user.id,
            name=form_data["name"],
            email=form_data["email"],
            phone=form_data["phone"] or None,
            company=form_data["company"] or None,
            tags=form_data["tags"] or None,
        )
        db.session.add(c)
        db.session.commit()
        flash("Customer created.", "success")
        return redirect(url_for("main.customers"))

    return render_template("customer_form.html", title="Add Customer", form_data=form_data)


@main_bp.route("/customers/<int:id>", methods=["GET", "POST"])
@login_required
def customer_detail(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form_data = {
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone or "",
        "company": customer.company or "",
        "tags": customer.tags or "",
    }

    if request.method == "POST":
        form_data = {k: (request.form.get(k) or "").strip() for k in ("name", "email", "phone", "company", "tags")}
        if not form_data["name"] or not form_data["email"]:
            flash("Name and email are required.", "danger")
            return render_template("customer_detail.html", customer=customer, form_data=form_data)

        customer.name = form_data["name"]
        customer.email = form_data["email"]
        customer.phone = form_data["phone"] or None
        customer.company = form_data["company"] or None
        customer.tags = form_data["tags"] or None
        db.session.commit()
        flash("Customer updated.", "success")
        return redirect(url_for("main.customer_detail", id=customer.id))

    return render_template("customer_detail.html", customer=customer, form_data=form_data)


@main_bp.route("/customers/<int:id>/delete", methods=["POST"])
@login_required
def customer_delete(id):
    customer = Customer.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted.", "info")
    return redirect(url_for("main.customers"))


@main_bp.route("/export")
@login_required
def export():
    # Dedicated export page OR direct download via format=
    fmt = (request.args.get("format") or "").lower()
    q = request.args.get("q", "").strip()

    if not fmt:
        return render_template("export.html")

    rows = _customer_query_for_user(current_user.id, q).all()

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "name", "email", "phone", "company", "tags", "created_at"])
        for c in rows:
            writer.writerow([
                c.id, c.name, c.email, c.phone or "", c.company or "", c.tags or "",
                c.created_at.isoformat() if c.created_at else "",
            ])
        return Response(
            buf.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=filaqora-customers.csv"},
        )

    if fmt in ("xlsx", "excel"):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Customers"
        ws.append(["id", "name", "email", "phone", "company", "tags", "created_at"])
        for c in rows:
            ws.append([
                c.id, c.name, c.email, c.phone or "", c.company or "", c.tags or "",
                c.created_at.isoformat() if c.created_at else "",
            ])
        out = io.BytesIO()
        wb.save(out)
        out.seek(0)
        return Response(
            out.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=filaqora-customers.xlsx"},
        )

    flash("Unknown export format.", "warning")
    return redirect(url_for("main.customers"))


@main_bp.route("/api-docs")
@login_required
def api_docs():
    return render_template("api_docs.html")


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form_data = {"name": current_user.name or "", "email": current_user.email}
    api_token = _ensure_api_token(current_user)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""
        form_data = {"name": name, "email": email}

        if not email:
            flash("Email is required.", "danger")
            return render_template("profile.html", form_data=form_data, api_token=api_token)

        existing = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing:
            flash("That email is already in use.", "danger")
            return render_template("profile.html", form_data=form_data, api_token=api_token)

        if password or password_confirm:
            if password != password_confirm:
                flash("Passwords do not match.", "danger")
                return render_template("profile.html", form_data=form_data, api_token=api_token)
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("profile.html", form_data=form_data, api_token=api_token)
            current_user.password_hash = generate_password_hash(password)

        current_user.name = name or None
        current_user.email = email
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("main.profile"))

    return render_template("profile.html", form_data=form_data, api_token=api_token)


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@api_bp.route("/customers", methods=["GET"])
@_require_api_token
def api_list_customers():
    user = request.api_user
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    pagination = _customer_query_for_user(user.id, q).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [c.to_dict() for c in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
    })


@api_bp.route("/customers/<int:id>", methods=["GET"])
@_require_api_token
def api_get_customer(id):
    c = Customer.query.filter_by(id=id, user_id=request.api_user.id).first()
    if not c:
        return jsonify({"error": "Not found"}), 404
    return jsonify(c.to_dict())


@api_bp.route("/customers", methods=["POST"])
@_require_api_token
def api_create_customer():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400
    c = Customer(
        user_id=request.api_user.id,
        name=name,
        email=email,
        phone=(data.get("phone") or "").strip() or None,
        company=(data.get("company") or "").strip() or None,
        tags=(data.get("tags") or "").strip() or None,
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@api_bp.route("/customers/<int:id>", methods=["PUT", "PATCH"])
@_require_api_token
def api_update_customer(id):
    c = Customer.query.filter_by(id=id, user_id=request.api_user.id).first()
    if not c:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    for field in ("name", "email", "phone", "company", "tags"):
        if field in data:
            val = (data.get(field) or "").strip()
            setattr(c, field, val or None if field != "name" and field != "email" else val)
    if not c.name or not c.email:
        return jsonify({"error": "name and email are required"}), 400
    db.session.commit()
    return jsonify(c.to_dict())


@api_bp.route("/customers/<int:id>", methods=["DELETE"])
@_require_api_token
def api_delete_customer(id):
    c = Customer.query.filter_by(id=id, user_id=request.api_user.id).first()
    if not c:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"ok": True}), 200

# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@main_bp.route("/admin")
@admin_required
def admin_dashboard():
    users = User.query.order_by(User.created_at.desc()).all()

    user_data = []

    for user in users:
        user_data.append({
            "id": user.id,
            "name": user.name or "—",
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "customer_count": Customer.query.filter_by(
                user_id=user.id
            ).count(),
        })

    return render_template(
        "admin.html",
        users=user_data,
    )

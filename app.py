import os
import sqlite3
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort
)
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf import CSRFProtect
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from flask_wtf.csrf import CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "aura.db")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

# ----------------- Admin API -----------------
@app.get("/api/admin/data")
@login_required
def api_admin_data():
    if not current_user.is_authenticated or str(current_user.get_id()) != "admin":
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    data = {}
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM enquiries ORDER BY created_at DESC")
        data["enquiries"] = [dict(x) for x in cur.fetchall()]
        cur.execute("SELECT * FROM bookings ORDER BY created_at DESC")
        data["bookings"] = [dict(x) for x in cur.fetchall()]
    return jsonify({"ok": True, "data": data})

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ----------------- User classes -----------------
class User(UserMixin):
    def __init__(self, id, email_phone):
        self.id = str(id)
        self.email_phone = email_phone


class Admin(UserMixin):
    def __init__(self, id="admin"):
        self.id = str(id)


# ----------------- User loader -----------------
@login_manager.user_loader
def load_user(user_id):
    # Admin special-case
    if str(user_id) == "admin":
        return Admin(id="admin")

    # Normal user: load from DB
    try:
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT id, email_phone FROM users WHERE id=?", (user_id,))
            row = cur.fetchone()
            if row:
                return User(id=row["id"], email_phone=row["email_phone"])
    except Exception:
        pass
    return None


# ----------------- Context processor -----------------
@app.context_processor
def inject_now():
    return {"year": datetime.now().year}


# ----------------- Public pages -----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/services")
def services():
    return render_template("services.html", title="Services — Aura Fest Events")


@app.route("/gallery")
def gallery():
    images = []
    img_dir = os.path.join(app.static_folder, "images")
    if os.path.isdir(img_dir):
        for name in sorted(os.listdir(img_dir)):
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")):
                images.append(f"/static/images/{name}")
    return render_template("gallery.html", title="Gallery — Aura Fest Events", images=images)


@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact — Aura Fest Events")


# ----------------- API endpoints -----------------
@app.post("/api/enquiry")
def api_enquiry():
    data = request.form if request.form else request.json
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    message = (data.get("message") or "").strip()
    if not name or not phone:
        return jsonify({"ok": False, "error": "Name and phone are required"}), 400
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO enquiries(name, email, phone, message, created_at)
            VALUES(?,?,?,?,?);
        """, (name, email, phone, message, datetime.utcnow().isoformat()))
        con.commit()
    return jsonify({"ok": True})


@app.post("/api/book")
def api_book():
    data = request.form if request.form else request.json
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    event_type = (data.get("event_type") or "").strip()
    date = (data.get("date") or "").strip()
    location = (data.get("location") or "").strip()
    budget = (data.get("budget") or "").strip()
    notes = (data.get("notes") or "").strip()
    if not (name and phone and event_type and date and location):
        return jsonify({"ok": False, "error": "Missing required fields"}), 400
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO bookings(name, email, phone, event_type, date, location, budget, notes, created_at)
            VALUES(?,?,?,?,?,?,?,?,?);
        """, (name, email, phone, event_type, date, location, budget, notes, datetime.utcnow().isoformat()))
        con.commit()
    return jsonify({"ok": True})


@app.get("/booking-success")
def booking_success():
    return render_template("booking_success.html", title="Booking Received — Aura Fest Events")


# ----------------- Event pages -----------------
@app.route("/wedding")
def wedding():
    return render_template("wedding.html", title="Wedding Decorations")


@app.route("/birthday")
def birthday():
    return render_template("birthday.html", title="Birthday Decorations")


@app.route("/babyshower")
def babyshower():
    return render_template("babyshower.html", title="Baby Shower Decorations")


@app.route("/corprate")
def corprate():
    return render_template("corprate.html", title="Corporate Events")


# ----------------- Signup / Login / Logout -----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        email_phone = email if email else phone
        hashed_pw = generate_password_hash(password)
        error = None
        try:
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO users (email_phone, password) VALUES (?, ?)",
                    (email_phone, hashed_pw)
                )
                con.commit()
        except sqlite3.IntegrityError:
            error = "Email or phone already registered."
        except Exception:
            error = "Signup failed. Please try again."
        # Always return JSON for AJAX requests, no redirect
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            if error:
                return jsonify({"ok": False, "error": error}), 400
            return jsonify({"ok": True, "name": name}), 200
        # Fallback for normal form POST (redirect)
        if error:
            return render_template("signup.html", error=error)
        return redirect(url_for("login"))
    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email_phone = request.form.get("email")
        password = request.form.get("password")
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute("SELECT id, password FROM users WHERE email_phone = ?", (email_phone,))
            user = cur.fetchone()
            if user and check_password_hash(user[1], password):
                login_user(User(id=user[0], email_phone=email_phone))
                return render_template("login_success.html", name=email_phone)
            else:
                error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)


@app.route("/dashboard")
@login_required
def user_dashboard():
    # Only normal users should hit this; admin will be redirected below.
    if getattr(current_user, "id", None) == "admin":
        # Prevent admin from viewing user dashboard; redirect to admin dashboard
        return redirect(url_for("admin_dashboard"))

    # Search bookings by email or phone
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # current_user.email_phone might be an email or phone string
        cur.execute("SELECT * FROM bookings WHERE email=? OR phone=? ORDER BY date DESC",
                    (current_user.email_phone, current_user.email_phone))
        bookings = [dict(x) for x in cur.fetchall()]

    return render_template("dashboard.html", title="My Bookings — Aura Fest Events", bookings=bookings)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ----------------- Admin -----------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        token = request.form.get("token")
        if token and token == os.getenv("ADMIN_TOKEN"):
            user = Admin(id="admin")
            login_user(user, remember=True)
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid token"
    return render_template("admin_login.html", error=error)


def _require_admin():
    if not current_user.is_authenticated or str(current_user.get_id()) != "admin":
        abort(403)


@app.route("/admin")
@login_required
def admin_dashboard():
    _require_admin()
    data = {}
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM enquiries ORDER BY created_at DESC")
        data["enquiries"] = [dict(x) for x in cur.fetchall()]
        cur.execute("SELECT * FROM bookings ORDER BY created_at DESC")
        data["bookings"] = [dict(x) for x in cur.fetchall()]
    return render_template("admin.html", title="Admin — Aura Fest Events", data=data)


@app.route("/admin/bookings")
@login_required
def admin_bookings():
    _require_admin()
    bookings = []
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT name, email, phone, event_type, date, location, budget, notes, created_at
            FROM bookings
            ORDER BY date DESC
        """)
        bookings = [dict(x) for x in cur.fetchall()]
    return render_template("admin_bookings.html", bookings=bookings)


# ----------------- Error handlers -----------------
@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", title="Forbidden", code=403, message="Forbidden"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", title="Not found", code=404, message="Page not found"), 404


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("CSRF token missing or incorrect.", "danger")
    return redirect(request.referrer or url_for("index"))


# ----------------- DB init -----------------
def init_db():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_phone TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT NOT NULL,
                event_type TEXT NOT NULL,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                budget TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT NOT NULL,
                message TEXT,
                created_at TEXT NOT NULL
            );
        """)
        con.commit()


# ----------------- Run -----------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)

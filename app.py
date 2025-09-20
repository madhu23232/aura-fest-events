import os
import sqlite3
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify
)
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf import CSRFProtect
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user
)
from flask_wtf.csrf import CSRFError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "aura.db")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"

class Admin(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return Admin(id="admin")
    return None

@app.context_processor
def inject_now():
    return {"year": datetime.now().year}

# ----------------------------
# Public Routes
# ----------------------------

@app.route("/")
def index():
    return render_template("index.html", title="Aura Fest Events | Premium Event Decoration")

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
    return redirect(url_for("booking_success"))

@app.get("/booking-success")
def booking_success():
    return render_template("booking_success.html", title="Booking Received — Aura Fest Events")

# ----------------------------
# Admin Routes
# ----------------------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        token = request.form.get("token", "")
        correct_token = os.getenv("ADMIN_TOKEN", "letmein123")
        if token == correct_token:
            user = Admin(id="admin")
            login_user(user)
            flash("Welcome back, Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin token!", "danger")
    return render_template("admin_login.html", title="Admin Login")

@app.route("/admin")
@login_required
def admin_dashboard():
    data = {}
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM enquiries ORDER BY created_at DESC")
        data["enquiries"] = [dict(x) for x in cur.fetchall()]
        cur.execute("SELECT * FROM bookings ORDER BY created_at DESC")
        data["bookings"] = [dict(x) for x in cur.fetchall()]
    return render_template("admin.html", title="Admin — Aura Fest Events", data=data)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin_login"))

# ----------------------------
# Error Handlers
# ----------------------------

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

# ----------------------------
# DB Initialization
# ----------------------------

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS enquiries(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT NOT NULL,
                message TEXT,
                created_at TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookings(
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
        con.commit()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)

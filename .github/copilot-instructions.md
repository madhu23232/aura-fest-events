# Copilot Instructions for aura_fest_events

## Project Overview
This is a Flask web app for managing and displaying event services (weddings, birthdays, baby showers, corporate events, etc.). Data is stored locally in SQLite (`aura.db`). The app serves static assets and Jinja2 HTML templates for each event type.

## Architecture & Key Components
- `app.py`: Main Flask entry point. Handles all routing, database access, and template rendering.
- `aura.db`: SQLite database for events, bookings, and user/admin data. No migration scripts; schema changes must be manual.
- `templates/`: Jinja2 HTML templates for all pages. Common layout in `base.html`. Event pages (e.g., `wedding.html`, `birthday.html`) follow a similar structure for easy extension.
- `static/`: Static assets organized by type:
  - `css/`: Stylesheets (e.g., `style.css`, `pages.css`, `login.css`)
  - `js/`: JavaScript files (e.g., `main.js`)
  - `images/`: Images for events and branding

## Developer Workflows
- **Run the app:**
  ```powershell
  python app.py
  ```
  App runs locally (default port 5000).
- **Install dependencies:**
  ```powershell
  pip install -r requirements.txt
  ```
- **Debugging:**
  Set `debug=True` in `app.run()` for Flask debug mode.
- **Database:**
  Edit `aura.db` directly for schema changes. No migrations or ORM detected.

## Project-Specific Patterns
- **Templates:**
  - All pages inherit from `base.html`.
  - Event pages use a consistent structure for easy duplication.
- **Static Files:**
  - Reference assets using `url_for('static', filename='...')` in templates.
- **Authentication:**
  - Admin login via `admin_login.html` and related routes in `app.py`.
- **Error Handling:**
  - Errors route to `error.html`.
- **Success Pages:**
  - Bookings route to `booking_success.html`.

## Integration Points
- No external APIs or background jobs. All data and logic are local.

## Conventions & Examples
- Route names and template filenames match event types (e.g., `/wedding` → `wedding.html`).
- To add a new event type:
  1. Create a template in `templates/` (e.g., `anniversary.html`).
  2. Add a route in `app.py` to render it.
  3. Add static assets if needed.

## Key Files for Reference
- `app.py`: For routing, logic, and database access patterns
- `base.html`: For template inheritance and layout
- `requirements.txt`: For dependencies

---

For unclear patterns, review `app.py` and `base.html`. If any section is unclear or missing, please provide feedback for further updates.

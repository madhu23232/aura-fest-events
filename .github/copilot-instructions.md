# Copilot Instructions for aura_fest_events

## Project Overview
This is a Flask-based web application for managing and displaying event services (weddings, birthdays, baby showers, corporate events, etc.). The app uses SQLite (`aura.db`) for data storage and serves static assets and HTML templates for various event types.

## Architecture & Key Components
- `app.py`: Main Flask application. Handles routing, database interactions, and template rendering.
- `aura.db`: SQLite database file. Used for storing event, booking, and user/admin data.
- `templates/`: Contains Jinja2 HTML templates for all pages (e.g., `index.html`, `admin.html`, `booking_success.html`).
- `static/`: Static assets (CSS, JS, images). Organized by type.

## Developer Workflows
- **Run the app:**
  ```powershell
  python app.py
  ```
  The app runs locally, typically on port 5000.
- **Database:**
  - Schema is managed directly in `aura.db`. No migration scripts detected; update schema manually if needed.
- **Debugging:**
  - Use Flask's built-in debug mode by setting `debug=True` in `app.run()`.
- **Requirements:**
  - Install dependencies with:
    ```powershell
    pip install -r requirements.txt
    ```

## Project-Specific Patterns
- **Templates:**
  - All pages use Jinja2 templating. Common layout in `base.html`.
  - Event pages (e.g., `wedding.html`, `birthday.html`) follow similar structure for easy extension.
- **Static Files:**
  - CSS, JS, and images are separated in `static/` subfolders. Reference them using Flask's `url_for('static', filename='...')`.
- **Authentication:**
  - Admin login handled via `admin_login.html` and corresponding routes in `app.py`.

## Integration Points
- No external APIs detected; all data is local.
- No background jobs or async processing.

## Conventions
- Route names and template filenames match event types for clarity.
- Error handling uses a dedicated `error.html` template.
- Booking success is routed to `booking_success.html`.

## Examples
- To add a new event type:
  1. Create a new template in `templates/` (e.g., `anniversary.html`).
  2. Add a route in `app.py` to render the new template.
  3. Add relevant static assets if needed.

---

For questions or unclear patterns, review `app.py` for routing and logic, and `base.html` for template inheritance.

*Please provide feedback if any section is unclear or missing details specific to your workflow.*

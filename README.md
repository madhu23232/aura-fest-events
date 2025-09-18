# Aura Fest Events — Full-Stack Website

A clean, modern event-decoration website inspired by leading brands. Built with **Flask (Python)** + **HTML/CSS/JS**.

## Features
- Home, Services, Gallery, Contact pages
- Booking form → stored in SQLite
- Enquiry form (AJAX) → stored in SQLite
- Simple Admin page (`/admin?token=...`)
- Responsive, modern UI

## Local Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edit SECRET_KEY and ADMIN_TOKEN if you want
python app.py
# open http://localhost:5000
```

## Deploy (one simple option)
- Create a repo on GitHub
- Push this folder
- Deploy to **Render**, **Railway**, **Fly.io**, **Vercel (via Python)**, or **Heroku** with a single click
- Set environment variables: `SECRET_KEY`, `ADMIN_TOKEN`
- Make sure the instance has write access for SQLite or switch to a cloud DB.

## Adding Gallery Images
Place photos into `static/images/` and they will auto-appear on the Gallery page.

---

Made for: **Aura Fest Events** 🎉

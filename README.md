# Company Site (Flask) — Render Ready

A minimal, production-ready scaffold for a company homepage using Flask + Gunicorn.
Includes a `render.yaml` for one-click deploy on Render.

## Local Dev
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="dev-secret"   # Windows PowerShell: $env:SECRET_KEY="dev-secret"
python app.py
# visit http://127.0.0.1:5000
```

## Deploy to Render (Web Service)
- Runtime/Language: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn wsgi:app`
- Plan: Free (preview) or Starter (production)
- Optional env: `PYTHON_VERSION=3.12.11`, `SECRET_KEY`

Or use **Blueprints**:
1) Push this repo to GitHub.
2) In Render, click **New → Blueprint** and select this repo.
3) Render provisions infra per `render.yaml`.

## Project Structure
- `app.py` — Flask factory + local dev server
- `wsgi.py` — Gunicorn entrypoint (`wsgi:app`)
- `templates/` — Jinja2 templates
- `static/` — CSS/JS/Images
- `render.yaml` — Render blueprint
- `requirements.txt` — Python deps
- `.python-version` — Suggested Python version
- `.gitignore` — Ignore venv/artefacts

## Git Quick Start
```bash
git init
git add .
git commit -m "Initial commit: Flask company site (Render ready)"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
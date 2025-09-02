# Company Site — Multilingual (zh‑CN / en / zh‑TW)

## Run locally
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="dev-secret"
python app.py
# open http://127.0.0.1:5000
```

## Deploy to Render
- Build: `pip install -r requirements.txt`
- Start: `gunicorn wsgi:app`
```
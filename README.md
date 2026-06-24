# Company Site — Multilingual (zh‑CN / en / zh‑TW)

## Run locally
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="dev-secret"
python app.py
# open http://127.0.0.1:5000

# HTTPS local development
export USE_HTTPS=1
python app.py
# open https://127.0.0.1:5000

# Or use custom certs:
# export SSL_CERT_FILE="/path/to/cert.pem"
# export SSL_KEY_FILE="/path/to/key.pem"
# python app.py
```

## Deploy to Render
- Build: `pip install -r requirements.txt`
- Start: `gunicorn wsgi:app`
```
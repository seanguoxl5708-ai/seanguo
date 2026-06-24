#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/start_private_preview.sh [REMOTE_PORT]
# Defaults to REMOTE_PORT=5000. Uses $CODESPACE_NAME from environment.

REMOTE_PORT=${1:-5000}
CODESPACE=${CODESPACE_NAME:-}
if [ -z "$CODESPACE" ]; then
  echo "CODESPACE_NAME is not set. Run this inside a Codespace or set CODESPACE_NAME."
  exit 1
fi

echo "Finding free local port between 5000 and 5010..."
for p in $(seq 5000 5010); do
  if ss -ltn | grep -q ":$p "; then
    continue
  fi

  FREE_PORT=$p
  export SECRET_KEY=${SECRET_KEY:-dev-secret}
  export PORT=$FREE_PORT
  unset USE_HTTPS

  LOGFILE="/tmp/seanguo_app_${FREE_PORT}.log"
  echo "Attempting to start app on local port $FREE_PORT (logs: $LOGFILE)"
  nohup python3 app.py > "$LOGFILE" 2>&1 &
  APP_PID=$!
  sleep 1

  if ! ss -ltn | grep -q ":$FREE_PORT "; then
    echo "App did not bind to $FREE_PORT, killing PID $APP_PID and trying next port."
    kill "$APP_PID" 2>/dev/null || true
    sleep 0.5
    continue
  fi

  echo "App bound to $FREE_PORT, attempting to forward remote $REMOTE_PORT -> local $FREE_PORT"
  if gh codespace ports forward --codespace "$CODESPACE" $REMOTE_PORT:$FREE_PORT 2>/tmp/gh_forward_err; then
    gh codespace ports visibility --codespace "$CODESPACE" $REMOTE_PORT:private || true
    BROWSE_URL=$(gh codespace ports --codespace "$CODESPACE" --json browseUrl,sourcePort,visibility | python3 - <<PY
import json,sys
try:
    data=json.load(sys.stdin)
except Exception:
    print("")
    sys.exit(0)
for p in data:
    if p.get('sourcePort')==int($REMOTE_PORT):
        print(p.get('browseUrl') or "")
        sys.exit(0)
print("")
PY
)
    if [ -n "$BROWSE_URL" ]; then
      echo "Private preview available at: $BROWSE_URL"
    else
      echo "Forwarding succeeded but browse URL not found. Use 'gh codespace ports' to inspect."
    fi

    echo "App PID: $APP_PID (logs: $LOGFILE)"
    echo "Keep this terminal open to keep the app and forwarding alive."
    trap 'echo "Stopping app $APP_PID"; kill "$APP_PID" 2>/dev/null || true' EXIT
    wait "$APP_PID"
    exit 0
  else
    echo "Forward failed for local $FREE_PORT (see /tmp/gh_forward_err). Killing app and trying next port."
    kill "$APP_PID" 2>/dev/null || true
    sleep 0.5
    continue
  fi
done

echo "Tried ports 5000-5010 but could not establish forwarding. Check 'gh codespace ports' and app logs." >&2
exit 1

#!/usr/bin/env bash
# Start Warm Bridge API (:8788) + Vite UI (:5174) together.
# Always use .venv-wb (not .venv — that tree is often read-only / missing Selenium).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

log() { echo "→ $*" >&2; }
die() { echo "✗ $*" >&2; exit 1; }

port_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn "sport = :$port" 2>/dev/null | grep -q ":$port"
  elif command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
  else
    # Fallback: try connect
    (echo >/dev/tcp/127.0.0.1/"$port") >/dev/null 2>&1
  fi
}

if [[ ! -x "$ROOT/.venv-wb/bin/python" ]]; then
  log "creating .venv-wb"
  python3 -m venv "$ROOT/.venv-wb"
fi
PY="$ROOT/.venv-wb/bin/python"

if [[ -n "${VIRTUAL_ENV:-}" ]] && [[ "$VIRTUAL_ENV" != "$ROOT/.venv-wb" ]]; then
  log "warning: active venv is $VIRTUAL_ENV — this script uses .venv-wb instead"
fi

log "ensuring package + LinkedIn extras"
"$PY" -m pip install -q -U pip
"$PY" -m pip install -q -e ".[linkedin]"

if [[ ! -d "$ROOT/web/node_modules" ]]; then
  log "npm install (web)"
  (cd "$ROOT/web" && npm install)
fi

if port_in_use 8788; then
  die "port 8788 already in use. Stop the other API (or: fuser -k 8788/tcp) then retry."
fi
if port_in_use 5174; then
  die "port 5174 already in use. Stop the other Vite (or: fuser -k 5174/tcp) then retry."
fi

API_PID=""
WEB_PID=""

cleanup() {
  echo "" >&2
  log "stopping…"
  [[ -n "${WEB_PID}" ]] && kill "$WEB_PID" 2>/dev/null || true
  [[ -n "${API_PID}" ]] && kill "$API_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

log "API  http://127.0.0.1:8788"
"$PY" -m warm_bridge.api &
API_PID=$!

healthy=0
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
  if curl -sf http://127.0.0.1:8788/api/health >/dev/null 2>&1; then
    healthy=1
    break
  fi
  # Bail early if API process died
  if ! kill -0 "$API_PID" 2>/dev/null; then
    die "API process exited before becoming healthy"
  fi
  sleep 0.4
done

if [[ "$healthy" -ne 1 ]]; then
  die "API did not become healthy on :8788 (curl /api/health failed)"
fi
echo "✓ API healthy  http://127.0.0.1:8788/api/health" >&2

log "UI   http://localhost:5174"
(cd "$ROOT/web" && npm run dev) &
WEB_PID=$!

echo "" >&2
echo "Warm Bridge running. Ctrl+C stops both." >&2
echo "  Demo:  Ver uma demo!          (offline — no Chrome)" >&2
echo "  Live:  Mapear via LinkedIn    (Chrome session + .venv-wb)" >&2
echo "  Never: source .venv for LinkedIn (use .venv-wb or npm run dev)" >&2
echo "" >&2

wait -n "$API_PID" "$WEB_PID" 2>/dev/null || wait

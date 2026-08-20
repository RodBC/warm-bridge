#!/usr/bin/env bash
# One-shot: writable venv + pip + npm for Warm Bridge.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv-wb/bin/python ]]; then
  echo "→ python3 -m venv .venv-wb"
  python3 -m venv .venv-wb
fi

echo "→ pip install -e \".[linkedin]\""
.venv-wb/bin/python -m pip install -U pip
.venv-wb/bin/python -m pip install -e ".[linkedin]"

echo "→ npm install (web)"
(cd web && npm install)

echo ""
echo "OK. Start with:  npm run dev   or   ./scripts/dev.sh"
echo "  UI  http://localhost:5174"
echo "  API http://127.0.0.1:8788"

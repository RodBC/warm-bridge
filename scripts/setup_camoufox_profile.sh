#!/usr/bin/env bash
# Create a dedicated Camoufox profile for Warm Bridge LinkedIn session.
# Does NOT store passwords. Seller logs into LinkedIn manually once (headed).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROFILE_DIR="${ROOT}/data/camoufox_profile"
SESSION_YAML="${ROOT}/data/linkedin_session.yaml"
EXAMPLE_YAML="${ROOT}/data/linkedin_session.yaml.example"

mkdir -p "${PROFILE_DIR}"

if [[ ! -f "${SESSION_YAML}" ]]; then
  if [[ -f "${EXAMPLE_YAML}" ]]; then
    sed "s|__PROFILE_DIR__|${PROFILE_DIR}|g" "${EXAMPLE_YAML}" > "${SESSION_YAML}"
    echo "Wrote ${SESSION_YAML}"
  else
    cat > "${SESSION_YAML}" <<EOF
# Gitignored — do not commit. Camoufox persistent profile for LinkedIn session.
profile_dir: ${PROFILE_DIR}
backend: camoufox
headless: false
enrich: true
enrich_cap: 16
max_mutuals: 40
EOF
    echo "Wrote ${SESSION_YAML}"
  fi
else
  echo "Keep existing ${SESSION_YAML}"
fi

echo
echo "=== Warm Bridge · Camoufox profile ==="
echo "Profile dir: ${PROFILE_DIR}"
echo
echo "Next steps:"
echo "  1. Install optional deps (once):"
echo "       pip install -e \".[linkedin]\""
echo "       python -m camoufox fetch"
echo "  2. Open Camoufox headed and log into LinkedIn (seller account):"
echo "       warm-bridge session-login"
echo "     Or complete login/2FA manually when Mapear opens the browser."
echo "  3. Check readiness:"
echo "       curl -s http://127.0.0.1:8788/api/linkedin-session/status | python -m json.tool"
echo
echo "Ops-only burner bootstrap (Layer 5):"
echo "  data/secrets/linkedin_burner.yaml + warm-bridge burner-login"
echo
echo "Docs: docs/LINKEDIN_SESSION.md"
echo "UI: Briefing → Avançado → Sessão LinkedIn"

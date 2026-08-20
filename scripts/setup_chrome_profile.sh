#!/usr/bin/env bash
# Create a dedicated Chrome profile for Warm Bridge LinkedIn session.
# Does NOT store passwords. You log into LinkedIn manually once.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROFILE_DIR="${ROOT}/data/chrome_profile"
SESSION_YAML="${ROOT}/data/linkedin_session.yaml"
EXAMPLE_YAML="${ROOT}/data/linkedin_session.yaml.example"

mkdir -p "${PROFILE_DIR}"

if [[ ! -f "${SESSION_YAML}" ]]; then
  if [[ -f "${EXAMPLE_YAML}" ]]; then
    sed "s|__USER_DATA_DIR__|${PROFILE_DIR}|g" "${EXAMPLE_YAML}" > "${SESSION_YAML}"
    echo "Wrote ${SESSION_YAML}"
  else
    cat > "${SESSION_YAML}" <<EOF
# Gitignored — do not commit. Local Chrome profile for LinkedIn Selenium.
user_data_dir: ${PROFILE_DIR}
profile_directory: Default
chrome_binary: ""
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
echo "=== Warm Bridge · Chrome profile ==="
echo "Profile dir: ${PROFILE_DIR}"
echo
echo "Next steps:"
echo "  1. Install Linux Chrome in WSL (once, sudo):"
echo "       sudo apt-get update && sudo apt-get install -y google-chrome-stable"
echo "  2. Open Chrome with this profile and log into LinkedIn:"
echo "       google-chrome-stable --user-data-dir=\"${PROFILE_DIR}\" https://www.linkedin.com/"
echo "  3. Close Chrome completely (profile lock)."
echo "  4. Check readiness:"
echo "       curl -s http://127.0.0.1:8788/api/linkedin-session/status | python -m json.tool"
echo "  5. Live pin QA:"
echo "       .venv-wb/bin/python scripts/validate_board_pins.py --live"
echo
echo "Docs: docs/LINKEDIN_SELENIUM.md"
echo "UI: Briefing → painel Sessão LinkedIn"

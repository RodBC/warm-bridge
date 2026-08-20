# LinkedIn Selenium session intake (deprecated)

> **Deprecated:** use [`docs/LINKEDIN_SESSION.md`](LINKEDIN_SESSION.md) — Camoufox is the default backend (`backend: camoufox`).  
> Selenium + Chrome remains available with `backend: selenium` in `data/linkedin_session.yaml`.

Legacy setup: `bash scripts/setup_chrome_profile.sh` + Linux `google-chrome-stable`.

All contracts (`/api/linkedin-map`, `/api/linkedin-session/status`, mock eval) are unchanged — implementation lives in `warm_bridge.linkedin_session`.

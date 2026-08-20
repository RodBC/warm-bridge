---
name: warm-bridge-sources
description: >-
  Network intake policy for Warm Bridge. Use when adding import adapters,
  LinkedIn/phone/vCard parsers, public research, or enrichment. Triggers: import,
  Connections.csv, phone CSV, scrape, LinkedIn, sources.yaml, vCard, research.
---

# Warm Bridge — sources skill

## Policy

Read `docs/sources.yaml`, `docs/RESEARCH.md`, and `docs/LINKEDIN_SESSION.md`.

| Tier | Meaning | Action |
|------|---------|--------|
| green | User-owned or official public | Build freely |
| yellow | Assisted / cautious | Seller’s own session; rate-limit; no invent |
| red | Mass send / fabricate edges | Do not ship |

**Primary intake (owner lock 2026-08-20):** LinkedIn Camoufox session — `linkedin_session.map_target` + auto login from `data/secrets/linkedin_account.yaml` (Career Fit burner state machine + Gmail App Password IMAP OTP).

**Legacy fallback:** Connections.csv / phone / paste via `imports` — still green tier, demoted in UI (“Legado”).

## Preferred architecture

```python
# Primary graph
linkedin_session.map_target(url) → network → build_find_result

# Auto session (ops / serve boot)
account.ensure_session_logged_in → burner.bootstrap (headless)

# Insight (parallel)
research.research_target(target) → insight_pack → board + ask hook

# Wedge API
POST /api/linkedin-map   # primary
POST /api/investigate    # legacy CSV + research
```

Modules: `warm_bridge.linkedin_session` (primary), `warm_bridge.research`, `warm_bridge.imports` (legacy).

### Login / OTP conventions

- Secrets: `data/secrets/linkedin_account.yaml` only — never API/UI password fields  
- Need **Gmail App Password** (16 chars), not Gmail login password  
- Challenge classifier lives in `burner/bootstrap.detect_challenge_from_text` (PT/EN)  
- SMS 2FA = out of scope (honest error; switch LinkedIn to email or authenticator)  
- Cookie persist: `driver.camoufox.launch_persistent` + feed nudge before context close  

Never invent mutuals or people from search. Empty graph or empty search → honest empty UI.

## Messaging

Drafts from `approach.py`. User sends on WhatsApp/LinkedIn. Never automate blast from API.

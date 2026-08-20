# CURRENT context — Warm Bridge

> **AIs: read this fully before coding. Update this file before you end a session with meaningful changes.**

**Last updated:** 2026-08-20  
**Repo:** `/home/decastro/studies/warm-bridge`  
**UI:** MUI + Lead Police board · RWD navy/blue · http://127.0.0.1:5174

## Goal

Profitable SaaS: **LinkedIn session scrape** + **public web insight** → ranked bridges + asks — minimal friction (Career Fit pattern).

Loop:

`target LinkedIn URL → auto Camoufox session → scrape mutuals → enrich + research → find bridges → ask → you send`

## What exists now

- Playbook + deterministic find/explain/tutor/approach  
- **Primary intake:** `linkedin_session` (Camoufox mutuals + enrich) — `sources.yaml` primary  
- **Auto login:** Career Fit–ported burner state machine (`burner/bootstrap.py`) — `_await_post_password`, PT challenge strings, feed nudge, already-warm short-circuit, IMAP App Password OTP  
- **Secrets preflight:** rejects normal Gmail password as IMAP secret; requires 16-char App Password or `totp_secret`  
- **Insight:** `warm_bridge.research` — DuckDuckGo public search, cited snippets  
- API: `POST /api/linkedin-map` (primary), `POST /api/investigate` (legacy CSV), `/api/research`  
- UI: **Mapear** (LinkedIn URL only) · session panel · CSV demoted to “Legado”  
- Eval: 17 cases incl. challenge classifier + OTP year-filter + app-password preflight  
- Docs: `README.md`, `docs/LINKEDIN_SESSION.md`, `docs/PRODUCT.md`, skills aligned LinkedIn-first  

## Session arc (2026-08-20) — structured

| Phase | What |
|-------|------|
| Product pivot | LinkedIn scrape primary; CSV → legacy; secrets yaml auto-boot |
| OTP breakthrough | Port Career Fit `burner_login` state machine into Warm Bridge |
| Camoufox lifecycle | `launch_persistent` + humanize + feed nudge for cookie persist |
| IMAP harden | Year-like `20xxxx` OTP filter; AUTH vs timeout errors |
| Preflight | Reject Gmail login password as App Password |
| Status probe | `_authed_url` + `logged_in_hint` (cookie files) |
| Dogfood | App Password saved; session warm on `/feed/`; `scripts/dev.sh` up |
| Hygiene | `.gitignore` covers secrets, camoufox profile, `.venv-linkedin/`, `tmp/` |

## Decisions locked (2026-08-20)

| Decision | Rationale |
|----------|-----------|
| LinkedIn scrape primary | Same wedge as Career Fit — less friction |
| CSV demoted / deprecated UX | Hard product pivot |
| Secrets in `data/secrets/linkedin_account.yaml` | Zero-touch after first boot |
| Public web research for insight | Cited hooks; never invent mutuals |
| Never invent people from search | Red tier in sources.yaml |
| Career Fit login state machine ported | Fixes false SMS / premature detect; cookie persist |
| SMS 2FA out of scope | Honest error; user switches to email/authenticator |

## Credentials (founder)

**Paste in chat — agent writes file, warms session, starts app. You only open UI.**

1. LinkedIn email (Gmail that receives LinkedIn codes)  
2. LinkedIn / account password  
3. Gmail **App Password** (16 chars — not normal Gmail password)  

Optional: `linkedin.com/in/…` · or `totp_secret` if authenticator 2FA  

Never commit `data/secrets/` or `data/camoufox_profile/`.

## Active priorities

1. **P0** Dogfood Mapear on a real target URL (session warm)  
2. **P1** Harden mutuals/enrich selectors  
3. **Later** Radar, landing, server outcomes  

## Last session

- Date: 2026-08-20  
- Done: Career Fit OTP port; secrets + warm session; README/skills/gitignore; context saved; commit+push  
- Blocked: none for session boot (profile already on feed)  
- Next: Mapear real target; harden mutuals selectors if empty/fragile  

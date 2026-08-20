# AGENTS.md — operating contract for every AI on Warm Bridge

You are building a **profitable SaaS**: warm paths to decision-makers (Lead Police UX) — drafts the user sends, not a spam cannon.

**Owner product direction (locked 2026-08-20, updated same day):** **LinkedIn session primary** — Camoufox scrape mutuals → board → ask. CSV/paste demoted to legacy fallback. Public web research enriches asks (cited URLs). Chat orders override older “CSV-first / no login” language in skills/history.

## Authority

- Product owner sets roadmap; durable truth is this file + [`docs/sources.yaml`](docs/sources.yaml) + [`docs/context/CURRENT.md`](docs/context/CURRENT.md).
- Prefer implementing what `sources.yaml` marks `enabled: true` and `primary: true`.
- Chat is ephemeral. Repo context is the source of truth.

## Before you write code

1. Read [`docs/context/CURRENT.md`](docs/context/CURRENT.md)
2. Read [`docs/sources.yaml`](docs/sources.yaml) — intake tiers (LinkedIn session primary)
3. Read [`docs/AI_BUILD_MAP.md`](docs/AI_BUILD_MAP.md) for code ownership
4. Read [`docs/PRODUCT.md`](docs/PRODUCT.md) / [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) as needed
5. Skim matching skill under [`.cursor/skills/`](.cursor/skills/)

## After you finish meaningful work

1. Update `docs/context/CURRENT.md`
2. Append `docs/context/log/YYYY-MM-DD.md`
3. Extend `docs/AI_BUILD_MAP.md` when modules/routes land
4. Encode durable conventions in skills / `.cursor/rules/`

## Product north star

```
target LinkedIn URL → auto session → scrape mutuals → enrich + public research → ranked bridges → ask → you send
```

**UX (Lead Police):** investigation board + spider-web + person pins from **session-observed mutuals** + cited public insights — not demo theater or invented mutuals.

**Long-arc:** NET memory → thicken edges → opportunity radar.

## Preferred patterns (hard-coded)

- **Primary graph:** `linkedin_session.map_target` → mutuals → `find` pipeline (Camoufox persistent profile).
- **Auto session:** `data/secrets/linkedin_account.yaml` → boot on `warm-bridge serve` + before map; Gmail OTP / pyotp for 2FA.
- **Insight:** `research.research_target` → cited snippets → board + ask hook.
- **Wedge API:** `POST /api/linkedin-map` (+ research). `POST /api/investigate` kept for legacy CSV path.
- **Legacy:** `imports` CSV/phone/paste — fallback only, not default UX.
- Deterministic score → explain → template ask; LLM polish optional under `playbook/approach-rules.md`.
- Manual send only (WhatsApp / LinkedIn). No mass-send from our servers.
- Never invent mutuals, people, or strength not in the import/session graph.

## Still banned

- Mass WhatsApp/DM send from Warm Bridge servers
- Fake “% fit” scores
- Inventing people/edges from web search (“probably knows…”)
- Committing real PII (`data/network.yaml`, `data/secrets/`, credentials, cookies) to git
- End-user password fields in FastAPI/UI (secrets file only)

## Skills

| Skill | When |
|-------|------|
| `warm-bridge-context` | Session handoff |
| `warm-bridge-product` | Scope / pricing |
| `warm-bridge-bridges` | Score, modes, asks, outcomes, evals |
| `warm-bridge-sources` | Session adapters, research, sources.yaml |

## Commit hygiene

Conventional commits. Never commit credentials, cookies, or real PII.

# Warm Bridge

**Warm paths to decision-makers — LinkedIn mutuals + cited public insight → ranked bridges + ask scripts.**

Paste a target LinkedIn URL. Warm Bridge scrapes **your** session mutuals (Camoufox), enriches with public web research, ranks bridges, and drafts the ask. **You** send. No mass-DM from our servers. No invented mutuals.

```
target LinkedIn URL → auto session → scrape mutuals → enrich + research → ranked bridges → ask → you send
```

That loop is the company. CSV/paste import is legacy fallback only.

**Long game:** a friendly **NET** — track who you reached and who helps, grow the spider-web, surface opportunities. Ship the Mapear wedge first; the ecosystem is how we retain and compound.

## Who pays

Field / B2B commercials who already get meetings via network — but waste time hunting *who* can open the door and *how* to ask without looking desperate.

## Why we win

| Pain | We ship | Moat |
|------|---------|------|
| Can’t reach the decision-maker | Ranked bridges from **session-observed** mutuals | Bridge taxonomy + strength-gated asks |
| Fear of burning a contact | Modes: intro / forward / intel / permission | Playbook in `playbook/` — not generic LLM spam |
| Tools that invent “% fit” or fake friends | Deterministic score + path proof + cited URLs | Explainability commercials trust |
| Friction to first path | Founder pastes 3 secrets → headless login → Mapear | Career Fit–style auto session |

## Sibling product

| Career Fit | Warm Bridge |
|------------|-------------|
| Job → tailored CV → DM recruiter | Target → warm bridge → ask for intro |
| Angle playbook on one bio | Bridge taxonomy on one graph |
| Candidate reach-out | Seller reach-out |

Same SaaS posture (paste secrets → headless Camoufox → UI-only dogfood). Different JTBD.

## Run it (dogfood)

```bash
cd warm-bridge
./scripts/setup.sh                # once: .venv-wb + pip + npm + camoufox fetch
```

**Credentials (paste in chat or write the file yourself — never commit):**

1. LinkedIn email (Gmail that receives codes)  
2. LinkedIn password  
3. Gmail **App Password** (16 chars — not your Gmail login password)

```bash
# agent writes data/secrets/linkedin_account.yaml (mode 600), or:
# copy data/secrets/linkedin_account.yaml.example → data/secrets/linkedin_account.yaml

.venv-wb/bin/warm-bridge burner-login   # headless Camoufox + IMAP OTP
./scripts/dev.sh                        # API :8788 + UI :5174
```

Open **http://127.0.0.1:5174** → paste target `linkedin.com/in/…` → **Mapear**.

```bash
.venv-wb/bin/warm-bridge eval           # regression (incl. challenge classifier)
.venv-wb/bin/warm-bridge session-status
```

Docs: [`docs/LINKEDIN_SESSION.md`](docs/LINKEDIN_SESSION.md) · [`docs/RESEARCH.md`](docs/RESEARCH.md)

Legacy CSV import (still works, demoted in UI):

```bash
warm-bridge import --file ~/Downloads/Connections.csv
```

## Repo map

| Path | Role |
|------|------|
| `AGENTS.md` | **Contract for every AI** — LinkedIn-session primary |
| [`docs/AI_BUILD_MAP.md`](docs/AI_BUILD_MAP.md) | Commit ledger + file/module ownership |
| `docs/PRODUCT.md` | Vision, tiers, exit criteria |
| `docs/ARCHITECTURE.md` | System, priorities, non-goals |
| `docs/sources.yaml` | Intake tiers (Camoufox primary) |
| `docs/LINKEDIN_SESSION.md` | Secrets gate + burner OTP ops |
| `docs/context/CURRENT.md` | Living session state — **source of truth** |
| `docs/context/log/` | Append-only day logs |
| `.cursor/skills/` | How AIs execute product/bridges/sources/context |
| `playbook/` | Bridge types, modes, anti-spam ask rules |
| `src/warm_bridge/linkedin_session/` | Camoufox map + Career Fit login state machine |
| `src/warm_bridge/research/` | Public cited insight |
| `web/` | Lead Police board — Mapear primary |

## Hard bans

- Inventing mutuals or people from web search  
- Mass-sending WhatsApp/DM from our servers  
- Fake “% fit” scores  
- Committing credentials, cookies, or real PII (`data/secrets/`, `data/camoufox_profile/`)

## AI rule (non-negotiable)

Chat is ephemeral. **Repo context is memory.**

1. Before coding: read `docs/context/CURRENT.md` + `AGENTS.md` (+ `docs/AI_BUILD_MAP.md` for code work)  
2. After meaningful work: update CURRENT + append `docs/context/log/YYYY-MM-DD.md`  
3. New durable ideas → skill, rule, or PRODUCT/ARCHITECTURE — not only chat  

## License

MIT — keep real contacts and secrets in `data/` (gitignored).

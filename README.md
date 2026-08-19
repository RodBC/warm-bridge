# Warm Bridge

**Warm paths to decision-makers — ranked bridges + ask scripts from *your* network.**

Stop cold-chasing buyers. Import LinkedIn + phone contacts, name the target, get the hottest bridge and a WhatsApp-ready ask. **You** send. The product does not burn your relationships or scrape LinkedIn for you.

```
target → bridges in your graph → path proof + why → ask mode → you send
```

That loop is the company. Everything else is distribution.

**Long game:** a friendly **NET** — track who you reached and who helps, grow the spider-web of contacts, and get suggestions (café nearby, setup helpers, events, posts, thin edges to fill). Ship the wedge first; the ecosystem is how we retain and compound.

## Who pays

Field / B2B commercials (starting wedge: reps like “parents as sellers”) who already get meetings via network — but waste time hunting *who* can open the door and *how* to ask without looking desperate.

Same insight healthtech uses when it sells “who to approach” from CRM: **intel on the path is the product.** Here the CRM is the seller’s own LinkedIn + cell.

## Why we win

| Pain | We ship | Moat |
|------|---------|------|
| Can’t reach the decision-maker | Ranked bridges from *user-owned* graph | Bridge taxonomy + strength-gated asks |
| Fear of burning a contact | Modes: intro / forward / intel / permission | Playbook in `playbook/` — not generic LLM spam |
| Tools that scrape & risk accounts | Official CSV / paste only | Trust + ToS hygiene |
| Vague “AI networking” apps | One-line **path proof** + deterministic why | Explainability commercials trust |

Scrapers are not the moat. **Path quality + ask craft + later reply outcomes** are.

## Sibling product

| Career Fit | Warm Bridge |
|------------|-------------|
| Job → tailored CV → DM recruiter | Target → warm bridge → ask for intro |
| Angle playbook on one bio | Bridge taxonomy on one graph |
| Candidate reach-out | Seller reach-out |

Same SaaS posture. Different job-to-be-done. Shared discipline: paste-not-scrape, manual send, durable AI context in git.

## Run it

```bash
cd warm-bridge
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

warm-bridge eval
warm-bridge find \
  --target-name "Marina Costa" \
  --target-company "Acme Saúde" \
  --target-title "Diretora de Compras"

# UI — two terminals
warm-bridge serve                 # API http://127.0.0.1:8788
cd web && npm install && npm run dev   # UI http://localhost:5174
```

Import real data (never commit PII):

```bash
warm-bridge import --file ~/Downloads/Connections.csv
cp profile/example.seller.yaml data/seller.yaml   # then edit
```

## Repo map

| Path | Role |
|------|------|
| `AGENTS.md` | **Contract for every AI** — read/write context or don’t touch the repo |
| [`docs/AI_BUILD_MAP.md`](docs/AI_BUILD_MAP.md) | Commit ledger + file/module ownership — **how / where / why** |
| `docs/PRODUCT.md` | Vision, tiers, exit criteria |
| `docs/ARCHITECTURE.md` | System, priorities, non-goals |
| `docs/context/CURRENT.md` | Living session state — **source of truth** |
| `docs/context/log/` | Append-only day logs |
| `.cursor/skills/` | How AIs execute product/bridges/sources/context |
| `.cursor/rules/` | Always-on Cursor enforcement |
| `playbook/` | Bridge types, modes, anti-spam ask rules |
| `src/warm_bridge/` | import → resolve → score → explain → approach |
| `web/` | Funnel UI: Rede → Alvo → Pontes → Pedir |

## AI rule (non-negotiable)

Chat is ephemeral. **Repo context is memory.**

1. Before coding: read `docs/context/CURRENT.md` + `AGENTS.md` (+ `docs/AI_BUILD_MAP.md` for code work)  
2. After meaningful work: update CURRENT + append `docs/context/log/YYYY-MM-DD.md` (+ AI_BUILD_MAP if layers changed)  
3. New durable ideas → skill, rule, or PRODUCT/ARCHITECTURE — not only chat  

## License

MIT — keep real contacts in `data/` (gitignored).

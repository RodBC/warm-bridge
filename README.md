# Warm Bridge

**Target → bridges in your graph → scored paths + approach scripts.**

Open-source core of a sales networking pipeline: commercials struggle to reach decision-makers; the ROI move is **warm paths**, not more cold calls. This repo packages the hard-won part — how to rank *possible bridges* from LinkedIn + phone contacts and suggest *how* to ask for the intro **without** sounding like spam laundered through a friend.

## Why this exists

Cold outreach to buyers underperforms. What works in the field (and mirrors how healthtech sells “who to approach” intel from CRM):

1. Name the **decision-maker** (or the role + company)
2. Search **your** network (LinkedIn 1sts + phone book) for bridges
3. Rank paths by bridge type + relationship strength
4. Ship a short **ask script** (WhatsApp / LinkedIn / call opener)

Later vision: multi-rep territories, CRM sync, relationship strength tutoring (who you can actually ask, who you burned, who owes you a favor).

This v0 ships the **IP layer** — bridge taxonomy, scoring, approach playbook — plus a fast local pathfinder. Scraping LinkedIn (or anyone else’s CRM) is intentionally out of scope for the public repo; you **import** exports the user already owns.

## What's in the box

| Path | Purpose |
|------|---------|
| `playbook/` | Bridge types, scoring weights, approach rules — the product moat |
| `corpus/examples/` | Sanitized before/after approach patterns |
| `profile/` | Seller + network schema + fictional example |
| `prompts/` | LLM prompts for path explain / approach polish / territory brief |
| `evals/` | Local bridge-ranking regression cases |
| `src/warm_bridge/` | Fast path: find + score bridges + draft asks **without** an API call |

### Performance idea

Don't ask an LLM to “figure out the network” every time.

1. Normalize contacts into a local graph (CSV / vCard / LinkedIn export)
2. Match target → candidate bridges with deterministic rules
3. Score with `playbook/bridge-types.yaml` weights
4. Render approach drafts from templates
5. Optionally polish with an LLM using `prompts/` + `playbook/approach-rules.md`

## Quick start

```bash
cd warm-bridge
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Rank bridges to a target (uses profile/example.network.yaml)
warm-bridge find \
  --target-name "Marina Costa" \
  --target-company "Acme Saúde" \
  --target-title "Diretora de Compras"

# Draft approach scripts for top bridges
warm-bridge approach \
  --target-name "Marina Costa" \
  --target-company "Acme Saúde" \
  --locale pt

# Show seller / territory brief
warm-bridge profile

# Run evals
warm-bridge eval
```

Outputs land in `data/out/` (gitignored): ranked JSON + message drafts.

### Your private network

```bash
cp profile/example.network.yaml data/network.yaml
cp profile/example.seller.yaml data/seller.yaml
# edit real contacts — keep PII off GitHub
```

`data/network.yaml` and `data/seller.yaml` are gitignored.

## Bridge types (same graph, different lens)

| Type | Meaning |
|------|---------|
| `direct` | You already have the target as a contact |
| `same_company` | Bridge works/worked where the target sits |
| `mutual_hint` | Bridge notes mention the target / company |
| `phone_warm` | Strong phone-book relationship + company/role overlap |
| `alumni` | Shared school or past employer signal |
| `title_adjacent` | Bridge title sits next to the buyer role (peer / ex-peer) |

Rules that matter live in `playbook/approach-rules.md`.

## Roadmap (platform)

- [ ] Import adapters (LinkedIn connections CSV, Google/Apple contacts, HubSpot notes) — user-supplied files only  
- [ ] Relationship-strength tutoring (favor bank, recency, “can I ask this person?”)  
- [ ] Optional LLM provider for approach polish  
- [ ] Team / territory mode (parents-as-reps: shared graph, private asks)  
- [ ] CRM export of “who to approach” for managers (healthtech-style intel layer)

## Public repo hygiene

- Example seller + network are **fictional**  
- Corpus examples are **sanitized patterns**, not real outreach logs  
- Put real identity and contacts only under `data/`  
- No ToS-hostile scraping in core

## License

MIT

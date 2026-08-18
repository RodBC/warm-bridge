# Warm Bridge

**Alvo → pontes na sua rede → caminho ranqueado + pedido pronto.**

SaaS wedge for field/B2B sales: decision-makers are hard to reach; warm paths beat cold spray. Import LinkedIn + phone contacts, name the buyer, get the best bridge and a WhatsApp-ready ask — **you** send.

## Product thesis

Same commercial posture as Career Fit, different job-to-be-done:

| Career Fit | Warm Bridge |
|------------|-------------|
| Job → tailored CV → DM recruiter | Target → warm bridge → ask for intro |
| Angle playbook on one bio | Bridge taxonomy on one graph |
| Paste JD + recruiter cards | Paste/export Connections + phone book |

Moat = **path proof + ask craft that doesn’t burn relationships**, not scrapers.

See `docs/ARCHITECTURE.md`.

## Quick start

```bash
cd warm-bridge
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# CLI
warm-bridge find \
  --target-name "Marina Costa" \
  --target-company "Acme Saúde" \
  --target-title "Diretora de Compras"

warm-bridge approach --target-name "Marina Costa" --target-company "Acme Saúde" --locale pt
warm-bridge import --file corpus/examples/linkedin-connections-sample.csv
warm-bridge eval

# UI (two terminals)
warm-bridge serve          # API :8788
cd web && npm install && npm run dev   # UI :5174
```

## What's in the box

| Path | Purpose |
|------|---------|
| `playbook/` | Bridge types, modes, anti-spam ask rules |
| `corpus/examples/` | Ask patterns + sample LinkedIn/phone CSV |
| `profile/` | Seller + network schema (fictional examples) |
| `prompts/` | Optional LLM polish (not required for v0.2) |
| `src/warm_bridge/` | Import → resolve → score → explain → approach |
| `web/` | Commercial funnel UI (Rede → Alvo → Pontes → Pedir) |
| `docs/ARCHITECTURE.md` | Priorities, anti-scrape, what we borrow from career-fit/entrep |

### Performance idea

1. Normalize user-owned imports into a local graph  
2. Resolve whether the target is already in-graph (`CONFIRMED` / `LIKELY` / `NOT_IN_GRAPH`)  
3. Score bridges with playbook weights  
4. Explain *why* (deterministic bullets) + confidence bands (not fake %)  
5. Fill ask templates by mode; optional LLM later  

## Private data

```bash
cp profile/example.seller.yaml data/seller.yaml
cp profile/example.network.yaml data/network.yaml
```

`data/*.yaml` is gitignored.

## License

MIT

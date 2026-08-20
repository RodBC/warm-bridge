# Public web research

Primary **insight** layer when LinkedIn login is not used. Complements owned graph (CSV/phone/paste).

## What it does

- Builds queries from target name, company, title, optional LinkedIn URL slug
- Fetches **public** results via DuckDuckGo HTML lite (`html.duckduckgo.com`)
- Returns cited `{title, url, snippet, kind}` items — never invents people or mutual edges
- Optional hook line woven into bridge asks (`approach.py`)

## What it does not do

- Log into LinkedIn
- Invent bridges (“Ana probably knows them”)
- Replace your network — bridges still come from `imports` only

## API

```bash
warm-bridge research --target-name "Marina Costa" --target-company "Acme Saúde"
curl -X POST http://127.0.0.1:8788/api/research \
  -H 'Content-Type: application/json' \
  -d '{"target":{"name":"Marina Costa","company":"Acme Saúde"}}'
```

**Investigate** (wedge):

```bash
warm-bridge investigate --target-name "…" --target-company "…" --network data/network.yaml
POST /api/investigate  # find + research; requires non-empty network
```

## Rate limits

- ~1.2s minimum between search requests (`search.py`)
- Cap queries (default 3) and items (default 8)
- Polite User-Agent string

## Policy

See `docs/sources.yaml` → `public_web_research` (green).

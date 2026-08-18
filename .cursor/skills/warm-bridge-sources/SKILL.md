---
name: warm-bridge-sources
description: >-
  Network intake policy for Warm Bridge. Use when adding import adapters,
  LinkedIn/phone/vCard parsers, or enrichment. Triggers: import, Connections.csv,
  phone CSV, scrape, LinkedIn, sources.yaml, vCard.
---

# Warm Bridge — sources skill

## Policy

Read `docs/sources.yaml` and `docs/entrep-transfer.md`.

| Tier | Meaning | Action |
|------|---------|--------|
| green | User-owned or official | Build freely |
| yellow | Assisted / cautious | User-initiated only; no login bypass |
| red | ToS-hostile / fragile | Do not ship in public core |

LinkedIn automated scrape = **red**. Mass send = **red**.

## Preferred architecture

```python
# Conceptual — keep adapters thin
class NetworkSource(Protocol):
    def load(self, raw: str) -> list[dict]: ...
```

Backends today: LinkedIn Connections CSV, phone CSV, paste cards.  
Later: vCard, Google OAuth, browser-assist (yellow, private-first).

## Messaging

Drafts from `approach.py`. User sends on WhatsApp/LinkedIn. Never automate blast from API.

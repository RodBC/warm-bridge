# Entrep → Warm Bridge transfer notes

Source repo: `/home/decastro/entrep` (RepHelp / reputation intel).  
**Do not fork scrapers or the reputation vertical.** Steal mechanics.

## Worth borrowing

| Pattern | Where in entrep | Use in Warm Bridge |
|---------|-----------------|--------------------|
| Identity resolution + audit statuses | `ReclameAqui/.../resolver/identity.py`, `docs/identity-resolution.md` | `resolve.py`: CONFIRMED / LIKELY / NOT_IN_GRAPH |
| Fuzzy name match when lists collide | `rephelp/scrapers/gmaps_backend.py` match_score | Contact ↔ target name collisions |
| “Show their data” outbound (Pulse) | `rephelp/reports/pulse_email.py`, PRODUCT_PLAN GTM | UI **path proof** line — sell the path, not features |
| Brand → location hierarchy | hospital multi-location docs | Later: Account → targets → paths |
| Source tiers green/yellow/red | `sources.yaml` | `docs/sources.yaml` here |
| Traceable run ids | GMaps manifests | Later: import_id → find_id audit |

## Ignore

- Reclame Aqui / Maps crawlers as “search infrastructure”  
- Streamlit as the customer-facing product UI  
- Complaint evolution scoring weights  
- Treating scrape farms as moat  

## Creative caution

Entrep’s strongest lesson: **resolve ambiguous entities with an audit trail.**  
Weakest lesson: **public-web scrape = product.** For Warm Bridge, moat is graph quality + bridge confidence + ask conversion.

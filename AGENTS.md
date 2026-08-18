# AGENTS.md — operating contract for every AI on Warm Bridge

You are building a **profitable SaaS**, not a LinkedIn scraper and not a spam cannon.

## Before you write code

1. Read [`docs/context/CURRENT.md`](docs/context/CURRENT.md)  
2. Read [`docs/PRODUCT.md`](docs/PRODUCT.md) if the task touches product scope  
3. Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) if the task touches system design  
4. Skim the relevant skill under [`.cursor/skills/`](.cursor/skills/)

## After you finish meaningful work

1. Update [`docs/context/CURRENT.md`](docs/context/CURRENT.md) (status, decisions, next)  
2. Append a short entry to `docs/context/log/YYYY-MM-DD.md` (create if missing)  
3. If you introduced a durable convention, encode it in a skill or `.cursor/rules/` — do not leave it only in chat  
4. New product ideas → `docs/PRODUCT.md` or CURRENT **Open questions / Ideas**; shipped capabilities → **What exists now**

**Chat is ephemeral. Repo context is the source of truth.**

## Product north star

```
target → bridges in your graph → path proof + why → ask mode → you send
```

**Long-arc (do not build ahead of the wedge):** NET memory (reached DMs + helpers) → thicken edges → opportunity radar + friendly spider-web UX. See `docs/PRODUCT.md` Ecosystem arc.

If a feature does not tighten the wedge loop *or* clearly advance the sequenced NET arc (and willingness to pay), do not build it.

## Hard bans

- Automated LinkedIn (or phone-book) harvesting in the public core  
- Mass WhatsApp/DM sending from our servers  
- Inventing mutuals, shared history, or relationship strength not in the import  
- Fake precision UI (“87% fit”) — use confidence bands + why bullets  
- Shipping scrapers-as-moat (wrong business)

## Preferred patterns

- Deterministic score → explain → template ask; LLM polish optional and constrained by `playbook/approach-rules.md`  
- Intake via user-owned LinkedIn export / phone CSV / paste (`docs/sources.yaml`)  
- Manual send is a feature: quality over spray; relationship is the asset  
- Borrow funnel UX ideas from Career Fit; borrow identity-resolution *ideas* from entrep — never their red-tier scrapers  

## Skills (project)

| Skill | When |
|-------|------|
| `warm-bridge-context` | Any session — read/write context |
| `warm-bridge-product` | Roadmap, pricing, scope fights |
| `warm-bridge-bridges` | Scoring, modes, ask templates, evals |
| `warm-bridge-sources` | Imports, LinkedIn CSV, phone CSV, source tiers |

## Commit hygiene

Conventional commits (`feat`, `fix`, `docs`, `chore`, `refactor`). Keep PRs small. Never commit `data/network.yaml`, `data/seller.yaml`, or real PII.

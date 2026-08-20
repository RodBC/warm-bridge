# Architecture & critical path — Warm Bridge

> AIs: also read `docs/context/CURRENT.md` and follow `AGENTS.md`. After changes, update context + daily log.  
> For **where code lives**, read [`docs/AI_BUILD_MAP.md`](AI_BUILD_MAP.md).

## Product thesis

Comerciais travam no tomador de decisão:

**rede importada + alvo → insight público citado → pontes ranqueadas → pedido curto → você manda**

O IP difícil de copiar não é scraper. É: taxonomia de pontes + quando pedir o quê + texto que não queima a relação + memória de alcance.

## Wedge comercial (o que vende agora)

| Entrega | Por que paga |
|---------|----------------|
| Import Connections.csv / phone / paste | Grafo sem login LinkedIn |
| **Investigar** (find + pesquisa pública) | Pontes + gancho citado no mesmo fluxo |
| “Melhor caminho” em 1 linha (prova) | Substitui caça manual |
| Mensagem WhatsApp/DM pronta | ROI no mesmo dia |

Manual send é feature. LinkedIn Selenium session é **opcional** (ban risk).

## Prioridades

| Priority | Build | Why |
|----------|-------|-----|
| **P0** | Owned graph intake (CSV / phone / paste) | Primary graph — no LI login |
| **P0** | Public web research + `/api/investigate` | Cited insight without inventing edges |
| **P0** | Path proof + drafts + Lead Police board | Conversão |
| **P1** | Casos + favor-bank | Retention |
| **P2** | Optional Selenium `linkedin-map` | Owners who accept session risk |
| **Later** | Opportunity radar, landing, team graph | After wedge reliable |

## Intake (ordered)

| Need | Approach |
|------|----------|
| Grafo | `imports` — Connections.csv primary |
| Insight | `research` — DuckDuckGo HTML, cited URLs |
| Wedge API | `POST /api/investigate` |
| Optional mutuals | `linkedin_selenium` — yellow, not default |

## Non-goals

- Inventar pessoas/pontes a partir de busca web  
- Login LinkedIn como requisito do happy path  
- Demo fixture como UX padrão  
- Mass-send  

See [`docs/RESEARCH.md`](RESEARCH.md) and [`docs/sources.yaml`](sources.yaml).

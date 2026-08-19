# Architecture & critical path — Warm Bridge

> AIs: also read `docs/context/CURRENT.md` and follow `AGENTS.md`. After changes, update context + daily log.  
> For **where code lives and why** (commit ledger, module ownership, extension cheat sheet), read [`docs/AI_BUILD_MAP.md`](AI_BUILD_MAP.md).

## Product thesis

Comerciais travam no tomador de decisão. O que funciona no campo (e espelha a lógica de “vender quem abordar” da healthtech):

**alvo → pontes na *sua* rede (LinkedIn + celular) → ranking honesto → pedido curto → você manda**

O IP difícil de copiar não é scraper. É: taxonomia de pontes + quando pedir o quê + texto que não queima a relação.

## Wedge comercial (o que vende agora)

| Entrega | Por que paga |
|---------|----------------|
| “Melhor caminho” em 1 linha (prova) | Substitui 30 min caçando quem conhece quem |
| Lista ranqueada com *por quê* | Confiança pra pedir intro sem constranger |
| Mensagem WhatsApp/DM pronta | ROI no mesmo dia — pais/reps mandam e medem resposta |
| Import CSV LinkedIn / celular | Onboarding sem integração pesada |

Manual send é feature: qualidade > spray. Relação é o ativo.

## Prioridades

| Priority | Build | Why |
|----------|-------|-----|
| **P0** | UI + API local | Sem isso só o CLI existe — não vende |
| **P0** | Import LinkedIn Connections + phone CSV + paste | Intake = distribuição |
| **P0** | Path proof + confidence bands + drafts | Conversão do wedge |
| **P1** | Strength tutoring (“posso pedir pra essa pessoa?”) | Reduz burn de rede |
| **P1** | Conta/território (multi-alvo por empresa) | Pais = várias contas/semana |
| **P2** | LLM polish opcional | Só depois do determinístico estável |
| **P2** | Reach / outcome tracker (DMs, bridges, intros) | Memória do ecossistema — sem isso não há NET |
| **Later** | Opportunity radar (cidade, eventos, setup helpers, posts) | Sugestões que densificam a rede |
| **Later** | NET UI (spider-web / edge graph) + UX field-first | Visualizar e expandir pontos de contato |
| **Later** | CRM sync / team graph | Expansão multi-rep |

## LinkedIn scraping — critical take

**Não shipar scraper de LinkedIn no core público.** Mesmas razões do Career Fit: ToS, fragilidade, moat errado, risco.

### Mesmo outcome, intake limpo

| Need | Approach |
|------|----------|
| Grafo 1º grau | Export oficial `Connections.csv` ou paste |
| Celular | CSV / vCard que o usuário exporta |
| Notas de relação | Campo `notes` / tags — o ouro do scoring |
| Enrichment depois | OAuth / partners / browser-assisted *user-initiated* — nunca harvester headless no OSS |

## O que pegamos (e o que não) dos outros repos

| Fonte | Pegar | Ignorar |
|-------|-------|---------|
| **career-fit** | Funil paste→rank→draft, FastAPI+Vite, anti-scrape, manual send | CV/LaTeX, “% fit” cosmético, visual cream-teal |
| **entrep** | Resolução de identidade com audit, “mostrar a prova” (Pulse), hierarquia conta→pessoa | Scrapers RA/Maps, Streamlit como produto, domínio de reputação |

## System sketch

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Vite web    │────▶│  FastAPI     │────▶│  warm_bridge core   │
│  rede/alvo   │     │  /import     │     │  import→resolve     │
│  pontes/ask  │     │  /find       │     │  score→explain→ask  │
└──────────────┘     └──────────────┘     └─────────────────────┘
```

## Non-goals (for now)

- Disparo em massa de WhatsApp/DM pelo app  
- Inventar mutuals que não estão no import  
- “AI aplica/vende por você”  
- Index/embeddings sem necessidade — o grafo do usuário já é pequeno o bastante pra regras

## Moat checklist

1. Playbook de modes (intro / forward / intel / permission) amarrado a strength  
2. Explainability (“why”) que o comercial confia  
3. Corpus de asks que não cheiram a spam-pela-amiga  
4. Depois: dados de conversão (qual ponte respondeu) — feedback loop proprietário

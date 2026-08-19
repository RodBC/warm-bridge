# CURRENT context — Warm Bridge

> **AIs: read this fully before coding. Update this file before you end a session with meaningful changes.**

**Last updated:** 2026-08-19  
**Repo:** `/home/decastro/studies/warm-bridge` (own git → `origin` github.com/RodBC/warm-bridge)  
**Sibling SaaS:** `/home/decastro/studies/career-fit` (same AI-context discipline; different JTBD)  
**Inspiration (patterns only):** `/home/decastro/entrep` identity resolution + Pulse “show the proof”

## Goal

Ship a profitable SaaS that turns a seller’s **user-owned network** + a **decision-maker target** into **ranked bridges + approach scripts**, without burning relationships or scraping LinkedIn.

Loop:

`target → bridges in your graph → path proof + why → ask mode → you send`

**Long-arc (ecosystem / NET):** track decision-makers + helpful bridges → thicken the edge graph (spider web) → suggest next moves (same-city café, setup helpers, events, posts, thin edges to grow) → friendly UI/UX. Wedge ships first; NET is the retention moat.

## What exists now

- Playbook: `playbook/bridge-types.yaml`, `modes.yaml`, `approach-rules.md`, `structure.md`  
- Core Python: import / resolve / paths / explain / tutor / accounts / approach / **outcomes**  
- API: FastAPI on `:8788` — `/api/find`, `/api/find-account`, `/api/outcomes`, …  
- UI: send-ready workspace + account mode + **reach history** (localStorage, status chips)  
- CLI: `find` (incl. `--seller`), `approach`, `import`, `eval`, `profile`, `serve`  
- AI contract: `AGENTS.md`, `.cursor/rules/`, `.cursor/skills/`, this context system  
- **Code archaeology for AIs:** `docs/AI_BUILD_MAP.md` (commit layers, module map, where-to-edit)  
- Samples: `corpus/examples/linkedin-connections-sample.csv`, phone CSV, ask patterns  
- Real CSV checklist: [`docs/CSV_VALIDATION.md`](../CSV_VALIDATION.md) (no PII in repo)

## Decisions locked

| Decision | Rationale |
|----------|-----------|
| No automated LinkedIn/phone harvester in public core | ToS, bans, fragility; wrong moat |
| Deterministic score → explain → template ask; LLM optional | Fast, cheap, controllable |
| Manual send of WhatsApp/DM | Quality + compliance; product is drafts not spam |
| Confidence bands + why, never fake % fit | Commercials trust explainability |
| Separate `direct` vs `bridge` buckets | “You already know them” ≠ “ask someone for intro” |
| Context must live in git | Chat is ephemeral; SaaS iteration needs memory |
| Borrow Career Fit funnel + entrep resolution *ideas* only | Don’t fork scrapers or reputation vertical |
| Code archaeology in `AI_BUILD_MAP.md` | Agents extend ownership tables when adding layers — not chat archaeology |
| Outcomes browser-first; API validate/echo only | Foundation for NET memory without server PII yet |

## Active priorities (P0 → P2)

1. **P0** Keep context/skills discipline as default agent behavior  
2. **P0** Validate ranking with a **real** Connections/phone export (parents / field seller) — checklist in `docs/CSV_VALIDATION.md`  
3. **P1** ~~Strength tutoring UX~~ — shipped (`tutor.py` + ask dock)  
4. **P1** ~~Account / multi-target workspace~~ — shipped (`accounts.py`, `/api/find-account`)  
5. **P1** ~~Persist network in browser session~~ — shipped (`web/src/storage.ts` v2)  
6. **P1** ~~Outcome / reach logging~~ — shipped (`outcomes.py`, `web/src/outcomes.ts`, Histórico + chips)  
7. **P2** Optional LLM polish behind `playbook/approach-rules.md` **or** healthtech-path landing — leave open  
8. **Later** Opportunity radar: same-city café, common-friend/ex-colleague setup, events, LinkedIn topic posts, territory underuse  
9. **Later** NET UI — spider-web / edge graph, user-friendly (list-first, graph when useful, mobile for field)  
10. **Later** Team territory graph; CRM export of “who to approach”

## Open questions

- Exact Pro price ($29–49 draft)  
- Whether Team (parents co-selling) ships before LLM polish  
- vCard / Google Contacts adapter priority vs LinkedIn CSV alone  
- Cross-link / shared auth with Career Fit later?  
- How much graph UX in Pro vs Team (spider web can distract from “send the ask”)?  
- Next after outcomes: LLM polish vs marketing landing?

## Ideas captured (not yet scoped)

- Favor-bank / cooldown after asking a bridge  
- Pulse-style weekly email: “3 accounts with new warm paths”  
- Healthtech analogy landing page: sell the *path*, not the feature list  
- **Ecosystem NET:** living tracker of reached DMs + bridge helpers; densify edges; suggest café / events / setup helpers / posts / thin-spot contacts  
- “Where the net is thin” — intentional new contacts (still user-initiated adds)  
- Content assists tied to open accounts  

## Do not regress

- Inventing mutuals or closeness  
- Shipping LinkedIn credential stuffing / session hijack  
- Mass-send from our servers  
- Letting README go vague — stay decisive  
- Skipping context updates after meaningful work  

## Session handoff template

When updating this file, keep sections above and refresh **Last session**:

```
### Last session
- Date:
- Done:
- Blocked:
- Next exact task:
```

### Last session

- Date: 2026-08-19  
- Done: Stabilized send-ready + account layers (`4c4f8f9`); CLI `find --seller`; CSV checklist; outcome/reach logging (browser history + chips + thin `/api/outcomes`)  
- Blocked: Real CSV validation still needs your export (see `docs/CSV_VALIDATION.md`)  
- Next exact task: Run real CSV checklist **or** pick P2 (LLM polish vs landing)  

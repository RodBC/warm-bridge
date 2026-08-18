# CURRENT context — Warm Bridge

> **AIs: read this fully before coding. Update this file before you end a session with meaningful changes.**

**Last updated:** 2026-08-18  
**Repo:** `/home/decastro/studies/warm-bridge` (own git → `origin` github.com/RodBC/warm-bridge)  
**Sibling SaaS:** `/home/decastro/studies/career-fit` (same AI-context discipline; different JTBD)  
**Inspiration (patterns only):** `/home/decastro/entrep` identity resolution + Pulse “show the proof”

## Goal

Ship a profitable SaaS that turns a seller’s **user-owned network** + a **decision-maker target** into **ranked bridges + approach scripts**, without burning relationships or scraping LinkedIn.

Loop:

`target → bridges in your graph → path proof + why → ask mode → you send`

## What exists now

- Playbook: `playbook/bridge-types.yaml`, `modes.yaml`, `approach-rules.md`, `structure.md`  
- Core Python: import / resolve / paths / explain / approach  
- API: FastAPI on `:8788` (`warm-bridge serve`)  
- UI: Vite React on `:5174` (`web/`) — Rede → Alvo → Pontes → Pedir  
- CLI: `find`, `approach`, `import`, `eval`, `profile`, `serve`  
- AI contract: `AGENTS.md`, `.cursor/rules/`, `.cursor/skills/`, this context system  
- Samples: `corpus/examples/linkedin-connections-sample.csv`, phone CSV, ask patterns  

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

## Active priorities (P0 → P2)

1. **P0** Keep context/skills discipline as default agent behavior  
2. **P0** Validate ranking with a **real** Connections/phone export (parents / field seller)  
3. **P1** Strength tutoring UX (“posso pedir intro pra essa pessoa?”)  
4. **P1** Account / multi-target workspace (several buyers at one company)  
5. **P1** Persist network in browser session / local file without YAML friction  
6. **P2** Optional LLM polish behind `playbook/approach-rules.md`  
7. **P2** Outcome logging (did the bridge reply / intro land?)  
8. **Later** Team territory graph; CRM export of “who to approach”

## Open questions

- Exact Pro price ($29–49 draft)  
- Whether Team (parents co-selling) ships before LLM polish  
- vCard / Google Contacts adapter priority vs LinkedIn CSV alone  
- Cross-link / shared auth with Career Fit later?

## Ideas captured (not yet scoped)

- Favor-bank / cooldown after asking a bridge  
- Pulse-style weekly email: “3 accounts with new warm paths”  
- Healthtech analogy landing page: sell the *path*, not the feature list  

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

- Date: 2026-08-18  
- Done: Decisive README/PRODUCT/AGENTS; cursor rules+skills; docs/context system; sources.yaml; entrep-transfer notes; logged prior wedge (import/resolve/API/UI) into durable context  
- Blocked: none  
- Next exact task: Run real-CSV validation (import one seller network → one real target → judge if #1 bridge matches human instinct)  

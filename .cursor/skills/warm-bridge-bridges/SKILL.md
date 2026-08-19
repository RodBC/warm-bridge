---
name: warm-bridge-bridges
description: >-
  Implements bridge scoring, identity resolution, explainability, and approach
  drafts. Use when editing playbook, paths/resolve/explain/approach code, evals,
  or ask templates. Triggers: bridge, path, score, approach, intro, WhatsApp,
  confidence, resolve.
---

# Warm Bridge — bridges skill

## Rules of craft

Follow `playbook/approach-rules.md`, `structure.md`, `bridge-types.yaml`, `modes.yaml`.

- User-owned graph only — never invent mutuals  
- Strength gates the ask (low → permission/intel; high → intro)  
- One ask per message; include an easy out  
- Path proof + why bullets > fake % scores  
- Direct target ≠ bridge ask (separate buckets)

## Code path

1. `imports` — normalize CSV/paste → contacts  
2. `resolve.resolve_target` — CONFIRMED / LIKELY / NOT_IN_GRAPH  
3. `paths.find_bridges` — deterministic scores  
4. `explain.enrich_ranked` — confidence, path_label, why  
5. `approach.build_approach` — mode templates  
6. Optional LLM only via `prompts/approach_polish.md` + approach-rules  

Account map (N targets, one company): `accounts.find_account` → loops `build_find_result` — do not fork scoring in UI.

Reach / outcomes (NET memory foundation): `outcomes.normalize_event` + `web/src/outcomes.ts` — allowed statuses only; auto-log `copied` on Copiar/WhatsApp; user chips for Enviei / Respondeu / Intro feita / Sem resposta. Do not invent replies. API `POST /api/outcomes` validates/echoes; browser is source of truth.

Full ownership map: `docs/AI_BUILD_MAP.md` §4. Tutoring: `tutor.py` → attached in `enrich_ranked`.

## Evals

Run `warm-bridge eval` after changing weights, signals, mode selection, or outcome status schema.

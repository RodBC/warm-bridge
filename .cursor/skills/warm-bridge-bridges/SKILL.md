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

## Evals

Run `warm-bridge eval` after changing weights, signals, or mode selection.

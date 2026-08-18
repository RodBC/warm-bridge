# Approach rules (anti–spam-through-friend)

Goal: **ask for a bridge without burning the relationship**.
Field sales get meetings via network; the product fails if every ask feels like using people.

## Hard rules

1. **User-owned graph only** — Rank contacts the seller imported. Do not invent mutuals, fake LinkedIn degrees, or scrape third-party graphs in the public core.
2. **Facts stay fixed** — Company, title, and notes come from the network file. Approach text may *reframe* why this bridge matters; it must not invent shared history.
3. **One ask per message** — Intro **or** intel **or** permission to name-drop. Stacking asks raises rejection.
4. **Bridge-type picks the template** — `same_company` ≠ `alumni`. Wrong template burns trust.
5. **Strength gates the ask** — `low` / `unknown` → soft intel or permission. `high` → clear intro ask.
6. **Make it easy to say yes** — Offer a 2–3 line blurb the bridge can forward. Never dump a pitch deck into WhatsApp.
7. **Tone matches channel** — PT WhatsApp for BR field sales; EN LinkedIn for global. Short. Spoken. No “I hope this message finds you well”.
8. **Protect the bridge** — Never pressure (“urgente”, “só depende de você”). Give an explicit out.
9. **Target clarity** — Name role + company + why *this* person, not “alguém de compras”.
10. **Human unevenness** — Real asks are slightly imperfect. Perfect symmetry + buzzwords reads as AI spam.

## Soft signals of “AI wrote this to use my friend”

Reject or regenerate if output has:

- Flattery paragraph about the bridge’s career
- Fabricated shared memories (“desde aquela feira em 2019…”) not in notes
- Multi-paragraph product pitch before the ask
- Guilt / urgency language
- Identical message to every bridge
- Claiming a closer relationship than `strength` allows

## Order of operations (performant path)

1. Normalize target (name / company / title).
2. Score contacts with `bridge-types.yaml` (deterministic).
3. Pick **approach mode** from type + strength (`ask_intro` / `ask_intel` / `ask_permission` / `peer_forward`).
4. Fill template from playbook + seller voice notes.
5. Only then optionally call an LLM for polish — with these rules in the system prompt.

This keeps the expensive part rare and reuses field IP as structured data.

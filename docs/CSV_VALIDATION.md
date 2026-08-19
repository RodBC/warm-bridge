# Real CSV validation checklist

**P0 human gate** — ranking quality vs instinct. Do **not** commit your export or any PII.

## Steps

1. Export **your** LinkedIn `Connections.csv` and/or phone contacts CSV (user-owned only).
2. Start API + UI: `warm-bridge serve` then `cd web && npm run dev`.
3. Paste/import into Rede (or CLI: `warm-bridge import --file …`).
4. Pick **one real target** (decision-maker you care about) and run Find / Conta.
5. Judge the top bridge: does #1 match your gut? Note misses (wrong person, missing mutual, strength too high/low).

## What to record (no PII in the repo)

In `docs/context/CURRENT.md` **Last session** or a daily log, write only:

- Import kind + approx contact count (e.g. “LinkedIn CSV ~420”)
- Whether top bridge felt right (yes / soft / no)
- One-line failure mode if wrong (e.g. “alumni ranked over same-company”)
- Locale / mode used (single vs account)

Never paste names, phones, or company lists into git.

## Pass criteria

- Top bridge is someone you would actually message for that target  
- Why bullets match facts in *your* notes/CSV (no invented mutuals)  
- Direct bucket separates “you already know the target” from intro asks  

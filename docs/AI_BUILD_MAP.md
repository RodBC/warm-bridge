# AI build map — how / where / why

> **Audience:** every AI agent touching this repo.  
> **Purpose:** durable memory of *what was built*, *which files own it*, and *why that shape* — so the next agent extends the right layer instead of inventing a parallel path.  
> **Read with:** [`docs/context/CURRENT.md`](context/CURRENT.md) (live state) → this file (code archaeology) → skill matching your task.

Chat is ephemeral. This map + `CURRENT.md` + daily logs are the handoff.

Sibling discipline (same pattern, different JTBD): `/home/decastro/studies/career-fit/docs/AI_BUILD_MAP.md`.

---

## 1. Commit ledger (oldest → newest)

History is short and intentional. Treat each commit as a **layer**, not a random dump.

| Commit | Title | Layer introduced | Why |
|--------|-------|------------------|-----|
| `fd74bf0` | `first commit` | *(noise)* | Placeholder README; ignore for product archaeology. |
| `21834a5` | `feat: scaffold Warm Bridge — target → ranked bridges → approach scripts` | **Core IP + CLI** | Mirror Career Fit SaaS posture: playbook IP, fictional examples, deterministic pathfinder CLI, optional LLM prompts, private network gitignored. Prove the wedge without API/UI. |
| `815efd3` | `feat: commercial wedge — import, resolve, API, and Vite UI` | **Distribution surface** | Bring Career Fit’s paste→rank→draft funnel + entrep-style identity resolution: LinkedIn/phone intake, path proof with confidence bands, FastAPI `:8788`, PT-first UI for WhatsApp asks. |
| `2091f51` | `docs: decisive README plus durable AI context system` | **Agent operating system** | Force every AI to read/write durable SaaS state (`AGENTS.md`, `CURRENT.md`, skills, source tiers). Stop chat-only memory. |
| `51040e9` | `docs: point ARCHITECTURE at the AI context loop` | **Doc glue** | Make ARCHITECTURE point agents at CURRENT/AGENTS so systems work doesn’t skip memory. |
| `4d52cf2` | `docs: lock ecosystem NET vision into product planning` | **North-star expansion** | Capture long arc (reach tracker, spider-web, opportunity radar, friendly UX) while keeping wedge-first sequence explicit. |
| `821f3a2` | `docs: sequence NET long-arc in AGENTS north star` | **Contract alignment** | Put NET sequencing in AGENTS so agents don’t build radar/graph ahead of the wedge. |
| `4c4f8f9` | `feat: send-ready workspace and account multi-target map` | **Wedge UX + account map** | Strength tutoring, localStorage session, ask dock, `accounts.py` + `/api/find-account` — one commit (files were entangled). |
| `c12b62c` | `feat: outcome / reach logging` | **NET memory foundation** | Browser-first reach history + status chips; thin `POST /api/outcomes` validate/echo; no server PII store. |
| `68f3bdd` | `feat: LinkedIn-first session intake and Career Fit OTP bootstrap` | **Primary graph + auto login** | Camoufox `linkedin_session` primary; CSV legacy; burner state machine port; IMAP App Password OTP; research insight; Mapear UI; secrets gitignored. |

**Invariant across layers:** session-observed graph (Camoufox primary; CSV demoted) · deterministic score → explain → template ask · you send · never invent mutuals · no fake `% fit` · direct ≠ bridge buckets.

When you add a meaningful feature, **extend this ledger** in the same table (one row, commit hash after push if known).

---

## 2. Layer cake (dependency direction)

```
playbook/ + profile/ + corpus/ + prompts/     ← IP & rules (edit carefully)
        ↓
src/warm_bridge/{models,paths,approach}      ← score + draft path
        ↓
src/warm_bridge/{linkedin_session,imports,resolve,explain,tutor,accounts,outcomes}  ← Camoufox session/CSV ingest + identity + proof + tutoring + account map + reach schema
        ↓
src/warm_bridge/{cli,api}                    ← entrypoints (same core)
        ↓
web/                                         ← UX only; calls API
        ↓
docs/ + AGENTS.md + .cursor/                 ← product memory & agent contract
```

**Rule:** never put scoring, mode selection, or ask templates in the UI. UI calls API; API calls core; core reads playbook/profile.

---

## 3. Directory map — where things live

| Path | Owns | Why it exists | Do not |
|------|------|---------------|--------|
| `playbook/bridge-types.yaml` | Bridge taxonomy + base scores + signals | Deterministic ranking vocabulary | Invent types without eval cases |
| `playbook/modes.yaml` | Ask modes gated by strength/type | Strength → ask hardness | Skip gates and always `ask_intro` |
| `playbook/approach-rules.md` | Anti-spam-through-friend craft | Constrains drafts + future LLM polish | Bypass when “just generating” |
| `playbook/structure.md` | Message skeleton (greeting→out) | Keeps WhatsApp/DM shape stable | Free-form novel message shapes |
| `profile/schema.yaml` | Seller + network contract | Document expected fields | Untagged free prose as source of truth |
| `profile/example.seller.yaml` | Demo seller (Rodrigo / Lead Police) | UI/API default when no `data/` | Commit real PII beyond public LinkedIn URL |
| `profile/example.network.yaml` | Eval / Marina Acme graph | Stable eval fixture | Break evals by swapping for Lead Police case |
| `profile/example.lead-police.yaml` | UI demo graph → Sabrina | `/api/example-network`; fictional bridges | Treat demo edges as real mutuals |
| `profile/example.account.yaml` | Demo account (multi-target) | Account workspace default | Commit real account PII |
| `data/` | Local runtime network/seller YAML | gitignored user data | Commit `network.yaml` / `seller.yaml` |
| `corpus/examples/` | Anonymized ask samples + CSV samples | Teaching + eval grounding | Treat as live user data |
| `prompts/` | Optional LLM prompt shells | Polish later; not on critical path | Call LLM from core without approach-rules |
| `evals/cases.yaml` | Path/mode regression cases | Guard weight/signal/mode edits | Skip `warm-bridge eval` after scoring changes |
| `src/warm_bridge/` | All product logic | Single Python package | Duplicate logic in `web/` |
| `web/` | Vite React funnel | Human happy path Rede→Alvo→Pontes→Pedir | Business rules or scrapers |
| `docs/` | Product + architecture + this map | Durable decisions | Leave decisions only in chat |
| `docs/context/` | Live handoff (`CURRENT.md` + logs) | Multi-agent continuity | Delete historical log entries |
| `docs/sources.yaml` | Green/yellow/red intake tiers | Policy for every new adapter | Invent edges or mass-send (red) |
| `docs/LINKEDIN_SESSION.md` | Camoufox profile + burner OTP ops + mock | Session setup for optional map | Commit cookies / passwords / secrets |
| `docs/LINKEDIN_SELENIUM.md` | Deprecated pointer to LINKEDIN_SESSION | Legacy selenium backend note | — |
| `docs/entrep-transfer.md` | Steal/reject from entrep | Identity/Pulse patterns only | Fork scrapers or Streamlit UI |
| `.cursor/rules/` + `.cursor/skills/` | Always-on + task skills | Encode conventions agents must follow | Invent conflicting one-off rules |

Private PII stays in `data/` (gitignored) or the user’s machine — never in corpus or profile examples.

---

## 4. Python module map (`src/warm_bridge/`)

| Module | Responsibility | Key symbols | Why separate |
|--------|----------------|-------------|--------------|
| `models.py` | Shared types + YAML load + `ROOT` | `Target`, `RankedBridge`, `load_yaml` | One truth for CLI/API |
| `paths.py` | Deterministic bridge scoring + mode pick | `find_bridges`, `score_contact`, `_pick_mode` | Pure, fast, eval-friendly; playbook-driven |
| `approach.py` | Template asks (PT/EN) | `build_approach`, `approaches_for_ranked`, `TEMPLATES_PT` | Drafts only; user sends |
| `imports.py` | LinkedIn CSV / phone CSV / paste → contacts | `detect_and_parse`, `parse_*`, `merge_networks` | Fallback intake; Selenium is primary |
| `resolve.py` | Target vs graph identity | `resolve_target`, `Resolution` (CONFIRMED / LIKELY / NOT_IN_GRAPH) | Entrep audit pattern; never invent people |
| `explain.py` | Path proof + confidence bands + why | `enrich_ranked`, `confidence_band`, `path_label` | Pulse-style “show the proof”; no fake % |
| `tutor.py` | Strength tutoring (“posso pedir intro?”) | `strength_advice`, `attach_tutor` | Plain-language gates from strength+mode; never invent closeness |
| `linkedin.py` | LinkedIn URL parse / normalize | `linkedin_slug`, `resolve_target_fields` | Identity helpers only — **no fetch** |
| `linkedin_session/` | Camoufox session mutuals → contacts | `map_target`, `fetch_mutuals`, `mock`, `session_status`, `burner/` (Career Fit login state machine + IMAP OTP) | Thin yellow adapter; headless burner OTP; never invent mutuals |
| `research/` | Public web insight on target/company | `research_target`, `search_public` | Cited snippets; never invent people |
| `accounts.py` | Account workspace + `build_find_result` | `build_find_result`, `find_account`, `proof_line` | Optional `insight_pack` on asks |
| `outcomes.py` | Reach event validate/normalize | `ALLOWED_STATUSES`, `normalize_event`, `validate_events` | Schema for NET memory; never invent replies; no server persist yet |
| `cli.py` | argparse commands | `find`, `approach`, `import`, `linkedin-map`, `burner-login`, `session-login`, `eval`, `profile`, `serve` | Power-user + scripts |
| `api.py` | FastAPI on `:8788` | `/api/find`, `/api/linkedin-map`, … | Thin HTTP over the same functions as CLI |
| `__main__.py` | `python -m warm_bridge` | — | Package entry |

### Critical find path (do not fork)

```
network (YAML | import text | API body)
  + Target(name, company, title)
  → resolve.resolve_target          # audit: already in graph?
  → paths.find_bridges              # deterministic scores + mode
  → explain.enrich_ranked           # confidence, path_label, why, bucket, tutor
  → approach.approaches_for_ranked  # optional drafts attached by contact_id
```

Import path:

```
Selenium session → linkedin_session.map_target → contacts[] → build_find_result
raw CSV/paste → imports.detect_and_parse → contacts[] → (CLI writes data/network.yaml | API returns merged network)
```

### HTTP surface (`api.py`) — keep thin

| Method | Path | Core call |
|--------|------|-----------|
| GET | `/api/health` | liveness |
| GET | `/api/linkedin-session/status` | `session_status()` — optional Camoufox/Selenium |
| POST | `/api/research` | `research_target()` — public insight pack |
| POST | `/api/investigate` | find + research — **primary wedge** |
| GET | `/api/example-seller` | load `profile/example.seller.yaml` |
| GET | `/api/example-network` | load Lead Police **offline demo** (`example.lead-police.yaml` — real public LI profiles, labeled) |
| POST | `/api/import-network` | `detect_and_parse` + optional `merge_networks` |
| POST | `/api/resolve-target` | `resolve_target` |
| POST | `/api/find` | `build_find_result` |
| POST | `/api/linkedin-map` | `map_target` → enrich seller/target → `build_find_result` (**canonical board source**) |
| POST | `/api/find-account` | `find_account` (N targets, shared company) |
| GET | `/api/example-account` | load `profile/example.account.yaml` |
| POST | `/api/outcomes` | `validate_events` — echo only; client is source of truth |
| POST | `/api/upload-seller` | YAML validate → return seller (no server persist yet) |

CORS allows Vite `:5174` (and `:5173` sibling). Adding a new capability: implement in a core module first, then expose CLI + one API route + `web/src/api.ts` helper.

---

## 5. Web map (`web/`)

| File | Role | Why |
|------|------|-----|
| `src/theme.ts` | MUI theme (RWD tokens) | navy `#05072e`, blue `#007bc0`/`#00a3e0`, Noto Sans |
| `src/App.tsx` | Send-ready workspace (MUI) | AppBar + Casos + Sessão LinkedIn panel; demo offline + Mapear LinkedIn; RWD navy/blue |
| `src/SpiderBoard.tsx` | Investigation spider-web | Cork board, red yarn edges, person pins (CDN photo + title-company); LI button only if real URL |
| `src/avatar.ts` | Portraits for pins | CDN `avatar_url` → allowlisted unavatar → initials; `boardLinkedInHref` → null for fakes |
| `src/api.ts` | Typed fetch | `investigate`, `researchTarget`, `linkedInSessionStatus` |
| `src/storage.ts` | `localStorage` session v8 | Persist network/seller/target/account; bump clears fictional cast |
| `src/cases.ts` | Casos recentes (last 12) | Browser case memory; reopen target; no server PII |
| `src/outcomes.ts` | Reach history (last 20) + favor lookback | Browser-first NET memory; auto-log `copied`; status chips |
| `src/tutor.ts` | Client fallback + favor-bank | Mirrors server when API older; soft-blocks recent asks |
| `src/styles.css` | Board-only CSS | Investigation board yarn/pins; chrome is MUI theme |
| `vite.config.ts` | Dev server + API proxy | Proxies `/api` → `:8788` |
| `scripts/validate_board_pins.py` | Pin contract harness | Asserts real `/in/` URLs, title/company, CDN photos after map |

**UI status:** Send-ready wedge + **account workspace** + **reach history** + **Lead Police spider board** (cork + red yarn + person pins; actionable with list + ask dock).

**Buckets in UI:** `bridges` vs `direct` come from API enrichment — keep them visually separate (“você já conhece” ≠ “pedir intro”).

---

## 6. Docs & agent contract map

| Doc / asset | When to read | When to write |
|-------------|--------------|---------------|
| `AGENTS.md` | Every session | When operating contract changes |
| `docs/context/CURRENT.md` | Before non-trivial work | End of meaningful session |
| `docs/context/log/YYYY-MM-DD.md` | Optional history | Append after meaningful work |
| `docs/PRODUCT.md` | Scope / pricing / NET vision | Product decision or ecosystem phase shifts |
| `docs/ARCHITECTURE.md` | Build order & LinkedIn stance | Priority table changes |
| `docs/AI_BUILD_MAP.md` (this file) | Before editing code layout | After new modules/layers land |
| `docs/sources.yaml` | Any ingest/scrape idea | New source tier decisions |
| `docs/entrep-transfer.md` | “Can we steal from entrep?” | New steal/reject rows |
| `.cursor/skills/warm-bridge-*` | Task-matched skill | New durable convention |

### Skills → code ownership

| Skill | Edit these first |
|-------|------------------|
| `warm-bridge-bridges` | `playbook/*`, `paths.py`, `resolve.py`, `explain.py`, `tutor.py`, `approach.py`, `outcomes.py`, `evals/`, `prompts/` |
| `warm-bridge-sources` | `linkedin_session/*`, `imports.py`, `docs/sources.yaml`, `docs/LINKEDIN_SESSION.md` |
| `warm-bridge-product` | `PRODUCT.md`, `ARCHITECTURE.md`, `CURRENT.md`, `accounts.py` for account scope — not random features |
| `warm-bridge-context` | `CURRENT.md` + daily log (+ this map when layers change) |

---

## 7. Where to change what (cheat sheet)

| User-facing need | Edit here | Not here |
|------------------|-----------|----------|
| New bridge type / weight | `playbook/bridge-types.yaml` + `paths.py` signals + `evals/cases.yaml` | Hardcoded strings in UI |
| Mode gating (intro vs permission) | `playbook/modes.yaml` + `paths._pick_mode` | Always escalate to intro |
| Ask wording / anti-spam craft | `playbook/approach-rules.md` + `approach.py` templates | Unconstrained LLM prompt only |
| LinkedIn / phone / paste parse | `imports.py` (+ `docs/sources.yaml` row) — fallback only | Parallel scoring path |
| Public web insight | `research/` → `/api/research` + `/api/investigate` + Insights UI | Inventing people from search hits |
| Target already-in-graph detection | `resolve.py` | Inventing contacts outside import/session |
| Path proof / confidence / why copy | `explain.py` (+ API `_proof_line`) | Fake “87% fit” meters |
| New API capability | core module → `api.py` → `web/src/api.ts` → `App.tsx` | UI-only duplicate of Python logic |
| Strength tutoring UX | `tutor.py` + `explain.enrich_ranked` + `web/src/tutor.ts` + ask dock in `App.tsx` | Invent closeness in UI copy |
| Multi-target account workspace | `accounts.py` → `/api/find-account` → `App.tsx` account mode + `storage.ts` v2 | Separate scoring per target in UI |
| Reach / outcome tracker (NET memory) | `outcomes.py` + `web/src/outcomes.ts` + `web/src/cases.ts` + ask-dock chips + Histórico; `POST /api/outcomes` validate only | Inventing replies; server PII DB this phase |
| LinkedIn session readiness | `linkedin_session/session_status.py` → `GET /api/linkedin-session/status` + Briefing panel + `scripts/setup_camoufox_profile.sh` | Treating Chrome setup as README-only |
| LinkedIn URL identity | `linkedin.py` + UI LinkedIn-first fields | Confusing with session scrape (that’s `linkedin_session`) |
| Opportunity radar / spider-web | `web/src/SpiderBoard.tsx` + `avatar.ts` (path graph now); radar suggestions still later | Pretty graph with no next action; inventing edges |
| vCard / Google Contacts | green adapter in `imports.py` when ready | Password scrape of Google |

---

## 8. Explicit non-builds (already decided)

Documented so agents stop re-proposing them:

1. Mass WhatsApp/DM send from our servers  
2. Inventing mutuals, shared history, or relationship strength not observed by session/import  
3. Fake precision UI (“87% fit”) — use confidence bands + why bullets  
4. Merging `direct` and `bridge` into one ranked list without labels  
5. ~~Spider-web / opportunity radar UI before reach/outcome memory exists~~ — path spider board shipped (Lead Police); opportunity *radar suggestions* still later  
6. Vector DB / embeddings before the user’s graph needs them  
7. Headless multi-account LinkedIn farms / credential stuffing  

Rationale lives in `ARCHITECTURE.md`, `PRODUCT.md`, `AGENTS.md`, and `docs/LINKEDIN_SELENIUM.md` (yellow session intake is intentional; fabrication and mass-send stay banned).

---

## 9. How to extend this map (mandatory for AIs)

After you add a **new module**, **new HTTP route**, **new NET-phase object**, or **new ingest backend**:

1. Add a row to §1 (commit ledger) and/or §4–5 tables.  
2. Update `docs/context/CURRENT.md` → What exists / Last session.  
3. Append `docs/context/log/YYYY-MM-DD.md`.  
4. If the convention is reusable, encode it in the matching `.cursor/skills/` file.

If you only polish copy inside an existing function, skip the ledger — still update CURRENT if priorities or behavior change.

---

## 10. Quick verification commands

```bash
warm-bridge eval              # path/mode regressions
warm-bridge serve             # API :8788
cd web && npm run dev         # UI :5174
# happy path: example network → target Marina Costa → proof line → copy ask
warm-bridge find \
  --target-name "Marina Costa" \
  --target-company "Acme Saúde" \
  --target-title "Diretora de Compras"
```

Do not claim a layer is “done” in CURRENT without these working for the paths you touched.

## Credentials — you paste, agent does everything

**You paste 3 things in chat. Agent writes gitignored secrets, warms session headless, starts dev. You only open the UI.**

### What to paste (credential gate)

1. **LinkedIn email** — use a Gmail that receives LinkedIn codes  
2. **LinkedIn password**  
3. **Gmail App Password** — 16 characters (**NOT** your normal Gmail password)

**How to get #3 (one minute):**  
Google Account → Security → 2-Step Verification (on) → App passwords → create one for “Mail” → copy the 16-char code.

Optional: **Your LinkedIn profile URL** (`linkedin.com/in/…`) — if omitted we infer from session after login.

### What the agent does (you do nothing)

1. Save `data/secrets/linkedin_account.yaml` (mode 600, never committed)  
2. Run `warm-bridge burner-login` — **headless** Camoufox + IMAP OTP (Career Fit state machine)  
3. Start / restart `scripts/dev.sh`  
4. You open only **http://127.0.0.1:5174** → paste target LinkedIn URL → **Mapear**

No Google Cloud OAuth. No Camoufox window. No LinkedIn tabs. No password fields in the UI.

### 2FA alternatives

| LinkedIn 2FA | Warm Bridge support | What to do |
|--------------|---------------------|------------|
| **Email OTP** (default) | Full — IMAP App Password polls Gmail | Paste the 3 fields above |
| **Authenticator app** | Supported | Add `totp_secret` to secrets yaml (or paste it in chat) |
| **SMS / phone** | Out of scope | LinkedIn → Settings → Sign in & security → two-step verification → switch to **email** or **authenticator** |

If bootstrap returns `SMS 2FA fora de escopo`, the account still uses phone 2FA — change it in LinkedIn settings, then re-run `burner-login`.

### Session config (profile path)

- Default profile: `data/camoufox_profile` (gitignored)  
- Optional: `data/linkedin_session.yaml` (from `.example`)  
- Debug headed browser: `WARM_BRIDGE_SESSION_HEADED=1`  
- Skip auto-boot on serve: `WARM_BRIDGE_SKIP_SESSION_BOOT=1`

### Ops commands

```bash
warm-bridge burner-login          # headless login + OTP → persist cookies
warm-bridge session-status        # readiness + logged_in_hint
bash scripts/dev.sh               # API + UI → http://127.0.0.1:5174
```

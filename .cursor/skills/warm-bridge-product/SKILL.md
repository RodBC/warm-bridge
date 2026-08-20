---
name: warm-bridge-product
description: >-
  Guards Warm Bridge SaaS scope, tiers, moat, and monetization. Use when debating
  features, pricing, scraping, roadmap order, or “should we build X”. Triggers:
  product, SaaS, roadmap, pricing, moat, scope, parents, field sales.
---

# Warm Bridge — product skill

## Aim

Profitable SaaS that sells **path leverage**: ranked warm bridges + human ask drafts grounded in **session-observed mutuals** + **cited public insight**.

## Decision test

Ship only if it improves at least one:

1. Time-to-first credible path proof  
2. Quality / reply rate of bridge asks  
3. Willingness to pay (Pro/Team)  
4. Retention (accounts, outcomes, territory)

## Moat order

1. Bridge playbook + anti-spam-through-friend craft  
2. Outcome data + Casos + favor-bank  
3. Public insight quality (cited hooks, not invented edges)  
4. Trust (no inventing mutuals; no mass-send)  
5. Network compounding (NET densifies with use)

## Default answers

- LinkedIn Camoufox session? **Primary** — Career Fit friction pattern; ban/ToS risk accepted for wedge.  
- Primary graph? **Session mutuals** via `POST /api/linkedin-map`.  
- CSV / phone / paste? **Legacy fallback only** (UI “Legado”).  
- Web search for insight? **Yes** — cited public snippets; never invent people.  
- Invent mutuals from search? **Never.**  
- Auto-send WhatsApp? **No**.  
- End-user password fields in UI/API? **No** — secrets file + agent paste only.  
- SMS OTP gateway? **No** — email OTP or authenticator only.  
- Demo fixture as default UX? **No** — eval/dev only.  
- Radar / monetizing before Mapear wedge? **No**.  

Read `docs/PRODUCT.md` + `docs/LINKEDIN_SESSION.md` before changing intake.  
Code: `linkedin_session/`, `research/`, `POST /api/linkedin-map`, `web/` Mapear.

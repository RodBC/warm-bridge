# Warm Bridge — Product

**One-liner:** The operating system for warm sales reach-out — find who in *your* network opens the door to the decision-maker, and how to ask without burning the bridge.

## Vision

Warm Bridge becomes the default **relationship operating system** for B2B/field commercials who already sell through people. Users import their graph once; the product continuously maps accounts → targets → bridges → asks, learns which paths convert, and **grows the net** so the base gets denser over time.

At scale this is not “AI that messages your friends.” It is:

- **Seller graph (NET)** — LinkedIn 1sts + phone trust + notes + edges that thicken with every touch  
- **Path engine** — bridges ranked with explainable why  
- **Ask factory** — intro / forward / intel / permission drafts that sound human  
- **Lead / DM tracker** — who you reached, who helped, what’s stuck, what to work up next  
- **Opportunity radar** — suggestions that make the spider-web *useful*, not decorative  
- **Friendly UI/UX** — graph + lists + next actions a non-technical rep can live in daily  

### Ecosystem arc (future NET)

**Phase today (wedge):** one target → best bridge → copy ask → you send.

**Phase next (memory):** keep score of decision-makers reached, bridges who actually open doors, asks pending, intros landed — a living pipeline, not a one-shot tool.

**Phase NET (spider web):** visualize and expand the edge graph — where your network is strong, where it’s thin, and **where to look for more points of contact** to enhance the base and work up leads.

The product keeps **suggesting the next move**, for example:

| Suggestion type | Example |
|-----------------|---------|
| Content leverage | LinkedIn posts/topics relevant to a target account or buyer persona (so warm touches aren’t only DMs) |
| Local proximity | People in the **same city** who can take a café / face-to-face — lower friction than cold remote |
| Setup helpers | Common friends / ex-colleagues who can **arrange** the meeting, not only introduce by text |
| Reach list | Prioritized people to contact this week (bridges + adjacent titles) |
| Area / territory | Who’s in your selling region that you underuse |
| Events | Meetups, congresses, association nights where your graph + targets overlap |
| Projects / accounts to watch | Companies and initiatives where the net is warming — keep an eye, don’t lose the thread |

**UX bar:** spider-web / edge-graph views must stay **user-friendly** — clear path proof, progressive disclosure (list first, graph when useful), mobile-ready for field WhatsApp workflows. Pretty graph with no next action is a fail.

Intake is **LinkedIn-first** (seller’s own Selenium session → observed mutuals). CSV/paste are demoted fallbacks. Suggestions enrich *how to use and grow* the graph; they do not license mass harvesting or inventing edges.

## Why this wins money

| Buyer pain | Our answer | Monetization hook |
|------------|------------|-------------------|
| Can’t get the decision-maker | Ranked warm paths from their own network | Paid seat when weekly accounts matter |
| Asking wrong / too hard burns contacts | Strength-gated ask modes + playbook | Quality of asks = upgrade |
| Healthtech-style “who to approach” is expensive | Same job, DIY graph, faster ROI | Underprice CRM intel for SMB/field |
| Tools burn accounts with reckless multi-account farms | Seller’s **own** session only; rate-limited; never invent mutuals | Trust differentiator |

## Tiers (draft)

### Free — Prove the path

- 1 seller profile  
- 1 network import  
- 5 path finds / month  
- Path proof + why + 1 ask draft  

**Purpose:** acquisition; let “melhor caminho” sell itself in one afternoon.

### Pro — $29–49/mo (TBD)

- Unlimited finds  
- Strength tutoring (“can I ask this person?”)  
- Multi-target per account / territory  
- Outcome logging (bridge replied? intro happened?)  
- Optional LLM polish behind approach-rules  
- **Roadmap into Pro:** reach tracker + weekly opportunity radar (local / events / setup helpers)

### Team — higher

- Shared territory graph (e.g. family/partners selling same book)  
- Private asks per rep  
- Manager view: which accounts lack bridges  
- Shared NET view: thin edges vs dense pockets in the territory  

## Moat (priority order)

1. **Bridge playbook + anti-spam-through-friend craft** (in repo)  
2. Outcome data (which bridge types convert) + **tracked DM/bridge history**  
3. Notes / strength tutoring + **suggestion quality** (café, events, setup helpers)  
4. Brand trust: seller’s own session only; no inventing edges; no mass-send  
5. **Network compounding** — the longer you use it, the denser and smarter your NET gets (hard to rip-and-replace)

## Exit criteria for current MVP

- User imports Connections.csv (or phone/paste) → **Investigar** → imported bridges + cited public insights  
- User copies WhatsApp/LinkedIn ask (optional public hook)  
- No LinkedIn login on happy path  
- Casos recentes survive refresh; favor-bank soft-blocks repeat asks on the same bridge  
- AI agents consistently update `docs/context/` and extend `docs/AI_BUILD_MAP.md` on new layers without being reminded twice  

## Explicit non-goals (6 months)

- Becoming a LinkedIn growth-hacking / mass-DM tool  
- Auto-sending messages on the user’s behalf  
- Competing with enterprise CRM graph vendors on scraped data  
- Inventing bridges from web search  
- Default UX requiring Selenium session or offline demo  

## Ideas backlog (not committed scope)

- Validate ranking with parents’ live LinkedIn session (north-star experiment)  
- Account workspace: many targets under one company *(shipped)*  
- Favor-bank / “last ask” cooldown per bridge *(v0 shipped — browser outcomes)*  
- Sibling cross-sell with Career Fit (candidate warm paths ↔ seller warm paths)  
- **NET UI:** spider-web / edge graph with filters (city, company, strength, last touch) *(path board shipped; radar suggestions later)*  
- Decision-maker CRM-lite: status (not contacted / asked bridge / intro’d / meeting / won-lost)  
- Suggestion engine v0: same-city café candidates; ex-colleague setup helpers; event overlaps  
- Content assists: topic prompts for LinkedIn posts tied to open accounts  
- “Where the net is thin” — gaps to fill with intentional new contacts (still user-initiated adds)   
- CSV Connections import as optional fallback (demoted; not default UX) 

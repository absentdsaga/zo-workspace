---
name: vurt-clipper-recruitment
description: VURT clipper recruitment protocol. Use when planning, recruiting, or operating VURT's paid clipper program — outreach to Clipping Culture / Clip Ship, Whop campaign launch, fan-edit account DM campaigns, rate card design, anti-fraud guardrails, brief writing. Pairs with vurt-cd for the creative brief and vurt-captions for source-clip assets.
type: ops
metadata:
  author: dioni.zo.computer
compatibility: Created for Zo Computer
---
# VURT Clipper Recruitment Protocol

This skill exists because VURT is the first major vertical-drama brand with the catalog control and AVOD alignment to run an open clipper program — and the lane is open. ReelShort, DramaBox, ShortMax, NetShort, GoodShort don't run open clipper bounties. DramaPops launched theirs in March 2026 (small/mid-tier). The infrastructure (Whop, Discord, Clipping Culture, Clip Ship) is mature; we plug in, we don't build.

## When to load this skill

- Anyone asks about clippers, clipping programs, Whop, paid-creator distribution, fan-edit recruitment for VURT
- Outreach to Clipping Culture, The Clip Ship, Clouted, or any clipping agency
- Drafting a clipper brief, rate card, or program rules
- Setting up the VURT Clipper Discord
- Building / DMing the BookTok / DramaTok / ReelShort fan-edit list
- Designing anti-fraud guardrails or measurement framework
- Compensation / KPI / attribution decisions for clipper payouts

## Pre-flight (every time)

1. **Read** `references/trade-secrets-summary.md` — daily-load synthesis of the four deep-research refs. Top 10 trade secrets, what to copy from Fixated, industry benchmark bands, forbidden moves. Load this every conversation.
2. **Read** `references/research-findings.md` — full operational research on MrBeast/Vyro, Whop, Clipping Culture, N3on/Adin Ross, Tate, vertical-drama competitor analysis. Don't generalize from training data; the field moves quarterly.
3. **Read** `Documents/VURT-Clipper-Recruitment-Strategy.md` — the strategy doc that anchors all tactical work.
4. **Check budget assumptions** — per `feedback_pitch_strategy_levers` memory rule, never plug in dollar amounts unless Dioni has explicitly set them. Present rate cards as frameworks with industry benchmarks; let Dioni decide actual numbers.
5. **Check the active-titles list** in `Skills/vurt-social-tracker/state.md` — only clippable shows go into a brief.

### Deep-research refs (load on demand — don't rebuild)

- `references/fixated-and-trade-secrets.md` — Fixated profile (founders, $63M Eldridge raise, Internet Hall of Fame moat), CHOF Discord (4,229 verified), white-glove second server (~100), 14 founder quotes, adjacent 4K-scale operator scan
- `references/bot-stack-trade-secrets.md` — Sx Bot/Clipify documented features vs operator-configured logic, view-tracking infra (TikTok oEmbed, IG embed JSON, Phyllo OAuth), payout rails (Whop, Stripe Connect, Tipalti, USDC), 1099/IRS reality, anti-fraud at scale (cap-pegging detection pseudo-code), recommended VURT bot stack
- `references/discord-architecture-trade-secrets.md` — channel architecture, tier/role progression with metrics, onboarding gate stack, vault/drop mechanic, raid/stagger systems, captain hierarchy, retention kill list, public examples (Spade 26,925 verified May 2026, Clipping Club 3,418 verified), VURT Discord blueprint
- `references/sourcing-retention-trade-secrets.md` — recruiting funnel at 4K scale, vetting at the door, first-week retention (Vyro first-3-pay hack), 30/90/365-day retention, captain ratios, splinter-Discord risk, geography play, cultural framing, VURT 0→500→2,000 milestone plan

## Phase 1 — Strategic positioning

When Dioni or Mark asks anything strategic ("should we do this?", "is the lane really empty?", "what comp rate?", "which agency?"), the answer must be grounded in:

- **The lane is empty at the top tier** — confirmed via search of @reelshortapp, @dramaboxshorts, @shortmaxapp, @netshortdramas TikTok ecosystems and Whop search. Only DramaPops Drama Lab is running open clipping in vertical drama, since March 2026.
- **The infrastructure is mature** — Whop processed 3.5B+ clipped views, runs KYC + anti-fraud + 24-hour payout buffer. Don't reinvent.
- **The economics window is $1–$2 CPM** for VURT specifically. Below $0.50 = spam farms. Above $2 = crypto auction we can't win. Vyro's $3 CPM is reference, not target.

## Phase 2 — Tactical execution

### Outreach to Tier A partners
Use `templates/outreach-clipping-culture.md` and `templates/outreach-clip-ship.md`. These are vetted against entertainment-IP outreach norms (music labels and Netflix-tier briefs).

### Whop campaign listing
Use `templates/whop-listing-copy.md`. Mirror language style of Clipping Culture, Brez Clips, ClipHaus listings — punchy, clear rules, clear cap.

### Fan-edit DMs
Use `templates/dm-script-tiktok-fan-edits.md`. Targets: BookTok-romance edit accounts (5K–500K followers), ReelShort/DramaBox actor fan-edit accounts, FilmTok dialogue-edit creators. Keep DM under 80 words — these creators get pitched constantly, brevity wins.

### Master brief
Use `templates/clipper-brief-master.md`. Always includes: source-content pack URL, watermark spec, hashtag list, face-time minimum, length range, geo target, on-screen brand attribution rule (myvurt.com / @myvurt for ≥2s).

## Phase 3 — Anti-fraud + measurement

Mandatory guardrails listed in `references/anti-fraud-checklist.md`. Single most important: pay only on verified platform-native views with ≥30% average watch-through, pulled 14 days post-publish.

Measurement layers:
- **Pay metric** = qualified views (CPM + watch-% floor)
- **Promotion metric** = UTM-tagged myvurt.com clicks per clipper (used to promote Tier 2 → Tier 1 → Tier 3)
- **Brand health metric** = comment sentiment + share rate per clip (separate dashboard, not tied to pay)

## Phase 4 — Operational rhythm

- **Weekly:** Pull view data, post leaderboard in Discord, approve next round of submissions
- **Bi-weekly:** Rate card review — adjust if average CPM-cost-per-clipper-recruited drifts off target
- **Monthly:** Promote top 5 Tier 1 → Tier 3 (Brand Ambassador). Pay leaderboard bonus. Refresh source-pack with new episodes.

## Forbidden moves

- **Don't run an affiliate-paywall pyramid** (Hustlers University pattern). Coordinated-takedown risk on TikTok/Meta is real and increasing.
- **Don't pay on clicks/signups** as the primary metric. We're AVOD. Views are the revenue event.
- **Don't allow bare reposts of VURT-cut social clips.** Clippers must add edit value.
- **Don't promise rev-share.** Attribution at clip scale is impossible without pixels we don't control. Whop campaigns have proven this fails.
- **Don't pre-fill dollar amounts in any external doc** — rate cards go to Dioni as frameworks; she sets the numbers.

## Subagent guidance

When research is needed:
- For platform-by-platform comp data → spawn general-purpose agent with prompt scoped to "real 2026 numbers from Whop/Vyro/Discord clipping ecosystems, with sources"
- For competitor intel on a specific vertical-drama brand → spawn agent with explicit instruction to check actual TikTok handles, Whop search, and the brand's "Business Cooperation" / "Partners" page
- For fan-edit account discovery → use TikTok hashtag scraping if available, otherwise hand-build CRM

### Operational subagent roles (spawn as general-purpose with these scoped prompts)

**campaign-ops** — when launching or auditing a clipper campaign
> "You are the VURT clipper-program campaign ops lead. Read `Skills/vurt-clipper-recruitment/references/trade-secrets-summary.md` and `discord-architecture-trade-secrets.md` first. Validate the brief against: source-pack URL, watermark spec, hashtag list, face-time minimum, length range, geo gate (US/CA/UK/AU/NZ), `myvurt.com`/`@myvurt` ≥2s overlay, anti-fraud guardrails, no spoiler beats. Output: pass/fail per item + concrete fixes. Never plug in dollar amounts — flag them as Dioni-set."

**fraud-watch** — when reviewing a cohort's submissions or weekly view data
> "You are the VURT clipper anti-fraud auditor. Read `references/anti-fraud-checklist.md` and the cap-pegging detection pseudo-code in `references/bot-stack-trade-secrets.md` §6. Inspect the submitted view data for: cap-pegged view counts, sub-5-min-from-drop submissions, identical filename/metadata signatures across accounts, datacenter/VPN ASN flags, watch-through <30%, geo mismatch. Output: per-clipper pass/flag/kill recommendation + StreamAlive-pattern check on the cohort as a whole."

**captain-coach** — when designing or auditing the captain layer
> "You are the VURT captain-program designer. Read `sourcing-retention-trade-secrets.md` §6 and `discord-architecture-trade-secrets.md` §6. Validate the captain ladder against: 1:50 active-clipper ratio, 10% override capped per-recruit (not uncapped), platform-bound commission (not captain-bound), founder-direct DM access for Tier 3 to block splinter risk, NDA-light non-poach. Output: structural risks + concrete fixes. Frame compensation as benchmark bands, never plug in numbers."

## Pre-ship rubric

Before any clipper outreach goes external:
- [ ] Brief specifies show, source URL, length, face-time, hashtag, watermark, geo, attribution overlay
- [ ] Rate card uses framework language (industry benchmark X, VURT pays Y) — not pre-filled assumptions
- [ ] Anti-fraud guardrails are listed in the brief, not just internal docs
- [ ] No spoilers in the source pack (no finale-beat clips for active titles)
- [ ] vurt-cd voice rules respected on any external-facing copy (no forbidden phrases, no library-genre tagging)
- [ ] Dioni has signed off on spend ceiling for the period

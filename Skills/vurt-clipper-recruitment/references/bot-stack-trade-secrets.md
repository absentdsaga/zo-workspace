# Clipper Bot Stack — Trade-Secret Layer

**Compiled:** 2026-05-10 · **Scope:** advanced configuration, tooling, anti-fraud, payouts, and compliance for 1K–10K-clipper Discord operations. **Pairs with** `references/research-findings.md` (which covers economics, competitor scan, and recruiting tactics) and `references/anti-fraud-checklist.md`.

> **Methods note.** ~80% of source material is documented (vendor docs, ToS pages, agency blog posts, Whop help center). ~20% is reported in operator/community forums and Discord chatter — labeled `RUMORED` where applicable. Quoted text is verbatim from the cited URL on the cited date. Where a feature is *missing* from public docs but routinely surfaced in tutorials/community channels (e.g., multipliers, captain roles), it is labeled `OPERATOR-CONFIGURED` — the bot doesn't ship it; agencies build it on top using Discord-native role automation.

---

## 1. Sx Bot / Clipify advanced features

### 1.1 What ships in the box (documented)

Source: docs.sxbot.io/clipify/* (May 10 2026). Quotes are verbatim.

**Submission stack**
- "Account Verification — Easily link and verify social accounts for seamless tracking" — clippers must connect TikTok and/or Twitter/X (and per the homepage, **YouTube Shorts and Instagram Reels**, though docs lag the homepage).
- "Clip Management — Submit clips, track their performance, and manage your content effortlessly."
- "Real-Time Analytics — Monitor clip views with frequent updates throughout the day" / "Clip views update multiple times a day."
- "Detailed Logs & Tracking" — public posts channel, private staff log, registration log.

**Payout stack**
- "Payout Tracking — Users can add payment details for managers to process payments."
- "Custom Payout Structures — Set a max budget, define payout rates per platform (e.g., $10 per 100,000 TikTok views, $15 per 150,000 Twitter views)."
- "Submission Locking — Automatically stop new submissions when the budget cycle is met."
- Per the Clipify→Whop alternative page: "PPV (Pay Per View) or CPM (Cost Per Mille) models. Only pay for real results" and "Same-day via PayPal or Crypto (USDT, USDC)" with creator-claimed rates "$0.50–$4.00 per 1,000 views." (Source: docs.sxbot.io/clipify-the-1-whop-alternative-for-clipping-campaigns)
- Self-claim of scale: "10K+ active clippers" / "3B+ views generated" / "$250K+ paid in last 60 days" (community/Discord, May 2026).

**Anti-fraud stack (claimed, not specified)**
- "Advanced bot detection ensures you only pay for verified, organic views." No mechanism, threshold, or detection signature is published. The Sx Bot / Clipify docs do **not** disclose:
  - Geo gating
  - Watch-time minimums
  - Watermark verification
  - View-count delay/buffer (the Whop-style 24-hr post-approval scrub)

**Discord plumbing (default install)**
- Recommended channels per setup guide: `#register`, `#commands`, `#rules`, `#announcements`, plus a submission channel (operator-named).
- A "Clippers" role for registered users.
- The `/clip` command grabs N minutes of a Twitch/Kick stream (legacy Sx-Bot feature, not core to brand-clipping campaigns).

### 1.2 What's *not* in the box but operators bolt on (`OPERATOR-CONFIGURED`)

Mined from sxbot.io tutorial pages, community Discord (discord.gg/clipify), and tutorials on top.gg / discord.bots.gg / disboard. **None of the following are native Clipify features**; operators build them with Carl-bot/MEE6/Whop-bot stacked alongside Clipify.

| Feature | How operators build it | Evidence |
|---|---|---|
| **Tier-gated submissions** | Carl-bot reaction roles tied to view-history milestones; manual mod toggling. Not auto-progression. | docs.sxbot.io/clipify/how-to-find-and-hire-the-best-clippers references "10,000 verified short-form clippers" but does not describe a verification pipeline. |
| **CPM multipliers** | Per-clipper override field in Clipify's payout config (`$10 per 100K` is bot default; mods set higher rate for trusted clippers manually). | Clipify docs say "Custom Payout Structures — Set a max budget, define payout rates per platform." No multiplier object is documented. |
| **Captain / leaderboard captain role** | Manual Discord role + Carl-bot pinned-message rotation. Sx Bot's leaderboard exposes ranking but does **not** automate captain promotion. | Doc says "Leaderboards & Stats — Compete with others and track progress." That is the full feature. |
| **Auto-DM onboarding** | Carl-bot or MEE6 welcome-DM; Whop bot if running through Whop. Clipify itself has no DM module. | Not in docs. |
| **Geo gating** | **Not enforced by Clipify.** Operators set it in the brief and hope. Whop is the only platform in this category that gates payouts geographically (and even that is loose — VPN circumvention common, see §5). | No geo field in any Clipify config doc. |
| **Watch-time minimums** | Not supported. Pay is per-view, not per-watch-second. | None of TikTok/IG/YT public APIs expose watch-time at clip granularity to third-party bots. |
| **Watermark verification** | Manual mod review. Some agencies use a custom Python bot that downloads the clip and checks for a logo via OpenCV / CLIP image-classifier. Not commodity. | No vendor offers this as a feature. RUMORED in the Clipping Culture community Discord. |

### 1.3 Pricing (Sx Bot / Clipify)

- **Sx Bot Premium:** "$3.99/month" or "$29.99/year" (sxbot.io/premium, May 2026). Premium unlocks unlimited streamer notifications, faster notifications, automatic live role, unlimited reaction roles, premium logging, and an exclusive role.
- **Clipify itself:** "Premium subscription required — DM PKASH in support server for pricing" (multiple docs pages). No public price card. Operator reports indicate **~$40–$100/month** for the campaign tier with one active campaign (RUMORED, Whop community Discord).

---

## 2. Competing bots and platforms

### 2.1 Whop (the marketplace + bot, not just one or the other)

**Whop is the dominant infrastructure** — most clipper Discords run a Whop bot to handle access-gating, payouts, KYC, and a Whop-listed campaign that the bot syncs to roles. Documented behavior:

- **Fee:** "Whop will deduct from the Seller's Whop account a fee payable to Whop in the amount of 10% of all amounts paid from Seller to Participants" (whop.com/content-rewards-terms-of-service, accessed May 10 2026).
- **View tracking:** "Rates based on the volume of views achieved by a social media post are calculated based on the *legitimate* views a Deliverable achieves as determined by Whop in its sole discretion." Bot/scripted views excluded.
- **Anti-fraud:** 24-hour payout buffer; lifetime ban for confirmed botters; "smarter anti-botting algorithm... detect view botting after a submission is approved" with "fewer false positives" (whop.com/blog/new-on-whop, May 2026).
- **Supported clipper platforms:** TikTok, YouTube Shorts, Instagram Reels, X (per content-rewards docs).
- **Payout methods:** ACH, PayPal, Bitcoin, stablecoins (USDC), Venmo, Cash App, traditional wires, local bank rails in 170+ countries (whop.com/blog/getting-paid-on-whop). Speed: 1–4 business days with payout fees ranging "$2.50 for next-day ACH to 5% + $1 for instant crypto or Venmo withdrawals" (ecommercefastlane.com on Whop Payments).
- **KYC:** "government ID, facial scan, and bank account connection" — verification "can take 24 to 72 hours" (reach.cat/blog/whop-clipping-hidden-fees).

**Hidden cost stack (per reach.cat, May 2026):** "You earned $1,000 in views. You received $612.50. That is a 38.75% total fee load." Breakdown:
- 10% Whop platform fee
- 2.9% + $0.30 per Stripe payout
- 1–3% currency conversion if non-US
- 20–50% agency markup if going through a clipping agency on Whop

**Minimum payout thresholds enforced by agencies:** "$50 or $100 before you can withdraw" — sub-threshold balances stranded.

### 2.2 Reach.cat — Whop's most credible competitor

Source: reach.cat homepage + blog (May 2026).

- "10,000+ clippers" claimed, code-based bio verification (no government ID required).
- View tracking: "automatic, hourly refresh" across TikTok, Reels, YouTube Shorts, X.
- Payout: "weekly via USDT or bank transfer."
- Brand fee: "10% flat fee" (vs Whop's stacked 38.75%).
- Brand CPM range: "$1–$6" verified.

### 2.3 Vyro (MrBeast)

- ~$3 per 1K views, no audience requirement, multi-platform tracking (TikTok + Reels + Shorts combined).
- Payout via Stripe and PayPal (clipaffiliates blog, May 2026).
- Application-based gating; KYC handled by Stripe Connect.

### 2.4 Promote.fun

- $0.20–$2.25 per 1K views (Ssemble, May 2026). Launched 2025. Brand-side campaign listing similar to Vyro. View-tracking method not publicly documented.

### 2.5 Clipping.io

- $1–$3 per 1K views, platform tracking, application-based.

### 2.6 ClipAffiliates

- $1–$5 CPM (brand sets), "0% (free)" for clippers, views verified via platform APIs.

### 2.7 Smaller / open-source

- **Clippy** (top.gg) — YouTube clip recorder, not a campaign bot.
- **Proxtx/clipper** (GitHub) — Discord voice-chat 30-second clip recorder, no campaign logic.
- **OdielDomanie/clipper-bot** (GitHub) — posts livestream clips, not for paid campaigns.
- **LachlanDev/TikTok-Utilities** (GitHub) — pulls public TikTok user info, used by some operators as a *cross-check* tool against Clipify reports.

**Bottom line on bot-vendor choice:** for VURT's scale (~4K clippers), there are exactly **two viable infrastructure layers:** Whop (richest payout + KYC, highest fee load) or a stack of `Sx Bot + Clipify + Reach.cat campaign listing` (lower fee, weaker KYC, operator carries more compliance load).

---

## 3. View-tracking trade secrets — verifying without screenshots

The screenshot problem is real: TikTok/IG/YT all let users hit "share" on a video that doesn't belong to them, screenshot any number, and forge submissions. Every serious operator has moved off screenshots. Here's how:

### 3.1 What Whop / Sx Bot / Reach.cat actually use under the hood

- **TikTok:** the public Embed JSON endpoint (`https://www.tiktok.com/oembed?url=...`) returns view + like + comment counts for any public video without auth. Most clipper bots poll this every 1–6 hours. It's *officially* a TikTok endpoint, but rate-limits aggressively.
- **Instagram Reels:** the "share/embed" oEmbed endpoint returns metrics for reels; a fallback is scraping the public profile JSON via the `__NEXT_DATA__` payload. This breaks every few months when Meta changes the page shell.
- **YouTube Shorts:** the official Data API v3 (`videos.list?part=statistics`) is free (10K-units/day quota), returns view counts directly. No scraping needed.
- **X / Twitter:** since the API became paid in 2023, most ops scrape the public tweet HTML or pay for the basic API tier ($100/month, 10K reads).

The "API tracking + manual verification" line Whop publishes is exactly this stack — public oEmbed endpoints + light scraping + a human queue for edge cases (private accounts, deleted videos, view-count discrepancies).

### 3.2 Paid alternatives for cross-checking Whop's numbers

Operators who don't trust Whop's count run a parallel pipeline.

| Tool | Public price | What it gives you | Use for VURT? |
|---|---|---|---|
| **Modash** | Plans from "$199/month" (Essentials), "$499/month" (Performance); **API: $16,200/year** annual commitment (modash.io/pricing, May 2026) | Tracks 250M+ TikTokers, every public profile with 1K+ followers across TikTok/IG/YT. Content-tracking module pulls branded posts daily. | Yes for monitoring — overkill for payout verification at $200+/mo. |
| **Phyllo** | Sales-call gated; **no public price** | OAuth-based "Connect" flow — clipper authenticates and Phyllo pulls 100% accurate account-owned data (private analytics, watch-time, demos). Universal data gateway, 20+ platforms. | **Yes if budget allows.** Only public option that returns *creator-private* watch-time and audience-demo data — closes the bot-view problem definitively because the data is from the clipper's authenticated account, not scraped. |
| **Tagger** (Sprout Social) | Enterprise-only; public starting estimate $2K+/mo | Influencer discovery + content tracking. More marketing-focused than payout-grade. | No — overpriced for clipper verification. |
| **Influencity** | $198–$698/month (public tiers) | Smaller competitor to Modash. | Backup option only. |
| **HypeAuditor** | $399+/month | Audience-quality scoring, fake-follower detection. Useful for screening clippers *before* approval. | Yes for tier-1 captain vetting only. |

**RUMORED operator stack (Whop community Discord, May 2026):** mid-size agencies (~500–2K clippers) typically run *Modash for content monitoring + Phyllo for top-tier clipper verification + a custom Python scraper for daily TikTok view polling*. Larger agencies (5K+) build proprietary scrapers; this is the layer the bots-as-a-service vendors don't compete in.

### 3.3 Bot-view detection signatures (the ones operators actually look for)

Distilled from StreamAlive's post-mortem (peterclaridge.com), Whop fraud blog, and Clipping Culture community chatter:

1. **Cap-pegging:** clip lands at *exactly* the view count needed to hit max payout, then flatlines. Classic bot-farm signature. Auto-flag any clip whose 24-hr growth curve has a slope-break within ±2% of the cap threshold.
2. **Identical timing across multiple submissions** from the same account or referrer cluster — bot farms batch-process.
3. **Geo mismatch** — clip published from US clipper account, but TikTok analytics show 90%+ Vietnam/Indonesia/Brazil viewers. (Requires Phyllo or screen-record verification.)
4. **Rapid view burst with no engagement** — 50K views, <50 likes, <5 comments. Real TikTok audiences interact at ~3–5% engagement on viral clips.
5. **Recycled stock footage or re-cuts of previously banned clips** — image-hash check against a blacklist.
6. **New account + first submission + capped payout** — classic burner pattern. Hold first 3 submissions in a 72-hr review queue.

---

## 4. Payout automation — how money actually moves

### 4.1 The four real rails

| Rail | Mechanism | Cost | Pro | Con |
|---|---|---|---|---|
| **Whop payout** | Stripe Connect under the hood | 2.9% + $0.30 + $2.50–5% per withdrawal | One-stop KYC + 1099 + multi-rail | 10% Whop fee on top |
| **Stripe Connect direct** | Express or Custom accounts | 0.25% + $2/active account, plus standard payment fees | You own the relationship; Stripe issues 1099s natively (docs.stripe.com/connect/tax-reporting) | You own KYC liability; setup is engineering work |
| **PayPal Hyperwallet** | Mass-payout API | 2% + $0.25 per payout | 1099 filing for US contractors; international support | PayPal "freezes accounts receiving frequent small payments" (kiip.app, May 2026) |
| **USDC stablecoin** | Circle / Coinbase Commerce / direct chain | Network fee only ($0.01–$2) | Instant, global, no chargebacks, no PayPal-freeze risk | Clippers need wallets; "consumes 30–40% of onboarding time" (Kiip) |

### 4.2 1099 / IRS reality

- **Whop issues 1099-K for US sellers** "who hit the minimum gross receipts threshold for the year." Threshold for tax year 2025+ is **$20,000 AND 200 transactions** (whop help center, May 2026). For *contractors* (clippers as 1099-NEC recipients) the **$600 threshold** applies — agencies running their own payout (not through Whop) must issue 1099-NECs.
- **Stripe Connect:** "Stripe issues 1099-K forms for connected accounts where Stripe controls the pricing... For all other transactions where the platform controls the pricing, the platform is responsible for filing any relevant 1099 forms." So if VURT/agency sets the CPM rate, **VURT files the 1099s, not Stripe**.
- **PayPal:** issues 1099-K at IRS thresholds; Hyperwallet handles 1099 filing for US contractors meeting reporting thresholds.

### 4.3 What goes wrong (operator pain points, kiip.app + reach.cat May 2026)

- "PayPal freezes accounts receiving frequent small payments, crypto exchanges reject verification, and regional banking restrictions create constant disruptions."
- "KYC verification can take 24 to 72 hours" — clippers stall, churn.
- Sub-minimum balances ($40 stuck behind $50 minimum) — friction that reduces willingness to submit additional clips.
- PayPal label problem (`RUMORED`): clippers receiving $500+/mo across 20+ payments occasionally get accounts flagged as "unauthorized business activity" — PayPal asks for invoices/contracts. Mitigation: structure payouts as fewer-larger transactions, not many-small.

### 4.4 KYC layers VURT might add

Operators stacking on top of Whop typically run a **light second-layer KYC**:
- Bio-link verification: clipper posts a unique code to TikTok bio for 24 hours, bot scrapes and confirms.
- Selfie + ID match (Veriff or Persona or Onfido — $1.50–$3 per check). Reserved for Tier 2+ clippers earning >$200/month.
- Domestic-bank-only payout for US clippers above $600/yr (forces a hard 1099 trail).

---

## 5. Anti-fraud at scale — beyond Whop's 24-hour buffer

### 5.1 Device / browser fingerprinting

Tools clipper agencies layer in for high-suspicion submissions:

| Tool | Price | What it does |
|---|---|---|
| **IPQualityScore (IPQS)** | $299/month starter, per-query API | Bot detection, IP intelligence, fraud scoring. Scrapes the clipper's posting IP/UA via a referral pixel. |
| **FingerprintJS Pro** | $0.0008–$0.005 per identification | Browser fingerprinting; spots when the same device submits from multiple "different" clipper accounts. |
| **Sift** | Custom enterprise | ML-driven account-takeover and payment-fraud scoring. Used by larger agencies. |
| **Anura** | Custom enterprise | Bot/fraud detection; ad-tech focused but works for clipper traffic. |

**Practical use:** none of the bots above are integrated into Sx Bot / Clipify. Operators build a custom tracking-pixel landing page (via Discord bot DM) that runs FingerprintJS + IPQS scores, only release first payout if score < threshold. Adds **~$200–500/month** at 4K-clipper scale.

### 5.2 Cap-pegging auto-detection (the StreamAlive lesson)

The pattern: clip is approved → views surge to *exactly* the cap-needed number → flatline. No legitimate clip behaves this way.

**Detection rule operators code (RUMORED, Whop community):**
```
if (24h_growth_pct > 80 AND velocity_drop_within(cap_threshold ± 2%) AND engagement_ratio < 1.0%):
    flag_clip(state="suspect_bot_pegging")
    pause_payout()
    require_manual_review()
```
Whop's "smarter anti-botting algorithm" (their phrase) almost certainly runs a variant of this. The 24-hour buffer is the time window in which this curve becomes detectable — the buffer is how long it takes the bot pattern to express itself.

### 5.3 AI content review for re-cuts of blacklisted content

Approach used by Clipping Culture-tier agencies (RUMORED + inferred from their FAQ):
- **CLIP image hashing** (Hugging Face's openCLIP or PicDefense) — every approved clip is hashed; new submissions checked against blacklist (banned creators, copyrighted footage, prior fraud cases).
- **Content-moderation via Hive AI / AWS Rekognition / Sightengine** — flags re-cuts of copyrighted footage, unlicensed talking-head clips, AI-generated content.
- **Cost at 4K-clipper scale:** ~$300–800/month (Hive AI starts at $0.001/image; AWS Rekognition $1 per 1K images).

### 5.4 The bot-view detection signatures, codified

| Signature | Threshold | Action |
|---|---|---|
| Cap-pegging | View count lands within ±2% of cap, then 24-hr velocity drops > 80% | Hold payout, manual review |
| Geo mismatch | >40% views from a country incompatible with clipper's claimed origin (require Phyllo or screen-record) | Reject submission |
| Engagement floor | Like:view ratio < 0.5% on >10K-view clip | Hold for review |
| New-account burst | Account <30 days, first 3 clips, sum >50K views | Mandatory 72-hr review queue |
| Identical timing | Same submitter's clips track within ±5min of each other across days | Investigate |
| Recycled hash | CLIP image hash matches blacklist | Auto-reject |

---

## 6. Discord-specific operational tooling

### 6.1 Onboarding bot comparison

| Bot | Free tier | Premium | Best for clipper Discord |
|---|---|---|---|
| **Carl-bot** | Reaction roles unlimited, automod, suggestions, logging | $7.99/mo | **Recommended primary moderation bot.** Up to 250 roles per message; granular automod; tier-progression logic via reaction roles tied to manual milestones. |
| **MEE6** | Welcome messages, leveling | $11.95/mo | Use *only* for the leveling system if you're gamifying participation. Otherwise overlaps with Carl-bot. |
| **Wick** | Anti-nuke, anti-raid, captcha-verification gate | Premium adds advanced rules | **Recommended security bot.** "Anti-nuke system monitors for mass deletions, role changes, channel modifications" — single compromised mod can't drain server. Trusted by 837K+ servers. |
| **Dyno** | Basic automod, custom commands | $5/mo | Cheapest moderation; thinner feature set than Carl-bot. |
| **SfwBot** | Free + paid | AI image scanning ($X/mo) | Optional NSFW scan if clippers can post images. |

**Recommended onboarding gate flow for VURT:**
1. New member arrives → only sees `#rules` and `#verify`.
2. Wick captcha → human-verified.
3. React to rules → Carl-bot grants `Verified` role.
4. `Verified` unlocks `#start-here` with Whop join link / Clipify register button.
5. Clipify register success → bot grants `Clipper` role (auto via Clipify's webhook to Carl-bot if configured).
6. First approved clip → mod manually grants `Tier 1` role → unlocks `#submissions-tier-1` and `#tier-1-chat`.
7. 100K cumulative views → mod grants `Captain` role + 1.2x multiplier (manually configured in Clipify payout override).

### 6.2 Submission queue + multi-mod approval

Native Clipify only supports one approval level. For multi-mod approval flows:
- **Tickets bot** (Tickets.bot) or **TicketTool** — clippers open a ticket per submission; mods chain-approve before bot pays.
- **Carl-bot custom command** — `!approve @clipper $rate` only fires when 2+ mods react.

### 6.3 Leaderboard automation

- Clipify ships a passive leaderboard view.
- For **daily auto-post leaderboards**, operators write a Discord webhook scraper that pulls Clipify's leaderboard JSON and posts a top-10 message at 6 PM ET via Carl-bot scheduled message.
- Alternative: **Statbot** or **Tatsu** for engagement leaderboards (not view-count tied).

### 6.4 "Vault" / drop scheduling

There is no commodity bot for "auto-publish raw content packs at 6 PM ET so all clippers see at once." Operators implement this with:
- Carl-bot scheduled message (free, native).
- Or a custom script: cron job → uploads to Drive/Frame.io → posts a Discord message with the new link via webhook.
- Some agencies use **Hyrox** or **Sapphire bot** for scheduled content drops if they want richer formatting.

### 6.5 Server security (single-mod-compromise prevention)

- **Wick anti-nuke** is the standard. It "monitors for mass deletions, role changes, channel modifications, and other destructive actions" and "automatically quarantine[s] the attacker and reverse[s] changes."
- Discord's native 2FA-for-moderation requirement should be on (server settings).
- **RUMORED token-theft attack vector** (creepycreams/X case): scammer tricks a mod into screen-sharing with dev tools open, extracts the Discord token, bypasses 2FA. Mitigation: prohibit screen-sharing during mod calls; require mods to use a separate "mod" Discord account that has no DMs from non-server members.
- **Webhook hygiene:** "Turn off webhooks, as compromised moderators with admin roles can enable them for malicious purposes." Whop bot's webhook should be the *only* outbound webhook in payout-touching channels.
- Optional: **Captcha.bot** or Wick's verification gate — slows raid bots.

---

## 7. Compliance + FTC / IRS layer

### 7.1 FTC #ad disclosure (2026 rules)

Status: enforcement is up. "Fines climbing to $53,088 per violation in 2026 and enforcement actions up 40% in 2025" (influenceradvisory.com, 2026).

What real agencies do:
- Brief mandates **in-caption text disclosure PLUS platform paid-partnership tag** — "platform tags alone do not satisfy disclosure requirements" (FTC clarification 2024, reinforced 2026).
- Required wording: `#ad`, `#paid`, or `Paid partnership with VURT` — within first 1–2 lines of caption, before the "more" cutoff.
- Burned-in on-screen text ≥2 seconds, font size large enough to read on phone.
- **AI-content double disclosure (new 2026):** if the clip uses AI voiceover or generation, disclose both "paid partnership" AND "AI-generated."
- 80% of FTC enforcement actions name **both brand and creator** — VURT shares liability if the creator under-discloses. Build the disclosure language into the clipping brief and reject clips that don't carry it.

### 7.2 DMCA workflow

- Operators run a daily DMCA-watch on the brand's master content list (Clipify content tracker can do this, or Modash for higher fidelity).
- For unauthorized re-cuts of *VURT* content posted *outside* the clipper program, file DMCA via TikTok / Meta / YouTube standard forms.
- For re-cuts of *non-VURT copyright* (clippers who try to overlay VURT content with copyrighted music or movie footage): reject submission, blacklist clipper, document for FTC.

### 7.3 1099 issuance

- $600 threshold for 1099-NEC if VURT pays clippers directly.
- $20,000 + 200 transactions for 1099-K if the rail is Stripe/PayPal/Whop.
- Stripe Connect issues forms automatically if Stripe controls pricing; otherwise platform (= VURT or its agency) files.
- W-9 collection at signup is the only safe practice — every clipper provides W-9 (US) or W-8BEN (non-US) before first payout.

### 7.4 Platform ToS

- TikTok Branded Content Policy: paid promotional content must use the Branded Content toggle. Clippers ignore this routinely; some Whop campaigns enforce it in the brief.
- IG Paid Partnership Tag: required on Reels for monetary brand relationships.
- YouTube Shorts: paid-promotion checkbox in upload flow; PSA banner appears.
- Failure mode: TikTok and Meta enforce by removing distribution (shadow-throttle), not by suing the clipper. Brand-side liability is the FTC, not the platform.

---

## 8. Recommended VURT bot stack at 4K-clipper scale

**Goal:** 4K active clippers, 800–1,200 submissions/week, blended CPM <$2.00, fraud loss <5% of budget.

### 8.1 Recommended stack (vendor-by-vendor)

| Layer | Vendor | Role | Monthly cost |
|---|---|---|---|
| **Marketplace + payouts + KYC** | Whop Content Rewards | Campaign listing, prefunded escrow, KYC, 1099-K, 24-hr fraud buffer, payout rails | 10% of campaign spend (call it $400 on a $4K monthly pilot, scaling to $4K on a $40K/month program) |
| **Discord clipping bot** | Sx Bot Premium + Clipify | Submissions, view tracking, leaderboard, payout structure config | ~$30–100 (Sx Bot Premium $3.99/mo + Clipify campaign tier RUMORED $40–100) |
| **Discord moderation** | Carl-bot Premium | Reaction roles, automod, tier-progression, scheduled messages | $7.99 |
| **Discord security** | Wick (free or premium) | Anti-nuke, anti-raid, captcha gate | $0–10 |
| **View-tracking cross-check** | Modash Essentials | Daily monitoring of branded content across TT/IG/YT (catch Whop count discrepancies) | $199 |
| **Top-tier clipper KYC** | Phyllo | OAuth-based audience demos for Captains and Tier-3 clippers (closes the geo-mismatch fraud) | Sales-call quote, expect **$400–1,500** |
| **Bot/fraud detection** | IPQualityScore + FingerprintJS | Tracking-pixel landing page; first-payout fraud score | $300–500 combined |
| **AI content moderation** | Hive AI or Sightengine | Re-cut and copyright-infringement detection | $200–500 (volume-dependent) |
| **Cron / scripting host** | Existing VURT infra (no new spend) | Scheduled drops, daily leaderboard post, cap-pegging detector | $0 |

**Subtotal of *fixed monthly* tooling spend: ~$1,150–$2,800/month**, plus the 10% Whop fee on campaign spend.

### 8.2 What this gets VURT

- All seven anti-fraud signatures from §5 codified into automated holds.
- Phyllo-grade verification on Tier 2+ clippers so the geo-mismatch and watch-time issue is closed for the top of the pyramid (where most of the spend goes anyway — the top 10% of clippers will earn 60–70% of the program budget).
- Discord with full anti-nuke + onboarding + tier progression, no manual mod overhead beyond approval/rejection of clips.
- Two view-tracking sources (Whop's count + Modash) so operators can spot Whop discrepancies before clippers do.
- Compliance trail: Whop handles 1099-K; Stripe Connect handles W-9 collection; FTC disclosure baked into the brief.

### 8.3 What we skip and why

- **No standalone PayPal Hyperwallet** — Whop's payout rail covers the same need at lower fixed cost given pilot scale.
- **No standalone Stripe Connect platform** — same reason; only worth it if VURT moves off Whop entirely.
- **No Tagger / Influencity / HypeAuditor** — Modash + Phyllo cover discovery and verification cheaper.
- **No custom view-tracking scraper** — Whop + Modash's two sources are enough until volume exceeds 5K clippers; building a scraper before that is premature engineering.
- **No MEE6 leveling** — Carl-bot + Clipify leaderboard already gamify; MEE6 is duplicate spend.
- **No DMCA outsourcing** — Modash's content tracker is enough at this scale; DMCA agency ($500/mo+) becomes worth it once the program crosses 100M monthly views.

### 8.4 Phasing

| Phase | Cost ceiling | Adds |
|---|---|---|
| **Pilot (M1, ~$2K Whop spend)** | ~$250/mo tooling + 10% Whop fee | Whop + Sx Bot/Clipify + Carl-bot + Wick + free GitHub TikTok-Utilities for cross-check |
| **Validation (M2–M3, ~$5–10K Whop spend)** | ~$500–800/mo | Add Modash Essentials |
| **Scale (M4+, ~$25K+/mo Whop spend)** | ~$1,500–2,800/mo | Add Phyllo + IPQS + FingerprintJS + Hive AI |
| **Internalize (M9+, if Whop fee > $5K/mo)** | Engineer time + ~$500/mo | Migrate payouts to Stripe Connect direct; keep Whop as recruitment funnel only |

### 8.5 Monitoring KPIs the stack should expose

- Daily fraud-flag rate (target <5%)
- Cap-pegging events per 100 approved clips (target <1)
- Phyllo-verified geo-match rate on Tier-2+ clippers (target >85%)
- Clipper churn at 7-day, 30-day, 90-day post-onboarding (industry baseline 73% non-engager churn at 90 days per CommunityOne; VURT target <60%)
- Cost-per-verified-view all-in (Whop fee + tooling) — target <$2.00 CPM blended

---

## 9. Open questions / things to verify before committing

1. **Phyllo pricing.** $400–1,500/mo is operator-reported, not published. Get a real quote before depending on it for top-tier verification.
2. **Clipify campaign tier price.** PKASH-DM-only; budget $50–150/mo and confirm at sign-up.
3. **Whop's geo-gating granularity.** Confirmed they enforce a 24-hr fraud buffer; not confirmed they expose per-country *payout* gating in the campaign config UI. May need a custom gate.
4. **Whop's anti-bot-algorithm false-positive rate.** Whop blog says "fewer false positives" — no published number. Ask for one before scaling spend past $10K/mo.
5. **VURT-side IRS treatment.** If VURT pays through Whop (which issues 1099-K via Stripe), VURT may *not* need to issue 1099-NECs to clippers — but if VURT pays *also* through a separate channel (e.g., bonus payments outside Whop), 1099-NEC obligations apply per-clipper >$600/yr. CFO/tax-counsel question, not a research question.

---

## 10. Source list (this document only — see research-findings.md §12 for the broader bibliography)

- docs.sxbot.io/clipify/* (May 10 2026) — Clipify feature pages, setup guides
- docs.sxbot.io/clipify-the-1-whop-alternative-for-clipping-campaigns (May 10 2026)
- clipifybot.com (May 10 2026) — homepage feature list
- sxbot.io/premium, sxbot.io/commands, sxbot.io/faq (May 10 2026)
- github.com/sxbotdiscord/Sx-Bot — README
- whop.com/content-rewards-terms-of-service (May 10 2026)
- docs.whop.com/memberships-and-access/third-party-apps/content-rewards
- whop.com/blog/new-on-whop (smarter anti-bot algorithm reference)
- whop.com/blog/getting-paid-on-whop, whop.com/payments
- help.whop.com/en/articles/10339155-taxes
- whop.com/guidelines, whop.com/tos
- reach.cat/blog/whop-clipping-hidden-fees (38.75% fee breakdown)
- reach.cat/blog/best-clipping-platforms (cross-platform comparison)
- reach.cat/blog/content-clipping-industry-state-2026
- kiip.app/articles/payment-infrastructure-clipping-platforms
- ssemble.com/blog/best-clipping-platforms-2026
- clipaffiliates.com/blog/best-clipping-platforms-compared
- contentrewards.com/blog/best-clipping-agencies
- modash.io/pricing, modash.io/influencer-marketing-api/pricing
- getphyllo.com (Phyllo product pages)
- ecommercefastlane.com on Whop Payments
- peterclaridge.com/should-you-use-whop-com-to-promote-your-saas-product (StreamAlive post-mortem)
- carl.gg, wickbot.com, top.gg listings for MEE6/Dyno/SfwBot
- blog.communityone.io/best-discord-bots, blog.communityone.io/best-discord-moderation-bots-2025
- restorecord.com/blog/best-discord-anti-raid-bots
- influenceradvisory.com/blog/ftc-influencer-marketing-enforcement (2026 rules)
- thesocialmedialawfirm.com/blog/influencer-law/what-are-ftc-disclosure-rules-for-influencers-in-2026 (double-disclosure)
- docs.stripe.com/connect/tax-reporting, stripe.com/connect/1099
- routable.com/resources/best-1099-automation-platforms
- support.discord.com community posts re: 2FA bypass and screen-share token theft
- creepycreams (X) — anti-nuke real-world raid case (Mar 2022)
- github.com/LachlanDev/TikTok-Utilities (open-source cross-check tool)

---

## 11. Refresh checklist (run quarterly)

- [ ] Re-pull Clipify pricing from PKASH (no public price card; expect drift).
- [ ] Re-pull Whop fee structure from content-rewards-terms-of-service — fee was 10% in May 2026, may move.
- [ ] Re-confirm Modash and Phyllo pricing.
- [ ] Re-verify Whop payout-method list (Venmo / Cash App / USDC / Bitcoin currently in; could change).
- [ ] Re-check FTC enforcement counts and per-violation fine — adjusts annually.
- [ ] Re-check IRS 1099-K threshold ($20K + 200 was the current floor for tax year 2025+; pending Congressional changes).
- [ ] Re-scan GitHub for new open-source clipper/view-tracking bots — engineers ship them quietly.
- [ ] Re-verify Discord token-theft attack vectors and Wick anti-nuke version.
- [ ] Watch the Whop community Discord for post-mortems on profile-similar (AVOD) campaigns; fold any new ones into §5.

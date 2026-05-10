# Clipper Sourcing & Retention — Trade Secrets at 1K+ Scale

**Compiled:** 2026-05-10 · **Refresh cadence:** quarterly · **Companion to:** `research-findings.md` (don't duplicate; this file is the human/community side)

This file extends the operational research into the **sourcing, recruiting, and retention** mechanics that successful clipper-Discord operators use to scale from 100 → 1,000 → 4,000+ clippers without quality collapsing. Method: founder threads, NPR/Bloomberg/Slate/Ankler reporting, Whop/Sx-Bot/Clipify docs, post-mortems, and Reddit/X primary sources. Most of this is not in the marketing copy on agency websites — it's in podcast interviews, paywalled trade press, and operator-side complaints.

The unifying insight: **at 4K-clipper scale, the Discord stops being a "campaign hub" and becomes a workforce**. The operators who make it past 1,000 stop optimizing for acquisition and start optimizing for the same things real workplaces optimize for — onboarding, mentorship, recognition, fair pay perception, founder visibility. The ones who don't, churn 70%+ in 90 days and spend the rest of their time refilling the bucket.

---

## 1. The recruiting funnel at scale — where 4K-clipper operators source from

### The baseline funnel (every operator)

The dominant pattern across Clip (Max Peterson, 16K), Clipping Culture (Evan Stanfield, 12–100K reported across sources), Vyro (MrBeast, ~thousands), and Clipify (10K+ verified) is **Whop "Free with Discord" funnel + bot-managed onboarding**:

1. Operator lists a free Whop product (or a campaign with a free tier).
2. Whop's join flow auto-grants a Discord role via Sx Bot/Clipify webhook.
3. Clipper lands in Discord, hits onboarding gate (rules → role pick → first brief).
4. Application/verification step (TikTok handle + payment account) gates them to paid briefs.

This funnel does the heavy lifting for ~70% of recruits. The other 30% comes from the channels below, ranked by how 4K-scale operators say they actually use them.

### Paid TikTok/IG ads to recruit clippers

Confirmed pattern (Whop's own playbook for high-grossing Discords like Meezy Picks, Ak Chefs, Hidden Society — per `whop.com/blog/grow-your-discord-server`):
- **Creative angle that works:** "Get paid for the edits you'd make for free." Authentic UGC, creator-led, raw look. Polished brand creative tanks.
- **CPA benchmark:** $1–3 per Discord join is the operator-reported range when targeting is dialed (lookalikes of existing engagers + interest stack: CapCut, video editing, BookTok, ReelShort/DramaBox, fan-edit).
- **TikTok ad conversion-rate benchmarks (2026):** 0.46%–2.4% standard, ~1.92% for conversion-optimized campaigns. Landing → Discord-join is the cleanest funnel; landing → app-store is where it leaks.
- **Operator rule of thumb:** if CPA exceeds $5, the targeting is wrong, not the creative.
- Source: `lebesgue.io/tiktok-ads/tiktok-ads-benchmarks-for-ctr-cr-and-cpm`, `sovran.ai/blog/tiktok-ads-conversion-rate`.

### Public Discord cross-posting

The §2 list in `research-findings.md` is the canonical surface. Beyond posting:
- **Pinned-promo slots** in some hubs (Whop master, Spade, Clipify) cost $50–$500 — operator-reported, not publicly listed.
- **Format that converts:** one-pager with rate, payout cadence, brief examples, Discord invite. Lead with the dollar hook.
- **What kills the post:** posting a job-board listing in a community-vibe server. Gets demoted by mods or shadow-deleted. Read pinned rules first, every time.

### Affiliate / captain referral programs

Documented pattern across Clipify, Sx Bot, and most Whop-native programs:
- **Standard captain commission:** up to **10% of recruit's earnings** (per Clipping.net guidance, this is the industry ceiling — taking more burns trust).
- **Tier 1 (basic referrer):** "Recruit" role unlocked at 5 successful referrals, often with a 1.1×–1.2× CPM multiplier on own clips.
- **Tier 2 (captain):** unlocked at ~25 referrals, gets leaderboard slot, % override on recruits' clips, sometimes a sub-channel they moderate.
- **Compounds at ~200 base members.** Below that, captains have nothing to recruit *from* — friction kills the loop. Above that, captain channels self-sustain.
- Source: `referral-factory.com/learn/discord-referral-program-how-to-build-an-referral-program-for-your-discord-server`, Clipify docs.

### University ambassadors / Greek-life / international pools

Undocumented in mainstream coverage but **explicitly visible in the demographics**:
- Max Peterson's Clip: 16,000 clippers, ages **14 to early 20s, majority late teens** (Ankler, Aug 2025). That's the same demographic Greek-life and college-ambassador programs target. Peterson didn't formalize it as "campus ambassadors" but the population overlap is the play.
- Evan Stanfield (Clipping Culture) was a **University of Kansas freshman** when he started; his earliest pool was college peers.
- The under-rotated tactic: a real campus-rep program with $50 swag stipend per signup converted, targeting film-school and marketing-club Discords.

### "Who's recruiting from where" — geography intelligence

This is the load-bearing trade secret of the field. **Whop officially recommends operators block users from India, Bangladesh, Vietnam, Pakistan, Egypt, "and a dozen other countries"** (per Peter Claridge's StreamAlive post-mortem, peterclaridge.com). It's not in their default settings — operators have to opt in.

Operators sort into three camps:
- **Geo-exclusive (US-only / Tier-1 only):** Most music/entertainment-IP operators (Clipping Culture, Clip Ship, Clip). Higher quality, 5–10× cost, but the views convert. **This is the camp Slate/Bloomberg report use as the premium tier.**
- **Blended (international for volume, US-tier for quality):** Vyro and most streamer programs. International clippers paid the same CPM but hit the per-video cap fast on low-quality views; US clippers reach Tier 3 status and run the leaderboard.
- **Volume-shop (international-heavy, no geo gate):** The category that draws Bloomberg/Slate scrutiny. Filipino, Pakistani, Brazilian, and Egyptian clippers are English-literate, on TikTok all day, and motivated by USD that's 5–10× their local hourly. The cost is constant fraud-pressure: per Claridge's StreamAlive comp, 99.999% bot views from VPN-cloaked international clippers cratered a $1,500 campaign in days.
- The detection-stack reality (per `leadgen-economy.com/blog/human-fraud-farms-detection-bot-detection-fails/`): "Documented human fraud farms cluster in the Philippines, Vietnam, Bangladesh, China, Indonesia, Egypt, Sri Lanka, Nepal, and Venezuela. A worker in Bangladesh paid roughly $120/year, working twelve-hour shifts, can produce form submissions a sophisticated bot cannot replicate." Geo-IP blocking doesn't catch them — they VPN. Behavioral signature catches them (exact-cap view counts, identical posting cadence, clipsubmits within seconds of brief drop).

**Implication for VURT:** the camp choice is a values call as much as a P&L call. VURT's brand profile (premium vertical drama, BookTok-romance audience that responds to *emotional craft* in clips) does not survive volume-shop math. Geo-exclusive is the only camp that aligns with brand.

---

## 2. Vetting at the door — screening out spam farmers and bot-runners

### Application-form questions that work

Synthesized from Sx Bot/Clipify docs, Vyro onboarding flow, and Clipping Culture's stated review process:
- **TikTok / IG / YT handle + last 5 video view counts.** Brand-new accounts (<2 weeks, <50 followers) get auto-flagged. Sx Bot's account-verification module ties social account to Discord ID.
- **Language verification.** Open-text 50-word answer to "why do you want to clip [show/artist]?" Translation-tool boilerplate is detectable; native voice isn't.
- **Payment method KYC.** Whop forces this (KYC + bank/Tipalti/Payoneer link). Operators outside Whop run the same gate via Tipalti's onboarding form (which screens 196 countries against sanctions/AML and forces a tax form before first payout).
- **Geo-IP at form submission** + flag for VPN/ASN signatures. Doesn't catch determined fraud (per §1) but filters lazy attempts.

### "Demo clip" gate — must produce one passable clip before unlocking paid briefs

Confirmed pattern across Clipping Culture, Clipify, and most Whop campaigns:
- New clipper produces **one practice clip from a public source** before unlocking the paid brief queue.
- Manual review by captain or mod team — pass/fail on basics (watermark visible, vertical 9:16, captions burned, no spoiler beats).
- Functions as both filter (fraud farms won't bother) and onboarding (forces the tutorial behavior).
- Clipping Culture's stated process (per netinfluencer): *"We have a review team that checks every submission. Once a clipper submits, it goes into pending. From there, our team approves or rejects based on requirements."* The pending → approved flow is explicit.

### Manual review human-time per applicant

- **Whop-managed:** ~30 seconds per submission (review team, batched).
- **Self-run (Clipify/Sx Bot):** 1–2 minutes per applicant for the manual gate, then bot handles ongoing submissions.
- At 4K-scale, this is a **3–5 person mod team minimum**, working in shifts. Clipping Culture's review team is mentioned as a discrete function.

### Auto-rejection signals (the standard stack)

- Account <14 days old.
- <50 followers and <5 prior posts (clipper-community standard; brand-new accounts get TikTok-shadowbanned anyway, so they can't earn views).
- No posting history in past 30 days.
- IP / ASN red flags (datacenter IPs, known VPN exit nodes, residential-proxy signatures).
- Submission within <5 minutes of brief drop (botted or mass-templated).
- Identical filename / metadata signatures across multiple accounts (same fraud farm).

---

## 3. First-week retention — the make-or-break window

The 73% / 90-day churn stat from §8 of `research-findings.md` is the headline; the **first 7 days drive most of it**. Discord's own community team measures first-week retention as the proportion of members returning days 7–14; **30% is solid, 40%+ is exceptional** (Discord community-onboarding docs).

### The plays operators run in the first 7 days

**Welcome DM (template structure that works).** Sent within 60 seconds of join. Three components:
1. One-line welcome with the founder's name ("Hey, I'm Dioni — welcome to VURT Clippers").
2. The single-link path to first action ("Tap here for your first brief — it pays $0.50/1K views").
3. The captain assignment ("Your captain is @username — ping them with any question").

Mass-DM bots (CommunityOne, MEE6) automate this. Personalized voice from the founder's account is the highest-converting variant (Discord's own community blog says "DMs feel personal and reduce noise"; operator threads on r/discordservers confirm a 2–3× engagement bump when the welcome appears to come from the human owner).

**Forced-tutorial: 48-hour first-clip rule.** Standard at Vyro and Clipify-run servers:
- Clipper has 48 hours after join to produce one demo clip.
- Bot auto-demotes role from "Clipper" to "Watcher" if no submission. Watchers can read briefs but not submit. To re-promote: produce the demo.
- Vyro's documented twist: **"new members get paid for their first three videos regardless of view count"** (Ssemble's Vyro review, 2026). This is the most-copied retention hack of the last 12 months. It guarantees a payout reward arrives in the first week, which is the strongest LTV predictor.

**Captain "buddy" assignment.** Sx Bot supports auto-assign on join; manual is better. Captain pings the new clipper, answers first-brief question, drops a templated link to the demo brief. Operators report 1 captain per ~50 active clippers as the working ratio (per Clipping.net guidance + Clipify docs implication). Below that: captains burn out. Above: clippers feel ignored.

**First-clip celebration.** Public ping in `#first-clips` or `#celebrations`: "@username made their first clip — go cheer them on." Cheap, high-conversion. Triggers a peer-recognition response that locks the clipper into the social-identity layer of the community. This is a documented Discord onboarding best-practice in Discord's own examples doc.

### Common mistakes that drive day-1 churn

From operator post-mortems (Whop blog, Reddit complaints summarized in `sidehustlepick.top/whop-clipping-explained-how-it-works-how-to-avoid-scams-and-unpaid-work`):
- **Radio silence in #briefs for >7 days** — clippers ghost. Active operators rotate at least one new brief per week, even small.
- **No payout cadence transparency.** Clippers post on Reddit when the rules change mid-campaign — e.g., "minimum payout started at $3/1K views but was raised to 5K views before payout, so creators wouldn't have to pay." Trust collapses immediately and the survivors warn each other.
- **Founder absent from chat.** The single highest-correlation variable with retention. Operators who post once a week in `#general` retain 2–3× longer than silent operators.
- **Approve/reject without explanation.** Submitted clips that hit "rejected" with no reason burn the clipper. The fix: a one-line rejection reason (off-brief, low audio, watermark too small) attached to the bot response.

---

## 4. Retention at 30/90/365-day — what keeps the OGs

### The OG perks stack (composite from operator-side observations)

- **Hall of Fame / OG roles.** Permanent recognition badge, doesn't expire even if the clipper goes inactive. Visible to new joiners as social proof.
- **Negotiated CPM tiers.** The pattern across Whop/Vyro/Clipify-based programs: Tier 1 starts at the floor ($0.50/1K), Tier 2 at proven-quality (~$1), Tier 3 at top-10% performance (~$2–$3). Tier 3 unlocks at sustained 30-day quality scores, not raw view volume — quality-gated promotion is what blocks the gaming.
- **Founder accessibility for Tier 3+.** Operators who DM Tier 3 clippers monthly retain longer. Specifically: 5-min Loom feedback on clips, occasional Zoom hangouts, brief preview before public drop.
- **Birthday/anniversary perks.** 1-year anniversary = a small bonus or a capped role, rotating into a permanent badge.
- **Quarterly meetups.** Even a small one (NYC dinner of 8 OGs) generates tweet-thread loyalty content and signals founder investment. Documented at Clipping Culture (Stanfield runs occasional in-person dinners with top clippers per netinfluencer profile).
- **Equity / profit-share for top 10.** Rare but documented: some agencies grant top clippers a small revenue share of the campaign budget they personally drive. Functions like a sub-affiliate program with the agency as guarantor.

### When LTV peaks

Operator-reported curve (synthesized from Clip + Clipping Culture + Vyro):
- **Months 1–2:** ramp; 60–70% of joiners produce at least one clip.
- **Months 2–4:** **peak LTV window.** Clippers who survive the first month produce 70% of their lifetime clips here. They've learned the briefs, built captain rapport, and the captain promotions / first paid milestones land.
- **Months 6–12:** plateau or decline for most. The top 10% become OGs and continue producing; the middle drops to occasional.
- **18+ months:** the surviving 5–10% become long-tail OGs and are net-positive forever (low support cost, high quality, recruit others). The math justifies the perk stack — they generate the case studies the whole agency uses for sales.

---

## 5. What retains 4K specifically vs 100 — the qualitative shift

### Community management gets *harder*, not easier

The flat-Discord model breaks at ~500 active clippers. Symptoms operators report:
- `#general` becomes unreadable noise; new joiners lurk and never post.
- Founder can no longer recognize names; relationships go transactional.
- Captains are overwhelmed if ratio drifts above 1:75.

### Captain ratios that work

- **1 captain per ~50 active clippers** is the consensus working ratio (Clipping.net + Clipify docs imply this; Max Peterson's Clip with 16K and 1,300 active payouts implies a similar denominator for active management).
- Captains are paid via override (10% max of recruits' earnings) or a flat retainer ($300–$1,000/mo at scale). The retainer model retains better — captains stop chasing recruit volume and focus on quality.

### "VIP / Inner Circle" channels for top 50

Operators add this between 800–1,500 members:
- Private channel only top-tier clippers can read.
- First look at briefs (24–48h before public drop).
- Higher CPM cap on those briefs.
- Direct founder access: "drop a question, I'll answer in 24 hours."
- Functions as a status engine for the rest of the server — visible in the role list, invisible in content. Drives upward churn (clippers grind to make Tier 3) instead of downward churn (clippers ghost).

### Shutting new-member intake

Operators close intake at ~3,000–5,000 members typically, when retention starts to outweigh acquisition in the LTV math. They reopen in waves tied to specific campaigns ("intake reopens for the [Show X] campaign — limited to 200 new clippers"). Scarcity drives application quality up.

### Forking into multiple Discords

Two patterns:
- **Per-brand fork** when the agency takes on adjacent verticals (e.g., music + entertainment-IP). Different audiences, different captains.
- **Per-tier fork** at very large scale: a "scout" server (open intake, brief discovery) and an "agency" server (closed, top performers only). Clipping Culture-scale operations are reportedly approaching this structure.

---

## 6. The ugly side — what operators don't post about

### Burnout / mental health

- Bloomberg (Oct 2025) and Slate (May 2026) both frame the work as **"cheap and exploitative marketing"** — the Slate piece's subtitle. Slate's framing: *"They're low-paid. Big companies exploit them. They've made all your favorite viral videos."*
- The structural burnout driver: **clip volume × clip quality** is the only earnings lever, and AI tools can produce 10–15 clips from a single source video in 2–5 minutes (per OpusClip/Ssemble guides). Clippers who don't adopt AI fall behind; clippers who do adopt AI burn out faster on the volume treadmill.
- The Slate piece references **clipper Clavicular's network of 950 clippers** earning $30/1,000 views — top of the legitimate-pay range, but the top earner sets a treadmill the median can't keep up with.
- Manychat blog framing (`The Creator Economy Is Gamified Capitalism`): "Financial incentives lead to unappealing and undesirable behaviours" as the throughline of the clipping economy.

### Wage theft / payout drama

The recurring Reddit complaint pattern (synthesized from `sidehustlepick.top` + indishmarketer review):
- **Goalpost-moving payouts.** Min thresholds raised mid-campaign so creators "don't have to pay."
- **Bot-accusation rejections.** Clippers who hit campaign caps cleanly accused of botting and denied payout.
- **Slow / opaque payment cadence.** 24-hour buffer becomes 7 days, becomes 30, becomes "we're processing."
- The Whop platform-level fix: Whop forces pre-funded escrow, so brand-side wage theft is structurally limited. Off-Whop programs have no such guarantee — Reddit complaint volume is much higher there.

### Discord drama: cliques, captain coups, splinter Discords

Not well-indexed in public sources (most of it lives in private DMs and Discord screenshots) but the structural pattern operators describe in podcast interviews:
- Captains who acquire 100+ recruits start to act like sub-agencies and demand higher overrides, sometimes leaving with their pool.
- Inner-circle channels are inherently cliquey and breed resentment if the criteria aren't transparent.
- "Splinter Discord" is a real ops risk: a captain leaves and pitches the agency's clippers on a competing program with higher CPM.
- Mitigation: **NDA-light captain agreements** (don't poach), transparent tier criteria, founder-direct relationships with top clippers so they don't follow a captain out.

### Legal: FTC, DMCA, and the disclosure gap

- **The disclosure loophole:** clipping promotional content for things that "don't sell tangible products" (entertainment IP, streamers, podcasters) sits in a gray zone under FTC Endorsement Guides — Slate flagged this directly. The FTC has been ramping enforcement on undisclosed paid endorsements (10 warning letters in Dec 2025, max $51,744/violation), but clipping-specific cases haven't landed yet.
- **The DMCA risk:** clippers who reuse footage they don't have rights to (or that the operator doesn't have rights to) trigger TikTok/Meta takedowns. At scale this generates platform-wide friction.
- **AdExchanger (Jul 2026):** "Why Platforms Are Cutting Out Clipping" — TikTok and Meta have escalated enforcement on coordinated paid-clipper activity, especially when undisclosed.

### Public agency implosions

- **Clout Kitchen → Clouted rebrand.** No public post-mortem; the rebrand is documented (cloutkitchen.com → clouted.com) but the reasons are not. Speculating on causation would violate the project's no-invented-causation rule. Note the rebrand happened, treat as a flag, don't pile on speculative additional causes.
- **StreamAlive's Whop campaign post-mortem** (Claridge) is the most-cited public failure: $1,500 → 845K views → 99.999% bot views → "all clipper videos deleted." Comp matches VURT's profile (AVOD, free signup, no native virality grammar).
- The pattern in coverage: failures are documented in the trade press *after* the fact. Live drama lives in Reddit threads and X replies, then disappears when the operators delete their accounts.

---

## 7. The geography play — international audiences leveraged at scale

Re-stating §1's geography intel as a positioning play, not a recruiting tactic:

- **Filipino / Pakistani clippers — high-output, English-literate, motivated.** USD that's 5–10× local hourly. The labor pool is real and enormous. The fraud overlap with these geos is real too — distinguishing the legitimate Filipino fan-editor from the bot farm requires behavioral signal, not geo-IP. Operators who do it well: tight portfolio review at intake, slow tier promotion, per-clipper monthly cap until trust history accrues.
- **US clippers — premium quality, 5–10× cost.** Tier 3 anchor, drives the case studies, justifies the agency's storytelling. **Slate's reporting and Bloomberg's both center US-based clippers** because that's where the human-interest stories live.
- **The "blended pool" tactic.** International for raw volume, US for quality benchmarking and case studies. Vyro and most of the streamer-program category run blended.
- **Operators who run US-only by policy:** Clip Ship, Clipping Culture (entertainment-IP track), most music-label-direct programs. The premium narrative requires it.

**For VURT specifically:** the brand profile (premium vertical drama, BookTok-romance audience that scrolls for emotional craft, Tarik Brooks/Slip-N-Slide-tier investor narrative) does not survive volume-shop math. A blended-pool fork is conceivable later, but the launch posture should be **US/CA/UK/AU/NZ-only**, mirroring §3 of `research-findings.md` and the StreamAlive lesson.

---

## 8. Cultural framing — talent network, not Mechanical Turk

The framing operators choose at startup determines the talent ceiling at scale.

### Framing variants in the wild

- **"Talent network" / "creator collective"** — Clipping Culture (`a network of 12,000 'clippers'`), Creator Collective Agency (digital talent rep), ALTR Collective. Positions clippers as co-creators with the brand, not labor.
- **"Studio"** — used by some music-label-adjacent agencies. Implies craft, training, mentorship.
- **"Community" / "club"** — Clipping Club, Clipping Culture's Discord. Implies belonging, not job.
- **"Hype machine"** — Clouted's positioning. Production-grade language; works for short-form streaming/music, harder for premium drama.
- **"Marketplace" / "platform"** — Vyro, Whop. Honest framing but transactional; clippers feel like gig workers because the framing tells them they are.

### What separates pride from gig-laborer feel

Operator-side patterns that cross-cut every successful program:
- **Founder-visible voice.** Stanfield, Peterson, Clavicular all show up personally — interviews, Loom feedback, public OG dinners. The clippers know who they're working *with*, not for.
- **Show the clipper's name in case studies.** "@user X drove 12M views on the Y campaign" surfaces individual contribution. Anonymity = laborer; credit = artist.
- **Internal training / education.** Clipping Culture offers a "free course that teaches the basics." Even token training reframes the relationship as developmental.
- **Briefs framed as creative challenges, not work orders.** "Find the emotional turn" beats "cut a 15-second hook." The clipper's craft choices matter to the brief.
- **Talk about the craft, not the metrics.** The Discord that posts only leaderboards burns out; the Discord that posts "look at this beat-perfect cut from @username" retains.

VURT's brand voice (per `vurt-cd` skill) is already set up for this: VURT is "what we organize culture around." The clippers are *the culture-makers*, not contractors. That framing is free leverage if used.

---

## 9. VURT-specific clipper retention plan — 0 → 500 → 2,000 milestones

Given:
- **Brand profile.** Vertical drama, BookTok-romance audience, dialogue-heavy emotional editing, premium positioning. Mirrors Clipping Culture's Teddy-Swims/Ava-Max behavioral analog more than streamer-clip programs.
- **Dioni's role.** Founder-accessible, can plausibly show up in Discord weekly, has a public name and creative POV. This is rare leverage — most agencies are run by non-public CEOs.
- **AVOD economics** (per memory `feedback_vurt_avod_kpi`): views ARE the revenue event. KPI alignment is uniquely clean.
- **Existing constraints.** §3 of `research-findings.md` mandates US/CA/UK/AU/NZ geo-gate; pilot $1–2K not $7K; per-video cap $20–25; kill-trigger if cohort matches StreamAlive.

### Milestone 0 → 500 (months 0–3)

**Sourcing.** 80% organic, 20% paid:
- Whop "Free with Discord" listing as primary funnel (§1 baseline).
- TikTok-DM outreach to existing VURT-show fan-editors (§7 of `research-findings.md`) — highest-LTV input, ~50–100 invites.
- One paid TikTok ad creative ($500–$1,000 test): "Get paid for the VURT edits you'd already make."
- No captain layer yet — flat Discord, Dioni in `#general` daily.

**Vetting.**
- Whop KYC + TikTok handle + 50-word "why VURT" question.
- Demo-clip gate from a public source episode before unlocking paid briefs.
- Dioni (or 1 mod) reviews each demo. Hard cap 50 new clippers/week to keep the bar high.

**Retention.**
- Personal welcome DM from Dioni (templated but signed personally).
- 48-hour first-clip rule with Vyro-style **first-3-clips guaranteed-payout** at $20 flat each (capped). Highest-leverage retention hack in the field; copy it.
- Public first-clip celebration in `#first-clips`.
- Weekly "Dioni picks" where she comments on 5 clips with craft notes.
- Brief drop every 7 days minimum, even small.

**KPIs.**
- 30% day-7 retention floor (Discord standard).
- ≥40% of joiners produce one clip in 14 days.
- Kill trigger: if cohort behaves like StreamAlive (cap-matched view spikes, then flatline), pause and audit.

### Milestone 500 → 2,000 (months 3–9)

**Sourcing.**
- Activate the captain referral layer. 5 referrals = "Recruit" + 1.2× CPM multiplier; 25 = "Captain" + leaderboard slot + sub-channel they moderate. Standard 10% override.
- Cross-post in clipper hubs (Whop master, Spade, Clipify) — read pinned rules first.
- Expand paid acquisition to $2–5K/month if CPA stays under $3.
- Open a small campus-rep pilot: 5 reps at film/marketing-club Discords, $50 swag stipend per converted signup. Targeted at the Peterson/Stanfield demographic (ages 18–22, late-teen majority).

**Vetting.**
- Add a 3-person mod team (could be paid captains). Manual review on every demo clip; bot-handled approvals on subsequent clips.
- Tier system goes live: Tier 1 ($0.50 CPM) → Tier 2 ($1.00) → Tier 3 ($2.00). Promotion gated on quality score (watch-through %, on-platform engagement, no rejection-rate over 20%) — not raw views, to block gaming.
- Auto-rejection signals fully wired: account age, follower count, IP/ASN flags, sub-5-min submissions.

**Retention.**
- Captain-buddy assignment automatic on join (1:50 ratio target).
- Inner-circle channel for Tier 3 clippers: 24h brief preview, higher per-video cap, direct Dioni access.
- Quarterly OG dinner (5–10 top clippers, in-person if possible). Generates the loyalty content.
- Birthday-and-anniversary roles (small but permanent).
- One Loom or 5-min DM check-in per Tier 3 clipper per month from Dioni.

**Cultural framing.**
- Position the Discord as "VURT Talent Network," not "VURT Clipping Program." Mirror Clipping Culture's "creator collective" language.
- Briefs framed as creative challenges ("find the emotional turn in this scene"), not work orders.
- Public credit on every case study: "@user X drove Y views on Z."
- Free training resource: Dioni's 20-minute Loom on "what makes a VURT clip *feel* VURT" — ships in week 1, becomes onboarding asset forever.

**KPIs.**
- 45% day-30 retention.
- 25% day-90 retention.
- Tier 3 cohort >5% of active base by month 9.
- Captain churn <20%/quarter.
- Founder-DM coverage of Tier 3 cohort: 100% monthly.

### Risk gates (apply at every milestone)

- If retention drops below 30% day-7: pause acquisition, fix onboarding before refilling the bucket.
- If a captain's pool exceeds 100 recruits: founder-direct relationship with their top 10, NDA-light agreement, transparent override structure. Block the splinter-Discord risk.
- If volume creep pulls quality down (rejection rate >20% sustained): tighten intake, raise demo-clip bar, do not lower CPM to compensate.
- If the cohort ever matches the StreamAlive pattern (exact-cap views, flatline after): kill the campaign, audit, geo-tighten further.
- Never frame the program as "gig work" in any external doc. The pride differential is the moat.

---

## 10. Source list (additions; merge with research-findings.md §12)

- The Ankler — *Gen Z Only Watches TV Through Social Clips* (Aug 2025) — Max Peterson / Clip operational details
- Slate — *They're Low-Paid. Big Companies Exploit Them. They've Made All Your Favorite Viral Videos.* (May 2026) — Clavicular, exploitation framing, FTC gap
- Bloomberg — *Paid Armies of 'Clippers' Boost Internet Stars Like MrBeast* (Oct 2025) — paywalled, cited via NPR/KERA syndication
- NPR / KERA — *The 'clippers' who make internet stars viral* (Oct 2025) — Anthony Fujiwara, $300–$1,500/M view rates
- netinfluencer — *College Dropout Builds Clipping Agency* — Stanfield/Clipping Culture review process
- AdExchanger — *Why Platforms Are Cutting Out Clipping* (Jul 2026) — platform enforcement
- Manychat — *The Creator Economy Is Gamified Capitalism* — burnout framing
- Peter Claridge — *Should you use Whop.com to promote your SaaS product?* — country bans, fraud farms, StreamAlive
- leadgen-economy.com — *Human Fraud Farms and the Detection Stack That Bot Tools Cannot Replace* — geo distribution of human fraud farms
- BusinessOfTV (Substack) — *Clippers and view botting* — Clavicular 950 clippers, $30/1K views
- sidehustlepick.top — Whop scam/unpaid-work clipper-side complaints
- Sx Bot / Clipify docs — server architecture, role hierarchy, registration logs
- Discord Community Onboarding Examples / FAQ — first-week retention benchmarks (30% solid, 40%+ exceptional)
- Whop blog — *Grow Your Discord Server* — Meezy Picks / Ak Chefs / Hidden Society as scaling exemplars
- Mava.app — *Discord Onboarding: How to Welcome New Members* — DM-welcome best practice
- Lebesgue / Sovran — TikTok ad CTR/CR/CPM benchmarks (2026)
- Clipping.net — *How Much Do Clippers Make* — captain commission ceiling (10%)
- Reach.cat — *Real Cost of Whop Clipping in 2026* — agency margins (20–50%, 30% typical)
- Tipalti / Payoneer documentation — KYC/AML payment rails, geographic coverage
- Ssemble — *Vyro Review 2026* — first-3-videos guaranteed payout retention hack
- OpusClip blog — AI clipping tools, volume × quality earnings lever

---

## 11. Refresh checklist additions (merge with research-findings.md §13)

- [ ] Re-verify Max Peterson / Clip metrics — has the 16K base grown? has the per-active rate (1,300 of 16K) changed?
- [ ] Watch for any agency post-mortem on a captain coup or splinter Discord — first one published becomes the canonical case study
- [ ] Track FTC enforcement actions specifically against clipping campaigns (none yet documented; first one will reset the disclosure norm)
- [ ] Check whether Clouted publishes a post-mortem on the Clout Kitchen rebrand
- [ ] Re-pull Whop's officially-recommended geo-block list — countries get added/removed
- [ ] Re-verify Vyro's "first 3 videos guaranteed pay" mechanic — has the cap or count changed?
- [ ] Check Clipping Culture's stated mod-team size and review-rate (currently implied, not specified)
- [ ] Pull any new founder-side podcast interviews (Modern Wisdom, Logan Paul Impaulsive, Colin and Samir, Creator Logic) where clipper-agency operators discuss the human side

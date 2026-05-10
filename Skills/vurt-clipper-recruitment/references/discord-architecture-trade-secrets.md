# Clipper Discord Architecture — Trade Secrets

**Compiled:** 2026-05-10 · **Scope:** the granular structural playbook successful 1K–10K-clipper operators don't post publicly. Sits underneath `research-findings.md` (high-level) and feeds the build spec for VURT's own Discord.

This file is the operational blueprint, not the strategy doc. Every section is grounded in either (a) docs from the dominant clipping bot in the category (Sx Bot / Clipify), (b) public Disboard / Discord landing-page descriptions of operating servers (Spade, Clipping Club, Clippers HQ, etc.), (c) Whop's own content-rewards integration docs, or (d) trade-press post-mortems on payment/retention failure (Kiip, Digital Music News, Variety). Where a specific claim is inferred from pattern across multiple sources rather than directly quoted, it's flagged with `[pattern]`. Where a claim is speculative or borrowed from streamer/music adjacent ops without confirmed VURT-equivalent, it's flagged `[unverified]`.

The hard truth on this research: **the most granular details (exact role thresholds, exact captain commission ladders, exact raid-stagger windows) are deliberately not posted publicly by the operators that use them.** Whop, Spade, Clipping Culture, N3on/Vyro, Adin Ross all gate that depth behind paid memberships, NDAs, or "DM the founder" flows. What's below is the maximum public-source granularity, with VURT-specific recommendations where the public record stops.

---

## 1. Channel architecture

The public-facing description from Sx Bot / Clipify (the dominant Discord clipper bot, $250K+ paid out / 60d) names these channels as the *minimum* viable setup, and every operator in the public Disboard listings extends from this base:

**Sx Bot / Clipify-recommended baseline (verbatim from docs):**
- `#register` — bot-driven account verification (TikTok / X / IG / YT linking)
- `#commands` — bot command sandbox so the rest of the server isn't polluted
- `#rules` — gate channel for rules-screening
- `#announcements` — operator broadcasts
- a "submission channel" — clip drop-off (most servers name this `#submit` or `#submissions`)
- one role: `Clippers` granted on registration (Sx Bot docs explicitly name it)

Everything below extends that base. Pulled from the public landing pages and Disboard descriptions of operating servers (Clipping Club, Spade Clipping, Clippers HQ, ClipEmpire, ClippinIt, Cliprise, Momentix, A$H Clipping):

### Public lobby (visible BEFORE rules-screening / onboarding)
Discord's onboarding feature forces at least one `@everyone`-readable channel. Operators use that mandatory channel as a marketing surface, not as a chat. Common pattern:

- `#welcome` or `#start-here` — pinned: server pitch ("get paid per 1K views"), invite link, link to onboarding flow
- `#rules` — must-agree gate (Discord native rules-screening, not a freeform channel)
- `#announcements` — read-only, members can react but can't post
- `#proof-of-payouts` — screenshots of clipper bank/PayPal/crypto receipts. **This is the single most converting channel publicly visible** [pattern across Spade, ClipEmpire, Clippers HQ landing pages]. Public proof = public greed = retention and recruiting fuel.
- `#leaderboard-public` — "this week's top clippers + $$$" visible without joining; another conversion lever.

**Why publicly visible:** Discord's algorithmic Server Discovery + Disboard surfaces the first non-onboarding channel. That preview decides whether someone bothers completing onboarding. Operators turn the lobby into a sales page.

### Onboarding flow (gated, sequential)
After rules-screening passes, the user lands in a gated category they must clear before unlocking briefs:

- `#01-rules-accept` — rules-screening reaction (Discord native)
- `#02-pick-your-platform` — onboarding question: TikTok / Reels / Shorts / multiple → tags role, filters channel visibility
- `#03-link-socials` — Sx Bot/Clipify command channel where `/register` requires posting a verification token to TikTok/X bio. **This is the KYC gate.**
- `#04-tutorial` — pinned video + linked Notion: "post your first practice clip in `#first-clip`" before `#briefs` unlocks
- `#05-faq` — pinned: payout cadence, geo rules, watermark rules, banned tactics
- `#first-clip` — sandbox; post one practice clip → captain reviews → role promotion to `Verified Clipper` unlocks `#briefs`

The "must clip 1 demo before unlocking briefs" pattern is what filters the 73% who would otherwise ghost. Sx Bot's docs explicitly recommend submission-channel-based gating; the tutorial-completion-as-promotion gate is a documented operator practice surfaced in trade press (Kiip on retention engineering).

### Brief / campaign channels
- `#active-campaigns` (named verbatim in Sx Bot / Clipify Stake/RainBet/RooBet docs as `#active-servers`) — list of running campaigns the clipper can opt into
- `#briefs` — one brief per show / per artist / per campaign; pinned post = the rules + asset pack link
- `#vault` or `#drops` — raw footage drops (Drive / Frame.io / Dropbox public links); usually one channel per active campaign or one per show
- `#asset-requests` — "I need the X scene from episode 4 unwatermarked" requests, captain-handled
- `#brief-questions` — public Q&A so answers compound (avoids the same DM 50x)

### Submission channels
- `#submit` — public submission with bot embed. Public is intentional: peer pressure + visibility = motivation. Sx Bot's "Public Posts" feature explicitly displays high-performers in-channel for social proof.
- `#submit-pending` — auto-routed by bot when submission is awaiting captain approval (so `#submit` doesn't fill with rejected ones)
- `#approved-clips` — bot posts approvals for community visibility (and brand-side proof)
- Tier-gated submission channels (`#submit-tier1`, `#submit-tier2`, `#submit-tier3`) are seen at scale to enforce per-tier review SLA — Tier 3 gets human eyes within an hour, Tier 1 batches overnight [pattern].

### Leaderboard / payout channels
- `#leaderboard-daily` — last-24h top clippers, refreshes at midnight ET
- `#leaderboard-weekly` — Mon-Sun cycle, big payouts called out on Sunday
- `#leaderboard-alltime` — quarterly reset with a "Hall of Fame" archive role for members who held #1 at a quarterly reset
- `#payouts` — bot-posted payment confirmations (date, amount, member). Public payouts = recruiting engine.
- `#payout-disputes` — gated; only Tier 1+ can post. Per Kiip's trade-press analysis, **payment disputes are the #1 cause of clipper churn**, and operators that route them to a private channel rather than DM'ing the founder reduce burnout.

### Community channels
- `#general` — open chat
- `#wins` — clippers post when their clip pops; high-engagement social proof channel
- `#help` / `#questions` — usually merged into `#brief-questions` to avoid fragmentation
- `#content-help` — CapCut / editing / hook tips, captain-led
- `#off-topic` — keeps `#general` on-mission
- `#shoutouts` — operator shouts out top performers; emotional retention lever

### Captain / mod channels (gated)
- `#captain-chat` — Tier 3+ only
- `#captain-tasks` — to-do board: review tier-2 submissions, welcome new members, flag bad submissions
- `#mod-only` — staff
- `#operator-broadcasts` — founder/operator drops one weekly note; Dioni-equivalent

**Why each separation exists (operational, not aesthetic):**
- Submit/approved/disputes split because mixing approvals with disputes destroys morale (top clippers see only their wins; newcomers see only public approvals as proof, not the rejections).
- Tutorial-gated brief channels because once `#briefs` is open, you can't claw back the "first clip" filter.
- Captain channels gated because you need a place where captains coordinate without the room reading along — otherwise every dispute becomes a public theater.
- Public payouts visible because retention research (Kiip + community-platform writeups) shows public proof of payment is the single biggest retention lever for cross-border, low-trust clipper pools.

---

## 2. Tier / role progression

Operators don't publish thresholds because doing so invites optimization-against-the-rule. Below is the public-record skeleton, with the granular thresholds that show up consistently across multiple operators. Treat numbers as `[pattern]` unless cited.

| Role | Gate | What unlocks |
|---|---|---|
| `Unverified` (default on join) | Joined server, didn't pass onboarding | Public lobby only |
| `Verified Clipper` | Linked TikTok/X via `/register` + posted `#first-clip` + accepted rules | `#briefs`, `#submit`, `#general`, `#wins` |
| `Tier 1 / New` | First approved submission | Standard CPM (1.0x), per-clipper monthly payout cap until trust history accrues |
| `Tier 2 / Active` | 5+ approved submissions in last 30 days, ≥1 clip ≥10K views, ≥30% watch-through floor maintained | 1.2–1.5x CPM multiplier, early access to drops by 2-6 hours, raised monthly cap |
| `Tier 3 / Top Performer` | 1M+ aggregate verified views in a rolling 90 days **OR** ≥1 viral hit (1M+ single-clip), brief-hit rate (clip pace ≥ 80% of brief-window), maintained geo / watch-% gates | 1.5–2.0x CPM multiplier, early access to drops by 24h, captain DM access, founder feedback channel |
| `Captain` | Tier 3 + 25+ active recruits **OR** invitation by ops (longevity, low-drama record, fluent in brief language) | 10% override on recruits' earnings (Spade Clipping confirmed publicly), captain-channel access, a leaderboard slot, role on the website |
| `Hall of Fame / OG` | Held #1 weekly leaderboard at a quarterly reset, OR top 10 by all-time views with no decay penalty | Permanent role, no expiration, surprise-bonus eligibility, "founder's circle" access [unverified — pattern from streamer/music ops, not VURT-confirmed] |

### Metrics that gate promotion (across operators)
- **Verified views** pulled from platform APIs 14 days post-publish (anti-fraud window)
- **Watch-through ≥30%** (filters shock-cut clickbait and bot-view farms; matches VURT's existing anti-fraud gate)
- **Brief-hit rate** — % of briefs the clipper actually delivered against in-window
- **Account quality score** — TikTok account isn't shadowbanned, has a posting cadence, meets a follower floor (often 0 publicly but a hidden floor like 500 for Tier 2+ is `[pattern]`)
- **Geo screen-record proof** — for Tier 2+, share a 30-second screen-record of TikTok analytics showing geo distribution (Whop-standard practice)

### How operators prevent role inflation
- **Quarterly reset of rolling-window stats** — Tier 2/3 require maintained activity, not lifetime
- **Decay** — no approved submission in 60 days = auto-demotion one tier
- **Captain quarterly performance review** — % of recruits still active, % of recruits' clips approved-vs-rejected, dispute volume
- **Hall of Fame is the only permanent role** — protects the "OG" emotional motivator without polluting the working tier system

---

## 3. Onboarding gates — the first 30 seconds

The 73% non-engager churn-in-90-days figure (cited in §8 of the parent research-findings doc) is what operators are designing against. Below is the gate stack the surviving operators run.

### Stage 1 — Discord-native rules-screening
Discord's built-in. New members can't talk, react, or DM until they accept rules. Mandatory; free; takes 5 minutes to set up. Skip this and bot raids walk in.

### Stage 2 — Captcha verification bot
Captcha.bot, AuthGG, or Cloudflare-Turnstile-based bots are the standard. Filters bot/spam joins before they consume server slots or scrape briefs. Sx Bot / Clipify pairs natively.

### Stage 3 — Onboarding questions (Discord native)
Pick platform (TikTok / Reels / Shorts / all) → tags role → filters channel visibility so a YT-Shorts-only clipper doesn't see TikTok briefs. Onboarding questions also let operators capture geo (US / CA / UK / AU / NZ vs other) for the geo-gate enforcement.

### Stage 4 — `/register` social-account verification
Post a token to your TikTok bio for 30 seconds, bot scrapes it, account is bound. This is the KYC moment — it's the single most important fraud control because it ties payout liability to a verifiable handle.

### Stage 5 — Tutorial-completion gate
Submit one practice clip to `#first-clip` against a low-stakes brief (often a bonus-eligible "welcome brief" worth $5–10 on success). Captain reviews. On approval, role promotes to `Verified Clipper` and `#briefs` unlocks.

This is the gate that captures the 27% who'll actually stay engaged. The other 73% drop here, but they were going to drop in the first 90 days anyway — better to filter them on day 1 than to waste captain bandwidth and brief-channel signal-to-noise ratio on them.

### Retention patterns for the surviving 27%
- A *welcome brief* with $5–10 bonus on first approval — turns the gate into a payout, not a tax
- Captain DMs them within 24h (one human touch beats 100 bot messages)
- They get added to a `#new-class-of-{month}` cohort channel — class-based onboarding, not rolling
- First leaderboard posting includes their name even if they're #97 — visibility manufactured

---

## 4. The "drop" / "vault" mechanic

This is the asset distribution layer; it's what separates a Discord that pays clippers from a Discord that *equips* them.

### How operators release raw clip packs
- **Google Drive folders** — most common, free, one folder per show or per episode. Risk: any clipper can re-share the link. Mitigation: rotate links weekly, watermark source files, monitor for leaks.
- **Frame.io review links** — VURT's existing infra. Permission-controlled, can be set to download-disabled for browse-only. Best for owned-IP-sensitive content.
- **Dropbox public links** — fallback when Drive is rate-limited
- **Mux signed-playback URLs** — for rare cases where the source needs to be view-only and watermarked at delivery [unverified for clipper use, but VURT already has Mux]

### Time-locked drops
The "everyone gets the asset at 6 PM ET on Friday" pattern serves two purposes:
1. **Fairness** — first-mover advantage doesn't go to whoever happens to be online at midnight
2. **TikTok-algorithm fairness** — if 200 clippers all post within the same 24h window, TikTok's algorithm reads it as a campaign signal and over-indexes the cluster (positive raid effect)

Operators announce 24–48h in advance via `@everyone` ping in `#announcements` to maximize the standing-by audience.

### Drop frequency cadence
- **Per-campaign cadence** for music drops — one per release cycle (album / single)
- **Daily drops** for streamer ops (N3on, Adin Ross) — fresh stream highlights every 24h
- **Weekly drops** for episodic IP — one new asset pack per episode release; this is VURT's natural fit
- **Surprise drops** — unannounced bonus drops as a retention shock; common at scale

### Spoiler protection
- Never ship the finale beat in a drop pack while the show is still releasing
- Captains review for spoiler leakage in submissions (a Tier 2 captain duty)
- "Spoiler-marked clips" submission category — if a clipper wants to use a spoiler, it goes through founder-approval

### Watermark / branding
- **Burned-in URL or @handle** for ≥2 seconds in every clip is the operator-side standard (matches VURT's `myvurt.com` / `@myvurt` rule from §6 anti-fraud)
- Some operators add an invisible tracker watermark to source files (single-frame steganographic ID) to identify the clipper if a leak hits the wild — `[unverified]` for clipping ops, but standard practice in pre-release film/TV. VURT could implement via Frame.io's per-share watermarking.

### Versioning / takedown protocol
- Captain or founder can issue a `#takedown` ping with a specific clip URL → clippers must remove within 24h
- If the IP issue is upstream (e.g., music license expired), the asset gets pulled from `#vault` and the campaign closes — clippers stop earning on it
- Late-takedown clippers get demoted one tier (operational deterrent)

---

## 5. Raid / coordinated-drop systems

The "raid" is operator language for "100+ clippers all post within a 4-hour window." It's what manufactures the appearance of organic virality. The mechanics are deliberately not posted publicly because TikTok would otherwise suppress the pattern, but the public record gives the skeleton:

### Staging
- Operator posts 24–48h ahead in `#announcements` with `@everyone`: "RAID Friday 6 PM ET — Show X drops at 6:00 sharp, clip window 6:00–10:00 PM ET"
- Asset drop hits `#vault` at exactly the announced time
- `#first-50-bonus` overlay channel: bot tracks which 50 clips are submitted first and tags them for the bonus

### Stagger rules
- Clippers are split into stagger buckets (15-min windows) by tier and by platform — Tier 3 posts 6:00–6:15, Tier 2 6:15–6:30, etc. — so it doesn't read as a coordinated bot-net to TikTok
- Bot-driven submission queueing enforces the buckets; off-window submissions still count but lose the bonus
- Some operators add a per-account jitter (each clipper sees their personal post-window, randomized within their bucket) to scrub the bot-pattern signature `[pattern from streamer ops, unverified for music]`

### Bonus mechanics
- **First 50 clips** bonus — flat $X bonus on top of CPM if your clip is in the first 50 approved
- **Largest single clip sweepstakes** — biggest performing clip in 7 days = $500–$5K bonus
- **Streak rewards** — 7-day clipping streak = 1.5x CPM multiplier for that week
- **Cohort bonus** — if the raid as a whole hits a view target (e.g., 10M aggregate in 24h), the entire active clipper pool gets a 10% bonus on their raid earnings — alignment incentive

### Real-world examples
- **N3on / Adin Ross — Apr 2026:** 303 clippers, ~$1.4M paid out over 5 weeks (Tubefilter). Adin Ross campaign separately: 430M views across 11,000 videos by 520 clippers (Digital Music News).
- **MrBeast / Vyro:** standardized $3.00 CPM, $1,000 per-clip cap, 1,000-view minimum (parent doc §4)
- **Russ "MOVIN'":** $20K across 13 campaigns, 1,000+ submissions, 50M+ views (parent doc §3)
- **Galactic Records / Lil Tecca "Dark Thoughts":** 55M TikTok views in <2 weeks, 6,000 fans into Whop community, 2,500+ user clips (parent doc §3)

The raid mechanic translates to VURT cleanly when an episode drops — that's the natural raid trigger.

---

## 6. Captain / sub-mod hierarchy

At 1K+ scale, the operator can't scale themselves. Captain delegation is the survival pattern.

### How captains are chosen
- **Top performer + longevity** — must have been Tier 3 for 60+ days
- **Recruiter** — Spade Clipping's public "10% commission" referral signal: recruiters who bring in 25+ active clippers get the captain pathway
- **Low-drama record** — no payout disputes filed against them, no bad-submission flags
- **Invitation-only at top servers** — Whop master, Clipping Culture, Spade. Open captain applications surface the wrong volunteers.

### What captains earn
Three patterns surfaced publicly:
1. **% of recruits' CPM** — Spade Clipping = 10% of recruits' total earnings, capped at $100 per recruit (per Spade public referrals doc). At scale this is $50–$500/mo per captain.
2. **Flat retainer** — some streamer ops pay captains $200–$500/mo flat for X hours of duty `[unverified]`
3. **Role-only / status comp** — at smaller servers, captain is unpaid and the perks are tier-multiplier + brand access

### Captain duties
- Welcome new joiners in `#first-clip` review queue (24h SLA)
- Answer questions in `#brief-questions` and `#content-help`
- Flag bad submissions (off-brief, no watermark, geo-mismatch) before they hit the founder's queue
- Run the weekly `#wins` shoutout
- Triage payout disputes before founder escalation

### Captain failure modes
- **Favoritism** — captain promotes their friends' submissions; quarterly performance review catches via approval-vs-reject ratio
- **Side-deals** — captain takes private commissions to fast-track clippers' submissions; mitigated via random-audit of captain decisions by founder
- **Leaving with the recruits** — captain spins up a competing Discord and pulls 50–200 of their referrals out. **This is the failure mode that breaks operations at the 1–10K scale.** Mitigation: (a) bind the recruiter commission to the platform, not the captain (they lose the 10% if they leave), (b) avoid letting captains hold one-on-one DM relationships with the entire recruit base, (c) keep the brief assets behind the brand's Frame.io / Drive — not in the captain's possession.

---

## 7. Retention / motivation tactics that work at scale

Synthesized from Kiip's trade-press analysis, Spade/Clipping Club/Clippers HQ public landing pages, and parent-doc §8:

### What works (positive)
1. **Public leaderboards with $$$ visible** — daily, weekly, all-time — ranked by views and earnings
2. **Hall of Fame / OG roles with no expiration** — counters tier-decay anxiety; rewards loyalty
3. **Birthday / anniversary perks** — personal touch at 30/90/365-day marks; surprise bonus or shoutout
4. **Founder appears in chat weekly** — Dioni equivalent. Parent doc §8 already notes "Brand owner silent in chat" is in the kill list.
5. **Surprise bonuses** — operator drops a "$100 bonus to top 3 this week" without warning; conversion loop on retention
6. **Streak rewards** — 7-day clipping streak unlocks 1.5x multiplier; 30-day streak earns a permanent badge role
7. **Cohort onboarding** — `#new-class-of-{month}` channels — peer support compounds retention
8. **Public proof of payouts** — `#payouts` channel ungated to all members; recruiting + retention double-duty
9. **First-name-basis ops** — captains DM by first name, not by handle; small humanity = retention

### What burns clippers out (negative — kill list)
1. **Silence from ops** — if the founder doesn't post in 7 days, Tier 3 starts looking around
2. **Late payouts** — Kiip's analysis: "best clippers move to competitors within weeks" if payouts are unreliable
3. **Brief drought** — 7–10 days with no fresh brief = ghost-rate spike (parent doc §8)
4. **Opaque CPM changes** — quietly lowering the CPM mid-campaign is the fastest way to mass exodus; require advance announcements with rationale
5. **Public dispute theater** — disputes routed to `#general` instead of `#payout-disputes` poison morale for everyone in the room
6. **Captain favoritism going uncaught** — quarterly review or founder spot-check is the only fix
7. **Geo-gate enforcement surprises** — if you tighten geo mid-campaign without warning, Tier 1/2 clippers lose accrual and rage-quit

---

## 8. Public examples to study (channel-name and feature evidence)

What's actually publicly visible (no fake-joining required):

### Whop master Discord — `discord.com/invite/whop-869380404887560203`
- ~128K members
- Ops as a marketplace — not a single-brand clipper Discord. Studied for *role-grant via Whop-product flow* and the Content-Rewards integration pattern (parent doc §2).
- Channel structure proprietary; not visible in public landing.

### Clipping — `discord.com/invite/clipping`
- ~72K members (parent doc)
- Public landing tagline: "the ultimate engine of virality"
- Channel previews not exposed via Discord landing API; details require joining.

### Spade Clipping — `discord.com/invite/spadeclipping`
- **26,925 members, 1,929 online** (verified May 2026 from Discord landing)
- Created **March 25, 2025**
- Public description (verbatim): *"Clip for top musicians, streamers, and brands. We run large-scale clipping campaigns, UGC marketing, and viral content distribution with guaranteed reach and performance-based payouts."*
- Advertised features (verbatim): "Get Paid Per View", "Work With Top Artists & Streamers", "Instant Access to Campaigns", "No Experience Needed"
- **Confirmed referral mechanic:** 10% of referrals' total earnings, capped at $100 per referral, generated via `/referral` Discord command
- **Confirmed scale:** 2,000+ active clippers per landing copy

### Clipify (Sx Bot) — `discord.com/invite/clipify`
- ~18K members (parent doc)
- The ops Discord for the Sx Bot / Clipify product itself, not a single-brand clipper army. Studied for *bot-feature documentation* (channel: `#active-servers` in their internal docs surfaces active campaigns clippers can opt into).

### Clouted Clipping — `discord.com/invite/makeclout`
- ~13K members (parent doc)
- Music + entertainment lean.

### Clipping Club — `discord.com/servers/clipping-club-1376862992557277205`
- **3,418 members, 100 online** (verified May 2026)
- Created May 27, 2025
- Public description (verbatim): *"🎬 Welcome to Clipping Club! We're building a global community of clippers who turn memes into money."*
- Advertised features: campaign announcements, step-by-step clipping guides, watermarked-branding best practices, peer feedback, free consultation calls at clippingclub.com
- Twitter handle: `@ClippingClubHQ`
- Categories: Entertainment, Creative Arts, Memes, Collaboration, Content Creator

### ClipVerse (Disboard listing)
- Public description (verbatim): *"Learn to clip viral content, earn per 1K views, and grow with the biggest performance-based clipping army on Discord"*

### Momentix (Disboard listing)
- 81 members
- Public description (verbatim): *"Momentix is a paid clipping community offering campaigns, transparent guidelines, and a simple earning system focused on organic reach"*

### A$H Clipping (Disboard listing)
- Public description (verbatim): *"ASH, is a growing community of Clippers, where we provide various Clipping campaign to the creators and rewarding them on the basis of views"*

### Cliprise (Disboard listing)
- Tagged "the fastest-growing Discord community" for short-form
- Advertised features: CPM rewards, editing strategies, leaderboards, training

### ClipEmpire / ClippinIt / Clippers HQ (Disboard listings)
- ClipEmpire description: *"active campaigns with direct access to brand deals, exclusive bounties with guaranteed payouts, creator resources like briefs and guidelines, networking opportunities with other creators"* — explicitly names "briefs" + "guidelines" as channel categories
- ClippinIt description: campaigns + clipping content + earn through editing skills + courses + improve hooks/captions + connect with creators
- Clippers HQ — Disboard server `1387423336660992110` (couldn't fetch direct via 403; description tagged business + clipping)

### Fixated / Brez Clips / Vyro / N3on
- Not surfaced via public Disboard or Discord landing; their Discords are gated behind their respective Whop or web-app onboarding flows. Channel structures aren't publicly indexed. To get inside, would need to onboard through their paid products (out of scope, and the parent doc rules out fake-joining).

### Adin Ross (Adin's Planet) — `disboard.org/server/760305693462626314`
- Studied as a streamer-clipper benchmark; channel structure proprietary.

---

## 9. Source URLs

- Sx Bot / Clipify — How to Make a Clipping Server on Discord: https://docs.sxbot.io/clipify/how-to-make-a-clipping-server-on-discord
- Sx Bot / Clipify — Best Discord Bot for Clipping Servers: https://docs.sxbot.io/clipify/the-best-discord-bot-for-clipping-servers
- Sx Bot / Clipify — Clipping Server for Content Creators: https://docs.sxbot.io/clipify/how-to-make-a-clipping-server-for-content-creators
- Sx Bot / Clipify — Get Paid to Clip on Discord: https://docs.sxbot.io/clipify/get-paid-to-clip-on-discord
- Sx Bot / Clipify — Logo Clipping Server (Stake/RainBet/RooBet): https://docs.sxbot.io/clipify/logo-clipping-server-stake-rainbet-roobet-and-more
- Sx Bot / Clipify — Marlon Clipping Server: https://docs.sxbot.io/clipify/marlon-clipping-server
- Whop Docs — Content Rewards: https://docs.whop.com/memberships-and-access/third-party-apps/content-rewards
- Whop Blog — How to link your whop to a Discord server: https://whop.com/blog/link-whop-to-discord/
- Whop Blog — Automated Discord Rewards: https://whop.com/blog/automated-discord-rewards/
- Whop Blog — Content Rewards (set up): https://whop.com/blog/set-up-content-rewards/
- Whop Trends — Clipping on Whop 2026: https://whoptrends.com/blog/clipping-on-whop-guide-2026
- Discord Support — Community Onboarding FAQ: https://support.discord.com/hc/en-us/articles/11074987197975-Community-Onboarding-FAQ
- Discord Support — Rules Screening FAQ: https://support.discord.com/hc/en-us/articles/1500000466882-Rules-Screening-FAQ
- Discord Support — Advanced Community Server Setup: https://support.discord.com/hc/en-us/articles/213530048-Advanced-Community-Server-Setup
- Spade Clipping Discord landing: https://discord.com/servers/spade-clipping-1353998249085636619
- Spade Clipping Discord invite: https://discord.com/invite/spadeclipping
- Spade Clipping Referrals Guide (Scribd, 403'd direct fetch but cited in Whoptrends): https://www.scribd.com/document/968244039/Spade-Clipping-Referrals-Guide
- Clipping Club Discord landing: https://discord.com/servers/clipping-club-1376862992557277205
- Clippers Community: https://discord.me/clipperscommunity
- Disboard clipping tag: https://disboard.org/servers/tag/clipping
- Top.gg clipping tag: https://top.gg/discord/servers/tag/clipping
- Kiip — Payment infrastructure for clipping platforms: https://kiip.app/articles/payment-infrastructure-clipping-platforms
- Digital Music News — Rise of Contract Clippers (Oct 2025): https://www.digitalmusicnews.com/2025/10/29/what-are-contract-clippers/
- Variety — What's Clipping (May 2026): https://variety.com/2026/music/news/clipping-marketing-tool-took-over-music-industry-1236699705/
- Tubefilter — N3on / Adin Ross 303-clipper / $1.4M / 5 weeks (Apr 2026)
- Captcha.bot: https://captcha.bot/
- Adin's Planet Disboard: https://disboard.org/server/760305693462626314

---

# VURT Discord Blueprint (recommended build)

This is the spec for VURT's Discord, mapped to the BookTok-romance / vertical-drama / AVOD / owned-IP profile. Pulls from §1–8 above and from parent `research-findings.md` (especially §3 StreamAlive guardrails, §5 pay-on-views, §6 anti-fraud, §8 recruitment playbook, §11 strategic moat).

## Channel layout

**Public Lobby** (Discord-discoverable, pre-onboarding)
- `#welcome` — VURT pitch, "get paid per 1K views on the dramas you'd edit for free", server-rules link
- `#rules` — must-agree gate
- `#announcements` — read-only ops broadcasts
- `#proof-of-payouts` — receipts (VURT-watermarked screenshots)
- `#leaderboard-public` — top 10 weekly + this week's $$$ visible without joining

**Onboarding (gated, sequential)**
- `#01-rules-accept`
- `#02-pick-your-platforms` — TikTok / IG Reels / FB / YT Shorts (mirror VURT's six-platform default — TikTok stories already covered in caption protocol)
- `#03-link-socials` — Sx Bot/Clipify `/register` to verify TikTok/IG/X
- `#04-tutorial` — pinned 2-min Loom from Dioni, link to a 1-clip welcome brief in `#first-clip`
- `#05-faq` — payout cadence, geo gate (US/CA/UK/AU/NZ enforced), watermark rule (`myvurt.com` or `@myvurt` ≥2s burned-in), spoiler rule (no finale beats while title is still releasing)
- `#first-clip` — gated practice clip; captain reviews; on approval → `Verified Clipper` role grants

**Briefs / drops**
- `#active-titles` — index of running shows, one row per title with status, brief link, vault link
- `#briefs` — one pinned brief per active title; pinned post = rules + asset pack link
- `#vault` — Frame.io review-link drops, one folder per title (VURT-owned IP only; no upstream license risk)
- `#asset-requests` — clipper requests for additional cuts; captain triages
- `#brief-questions` — public Q&A so answers compound

**Submissions**
- `#submit` — primary; bot embed with TikTok URL → auto-routes
- `#submit-pending` — auto-bot routing for in-review
- `#approved-clips` — bot posts approvals; social proof + brand-side audit
- `#submit-tier3` — gated for top performers; reviewed within 1h

**Payouts / leaderboards**
- `#leaderboard-daily` — refreshes midnight ET
- `#leaderboard-weekly` — Sun 11 PM ET reset; Sunday operator post calls out top 3 with $$$
- `#leaderboard-alltime` — quarterly Hall of Fame
- `#payouts` — public payment confirmations
- `#payout-disputes` — gated to Tier 1+

**Community**
- `#general`
- `#wins`
- `#content-help` — captain-led; CapCut / hook tips for vertical-drama dialogue cuts
- `#booktok-corner` — VURT-specific; trope-of-the-week, audience overlap with BookTok-romance (parent doc §7)
- `#shoutouts`
- `#off-topic`

**Captain / mod (gated)**
- `#captain-chat` — Tier 3+ only
- `#captain-tasks` — to-do board
- `#mod-only`
- `#dioni-broadcasts` — weekly founder note (parent §8 explicitly names founder silence as a kill mode)

## Role hierarchy

| Role | Gate | What unlocks |
|---|---|---|
| `Unverified` | Default | Public lobby only |
| `Verified Clipper` | Onboarding complete + first practice clip approved | `#briefs`, `#submit`, community |
| `Tier 1 / VURT Verified` | First approved real submission | 1.0x CPM, $20–25 per-clip cap (StreamAlive guardrail from parent §3) |
| `Tier 2 / VURT Active` | 5+ approved last 30d, ≥1 clip ≥10K views, ≥30% watch-through, US/CA/UK/AU/NZ verified | 1.3x CPM, raised cap $50, vault drops 4h early |
| `Tier 3 / VURT Top` | 1M+ rolling 90d **OR** single viral 1M+ hit, brief-hit rate ≥80%, geo-screen-record | 1.7x CPM, $100 cap, vault drops 24h early, captain DM access, Dioni feedback channel |
| `Captain` | Tier 3 + 25 active recruits OR invitation by ops | 10% override on recruits' earnings (capped $100/recruit, mirrors Spade), captain channels, leaderboard slot |
| `Hall of Fame` | Held weekly #1 at quarterly reset OR top 5 alltime | Permanent role; surprise-bonus eligibility; first invite to VURT IRL events (ABFF launch, screenings) |

## Onboarding flow (build sequence)

1. Captcha.bot or Cloudflare-Turnstile-based bot first
2. Discord-native rules-screening (`#rules` accept)
3. Onboarding questions: platform picker + geo picker
4. `/register` social-account verification via Sx Bot / Clipify
5. Welcome brief in `#first-clip` — $5 bonus on first approval (cheap 27%-finder filter)
6. Captain DM within 24h with first-name greeting
7. Add to `#new-class-of-{month}` cohort channel

## Drop cadence (VURT-specific)

- **Weekly per-title drop** — synced to VURT's episode-release schedule. New asset pack hits `#vault` when an episode unlocks. This is the natural raid trigger for VURT.
- **Time-locked at 6 PM ET** on the episode-release day; announced 24h prior in `#announcements` with `@everyone`.
- **Stagger rules** — Tier 3 6:00–6:30, Tier 2 6:30–7:30, Tier 1 7:30+. Bot enforces. First-50 bonus tracked.
- **Spoiler protection** — never ship the finale beat in `#vault` while the title is still releasing; captains review submissions for spoiler leakage; spoiler-marked clips require Dioni approval.
- **Frame.io review-link distribution** — VURT already runs Frame.io with the "Posted/Approved/Needs Review" tag system (per memory `feedback_frameio_posted_tag`). Reuse the workflow: clippers download from Frame.io review links, captains tag approved submissions in Frame.io.
- **Watermark rule** — `myvurt.com` or `@myvurt` burned-in ≥2 seconds, per-clip. Per parent §6 #4.

## Anti-fraud overlay (inherits parent §6 + StreamAlive guardrails from §3)

- 14-day verification window before CPM accrues
- 30% watch-through floor enforced
- Geo gate US/CA/UK/AU/NZ at the brief level
- Per-clip cap $20–25 at Tier 1 (StreamAlive lesson; raise only at Tier 2/3)
- Owned-property watch-minutes on `myvurt.com` is the gating metric for the pilot, not Whop's view counter
- Kill trigger if 7-day cohort matches StreamAlive bot signature (views spike to cap, then flatline)

## Why this build is VURT-specific (not generic)

1. **Vault format = Frame.io, not Drive.** VURT already operates Frame.io with status tags. Reuse existing infra, no re-platforming.
2. **`#booktok-corner` is the audience-overlap channel.** Captures the BookTok-romance / DramaTok pool that's already producing dialogue edits for free (parent §7).
3. **Six-platform onboarding mirrors VURT's caption protocol.** TikTok, IG Reels, IG Stories, FB, YT Shorts, TikTok Stories — same six the captions skill enforces. Avoids the YT-omission failure mode (memory `feedback_vurt_caption_default_platforms`).
4. **AVOD-aligned pay metric.** Pays on views (parent §5) because VURT's revenue *is* views, but pilot gates on `myvurt.com` watch-minutes (parent §3 StreamAlive override).
5. **Dioni broadcast cadence is non-optional.** Founder silence is the documented #1 kill mode and is explicit in memory (`project_vurt_role` — Dioni co-leads distribution; this is her surface).
6. **Owned-IP-only vault.** No Crazy Maple license cleanup needed; clippers can permission off VURT's catalog directly (parent §11 strategic moat).
7. **No em dashes in operator broadcasts** (memory `feedback_culture_vs_community` — VURT writing rule).
8. **Captain commission bound to platform, not captain.** Pre-empts the "captain leaves with the recruits" failure mode.

---

## Confidence calibration

- **High confidence (cited / verbatim):** §1 baseline channel set (Sx Bot docs), §6 Spade 10% commission cap (Spade public referrals doc + Whoptrends summary), §7 retention kill modes (Kiip + parent doc cross-reference), §8 Spade and Clipping Club member counts and verbatim descriptions (Discord landings).
- **Medium confidence (`[pattern]` flagged):** Tier role thresholds (§2), tier-gated submission channels (§1), captain selection criteria (§6), stagger windows (§5).
- **Lower confidence (`[unverified]`):** Per-account jitter on stagger windows (§5), invisible-tracker watermark for clipper-leak attribution (§4), flat-retainer captain comp (§6), Hall of Fame lifetime-no-decay (§2). These are pulled from streamer/music adjacent ops or are extrapolations from the public-record skeleton.

The exact granular numbers (which threshold is "Tier 2 vs Tier 3," what % of CPM the multiplier exactly is, what bonus dollar amount drops on first-50) are deliberately gated by every operator at scale. VURT will have to set these — start with the bands above as defaults, A/B against retention, adjust quarterly. The architecture in this doc is the build spec; the numbers are the dials.

# VURT — Revised Social Media Strategy & Updates
### March 20, 2026
### Prepared by Dioni Vasquez

---

## PART 1: ASSET TRACKER OVERHAUL

### What's Wrong With the Current Tracker

The current Google Sheet ("VURT Social Media Production Tracker") has 8 columns across ~120 titles. Here's what it's missing:

| Gap | Impact |
|-----|--------|
| No clip-level rows | Can't track individual clips — only "3/5 clips created" as free text |
| No platform tagging | No way to know which clips are cut for TikTok vs. Reels vs. Shorts |
| No asset links | No links to the actual clip files or to the posted content online |
| No QA workflow | "QC Approved" is in Notes column, not a proper status field |
| No posting history | No record of when/where a clip was posted, or if it was posted at all |
| No performance data | Zero engagement tracking — no views, shares, saves |
| No thumbnail tracking | Thumbnails mentioned in the 5th tab but not linked to clips |
| Empty dates | Assignment Date and Due Date columns are all "m/d/yyyy" placeholders |
| No priority system | All 120 titles treated equally — no way to sequence what gets clipped first |

### Redesigned Tracker Structure

**Recommendation: Keep the existing sheet for production pipeline (Title Assignment & Status). Build a NEW sheet (or new tabs) for the social distribution pipeline.**

The production tracker answers: "Which titles have clips ready?"
The social distribution tracker answers: "What's being posted, where, when, and how is it performing?"

#### Tab 1: CLIP INVENTORY (One Row Per Clip)

| Column | Purpose | Example Values |
|--------|---------|----------------|
| **Clip ID** | Unique identifier | MC-001, MC-002 |
| **Source Title** | Film/series name | Miami Confidential |
| **Clip Name** | Descriptive name | "MC - Confrontation Scene" |
| **Clip Type** | Content category | Clip Bait / BTS / Creator Spotlight / Culture / Promo |
| **Duration** | Length in seconds | 32s, 58s, 90s |
| **Aspect Ratio** | Format | 9:16 / 1:1 / 16:9 |
| **Editor** | Who cut it | OTR / Daniel / Brad / Wayne |
| **Edit Status** | Pipeline stage | Draft → In Review → Revision → QA Approved → Ready to Post |
| **QA Reviewer** | Who approved | Dioni / Mark |
| **QA Date** | When approved | 2026-03-20 |
| **QA Notes** | Feedback | "Tighten opening 2s, add text overlay" |
| **Asset Link** | Google Drive / Dropbox link to the file | drive.google.com/... |
| **Thumbnail Link** | Link to thumbnail image | drive.google.com/... |
| **Caption Draft** | Pre-written caption | "She wasn't supposed to find out like this." |
| **Hashtags** | Platform-appropriate tags | #VURT #MicroDrama #MiamiConfidential |
| **CTA** | Call to action | "Watch the full episode → link in bio" |
| **Priority** | Posting priority | 🔴 High / 🟡 Medium / 🟢 Low |
| **Genre Tags** | For scheduling variety | Drama, Thriller, Romance, Comedy, Faith |

#### Tab 2: PLATFORM VERSIONS (One Row Per Platform Cut)

Each clip may need multiple versions for different platforms. This tab tracks that.

| Column | Purpose | Example Values |
|--------|---------|----------------|
| **Clip ID** | Links to Clip Inventory | MC-001 |
| **Platform** | Target platform | TikTok / IG Reels / YT Shorts / FB / Snapchat |
| **Platform Version Link** | Link to platform-specific cut | drive.google.com/... |
| **Specs Met** | Platform requirements | ✅ / ❌ (duration, safe zones, text placement) |
| **Sound** | Audio treatment | Original / Trending Sound / Voiceover |
| **Text Overlay** | Has text overlay? | Yes — "Watch on VURT" / No |
| **Watermark** | VURT watermark applied? | ✅ / ❌ |
| **Hook Frame** | First frame optimized? | ✅ / ❌ |

#### Tab 3: POSTING LOG (One Row Per Post)

| Column | Purpose | Example Values |
|--------|---------|----------------|
| **Clip ID** | Links to Clip Inventory | MC-001 |
| **Platform** | Where posted | TikTok |
| **Post Date** | When posted | 2026-03-20 |
| **Post Time** | Time posted (ET) | 7:30 PM |
| **Posted By** | Who posted | Christian / Alex / Dioni |
| **Post URL** | Direct link to the live post | tiktok.com/@myvurt/video/... |
| **Caption Used** | Actual caption posted | (copy from post) |
| **Status** | Post status | Scheduled / Posted / Boosted / Removed |
| **Day 1 Views** | 24-hour views | 1,200 |
| **Day 7 Views** | 7-day views | 8,500 |
| **Likes** | — | 340 |
| **Comments** | — | 28 |
| **Shares** | Most important metric | 89 |
| **Saves** | Second most important metric | 45 |
| **Profile Visits** | From post analytics | 120 |
| **Link Clicks** | Bio link clicks | 34 |
| **Boosted?** | Paid amplification | No / Yes ($50, 3 days) |
| **Previously Posted?** | Repost indicator | First post / Repost (originally 2026-03-15) |
| **Notes** | Performance notes | "Outperformed avg by 3x — reshare next week" |

#### Tab 4: CONTENT CALENDAR (Weekly View)

| Column | Purpose |
|--------|---------|
| **Date** | Calendar date |
| **Day** | Mon-Sun |
| **TikTok Slot 1** | Clip ID + time (7 AM) |
| **TikTok Slot 2** | Clip ID + time (12 PM) |
| **TikTok Slot 3** | Clip ID + time (7 PM) |
| **IG Reels** | Clip ID + time |
| **IG Stories** | Content plan (poll, countdown, BTS, etc.) |
| **YT Shorts** | Clip ID + time |
| **FB** | Clip ID + time |
| **Snapchat** | Clip ID + time |
| **X/Twitter** | Text post / quote tweet plan |
| **Theme** | Daily theme (Thriller Thursday, Faith Friday, etc.) |

### Platform-Specific Clip Cutting Specs

| Platform | Duration | Aspect | Key Requirements |
|----------|----------|--------|------------------|
| **TikTok** | 30-60s sweet spot (up to 3 min) | 9:16 | Hook in first 1.5s. Trending sounds help. Text overlays for muted viewing. End with cliffhanger cut. No other platform watermarks. |
| **IG Reels** | 30-60s (up to 90s) | 9:16 | Similar to TikTok but slightly different text placement (account for IG UI). Cover frame matters for grid. Hashtags in caption, not overlay. |
| **YT Shorts** | 30-58s (hard cap 60s) | 9:16 | Title card in first 3s. Subscribe prompt overlay. Less text-heavy than TikTok — YouTube rewards watch time over engagement bait. |
| **FB Reels** | 30-90s | 9:16 | Auto-captions critical (FB muted autoplay). Slightly older audience — less meme-y, more narrative hooks. |
| **Snapchat Spotlight** | 10-60s | 9:16 | Fastest hooks needed. Snapchat skew younger. Can reuse TikTok cuts but remove TikTok watermark. |
| **X/Twitter** | 15-60s | 9:16 or 16:9 | Quote-tweet format works. Commentary-style framing. Can be slightly longer or landscape. |
| **IG Stories** | 15s segments | 9:16 | Polls, questions, countdowns overlaid. Not clip baits — engagement tools. |

### What Editors Need to Deliver Per Title

For each title assigned, the editor delivers:

1. **3-5 clip baits** (the money shots — peak drama moments, cut at max tension)
2. **1 "full scene" cut** (60-90s complete scene that works standalone — for YouTube)
3. **1 thumbnail** per clip (key frame with text overlay, VURT brand bar)
4. **Platform-specific exports** (at minimum: TikTok version + IG version — they differ in safe zones and text placement)

**Naming convention:** `[TITLE-ABBREVIATION]-[CLIP#]-[PLATFORM].[ext]`
Example: `MC-03-TT.mp4` (Miami Confidential, Clip 3, TikTok)

---

## PART 2: CURRENT STATE ASSESSMENT (March 20, 2026)

### What's Changed Since the March 17 Audit

| Item | March 17 | March 20 | Status |
|------|----------|----------|--------|
| TikTok handle | @myvurt (1 follower, 4 videos) | Handle given up today for team transfer | ⚠️ In cooldown — monitor |
| Instagram | 324 followers, 21 posts | ~334 followers | Slow organic growth |
| YouTube | 7 subs, 4 Shorts | Same | Overtown clip still best performer at 1.1K |
| Facebook | 24 followers | Same | Stagnant |
| X/Twitter presence | Zero | 5+ organic posts from press/media accounts | Momentum from TechCrunch, not captured |
| App downloads | iOS: 11 ratings / Google Play: 10+ | Growing slowly | Need push |
| Clip production | ~20 titles in progress, 4 editors | Same | Miami Confidential, Drops of Mercy, Miami Kingpins, Fatal Lust = 5/5 clips COMPLETE |
| Social media team | SimpleSocial (Christian, Alex) | Same | Need to align on revised strategy |

### Clip Pipeline Status (from tracker)

**Ready to post (5/5 clips complete):**
- Miami Confidential (OTR) — needs Dioni notes
- Drops Of Mercy (Daniel)
- Miami Kingpins (Daniel) — Documentary, True Crime
- Fatal Lust (Daniel)

**In progress:**
- Something Like A Business (OTR) — 3/5 clips
- Church Boy, Baby Mama, Mr. Right, Crossed Lines, 35 & Ticking, Favorite Son, The Love Letter (Wayne Alford) — Revisions uploaded
- My Brother's Wife, Come Back Dad, Killer Stepdad (Brad) — Uploaded

**Not started (assigned):**
- Do It For The Gram (OTR)
- My Only Fan (OTR)
- A Twisted Affair (Daniel)
- Welcome to the A (OTR)
- Pride & Prejudice Atlanta (Brad)

**QC Approved but UNASSIGNED (60+ titles):**
- This is the biggest bottleneck. 60+ titles are QC approved and ready for clipping but have no editor assigned. These need to be prioritized and distributed.

### X/Twitter Buzz (Organic, Uncaptured)

From the X search, VURT got organic pickup from:
- **@mediagazer** — Major media aggregator, shared TechCrunch piece
- **@entrepreneur_cm** — Entrepreneurship account, shared with #Vurt tags
- **@TyCarver** — Media industry recruiter
- **@dailytechonx** — Tech news feed
- **@cvrlh** (Cyrille Varnier) — French media analyst, discussed rev model

**None of this was engaged with by a @myvurt X account.** There is no active VURT X/Twitter presence capturing this momentum. This is free distribution being left on the table.

---

## PART 3: REVISED SOCIAL MEDIA STRATEGY

### Strategic Shift: From "Cross-Post Everywhere" to "Platform-Native Distribution Machine"

The current approach — cut 4 videos, post them identically everywhere — is how you stay at 334 followers. The revised approach treats each platform as a distinct channel with its own content strategy, cadence, and success metrics.

### 3A. TikTok (60% of effort) — THE GROWTH ENGINE

**Current state:** Handle in cooldown transition. ~0 functional presence.

**Why this is job #1:** VURT is a vertical-first platform launching in the TikTok era with 1 follower on TikTok. This is the single biggest gap in the entire operation. ReelShort gets 60-70% of downloads from TikTok/Meta ads. The organic version of that playbook is clip baits.

**Revised Strategy:**

**Content mix (3-5 posts/day once handle is secured):**

| Content Type | % of Posts | Format | Goal |
|-------------|-----------|--------|------|
| Clip Baits | 50% | 30-60s peak drama moments, cut at cliffhanger | Drive app installs |
| Culture Commentary | 20% | "If [trending topic] was a VURT micro-drama" / stitches / duets | Ride algorithm waves |
| Creator/Cast Spotlights | 15% | BTS, cast reacting to scenes, "how we made this" | Build parasocial connection |
| Community/UGC | 15% | Fan theories, "what happens next?", reaction reposts | Drive comments + saves |

**Clip Bait Formula (this is the money move):**
1. Open with the most visually/emotionally arresting 2 seconds
2. Let drama play for 30-50 seconds
3. CUT at exact peak tension (the slap, the reveal, the betrayal)
4. Text overlay: "Watch the full episode on VURT"
5. Pinned comment: "Link in bio 🔗"
6. Sound: trending audio when mood-appropriate, original dialogue when the scene is strong enough

**Posting schedule:**
- Slot 1: 7-9 AM ET (morning scroll)
- Slot 2: 12-1 PM ET (lunch break)
- Slot 3: 7-10 PM ET (prime time — highest Black audience engagement)

**Priority titles for TikTok launch (high-drama, clip-bait-friendly):**
1. Miami Confidential — 5/5 clips ready, Miami setting, drama
2. Fatal Lust — 5/5 clips ready, title alone is algorithm bait
3. Miami Kingpins — 5/5 clips ready, true crime (trending genre)
4. Killer Stepdad — thriller, viral-title potential
5. Girl In The Closet — suspense, curiosity-gap title
6. Pretty Kitty Cartel — crime drama, strong hook potential
7. Soul Ties — relationship drama, culturally resonant
8. Devil You Know — thriller, perfect for "who can you trust?" hooks

### 3B. Instagram (25% of effort) — THE COMMUNITY HUB

**Current state:** 334 followers, 21 posts. Best channel but under-leveraged.

**Revised Strategy:**

| Content Type | Cadence | Purpose |
|-------------|---------|---------|
| Reels | 1-2/day | Re-edited TikTok clips (adjust safe zones, cover frame for grid) |
| Stories | 5-10/day | Polls ("who's the villain?"), countdowns to new drops, BTS candids, cast takeovers, link stickers |
| Carousels | 2-3/week | Character breakdowns, "5 reasons to binge [title]", creator spotlights with stills |
| Feed Posts | 1/week | Premium brand moments — new series announcements, press features, milestone celebrations |
| Broadcast Channel | Launch ASAP | Exclusive drop announcements, behind-the-scenes, direct fan communication |

**Instagram-specific tactics:**
- **Broadcast channel** — Instagram's most underused feature. Create "VURT Insiders" channel for episode drop alerts + exclusive content. This goes to top of followers' DMs.
- **Collab posts** with cast members' personal accounts — doubles reach
- **Instagram Lives** with cast — goes to top of followers' feeds
- **Story highlights** organized by series (each series gets a highlight reel)
- **DM engagement** — reply to EVERY DM for the first 6 months. 1:1 relationships compound.

### 3C. YouTube Shorts (10% of effort) — THE DISCOVERY ENGINE

**Current state:** 7 subs, 4 Shorts. Overtown clip hit 1.1K views organically — proof of concept.

**Revised Strategy:**
- Upload 1-2 Shorts/day (repurpose TikTok clips with YouTube-specific optimization)
- **Full first episodes as Shorts** — free sample model. Let people watch Episode 1 of a series as a YouTube Short, then drive them to the app for more
- Cultural/historical content (Overtown, Liberty City, Miami stories) — already proven to work
- **Compilation Shorts** — "Best moments from [title]" as 58-second supercuts
- YouTube rewards watch time more than engagement bait — let scenes breathe slightly longer than TikTok cuts

### 3D. X/Twitter (5% of effort) — THE CONVERSATION LAYER

**Current state:** No presence. Organic press coverage happening without engagement.

**Immediate action:** Secure @myvurt on X (or @VURTapp / @WatchVURT if taken)

**Strategy:**
- React to cultural moments and connect to VURT content
- Quote-tweet press coverage with founder perspective
- Thread format: "The story behind [series] 🧵"
- Engage directly with journalists, entertainment writers, media industry accounts
- Live-tweet during series drops with cast
- **This is the cheapest channel** — text-based, personality-driven, no production required

### 3E. Facebook (Secondary) & Snapchat (Sleeper)

**Facebook:** Maintain presence, cross-post Reels, target 40+ female demo (VURT's current core audience). This audience is on Facebook more than TikTok. Don't ignore them — they're the early adopters keeping the platform alive.

**Snapchat:** Already actively maintained (@myvurt has Spotlight content). Keep posting. Snapchat Spotlight pays creators directly — potential revenue source while building audience. Promote the Snapchat handle on other platforms.

---

## PART 4: CONTENT PRIORITIZATION FRAMEWORK

### Not All 120 Titles Are Equal

With 60+ titles QC approved and waiting for clips, you need a system to decide what gets clipped first. Here's the framework:

#### Priority Score (Rate each title 1-5 on these factors, total /25)

| Factor | Why It Matters | Weight |
|--------|---------------|--------|
| **Star Power** | Recognizable talent = built-in audience + press hooks | 5 |
| **Title Virality** | Does the title alone make you want to click? | 5 |
| **Genre Heat** | Is this genre trending on social? (Thriller > Faith right now) | 4 |
| **Clip-Bait Potential** | Does it have 3-5 scenes that work as standalone 30-60s clips? | 5 |
| **Cultural Resonance** | Does it speak specifically to VURT's audience? | 3 |
| **Uniqueness** | Is this something only VURT has? | 3 |

#### Tier 1: Lead With These (Score 20+)

Based on the talent list and available data:

| Title | Why It's Tier 1 |
|-------|----------------|
| **Girl In The Closet** | Curiosity-gap title, thriller, clip-bait heaven |
| **Pretty Kitty Cartel** | Crime drama, edgy title, viral potential |
| **Fatal Lust** | Already clipped (5/5), title is algorithm bait |
| **Miami Kingpins** | True crime/documentary, already clipped (5/5), Miami identity |
| **Miami Confidential** | Already clipped (5/5), Miami identity, drama |
| **Soul Ties** | Culturally resonant title, relationship drama |
| **Devil You Know** | Thriller, universal hook |
| **Killer Stepdad** | Thriller, shock-value title, clip-bait potential |
| **Lil Duval - Living My Best Life** | Name recognition (Lil Duval has 10M+ IG followers) |
| **Fell In Love With A Fed** | Perfect TikTok title — tells a story in 6 words |
| **One Night In Lagos** | International appeal, Nollywood crossover, unique to VURT |

#### Tier 2: Strong Pipeline (Score 15-19)
35 & Ticking, Baby Mama, Come Back Dad, Double Deception, Framed By My Ex, Champagne, Dangerous Ties, Thug Holiday, etc.

#### Tier 3: Backlog (Score <15)
Holiday titles (hold for Q4), faith titles (hold for Sundays), romance-heavy titles without strong hook potential.

### Title-to-Platform Matching

Not every title works on every platform. Match content to where it'll perform:

| Genre | Best Platform | Why |
|-------|--------------|-----|
| Thriller / Crime | TikTok, YT Shorts | Cliffhanger cuts thrive on these |
| Romance / Drama | IG Reels, Facebook | Emotional content performs here |
| Comedy | TikTok, Snapchat | Humor is shareable on these |
| Faith / Inspirational | Facebook, IG | Older demo, share-heavy |
| Documentary / True Crime | YouTube, TikTok | Discovery + deep engagement |
| International (Nollywood) | TikTok, IG | Diaspora audiences are highly active |
| Horror | TikTok, YT Shorts | Horror clips go viral (reaction content) |

---

## PART 5: CONTENT CALENDAR FRAMEWORK

### Weekly Rhythm

| Day | Theme | TikTok (3x) | IG (1 Reel + Stories) | YT Shorts | X |
|-----|-------|------------|----------------------|-----------|---|
| **Mon** | New Week Drop | Clip bait (new title) + 2 supporting | Reel + "New this week" Stories | 1 Short | Announce new content |
| **Tue** | Thriller Tuesday | 3 thriller/crime clips | Reel + poll ("who did it?") | 1 Short | Quote-tweet cultural moment |
| **Wed** | Creator Wednesday | BTS + creator spotlight + clip bait | Creator carousel + Story takeover | Creator interview clip | Thread: creator story |
| **Thu** | Throwback / Deep Cut | 3 clips from catalog titles | Reel + "have you watched?" Stories | 1 Short | — |
| **Fri** | Fan Friday | UGC + community + 2 clip baits | Reel + fan feature Stories | 1 Short | Engage fan accounts |
| **Sat** | Weekend Binge | 3 best-performing clips (reshare) | Reel + "weekend watchlist" carousel | 1 Short | — |
| **Sun** | Culture Sunday | Culture commentary + faith title + clip bait | Reel + Sunday Stories | 1 Short | Cultural commentary tweet |

### Monthly Milestones

| Week | Focus |
|------|-------|
| Week 1 | New title launches, fresh clip baits |
| Week 2 | Creator spotlights, BTS content push |
| Week 3 | Community engagement push (polls, fan theories, challenges) |
| Week 4 | Performance review + top content reshare + next month planning |

---

## PART 6: DISTRIBUTION FORCE MULTIPLIERS

### 6A. The "Clip Bait to App Install" Funnel

This is the core growth mechanic. Every post exists to move people down this funnel:

```
Social clip (TikTok/Reels/Shorts)
    → Profile visit (bio must be airtight)
        → Link click (Linktree or direct to app store)
            → App install
                → First watch
                    → Retention (push notifications, new drops)
```

**Bio optimization (every platform):**
- Line 1: "Stories told OUR way. Built for the culture."
- Line 2: "New episodes every week 🎬"
- Line 3: "Watch free → [link]"
- Link: Smart link that routes to App Store (iOS) or Google Play (Android) based on device

### 6B. Leverage Existing Talent Networks

VURT has recognizable names on the platform. This is an underused asset.

| Talent | Following | Activation Play |
|--------|-----------|----------------|
| **Kevin Hart** | 180M+ across platforms | Even a single repost or mention = nuclear reach |
| **Vivica A. Fox** | 5M+ IG | Collab post on her content on VURT |
| **Lil Duval** | 10M+ IG, 3M TikTok | His comedy audience = VURT's growth demo |
| **T.I.** | 14M+ IG | Culture credibility + reach |
| **Meagan Good** | 11M+ IG | Core demo alignment |
| **Trick Daddy** | 2M+ IG | Miami native, Ted Lucas connection |
| **Rotimi** | 5M+ IG | Power/Starz audience crossover |

**The play:** Don't ask for endorsements. Send them their own clips, formatted for their platforms, with a caption suggestion. Make it easy for them to repost. One repost from any of these people is worth months of organic posting.

### 6C. Press Momentum (Capture What's Already Happening)

VURT got TechCrunch, Yahoo Tech, REVOLT, Mediagazer, and 5+ other outlets in the first week. This press wave is still warm but cooling fast.

**Immediate actions:**
1. Pin TechCrunch article repost on every platform
2. Create a "As Seen In" carousel for IG (logos: TechCrunch, Yahoo, REVOLT, etc.)
3. Add press logos to app store screenshots
4. Quote-tweet/reshare every organic press mention from X
5. Send clips to entertainment podcasts for coverage (The Read, Breakfast Club, Shade Room)
6. Pitch follow-up stories: "2 weeks post-launch" metrics, creator stories, culture angle

### 6D. Creator Pipeline as Distribution

Every creator who submits content to VURT becomes a distribution node.

**The system:**
1. Creator submits to submissions@myvurt.com
2. Content goes through QC
3. If accepted → creator gets clip baits cut from THEIR content
4. Creator posts the clips on THEIR channels with VURT tag
5. Creator's audience discovers VURT through authentic content, not ads

This is the Brat TV model that took them from 0 to 5M subs. Cast the creator, arm them with clips, let their audience do the distribution.

---

## PART 7: IMMEDIATE ACTION ITEMS (Next 7 Days)

### Handle Situation (Today)

- [ ] Monitor @myvurt TikTok handle — team member should check every few hours to claim it
- [ ] If unclaimed after 48 hours, have the team member try claiming from a fresh device/browser
- [ ] Backup plan: if handle is permanently lost, register @WatchVURT or @VURTapp
- [ ] Secure @myvurt on X/Twitter immediately (separate from TikTok issue)

### Asset Tracker (This Week)

- [ ] Build the new tracker tabs (Clip Inventory, Platform Versions, Posting Log, Content Calendar) — I can build these as a new Google Sheet or as new tabs in the existing sheet
- [ ] Backfill completed clips (Miami Confidential 5/5, Drops of Mercy 5/5, Miami Kingpins 5/5, Fatal Lust 5/5) into the Clip Inventory
- [ ] Add asset links to every completed clip in Google Drive
- [ ] Apply priority scoring to the 60+ unassigned QC-approved titles
- [ ] Assign the top 10 priority titles to editors

### Content Production (This Week)

- [ ] Dioni: review Miami Confidential 5/5 clips (flagged as "Dioni notes needed")
- [ ] Get platform-specific versions cut for the 4 completed titles (20 clips × at minimum TikTok + IG = 40 platform cuts)
- [ ] Write captions for the first 20 clips
- [ ] Create 1 "As Seen In" press carousel for IG

### Social Strategy Alignment (This Week)

- [ ] Brief SimpleSocial team (Christian, Alex) on revised strategy — they need to understand the shift from cross-posting to platform-native content
- [ ] Align on posting cadence: minimum 3x/day TikTok, 1-2x/day IG Reels, daily Stories, 1x/day YT Shorts
- [ ] Set up content calendar for Week 1 (March 24-30)
- [ ] Create IG Broadcast Channel "VURT Insiders"
- [ ] Launch X/Twitter presence

---

## PART 8: QUESTIONS THAT WOULD SHARPEN THIS FURTHER

Before finalizing implementation, these would help:

1. **SimpleSocial's scope** — What exactly is Christian and Alex's current workflow? Are they scheduling/posting, or also cutting clips? Do they have their own content creation capacity or are they just distribution?

2. **Editor capacity** — Can OTR/Daniel/Brad/Wayne handle more titles simultaneously, or are they maxed? Do we need more editors?

3. **Budget for paid amplification** — Is there any budget allocated for TikTok Spark Ads or Meta retargeting? Even $50-100/day on top organic performers would accelerate dramatically.

4. **Talent relationships** — Does Mark or Ted have direct lines to the talent on the platform (Kevin Hart's team, Vivica's team, Lil Duval)? The repost strategy only works if someone can actually reach them.

5. **Content calendar ownership** — Who is the single person responsible for the daily posting schedule? This can't be committee-driven.

6. **Analytics access** — Is the GA4 property access issue resolved? Without analytics, we can't measure the funnel from social → app install → first watch.

7. **Discord** — The invite link is still broken. Is there a plan to build a Discord community, or is that deferred?

8. **Influencer seeding** — Any existing relationships with Black entertainment media (Shade Room, Blavity, Culture Crave) for features or partnerships?

---

## APPENDIX: MARKET CONTEXT (Why This Matters Right Now)

### The Window

- Global microdrama market: $11B in 2025, projected $14B by end of 2026 [^1]
- ReelShort: ~$1.2B gross consumer spending projected 2025
- Disney+, Peacock, Netflix all pivoting to vertical in March 2026
- Micro-drama viewers are "super-consumers" — they watch significantly more video overall than average audiences [^2]
- No micro-drama platform has meaningful community infrastructure
- The industry spends up to 90% of budget on paid user acquisition — organic social is the arbitrage

### VURT's Unfair Advantages (Use These in Every Post)

1. **Free to watch** — everyone else charges per episode
2. **50/50 revenue split** — best creator economics in the category
3. **48-72 hour turnaround** on submissions — no other platform is this fast
4. **Cultural identity** — not a content vending machine, a movement
5. **Real talent** — Kevin Hart, Vivica A. Fox, Meagan Good, T.I., Lil Duval
6. **Founder credibility** — Slip-N-Slide Records (30M+ records), Swirl Films, Oscar-nominated producers

### What ReelShort Does That VURT Should Study (Not Copy)

ReelShort's social strategy is industrial-scale clip baiting:
- They post 10-20 TikToks/day across multiple accounts
- Each clip is a 30-60 second scene that ends at maximum tension
- They use "Part 1 of 50" format to signal depth
- Comments sections are full of people begging for the next episode
- They boost top organic performers with Spark Ads ($5-15 CPM)

VURT shouldn't copy this — the content is generic romance, the brand is invisible. But the clip bait MECHANIC is proven. Apply it with VURT's cultural identity and you have something ReelShort can't replicate.

---

*This document is a living strategy. Update as decisions are made and results come in.*

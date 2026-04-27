# VURT Caption Winning Patterns — Evidence-Based

Updated: 2026-04-23 from vurt-daily-2026-04-22 data pull. Refresh after each daily report.

These are **patterns that proved themselves**, not theory. Clone the structure when writing new captions. Do not invent new structures until you have data saying they beat these.

---

## TikTok Save Leaderboard — the 4 posts that cleared 1%

Save% is the strongest re-surfacing signal on TikTok. Out of 29 @myvurt posts with ≥100 views, only 4 crossed the 1% threshold:

| # | Caption opener | Views | Saves | Save % | Pattern |
|---|----------------|------:|------:|-------:|---------|
| 1 | "I keep waiting for Spence to leave. Because I can't wrap my…" (Come Back Dad — Tatyana Ali monologue) | 1.1K | 28 | **2.47%** | 1st-person inner monologue, confession tone, no setup |
| 2 | "She just told the judge he was a client. In open court. With…" | 569 | 8 | **1.41%** | Courtroom reveal, staccato sentences, escalation |
| 3 | "When your father announces your future at dinner. And calls…" | 283 | 3 | **1.06%** | Generational/legacy stakes, "when your [family]" hook |
| 4 | "Uncle 3D turned a little league pep talk into a whole coach…" | 691 | 7 | **1.01%** | Character-name hook, ordinary-moment-flips-to-stakes |

### What every winner has in common

1. **One voice, one stake.** Either a character's inner thought OR a single observable action. Never summarize the whole scene.
2. **Staccato sentence rhythm.** Short. Short. Slightly longer. Cuts like thought, not narration.
3. **Family, legal, generational, or relational stakes.** Marriage ("I can't wrap my"), courtroom exposure, father's dinner announcement, uncle-coach dynamic. These are the themes saving.
4. **Character specificity.** Spence. Uncle 3D. "The judge." Named or role-specific, never "a man" or "someone."
5. **No VURT brand line in the hook.** The show sells itself. CTAs go at the end, not the top.
6. **Open-loop, not closure.** Every winner leaves a question the viewer has to come back to resolve. Never summarize what happened — hand the viewer the hook and force them to finish it in the clip or on the site.

### Anti-patterns (things that killed on TikTok — <0.5% save)

- VURT-at-the-station type captions ("VURT live at 99 Jamz. The same station…") — 0.73% save despite views
- "The audience voted to handle it themselves…" — meta-format description, 0.85% save
- Actor / director UGC shoutout captions (Nicki Micheaux reel type, 1 view range) — readers don't save talent attribution

---

## Instagram Top Reach — winners vs losers (7d)

| Rank | Caption | Reach | Saves | Shares | Type |
|------|---------|------:|------:|-------:|------|
| 1 | "The rule. The one they swore they'd keep…" | **5,917** | 58 | 33 | Clip Reel, Favorite Son (Pastor Wilson / the promise broken) |
| 2 | "I am more than your party planner. I am your…" | **3,887** | 18 | 24 | Clip Reel, character declaration |
| 3 | "Vanity handles business. Avery can't even order…" | **2,678** | 15 | 5 | Clip Reel, character contrast |

vs. losers:

| Caption | Reach |
|---------|------:|
| "Verticals are here. Stories are evolving. VUR…" (brand carousel) | **41** |
| "VURT Filmmakers Spotlight: Racheal Leigh Prod…" (director photo) | **175** |
| "Straight from the director. Racheal Leigh bro…" | **254** |
| "The pastor called it destiny. Only one person…" | **490** |

### IG pattern readout

- **Clip reels with character-rooted captions are 20–140× the reach of brand posts and director spotlights.**
- "The rule." was the single best post of the week across IG *and* the template is free to reuse: declarative opening sentence fragment + implied betrayal. The 58 saves + 33 shares proves it's not a fluke — users wanted to bookmark and send.
- **Kill or reduce on IG:** brand narrative carousels, director headshot spotlights as standalone, "Verticals are here" style conceptual posts. If it's not in-world, it's not earning reach.
- Director spotlights belong on **LinkedIn**, not IG main feed. If they go to IG, tuck in Stories only.

---

## Facebook Pattern — it's a paid-ads channel, not an organic algo channel

**CORRECTION (verified via Graph API 2026-04-23):** Earlier notes claimed FB "Recommended feed" drove 98% of views. That was wrong — the script's `(total − organic)` bucket was labeled "Recommended" but it's actually **paid ads**.

- 14-day FB page: **447,266 video views total → 439,260 PAID (98.2%) / 8,006 ORGANIC (1.8%)**.
- **Apr 17 "double-drop" spike was not a double-drop win:** 75,719 views that day = **74,871 paid / 848 organic**. The two actual organic posts ("He tried to return a phone" / "Vanity runs the room") scored 22 and 77 views respectively. Spike is ad spend, not content cadence.
- Organic FB page distribution is effectively dead (avg ~570 organic views/day across the whole page).
- **GA4 confirms the quality problem:** fb/paid_ads delivered 73,436 sessions at **4.9% engagement** in 14d. That's not a content channel, that's a landing-page stress test.

### FB directive (revised)
- Stop framing FB posts as "feed the Recommended algo." There is no Recommended algo for us at this page size — there is paid traffic we buy and a trickle of organic from followers.
- Keep `myvurt.com` clickable in line 1 (still true — this is the only surface where the link actually routes in-feed).
- FB posting cadence is mostly a hygiene exercise to keep the page active for ad attribution, not a reach play. Reallocate editorial attention accordingly.
- If we want FB to become an organic channel, we need Reels distribution testing (different surface) — don't chase the old "Recommended" number; it was always paid.

---

## YouTube Pattern — catalog clip breakouts, not full-episode premieres

**CORRECTION (verified via YouTube Data API 2026-04-23):** Earlier notes called the top 3 lifetime videos "full-episode premieres." That was wrong on two counts:
1. None of the 42 uploads use YouTube's actual **Premiere** feature (no `liveStreamingDetails` on any video). "A VURT Premiere" is a title label, not the YT Premiere scheduling product.
2. None are full episodes. All three breakouts are **sub-3-minute catalog clips**: Come Back Dad (2:30, 166K, pub 2026-04-09), SLAB (0:56, 74.7K, pub 2026-04-13), SLAB (1:01, 40.5K, pub 2026-04-16).

### Real YT shape (all 42 uploads, 14d publishes)

| Clip | Dur | Views | Pub | Label |
|------|----:|------:|-----|-------|
| Come Back Dad | 2:30 | **166,366** | 2026-04-09 | "Premiere" (catalog clip) |
| SLAB | 0:56 | **74,717** | 2026-04-13 | "Premiere" (catalog clip) |
| SLAB | 1:01 | **40,495** | 2026-04-16 | "Original" |
| SLAB | 1:04 | 2,634 | 2026-04-17 | "Original" |
| Come Back Dad | 1:00 | 2,487 | 2026-04-14 | "Premiere" |
| 35 & Ticking "phone you told me was dead" | 0:59 | 1,847 | 2026-04-22 | "Original" |
| Favorite Son | 0:43 | 1,127 | 2026-04-21 | "Premiere" |
| 35 & Ticking | 0:26 | 686 | 2026-04-20 | "Premiere" |
| Bride to Be | 0:37 | 585 | 2026-04-22 | "Original" |
| Love Network Jam | 0:36 | 498 | 2026-04-14 | "Premiere" |

Median recent clip: ~600–1,500 views. The 3 breakouts (166K / 74K / 40K) are outliers, not a repeatable "premiere format wins" pattern. The common feature isn't "full episode" — they're short clips pulled from named shows that hit the Shorts algorithm.

### YouTube directive (revised)

- **Current cadence works, reframe the vocabulary.** Dioni is posting catalog clips (older, pulled from back-cat) in the morning and "premiere" clips (newer, spotlight-eligible) in the afternoon. That's a fine schedule — just don't claim these are YouTube Premieres, because they aren't.
- **Use YT's actual Premiere feature for originals.** If we want scheduling + countdown + live-chat lift, upload as Premiere, not regular upload with a "Premiere" title. That's a cheap test worth running.
- **Full episodes haven't been tested on YT yet.** We can't claim "full episodes win" because we haven't published any. If the business case is to drive myvurt.com, full episodes on YT are a cannibalization risk; if the business case is channel growth, they're a growth lever. Decide first, then test.
- **Named show + named talent in every title.** The breakouts all have it (Come Back Dad / SLAB). Keep this non-negotiable for the search compound effect (see Organic Search findings below).
- **Description gets show name, director, cast, genre keywords, `myvurt.com`.** Already in the 6-platform rule, re-asserting here.
- Treat the 166K / 74K outliers as **data points**, not the baseline. Don't set volume targets against them — they're one or two Shorts-feed surges, not a reproducible output of the format.

---

## Peak posting windows (ET)

Based on 7-day engagement patterns across IG + FB + TikTok:
- **11AM ET** (commute + lunch-break scroll)
- **1AM ET** (late-night insomnia scroll, highest save-rate window)
- **9PM ET** (prime evening scroll)

Post **60–90 minutes before** each peak to ride the curve up.

---

## Why save rate is the TikTok KPI (not the only one, but the leading indicator)

Save rate on TikTok is the highest-signal metric for VURT *specifically* because we sell episodic content that lives on another site. Reasoning:

1. **Saves are intent-to-return.** A like says "this passed my For You filter." A save says "I'm coming back for more of this." For a multi-episode drama whose next step is "go watch on myvurt.com," the save is the closest free signal to the intent we actually care about.
2. **Saves outperform other TikTok signals as re-distribution inputs.** TikTok's algo weights save rate heavily when deciding whether to push a video to a second and third wave of For You. A clip that gets 1,000 views + 28 saves (2.8%) will get re-surfaced; 1,000 views + 100 likes + 3 saves typically won't.
3. **Shares and F2F aren't reliable proxies yet at our volume.** Share rate gets noisy below 2,000 views per post, and "followers from non-followers" needs dev API access we don't have yet (submitted Apr 16, still in review). Save rate is the one we can measure today and compare across 29 posts.
4. **Save rate survives the top-of-funnel trap.** High-view / low-save posts are the classic "algo got confused" pattern — big FYP blast that nobody wanted to remember. We have examples: VURT/99 Jamz at 0.73%, "audience voted" at 0.85%. Removing these from the rotation doesn't cost us returning viewers; keeping them costs us future reach.

**Not the only KPI.** Watch-time ratio (avg watch / video length) matters too, especially for 45-60s clips. When the dev API unlocks, we'll add F2F conversion and completion rate per post. Until then, save rate is the primary and watch-time is the tiebreaker.

**Threshold:** 1.0% save rate = "worth cloning the structure of." Under 0.5% = "study the anti-pattern, don't repeat it." Between is "post again in a variant before deciding."

---

## Clone vs Experiment — 70/20/10 split

The concern: "if we only clone the 4 winners, we stop learning." Correct. But if we only experiment, we burn the FYP budget on unvalidated structures. The answer is a mixed portfolio, not a binary.

### The split (per week of TikTok + IG clips)

- **70% CLONE.** Each post maps to one of the 4 proven winner structures (inner-monologue, courtroom-reveal, generational stakes, character-name hook). This is the floor we don't drop below. Pattern is forced; the show/character specifics vary.
- **20% ADJACENT EXPERIMENTS.** New hooks *near* winners — e.g., "sibling" instead of "father" in generational stakes; "doctor" instead of "judge" in professional-reveal; "first-person observer" instead of first-person protagonist. These are hypothesis-driven: each experiment post has a written one-line hypothesis (e.g., "hypothesis: sibling-betrayal saves as well as father-announces-future because both tap family-legacy stakes"). Track save rate against the matching clone winner.
- **10% WILD.** Something outside the known pattern space — a visual-only post with no dialogue opener, a trend-audio experiment, a character-POV switch. This exists to detect what we don't yet know. Assume most of these will lose; keep one slot open anyway.

### Rules for experiments to count as "counted, not lazy"

- Every experiment post logs a one-line hypothesis before posting.
- A test runs with **≥3 posts** before it's judged. A single post isn't evidence either way.
- Winning criterion: save rate ≥ the matching clone winner, or ≥ 1.0% absolute. A tie with the clone is a win (we found a second pattern; it earns cloning privilege next month).
- Losing experiments get documented in a "what we tried and it didn't beat the clone" log so we stop re-running dead structures quietly.

### Monthly pattern review

Once a month, rank all experiments that hit the ≥3-post threshold by save rate. Any that beat the weakest current clone winner → promoted into the 70%. Any that beat none → archived with the hypothesis that failed, so we don't reinvent it.

This way: we hold the floor with proven structures, we keep 30% of our test budget on active learning, and every experiment generates a yes/no data point rather than vibes.

---

## What to copy into every new caption brief

1. Which TikTok winner pattern am I cloning, OR what's the one-line experiment hypothesis? (70/20/10 slot declared at brief-time.)
2. Is the IG version a clip reel with an in-world character line? (If not, fix it.)
3. Did I write the TikTok upper-third title overlay? (Required every time.)
4. Is the YT version labeled correctly (catalog clip vs actual YT Premiere product, not just a title label)?
5. Did I put the myvurt.com link first on FB? (Still required even though FB is mostly paid right now.)
6. Did I include show + cast + director names for the organic-search compound effect?
7. **Does every caption contain an open-loop hook?** Question form ("What would you do?", "Who else saw this coming?"), unresolved stakes ("Nobody saw it coming"), or invited judgment ("Is she wrong?"). Summaries kill comments — when captions became summary this week, median comments dropped **71%**. A question in the caption is the cheapest comment driver we have.
8. **Does the caption have an explicit share CTA?** At least one of: "Tag someone who'd lose it at this," "Send this to [relationship — your sister / your group chat / the friend who swore she'd never]," "Share if you've seen this happen." Shares re-enter someone else's feed — every share doubles reach for free. We're at 635 this week. Every reel without a share CTA is leaving shares on the table.

---

## Missed opportunities flagged in the data (refreshed 2026-04-23)

- **Girl in the Closet — BINGE MACHINE, ZERO SOCIAL.** Mux 14d: 13,131 views on Ep1 at **68% completion**, then Eps 2-7 run **91–93% completion** (highest of any show on the platform). Translation: when people start it, they finish the whole season. Still **not in active social rotation.** This is the #1 untapped clip source on the catalog — pull clips now.
- **Come Back Dad — also a binge completer.** Eps 1-7 run 80–93% completion in Mux. Social is posting to it but we can go deeper — the Tatyana Ali / "Spence" monologue is the proven TikTok winner (2.47% save).
- **Favorite Son — proven on social, under-distributed on player.** Ep1 only has 1,014 Mux views but 58% completion. The "the rule they swore" IG reel did 5,985 reach / 58 saves / 34 shares. We need more Favorite Son clips + a clearer player path for the traffic it's earning.
- **Organic Search is tiny but golden.** GA4 14d: google/organic 326 sessions at 55.2% engagement; google-play/organic 410 at **88.8% engagement**. Total organic search is <700 sessions/14d, but it's the highest-quality bucket we have. Captions with cast/director/show names compound here — never strip them.
- **Paid Social is burning money on low-engagement pages.** karma-in-hells landing = 53,609 sessions / **2.0% engagement**; killer-stepdad = 10,926 / 3.8%; baby-mama = 2,525 / 3.5%. Flag for Simple Social: either the creative or the destination page (or both) is broken on those titles. Compare to come-back-dad 18.5%, love-network-jam 48.3%, parking-lot 68.4% — those are working, but ads aren't pointed at them.

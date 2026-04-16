# VURT Deep Data Insights
### April 14, 2026 — Compiled from GA4, NPAW/Youbora, Meta Graph API, YouTube API, Social Cache

---

## INSIGHT 1: Fastly is Destroying Your Completion Rates (and Youbora May Be Inflating the Problem)

**The single most impactful thing in your data right now.**

| CDN | 7d Views | Buffer Ratio | Errors |
|-----|----------|-------------|--------|
| **Fastly** | **8,329** | **63.8%** ⚠️ | 11 |
| CloudFlare | 6,892 | 1.7% | 27 |
| Unknown | 2,683 | 0.1% | 11 |

Fastly handles 45% of your video traffic and has a **63.8% buffer ratio** — meaning viewers are buffering more than half the time they're watching. CloudFlare is at 1.7%. That's a **37x difference** in streaming quality on the same content, same videos, same audience.

**Why this matters for Mux vs Youbora:** Your dev team said Mux's dashboard shows considerably lower buffer rates. They're probably right — and here's why:

- Youbora measures buffer ratio as `time_buffering / (time_buffering + time_playing)`. If Fastly causes a long initial buffer before playback even starts, Youbora counts that entire wait. Mux may measure "rebuffer percentage" differently — often excluding initial load.
- Youbora may also be double-counting: if a viewer rage-quits during a buffer stall and reloads, that's two high-buffer sessions counted separately.
- The 63.8% on Fastly is likely real buffering, but the *aggregate* number (25-30% daily average) is dragged up massively by Fastly while CloudFlare streams are clean.

**Recommendation:** Before dropping Youbora entirely, ask the dev team to:
1. **Route 100% of traffic to CloudFlare for 48 hours** and compare Youbora vs Mux numbers. If they converge at ~2%, the "discrepancy" was always Fastly, not Youbora's methodology.
2. If they still diverge after Fastly is removed, *then* Youbora's measurement is the problem and Mux is the move.
3. Either way, **kill Fastly immediately**. It's actively driving viewers away.

**Estimated impact:** Your overall completion rate is ~15%. If Fastly's buffering is causing even 30% of abandonment on its 45% traffic share, fixing this alone could lift completion rates to ~20-22% — a 40%+ improvement without changing any content.

---

## INSIGHT 2: Your Organic Users Are 4-5x More Valuable Than Paid — But You're Spending on the Wrong Audience

**Fresh GA4 data (7d ending April 13):**

| Channel | Users | Sessions | Engagement Rate | Avg Duration | Bounce Rate |
|---------|-------|----------|----------------|-------------|-------------|
| Paid Social | 11,814 | 12,877 | **10.7%** | **34s** | **89.3%** |
| Direct | 1,112 | 1,708 | **51.9%** | **8m 0s** | **48.1%** |
| Organic Search | 208 | 344 | **66.0%** | **80m 4s** | **34.0%** |
| Organic Social | 309 | 355 | **38.3%** | **1m 24s** | **61.7%** |
| Referral | 28 | 105 | **59.0%** | **8m 58s** | **40.9%** |

**The math:**
- Paid Social: 11,814 users × 10.7% engagement = **~1,264 engaged users**
- Direct: 1,112 users × 51.9% engagement = **~577 engaged users**
- Organic Search: 208 users × 66.0% engagement = **~137 engaged users**

Paid is delivering volume, but **89% of paid users bounce immediately**. Direct users stay 14x longer (8 min vs 34 seconds) and engage at 5x the rate.

**What this tells you for investor conversations:**
- Your *real* user base — the people who actually watch content — is ~750-800 weekly engaged users from organic/direct channels
- Paid is a firehose that makes the DAU number look good (12K weekly) but the engagement rate (10.7%) tells you those aren't real viewers yet
- When paid stops (like it did March 31 → DAU cratered from 589 to 171), you see the true organic floor

**Actionable:** The paid social campaigns are useful for awareness, but the current targeting is bringing in people who land and leave. The geo data (below) shows why.

---

## INSIGHT 3: Trinidad & Tobago and Nigeria Are Paid Traffic Sinkholes

**Geo breakdown (7d):**

| Country | Users | Engagement Rate | Bounce Rate | Sessions/User |
|---------|-------|----------------|-------------|---------------|
| **United States** | 4,620 | **27.3%** | 72.7% | 1.18 |
| **Trinidad & Tobago** | 2,468 | **11.9%** | 88.1% | 1.26 |
| **Nigeria** | 2,444 | **3.7%** | 96.3% | 1.05 |
| **Kenya** | 1,112 | **6.5%** | 93.5% | 1.10 |
| South Africa | 456 | 12.2% | 87.8% | 1.07 |
| United Kingdom | 389 | 26.3% | 73.7% | 1.17 |
| **India** | 126 | **65.7%** | 34.3% | 3.10 |
| Jamaica | 19 | 58.3% | 41.7% | 1.26 |

**Nigeria:** 2,444 users with a **96.3% bounce rate** and **3.7% engagement**. That's ~90 engaged users out of 2,444. These are almost certainly coming from paid campaigns with broad African targeting.

**Trinidad & Tobago:** 2,468 users, 88% bounce. Better than Nigeria but still mostly wasted spend.

**Meanwhile India (126 users, 65.7% engagement, 3.1 sessions/user) and Jamaica (19 users, 58.3% engagement) are tiny but ridiculously engaged.** The UK mirrors US quality at 26.3%.

**The move:** If Simple Social is still running ads, the targeting should be:
- **Tier 1 (invest):** US, UK, Jamaica, Caribbean diaspora, India
- **Tier 2 (test):** South Africa, Trinidad (with tighter interest targeting)
- **Exclude:** Nigeria, Kenya, Ghana, Tanzania, Uganda — these are inflating DAU but contributing almost nothing to watch time

This alone could flip your paid engagement rate from 10.7% to potentially 20-25% by eliminating the bottom-of-funnel waste.

---

## INSIGHT 4: "Come Back Dad" Is Your Breakout — and the Data Proves a Specific Content Formula

**YouTube (14d):**

| Video | Views | Likes | Like Rate |
|-------|-------|-------|-----------|
| **Come Back Dad** | **127,435** | **4,642** | **3.6%** |
| Something Like A Business | 24,470 | 1,572 | 6.4% |
| Schemers | 10,952 | 321 | 2.9% |
| 35 & Ticking | 1,400 | 157 | 11.2% |

Come Back Dad is a **12x outlier** over the next best performer. But look at "Something Like A Business" — launched April 13 and already at 24.5K views with a **6.4% like rate** (higher than CBD's 3.6%). That's Kevin Hart's name doing the heavy lifting on click-through, and the content retaining them.

**The pattern that works:**
1. **Recognizable talent in the clip/thumbnail** (Kevin Hart, established actors)
2. **Emotional hook in first 2 seconds** (the Karma stabbing scene, Come Back Dad's family drama)
3. **Series that build sequential viewing** (Girl In The Closet has the best completion rate progression: Ep1 15% → Ep2 23% → Ep3 26% → Ep4 23% → Ep5 13%)

**Girl In The Closet completion curve** is the most important pattern in your NPAW data:

| Episode | Views | Completion Rate |
|---------|-------|----------------|
| Ep 1 | 1,909 | 14.9% |
| Ep 2 | 588 | 23.1% |
| Ep 3 | 349 | 26.2% |
| Ep 4 | 285 | 22.9% |
| Ep 5 | 164 | 12.7% |

**The funnel:** 1,909 → 588 → 349 → 285 → 164. You lose 69% between Ep1 and Ep2 (the biggest drop), but the people who come back are increasingly engaged (completion rises from 15% to 26%). Then Ep5 drops — which likely means the hook weakens or the story resolves.

**This is your pitch to investors:** "We have proven sequential retention. Viewers who make it past Episode 1 become increasingly engaged. The challenge is the Ep1→Ep2 bridge, and that's a content/UX problem we can solve."

---

## INSIGHT 5: App Users Are 85% Engaged vs 15% on Web — The Web Experience is Leaking Value

**Platform breakdown (7d):**

| Platform | Users | Engagement Rate | Avg Duration | Bounce Rate |
|----------|-------|----------------|-------------|-------------|
| Web | 13,279 | **15.4%** | 1m 14s | 84.6% |
| iOS | 167 | **81.2%** | 14m 38s | 18.8% |
| Android | 141 | **81.6%** | 133m 3s | 18.4% |

**The gap is staggering.** App users are 5x more engaged and watch 12-100x longer. But app is only 2.3% of your user base (308 out of 13,587).

This isn't just "apps are better" — it tells you the web experience has a specific problem. With 84.6% bounce on web and an average session of 1m 14s, most web visitors never get past the landing page or age verification.

**Android's 133-minute average** is wild — those are people binge-watching entire series. That's the VURT experience working as designed.

**The lever:** Every 1% of web traffic you convert to app downloads = ~133 users who go from 1-minute bouncers to 133-minute bingers. A simple "Download the app for the best experience" interstitial after the first episode could be massive.

BUT — since your CTA is myvurt.com (web, not app stores) to avoid platform fees, the real fix is making the web experience not suck. That means:
1. Fix Fastly CDN (Insight 1)
2. SSR the Angular SPA (or at minimum, pre-render landing pages)
3. Reduce age gate friction

---

## INSIGHT 6: Your Returning Users Are Gold — and You're Not Growing Them Fast Enough

**New vs Returning (7d):**

| Segment | Users | Sessions | Engagement Rate | Sessions/User |
|---------|-------|----------|----------------|---------------|
| New | 13,089 | 12,883 | **14.9%** | 0.98 |
| Returning | 757 | 1,519 | **50.3%** | 2.01 |

Returning users engage at **3.4x the rate** of new users and generate 2x the sessions per person. But returning is only **5.5%** of your user base.

**The retention equation:**
- You're acquiring ~13K new users/week (mostly paid)
- Only ~757 come back (5.8% retention rate)
- Of the returners, 50.3% engage (vs 14.9% of new)

**If you could move retention from 5.8% to 10%**, that's ~1,300 returning users → ~654 engaged. Combined with current ~1,950 engaged new users, total engaged goes from ~2,700 to ~2,600... actually about the same, but the *quality* is way higher because returners watch longer and go deeper into series.

**What drives return visits:** Direct traffic (52% engagement) is mostly returning users. They bookmark the site or type it in. Your social clips are the acquisition hook, and the on-platform content is what brings them back.

**Missing piece:** You have no email capture, no push notifications on web, no "remind me" feature. The entire return-visit mechanism is "hope they remember." A simple email capture ("Get notified when new episodes drop") on the show detail pages could transform this.

---

## INSIGHT 7: Your YouTube Is Actually Working — 613 Subs to 184K Total Views Is Insane Efficiency

**YouTube growth trajectory (from social cache history):**

| Period | Subscribers | Total Views | Views/Sub |
|--------|------------|-------------|-----------|
| ~Mar 20 | 31 | 12,514 | 404x |
| ~Mar 24 | 38 | 12,371 | 326x |
| ~Apr 2 | 39 | 12,514 | 321x |
| ~Apr 7 | 116 | 28,817 | 248x |
| ~Apr 10 | 394 | 108,232 | 275x |
| **Apr 14** | **613** | **184,229** | **300x** |

**300 views per subscriber** is extraordinary. Industry average for a new channel is 10-50x. This means the YouTube algorithm is aggressively recommending your content to non-subscribers.

Come Back Dad alone (127K views) accounts for 69% of total views. That one video brought in most of your subscribers — 394→613 happened while CBD was spiking.

**The strategy implication:** YouTube Shorts is your best *free* distribution channel. You're essentially getting the algorithmic push that normally costs ad dollars. Double down:
- Every title should get 5-8 Shorts clips (you're already doing this)
- "Something Like A Business" (24.5K in 1 day) is showing Kevin Hart's name drives initial discovery — then VURT's content retains
- The 35 & Ticking clip (1.4K views, 11.2% like rate) has the highest like ratio — that content resonates even without star power

---

## INSIGHT 8: The "Content Quality by Title" Data Reveals Which Shows to Push and Which to Shelve

**NPAW Content Quality (7d) — buffer ratio by show:**

| Title | Views | Buffer Ratio | Completion Rate |
|-------|-------|-------------|----------------|
| Ep 4 - Girl In The Closet | 285 | **29.6%** | 22.9% |
| Ep 3 - Girl In The Closet | 349 | **26.5%** | 26.2% |
| Ep 2 - Girl In The Closet | 588 | **27.5%** | 23.1% |
| Ep 3 - Come Back Dad | 348 | **27.3%** | 13.0% |
| Ep 1 - Come Back Dad | 1,482 | **25.0%** | 7.6% |
| Ep 1 - Girl In The Closet | 1,909 | **22.8%** | 14.9% |
| Karma In Heels | 321 | **20.4%** | 8.0% |
| Ep 2 - Come Back Dad | 515 | **20.9%** | 14.2% |
| Ep 1 - Killer Stepdad | 302 | **18.0%** | 7.9% |
| Ep 1 - Baby Mama | 256 | **14.5%** | 5.4% |
| **Ep 1 - Schemers** | 335 | **5.0%** | 6.3% |
| **Ep 2 - Favorite Son** | 132 | **3.0%** | 14.5% |

**Schemers and Favorite Son stream cleanly** (3-5% buffer) while Girl In The Closet and Come Back Dad — your most popular shows — have the worst buffer ratios (22-30%). This is probably CDN routing: popular content may be hitting Fastly more because of how Enveu distributes load.

**This is critical context for the Mux conversation:** If the dev team's Mux dashboard shows lower buffer rates, it might be because Mux is only measuring *its own* delivery pipeline while Youbora is measuring the full viewer experience including Fastly's failures. Ask the dev team: "Is Mux measuring buffer on all CDN paths, or only on content delivered through Mux's own infrastructure?"

---

## INSIGHT 9: Your Peak Hours Reveal Two Distinct Audiences

**Hourly activity (7d, UTC — convert to ET by subtracting 4):**

| UTC Hour | ET Hour | Users | Sessions |
|----------|---------|-------|----------|
| 19:00 | **3 PM ET** | 809 | 905 |
| 16:00 | **12 PM ET** | 722 | 790 |
| 23:00 | **7 PM ET** | 715 | 784 |
| 00:00 | **8 PM ET** | 643 | 728 |
| 02:00 | **10 PM ET** | 673 | 753 |
| 01:00 | **9 PM ET** | 660 | 733 |

**Two peaks:**
1. **Lunch break (12 PM ET)** — likely US office workers + Caribbean daytime
2. **Evening wind-down (3 PM - 10 PM ET)** — primetime viewing, likely the core audience

The 3 PM ET spike is interesting — that's after school/work for your 40s female demo (the current skew) and aligns with pickup/downtime. Your target 18-30 demo would spike later (9-11 PM ET), which you see as a secondary bump.

**Posting implication:** Drop new clips at **11 AM ET** (1 hour before lunch peak) so the algorithm has time to start distributing before your biggest audience window.

---

## INSIGHT 10: The Buffer Rate Trend Shows an Unstable System

**14-day buffer ratio trend:**

| Date | Views | Buffer Ratio |
|------|-------|-------------|
| 04/06 | 3,083 | 28.7% ⚠️ |
| 04/07 | 3,718 | **42.3%** ⚠️ |
| 04/08 | 770 | 38.9% ⚠️ |
| 04/09 | 536 | **0.0%** ✅ |
| 04/10 | 1,406 | 3.1% ⚠️ |
| 04/11 | 2,737 | 10.4% ⚠️ |
| 04/12 | 2,451 | 29.2% ⚠️ |
| 04/13 | 1,476 | 25.3% ⚠️ |

04/09 was **0.0% buffer at 536 views** — then it spikes right back to 29% by 04/12. This looks like Fastly goes down periodically, traffic fails over to CloudFlare (which works great), then Fastly comes back online and breaks everything again.

**The smoking gun for the dev team:** "When buffer ratio dropped to 0% on April 9, was Fastly offline?" If yes, that proves CloudFlare alone can handle the load perfectly and Fastly should be killed, not fixed.

---

## SUMMARY: THE 5 MOVES THAT MATTER MOST

1. **Kill Fastly CDN routing** — immediate, could lift completion 40%+
2. **Tighten paid ad geo-targeting** — exclude Nigeria/Kenya/Ghana, focus US/UK/Caribbean diaspora/India
3. **Get Mux access** — but first do the CloudFlare-only test to separate the CDN problem from the measurement problem
4. **Push Kevin Hart / recognizable talent content on YouTube** — Something Like A Business is proving the formula at scale
5. **Build a return-visit mechanism** — email capture on show pages, "new episode" notifications

Everything else (posting schedule, social strategy, content calendar) is optimization. These five are structural.

---

*Data sources: GA4 Property 518738893, NPAW/Youbora system "vurt", Meta Graph API v25.0, YouTube Data API v3, Social cache snapshots. All data pulled live April 14, 2026 06:30 ET.*

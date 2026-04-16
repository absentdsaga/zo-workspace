# VURT Deep Insights v2 — The Stuff You Don't Already Know
### April 14, 2026 — Cross-dimensional analysis from live GA4, NPAW, Meta, YouTube APIs

---

## 1. APRIL 13 WAS A SITE-WIDE BREAKAGE, NOT BAD TRAFFIC

Yesterday (April 13) had 3,277 users but only **34 engaged sessions** — a 0.9% engagement rate. That's not a traffic quality problem. **The site itself was broken.**

Evidence:

| Landing Page (Apr 13) | Sessions | Engaged | Bounce |
|------------------------|----------|---------|--------|
| Homepage `/` | 147 | **1** | **99.3%** |
| `/detail/karma-in-hells` | 156 | **0** | **100%** |
| `/detail/something-like-a-business` | 109 | **0** | **100%** |
| `/detail/come-back-dad` | 11 | **0** | **100%** |

The homepage normally has **41% bounce**. On April 13 it had **99.3%**. This isn't targeting — the homepage doesn't have a targeting problem. When every single page on the site bounces at 99%+, it's an infrastructure failure.

**Hourly breakdown confirms it was all day:**
- Every single hour on April 13 had 97-100% bounce rate
- Even 6 AM UTC (2 AM ET, low traffic) was 94% bounce
- No hour recovered

**This looks exactly like the SSR breakage you documented before** (the March bounce phases). Something broke server-side on April 13. Ask the dev team: what deployed or changed on April 12-13? Check Enveu release logs, CDN config changes, or DNS updates.

**Impact:** April 13 single-handedly dragged your weekly engagement rate from ~22% to ~17%. If it was a normal day (~20% engagement like April 12), your 7d engagement rate would be 2-3 points higher.

---

## 2. THE REAL REASON EVERYONE BOUNCES ON SHOW PAGES: SIGNUP WALL

**VERIFIED LIVE (April 14, 2026):** Every show detail page (`/detail/micro_series/*`) presents a **full-screen "Sign Up to Continue" registration wall** before users see any content. The site IS running full SSR (Angular 17.0.8 Universal, confirmed via `ng-server-context="ssr"`), so rendering isn't the issue. The wall IS.

**What a paid ad click actually sees (screenshot verified on mobile + desktop):**
1. VURT logo
2. "Sign Up to Continue" header
3. Full registration form: Name, DOB, Gender, Email, Country, Password
4. No video. No show preview. No content whatsoever.

**The numbers by show (Paid Social, last 7 days):**

| Landing Page | Paid Sessions | Bounce Rate | Avg Duration |
|---|---|---|---|
| girl-in-the-closet | 4,512 | 81.4% | 50s |
| karma-in-hells | 2,139 | **98.9%** | 3.9s |
| baby-mama | 2,137 | 96.5% | 8.6s |
| killer-stepdad | 1,805 | 96.5% | 24s |
| come-back-dad | 1,691 | 82.9% | 59s |
| favorite-son | 345 | 97.7% | 12s |

That's **12,629 paid sessions last week hitting a signup form instead of content.**

Two shows (girl-in-the-closet 81%, come-back-dad 83%) bounce notably less than the others (96-99%). Worth investigating if those have different page configs or if the signup wall triggers differently on them.

**Compare: Homepage does NOT hit the wall.** Paid Social to `/` = 58 sessions, 63.8% bounce. Direct to `/` = 862 sessions, 37.8% bounce. The homepage lets people see content.

**Africa bounce is worse (0.17-3.9 seconds vs 8-50 seconds for US)** because African users leave faster when they see a registration form for a platform they've never heard of. US users at least spend a few seconds reading it. But the root cause is the same for everyone: signup wall before content.

**This is the single highest-impact fix VURT can make right now.** Let people see the show before asking them to register. The AVOD model makes money on views, not signups.

---

## 3. YOUR WEB FUNNEL HAS A 99% DROP-OFF BEFORE VIDEO EVEN STARTS

Here's the actual event funnel from GA4 (7d, all platforms):

| Stage | Events | Unique Users | % of Total Users |
|-------|--------|-------------|-----------------|
| page_view | 17,843 | 13,179 | 100% |
| screen_viewed | 7,287 | 1,686 | **12.8%** |
| content_select | 521 | 188 | **1.4%** |
| video_start | 1,720 | 114 | **0.86%** |
| video_complete | 641 | 63 | **0.48%** |
| sign_up_success | 210+13 | 223 | **1.7%** |

**Only 114 unique users started a video in 7 days.** Out of 13,179. That's 0.86%.

Now — `video_start` likely only fires on web (app uses different event tracking). But even accounting for that: your ~308 app users are clearly the ones watching. Your ~13,000 web users are almost entirely bouncing before they see any content.

The critical drop is **page_view → screen_viewed** (100% → 12.8%). 87% of users never get past what GA4 considers the initial page load to an actual screen render. This is the age gate, the consent flow, the SPA hydration — whatever sits between "landed" and "saw content."

**Why this matters for your AVOD model:** You said you want web users because you make more money on them. But right now web users aren't viewers — they're bouncers. The web funnel isn't losing people at "watched but didn't sign up." It's losing them at **"never saw a single frame of content."**

The fix isn't in marketing or content strategy. It's in the 3-5 seconds between landing and first content render on web.

---

## 4. SHOW DETAIL PAGES ARE BROKEN AS AD LANDING PAGES — EVEN FOR US USERS

This isn't just an Africa problem. Show detail pages have terrible conversion even for American users:

**US users — Homepage vs Show Pages (7d):**

| Landing | Sessions | Engaged | Bounce | Avg Duration |
|---------|----------|---------|--------|-------------|
| `/` (homepage) | 749 | 429 | **42.7%** | 3m 30s |
| `/detail/something-like-a-business` | 71 | 2 | **97.2%** | 1m 6s |
| `/detail/karma-in-hells` | 54 | 7 | **87.0%** | 0m 54s |
| `/detail/come-back-dad` | 75 | 19 | **74.7%** | 1m 31s |

Your best performing show (Come Back Dad) still loses **75% of US users who land directly on it**. "Something Like A Business" — the Kevin Hart show doing 24.5K on YouTube — loses **97.2% of users who click through from ads**.

**But paid users who land on the HOMEPAGE engage at 45% bounce** (20 sessions from Paid Social → `/`, 11 engaged). The homepage converts paid traffic 2x better than show pages.

**The implication:** Your ads should link to the homepage or a custom landing page — NOT directly to show detail pages. The show pages aren't built for cold traffic. They assume you already know what you're looking for. A first-time visitor from an ad needs: hero video auto-playing, social proof, clear "watch free" messaging — before being asked to commit to a specific title.

---

## 5. ORGANIC SEARCH IS YOUR BEST-KEPT SECRET — 66% ENGAGEMENT, 80-MINUTE SESSIONS

| Channel | Users | Engagement | Avg Duration | Bounce |
|---------|-------|-----------|-------------|--------|
| Organic Search | 208 | **66.0%** | **80 min 4s** | 34.0% |
| Referral | 28 | 59.0% | 8m 58s | 40.9% |
| Direct | 1,112 | 51.9% | 8m 0s | 48.1% |
| Organic Social | 309 | 38.3% | 1m 24s | 61.7% |
| Paid Social | 11,814 | 10.7% | 0m 34s | 89.3% |

Organic search users are watching for **80 minutes per session**. That's binge-watching behavior. These are people who googled something like "Come Back Dad watch free" or "VURT streaming" and found you. They came with intent.

208 users generating 80-minute sessions = **~277 hours of watch time per week** from organic search alone. Your 11,814 paid users generating 34-second sessions = **~112 hours of watch time**. Organic search produces **2.5x more watch time from 57x fewer users.**

The site now has SSR (Angular Universal, confirmed April 14), which means Google CAN crawl it. The opportunity:
- Show title searches ("Girl In The Closet watch free", "Come Back Dad full episode") can rank
- Each of your 80 titles becomes a search landing page
- At even 50 organic search users per title per week x 80 titles = 4,000 high-intent users/week

With SSR already in place, the SEO investment is now about content/meta optimization, not engineering. This is lower-effort, higher-ROI than before.

---

## 6. "SOMETHING LIKE A BUSINESS" IS CONVERTING WORSE THAN IT SHOULD

Kevin Hart's name is generating massive top-of-funnel (24.5K YouTube views in 1 day, 6.4% like rate). But on VURT's site:

- 125 sessions on the show detail page
- **91.2% bounce**
- Only 11 engaged sessions
- Average duration: 4m 32s

Compare to "Come Back Dad":
- 98 sessions, 73.5% bounce, 26 engaged, avg 3m 50s

"Favorite Son" (much less known):
- 33 sessions, **51.5% bounce**, 16 engaged, avg 13m 7s

**Favorite Son has half the bounce of the Kevin Hart show with a fraction of the traffic.** This means the show detail page for "Something Like A Business" has a specific UX or content issue. Possible causes:
- The show description/thumbnail doesn't match what the YouTube clip promised
- The age gate or sign-up wall hits before any content loads
- The first episode doesn't auto-play, and the user has to navigate to find it

Whatever is wrong with this specific page is wasting your best content asset. Someone on the team should do a screen recording of landing on `/detail/micro_series/something-like-a-business` from a Facebook ad on mobile and watch exactly where people drop.

---

## 7. INDIA IS A REAL MARKET, NOT AN ACCIDENT

| Metric | India | United States |
|--------|-------|---------------|
| Users (7d) | 126 | 4,620 |
| Sessions/User | **3.10** | 1.18 |
| Engagement Rate | **65.7%** | 27.3% |
| Bounce Rate | **34.3%** | 72.7% |
| Show page bounce | **0-37%** | **75-97%** |

Indian users:
- Return 3x per week (vs 1.2 for US)
- Browse across shows (Favorite Son, Karma In Heels, Schemers, The Parking Lot, Along Came Love, Come Back Dad, One Night In Lagos)
- Watch 23-47 minutes per session on show detail pages
- **Show pages actually work for them** (the SPA loads, content plays)

These are 126 users generating the behavior your entire platform is designed for. They found VURT organically (most on Direct/Organic), and the product works for them.

**India context:** ReelShort and DramaBox are both growing aggressively in India. The micro-drama format resonates there. You have a natural audience without spending a dollar on it.

**Not saying to pivot to India.** Saying: Indian users demonstrate what engagement looks like when the signup wall isn't blocking them (likely returning/registered users). If show pages were open to cold traffic, other markets could look similar.

---

## 8. YOUR ENGAGEMENT RATE IS IN A STRUCTURAL DECLINE — AND PAID IS THE CAUSE

21-day trend:

| Date | DAU | Engagement | Phase |
|------|-----|-----------|-------|
| Mar 24 | 5,703 | 11.4% | Heavy paid |
| Mar 27 | 9,201 | 9.0% | Peak paid spend |
| Mar 31 | 171 | **65.4%** | Paid stopped |
| Apr 1 | 1,991 | **34.6%** | Paid restarted (new campaign) |
| Apr 4 | 1,033 | **41.3%** | Lower spend |
| Apr 7 | 2,572 | 24.4% | Scaling up again |
| Apr 12 | 1,336 | 18.4% | Fully diluted |
| **Apr 13** | **3,277** | **0.9%** | **Site broken** |

The pattern: every time paid scales up, engagement rate drops proportionally. When paid stops, engagement jumps to 40-65% from organic users alone.

**This isn't just "paid brings low-quality traffic."** The trend shows engagement rate declining even within the paid-on periods (34.6% → 24.4% → 18.4% over 12 days). That means either:
1. The ad targeting is getting broader/lazier over time (audience fatigue)
2. The same users are being re-served ads and bouncing again (frequency capping issue)
3. The site experience is getting worse (the show detail page problem compounding)

**The healthy baseline is 600-1,000 organic/direct users at 35-65% engagement.** That's your real product-market fit signal. Paid is inflating DAU while masking the real health of the product.

---

## 9. THE "DIRECT" TRAFFIC TO SHOW PAGES IS ACTUALLY MISATTRIBUTED SOCIAL

166 "Direct" sessions landed on `/detail/micro_series/karma-in-hells`. People don't type that URL. This is social traffic where the referrer is being stripped — likely because:
1. Instagram/TikTok in-app browsers don't always pass referrer headers (most common cause)
2. Link shorteners (Linktree, bit.ly) can strip attribution
3. HTTPS redirect chain (myvurt.com → www.myvurt.com 301 redirect) may drop referrer in some browsers

This means your "Paid Social" numbers are understated and your "Direct" numbers are overstated. The real paid social traffic to show pages is probably 2-3x what GA4 reports. Which means the real paid social bounce rate on show pages might be even higher than the 93% you see.

**Fix:** Add UTM parameters to every social link. `myvurt.com/detail/micro_series/karma-in-hells?utm_source=instagram&utm_medium=social&utm_campaign=karma_launch`. This gives you real attribution.

---

## 10. 46 APP UNINSTALLS VS 48 WATCHLIST ADDS — YOUR APP RETENTION IS NET ZERO

From the event data (7d):
- `app_remove`: **46 events** (29 users uninstalled)
- `add_to_watchlist`: **48 events** (25 users)
- `first_open`: 182 events
- `app_update`: 50 events

You're getting 182 new app installs/week but losing 46 uninstalls — a **25% churn rate** on installs. Combined with only 48 watchlist adds across 25 users, the app is not building habits.

The 308 app users who ARE engaged (81% engagement, 15-133 min sessions) are incredibly valuable. But you're churning almost as many as you're adding. The app needs a "come back" mechanism — push notifications for new episodes of shows they've watched.

---

## THE REAL PRIORITIES (in order of impact)

1. **Remove or delay the signup wall on show detail pages** — This is THE issue. 12,629 paid users/week are hitting a registration form instead of content. For an AVOD platform, this is money on fire. Let people watch first, ask them to sign up after they're hooked (like the 10th video rule on the app).
2. **Investigate and fix the April 13 site breakage** — this is urgent, it may still be broken today
3. **Redirect paid ads to homepage OR create signup-free show landing pages** — Even with the wall fixed, cold traffic converts better through homepage (37-44% bounce) than direct show links
4. **Add UTM params to all social links** — you're flying blind on attribution. Instagram/TikTok in-app browsers strip referrers, making organic social look like "Direct"
5. **Capitalize on SSR for SEO** — SSR is already live (verified). Now optimize meta/content for organic search, which generates 2.5x more watch time than paid at zero cost

---

*Raw data pulled live from GA4 Property 518738893, NPAW system "vurt", YouTube API, Meta Graph API v25.0. Cross-tabulated dimensions: country×landing_page, landing_page×source, date×source, date×country, date×hour. All timestamps April 14, 2026 06:30 ET.*


# Dead-vs-Working Bounce Investigation — Findings Report
Date: 2026-04-16
Scope: 3 DEAD (96-98% bounce), 2 WORKING (79-80% bounce) show detail pages
Method: Playwright iPhone UA, fbclid param, 15s observation, HLS manifest + HTML capture

## TESTED AND RULED OUT
| Hypothesis                              | Result  |
|---|---|
| Video skips into mid-scene               | FALSE — all start at currentTime ≈ 0      |
| First video muted vs unmuted             | FALSE — ALL unmute within 4-5s of age gate |
| Different resolution / bitrate / codec   | FALSE — all 1080x1920 master, same HLS tiers |
| Different CDN                            | FALSE — all on stream.mux.com             |
| Different HLS version / format           | FALSE — all v5, same structure            |

## DIFFERENCES FOUND (but weight on bounce unverified)

### 1. Opening-frame content (previously flagged)
DEAD shows: raw scene first frame (baby-mama near-black)
WORK shows: also raw scene, just slightly different lighting
Weight: LOW — earlier brand-card claim was overstated. WORKING shows don't have branding cards either, they just happen to start on a less-dark frame.

### 2. Visible per-card engagement counters (social proof)
karma-in-hells: "Share 24" on Ep 1 card
baby-mama: "Share 0 / 0 comments / 0 likes" — literal zero engagement on every card
killer-stepdad: "Share 6"
girl-in-the-closet: "Share 11"  
come-back-dad: "Share 7"
Weight: UNCLEAR — baby-mama is the outlier here (100% zero engagement visible).

### 3. Episode count
karma-in-hells: only 3 episodes on page
All others: 4 episodes
Weight: UNCLEAR — fewer episodes may feel less substantive.

### 4. Episode-level description visibility
ONLY killer-stepdad has a description on Ep 1 card ("A man's aggressive attempt...")
All 4 others have no description text on cards
Weight: LOW — doesn't correlate with bounce (killer-stepdad is DEAD with a description).

### 5. URL slug typo
/detail/micro_series/karma-in-hells — show is actually "Karma In Heels"
og_title says "Heels" but page title says "Hells"
Weight: LOW — user doesn't usually see URL, but branding inconsistency is sloppy.

### 6. SEO/meta description length
Long: girl-in-the-closet (577 chars)
Short: karma/killer (184 chars)
Weight: LOW for bounce; relevant for search, not for clickthrough behavior.

## NOT RULED OUT (need external data we can't get)

### A. Ad creative ↔ landing page mismatch (STRONGEST UNVERIFIED HYPOTHESIS)
The ads driving to /karma-in-hells may be using a creative asset (poster, clip, text) that doesn't match what the user sees on the landing page. 
User clicks ad showing vibe X → lands on page with completely different video preview → swipes.
Requires: Meta Ads Manager access to pull the actual ad creative tied to each landing URL.

### B. Audience targeting differences per campaign
Different shows may be targeting different interest audiences. DEAD shows may be in campaigns with broader/lower-intent targeting.
Requires: Ads Manager campaign-by-show breakdown.

### C. Bounce metric itself is broken
Post-SSR engagement timer is verified broken (earlier investigation). All bounce rates in GA4 are inflated. The DEAD/WORK split may reflect which shows have users who happen to NAVIGATE to another URL (triggering a "real" engaged session despite broken timer), not which shows retain viewers.
Requires: NPAW play-through % per show, not GA4 bounce, for actual retention.

## MY RECOMMENDATION
Stop trying to explain bounce with landing-page-only data. Three actions that would actually answer this:

1. Pull Meta Ads Manager breakdown: for each campaign, which show URL is the destination, what's the CTR, what's the dwell time.
2. Pull NPAW per-title play-completion % (not GA4 bounce) — that's the true retention metric independent of the broken engagement timer.
3. Run the 3 DEAD campaigns and 2 WORKING campaigns side-by-side with the SAME ad creative and SAME audience to isolate landing-page effect vs campaign effect.

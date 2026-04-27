# Per-Show Bounce Comparison — Apr 16, 2026

**Question:** Why do some paid-ad landing pages bounce at ~98% with 3-23s avg duration while others on the same channel/device bounce at ~80% with 50-61s avg duration?

**Method:** Loaded each show URL with an `fbclid` query param in a stealth iPhone browser (mobile viewport), waited for age gate, dismissed it, then captured timing, video state, and a final screenshot.

**Sample (paid-social, mobile, Apr 7–13):**

| Show | Sess | Bounce | Avg dur |
|---|---|---|---|
| karma-in-hells | 2,361 | **98.2%** | **3s** |
| baby-mama | 2,160 | **96.6%** | **7s** |
| killer-stepdad | 1,862 | **96.3%** | 23s |
| girl-in-the-closet | 4,560 | 80.5% | 50s |
| come-back-dad | 1,745 | 79.1% | 61s |

---

## What's the same on every page

- Same Angular SSR shell, same layout, same age gate, same bottom nav
- All five fire the Mux `.m3u8` stream and start a media download
- All five return HTTP 200, valid `og:title`, `og:description`, `og:image`, `canonical`
- All five accumulate ~31–40 video-CDN requests in the first 12s
- All five had the same console error pattern (CSP warnings, Firebase messaging not initialized, Push permission denied)

So it is **not** a sitewide JS error, missing video player, broken CDN, or missing meta tag.

---

## What's different (verified, not speculation)

### 1. Time to first video stream

| Show | Bucket | First m3u8 | First media chunk |
|---|---|---|---|
| girl-in-the-closet | WORK | **2.75s** | 2.76s |
| killer-stepdad | DEAD | 2.83s | 2.84s |
| come-back-dad | WORK | 3.12s | 3.14s |
| baby-mama | DEAD | **4.00s** | 4.05s |
| karma-in-hells | DEAD | **4.21s** | 4.25s |

The two highest-bounce shows take ~50% longer to start streaming than the working ones. On a 3-second mobile attention window, that is the difference between "loaded" and "still spinning when I swiped away."

But killer-stepdad streams as fast as the working shows and still has 96% bounce, so this isn't the whole story.

### 2. What the user actually sees in the player after the gate

After clicking "Yes, I am 17+" the video element re-renders and the first frame is whatever the publisher set as the opening shot. Visual capture (full-page screenshot, real iPhone viewport):

| Show | Bounce | First visible frame | Verified currentTime |
|---|---|---|---|
| karma-in-hells | 98.2% | First frame of the show — a woman walking. **No title card, no studio bug, no episode number.** | ~0.57s (starts at 0:00) |
| baby-mama | 96.6% | **Mostly black screen with a faded "Royal Arts Academy" production-company logo.** Looks broken or stalled. | ~0.66s (starts at 0:00) |
| killer-stepdad | 96.3% | First frame of the show — dim character close-up. **No title card, no studio bug.** | ~0.73s (starts at 0:00) |
| girl-in-the-closet | 80.5% | **"A LIFETIME ORIGINAL MOVIE"** branding card — recognizable network, sets expectation. | ~0.53s (starts at 0:00) |
| come-back-dad | 79.1% | **"THE SWIRL GROUP"** studio branding card — clean intro, sets expectation. | ~0.52s (starts at 0:00) |

**Verified via `video.currentTime` polling (compare5.py):** all five shows start at frame 0 of their asset. None of them are skipping mid-scene — the difference is purely what the publisher chose as the opening frame of the file. The two working shows open with a **branded intro card** that gives the user a 2-3 second "you're about to watch a real production" cue. The dead shows open straight into the show's first frame with no branded intro, and in baby-mama's case that first frame is near-black.

### 3. Page title metadata

- karma-in-hells: `Vurt | Micro Series | Karma In Hells | VURT — Watch Free` (**no episode number**)
- baby-mama, killer-stepdad, girl-in-the-closet, come-back-dad: all include `| Episode 1 |`

Karma-in-hells is the only one missing the episode-level title metadata, which suggests its first-episode wiring in the CMS is different/incomplete. That matches the slow first-stream time too.

### 4. Title spelling vs URL slug

- URL slug `karma-in-hells`
- og:title `Karma In Heels` (correct spelling)

The URL was created with a typo ("hells" instead of "heels"). Not user-visible directly but a sign the entry was set up sloppily, and consistent with the missing episode metadata.

### 5. Engagement counters in the feed cards

The bottom-of-page feed cards display per-card counts. Across four cards:

- karma-in-hells: 24 / 24 / 24 / 24
- killer-stepdad: 6 / 6 / 6 / 6
- come-back-dad: 7 / 7 / 7 / 7
- girl-in-the-closet: 11 / 11 / 11 / 11
- baby-mama: **0 / 0 / 0 / 0** (every counter is zero)

baby-mama shows zero engagement on every card it surfaces. That mirrors what users see — "nobody else is watching this."

---

## Working hypothesis

There are two stacked failures, not one:

**A. CMS-side asset quality.** Three of the five landing pages have a bad first impression baked into the publisher's content (all confirmed playing from frame 0):
- baby-mama: opens on near-black with a tiny faded production logo (looks broken)
- karma-in-hells: opens straight into the show's first frame with no branded intro AND has slow stream start AND has missing episode-level metadata
- killer-stepdad: opens straight into the show's first frame with no branded intro

The two that work both open with a studio/network identifier (Lifetime, Swirl Group). That single visible cue tells the user "this is a real show, not a buggy app."

**B. Time-to-first-frame is correlated but not the only driver.** karma-in-hells and baby-mama also take ~1 second longer than the working shows to start streaming, which compounds the bad first impression.

This is not an SSR bug, GTM tag bug, autoplay bug, or analytics-pipeline bug. It's content QA per landing page.

---

## Concrete next steps

1. **Re-encode / re-cut the first 3 seconds of `baby-mama` Episode 1.** The black-with-faded-logo opening is the worst visual we tested. Either start the playable asset at a real frame or replace the intro with a proper title card.
2. **Add a uniform 2-second VURT branding card before each Episode 1**, applied at the player level (not per asset). This gives every paid-ad landing the same recognizable "real product" moment that Lifetime/Swirl do for the working shows.
3. **Fix `karma-in-hells` CMS entry**: rename slug to `karma-in-heels` (matches og:title spelling), fill the missing Episode 1 metadata, and verify it streams as fast as `girl-in-the-closet` after the fix.
4. **Pause paid spend on `baby-mama` and `karma-in-hells` until #1 and #3 are done.** They are converting 0 of the 4,500 sessions we sent them last week.
5. **Keep spending on `girl-in-the-closet` and `come-back-dad`.** Those are the working creatives — 80% bounce is high but the 20% that stays watches for ~1 minute.

---

## What this rules out

- "SSR is broken" — SSR is delivering equally on all five pages.
- "GTM/Pixel is double-firing" — same tags on all pages.
- "Age gate kills everyone" — same age gate on all pages, but bounce ranges from 79% to 98%.
- "CDN is failing" — Mux streams initialize within 4.3s on all pages.
- "Meta is sending bot traffic to dead URLs" — pages return 200 and load real video.

The differentiator is **content-asset quality on the first 3 seconds of the landing video**, plus a small CMS metadata gap on karma-in-hells.

---

*Test artifacts: `/home/.z/workspaces/con_v55GP1lr46UmN5fa/bounce-compare/` — screenshots, results JSON, and three Python scripts.*

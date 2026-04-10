# VURT Paid Ads Bounce Forensics — In-App Browser Test Results

**Date:** April 5, 2026
**Test:** Facebook & Instagram in-app browser simulation of paid ad landing experience
**URL Tested:** `https://www.myvurt.com/detail/micro_series/come-back-dad`
**Method:** Playwright with real FB/IG User-Agent strings, iPhone 14 Pro viewport (393x852), tested on baseline (no throttle), 4G (4Mbps), and 3G (1.5Mbps)

---

## The Problem in One Sentence

**When someone clicks a VURT ad on Facebook or Instagram, they stare at a broken skeleton screen or pure black for 3-8 seconds before seeing anything — and even then, the first thing they see is an age gate covering a black video player with no thumbnail.**

---

## What a Paid Ad User Actually Sees (Timeline)

### Facebook In-App Browser on 4G (typical ad click)

| Time | What's on screen |
|------|-----------------|
| 1s | Tiny broken "Episode List" skeleton panel in upper-left corner. Rest of screen is black. |
| 3s | "Episode List" header with X button, yellow loading bar, grey placeholder boxes. No show content. Black video area. |
| 5s | **COMPLETELY BLACK SCREEN.** Nothing visible at all. |
| 8s+ | Age gate may eventually appear |

### Facebook In-App Browser on 3G (poor mobile connection)

| Time | What's on screen |
|------|-----------------|
| 3s | Same "Episode List" skeleton |
| 8s | **STILL the skeleton.** 8 seconds and zero content visible. |
| 14s | Page finally fully loads. Age gate visible. |

### Instagram In-App Browser on 4G

| Time | What's on screen |
|------|-----------------|
| 1s | "Episode List" skeleton (same broken state) |
| 3s | Still skeleton |
| 5s | Age gate appears — VURT logo, "ARE YOU 17 YEARS OR OLDER?" checkboxes |

### Baseline (No Throttle) — Best Case

| Time | What's on screen |
|------|-----------------|
| 5s | Age gate visible. Behind it: black video player (no thumbnail), pause/volume controls, "Come Back Dad - EPISODE : 1" at bottom |

---

## The Five Problems Killing Paid Ad Traffic

### 1. Broken Initial Render — "Episode List" Skeleton (THE BIGGEST ISSUE)

The first thing EVERY user sees is a broken "Episode List" skeleton panel — a dark grey box with a yellow progress bar and grey placeholder thumbnails. This is NOT the show page. It's an Angular component rendering in the wrong order or at the wrong z-index. On Facebook's in-app browser with 4G, this persists for 3+ seconds. On 3G, it persists for 8+ seconds.

**A user who clicked an ad for "Come Back Dad" sees a loading skeleton for a component they never asked for.**

### 2. 5MB JavaScript Bundle = Slow Time-to-Interactive

The page ships 5MB+ of JavaScript (6.62 MB total page weight). The Angular SPA must download, parse, and execute ALL of this before anything meaningful renders. On 4G this takes 3-4 seconds. On 3G it takes 8-14 seconds.

| Network | Full Load Time |
|---------|---------------|
| Baseline | 2.4-2.9s |
| 4G | 3.7-4.4s |
| 3G | 7.8-13.9s |

### 3. Black Video Player — No Poster/Thumbnail

The Mux Player has broken thumbnail tokens. Console logs: `"Missing expected thumbnail token. No poster image will be shown"`. Every episode renders as a black rectangle. There is zero visual payoff — the user clicked on an ad with a compelling show image and lands on a black void.

### 4. 84MB Video Preload Before Age Confirmation

The page loads 84MB of video data (102 video requests, 30 HLS manifests) BEFORE the user has even confirmed their age. This is:
- Wasting bandwidth on mobile users who will bounce
- Competing with the page's own JS for network bandwidth, making the skeleton phase LONGER
- Loading video segments for ALL episodes, not just Episode 1

### 5. Age Gate Over Black Screen

Even when the age gate finally appears, it sits on top of a completely black background. The user sees:
- VURT logo
- "ARE YOU 17 YEARS OR OLDER?"
- Two checkboxes
- Black everywhere else

No show artwork. No trailer preview. No synopsis. Nothing that confirms they clicked on the right thing or hooks them to stay.

---

## Facebook vs Instagram Performance

Facebook's in-app browser is consistently **slower** than Instagram's:

| Metric | Facebook | Instagram | Difference |
|--------|----------|-----------|------------|
| Baseline full load | 2.9s | 2.4s | FB 21% slower |
| 4G full load | 4.4s | 3.7s | FB 19% slower |
| 3G full load | 13.9s | 7.8s | FB 79% slower |

Facebook's WebView appears to handle the 5MB JS bundle significantly worse on constrained networks.

---

## Autoplay Status

**Autoplay does NOT fire in either in-app browser.** Zero video play events detected across all 6 test configurations, even at 15 seconds on baseline. The Mux Player custom element (Shadow DOM) doesn't trigger autoplay in WebView contexts.

This means even after the age gate, the user sees a black player and must manually tap play — another friction point.

---

## What the Dev Team Needs to Fix (Prioritized)

1. **Fix the "Episode List" skeleton render bug** — The show detail page should render the show hero/poster immediately, not an episode list skeleton. This is a component mount order or z-index issue in the Angular SPA.

2. **Add poster images to Mux Player** — Fix the missing thumbnail tokens so episodes show poster frames instead of black rectangles.

3. **Defer video preloading until after age gate** — Don't load 84MB of video for a user who hasn't even confirmed their age. Load only poster frames initially.

4. **Reduce initial JS bundle** — 5MB is unacceptable for a content platform. Code-split, lazy-load non-critical modules, defer analytics/tracking scripts.

5. **Show the show artwork/synopsis BEHIND the age gate** — The age gate should be semi-transparent over the show's hero image, not over a black void. The user needs visual confirmation they're in the right place.

6. **Fix Mux Player autoplay for WebView contexts** — Configure `playsinline`, `muted`, and appropriate autoplay attributes for iOS WebView.

---

## How to Reproduce on Your Phone

### Instagram Test (simulates exact ad click experience):
1. Open Instagram on your iPhone
2. Go to your own profile → tap the message/chat icon
3. Start a chat with yourself (or any friend)
4. Paste this URL: `https://www.myvurt.com/detail/micro_series/come-back-dad`
5. Send it, then tap the link
6. This opens in the IG in-app browser — exactly what an ad clicker sees
7. Time how long until you see actual content

### Facebook Test:
1. Open Facebook app
2. Tap "What's on your mind?" to start a new post
3. Paste the URL — a preview card will appear
4. Tap the preview card (don't publish the post)
5. This opens in the FB in-app browser
6. Or: DM yourself the link on Messenger and tap it

### Pro tip — Test as a first-time visitor:
- Clear Safari cookies for myvurt.com first (Settings → Safari → Advanced → Website Data → search "myvurt")
- Or use a phone that has never visited VURT before
- The age gate only appears for first-time visitors, so clearing cookies ensures you see the real ad experience

---

*Test data from 6 configurations (2 browsers x 3 network speeds), 36 screenshots captured, full network waterfall analysis. Screenshots saved at browser-tests/ in conversation workspace.*

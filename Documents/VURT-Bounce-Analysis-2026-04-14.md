# VURT Bounce Rate Analysis — UX Deep Dive
### April 14, 2026

**Method:** Stealth browser testing across 8 mobile devices + desktop, capturing screenshots at every step of the user journey, network waterfall analysis, console error logging, and GA4 data cross-reference (Mar 31 – Apr 13). All tests see exactly what real users see (verified — no bot-detection artifacts).

---

## GA4 Data: Where the Bounces Actually Are

### Top Landing Pages (Mar 31 – Apr 13)

| Landing Page | Sessions | Bounce % | Engaged | Avg Duration |
|-------------|----------|----------|---------|-------------|
| `/` (homepage) | 2,458 | **33.5%** | 1,635 | 370s |
| `(not set)` | 1,411 | 29.1% | 1,001 | 2,331s |
| `/detail/micro_series/karma-in-hells` | 241 | **86.3%** | 33 | 216s |
| `/detail/micro_series/come-back-dad` | 223 | **69.1%** | 69 | 172s |
| `/detail/micro_series/something-like-a-business` | 165 | **84.8%** | 25 | 388s |
| `/detail/micro_series/favorite-son` | 44 | 43.2% | 25 | 1,040s |
| `/detail/micro_series/the-parking-lot` | 41 | 46.3% | 22 | 788s |
| `/detail/micro_series/killer-stepdad` | 23 | **91.3%** | 2 | 18s |
| `/detail/micro_series/baby-mama` | 19 | **94.7%** | 1 | 0.3s |
| `/detail/micro_series/the-love-letter` | 8 | **100%** | 0 | 0.9s |

### Paid Social Is the Dominant Traffic Source -- And It All Goes to Detail Pages

Paid Social accounts for **13,475 sessions (84% of all traffic)** with an overall **88% bounce rate**. Using `landingPage` (path only, no query strings) gives the accurate breakdown. The `landingPagePlusQueryString` dimension in the table above fragments paid social across thousands of unique fbclid URLs, making it appear much smaller.

| Landing Page | Paid Social Sessions | Bounce |
|-------------|---------------------|--------|
| girl-in-the-closet | **4,634** | 80% |
| karma-in-hells | **2,366** | 98% |
| baby-mama | **2,182** | 96% |
| killer-stepdad | **1,882** | 96% |
| come-back-dad | **1,778** | 79% |
| favorite-son | 385 | 88% |
| Homepage (/) | 58 | 62% |

**99.6% of paid social traffic lands on show detail pages, not the homepage.** Only 58 of 13,475 sessions go to homepage. The bounce problem is squarely on the detail page experience (age gate, page weight, no content context).

Direct traffic (1,797 sessions, 45% bounce, 7m 52s avg duration) represents genuine returning/direct users, not misattributed paid social.

### Shows That Actually Retain Users

| Show | Sessions | Bounce | Avg Duration | Why |
|------|----------|--------|-------------|-----|
| fatal-lust | 17 | **23.5%** | 1,747s (~29min) | Users watching multiple episodes |
| favorite-son | 44 | **43.2%** | 1,040s (~17min) | Strong engagement |
| the-parking-lot | 41 | **46.3%** | 788s (~13min) | Good retention |

These shows prove the platform works when users get past the gate. The bounce problem is getting them there.

---

## The Two User Flows

### Flow A: Ad Click → Detail Page (Paid Traffic)
This is where most bounces happen. User clicks a social ad and lands directly on a show page like `/detail/micro_series/karma-in-hells`.

| Step | What Happens | Time | Bounce Risk |
|------|-------------|------|-------------|
| 1. Ad click | Page starts loading | 0s | — |
| 2. First paint | VURT logo + black screen | ~0.4s | Low |
| 3. Age gate appears | Full-screen modal over black/loading video | ~3.5s | **HIGH** |
| 4. User taps "Yes, I am 17+" | Gate dismisses, video starts loading | +3.7s | **HIGH** |
| 5. Video plays | Fullscreen vertical video, no title/context | +2-3s | Medium |
| **Total: Ad click → video** | | **~9-11s** | |

### Flow B: Homepage → Click Show (Organic Traffic)
User arrives at myvurt.com, browses, clicks a show.

| Step | What Happens | Time | Bounce Risk |
|------|-------------|------|-------------|
| 1. Homepage loads | Content rows visible (shows, categories) | ~3.5s | Low |
| 2. User clicks a show | Navigates to detail page | +6.2s | Medium |
| 3. Age gate appears | Same modal | +0s | **HIGH** |
| 4. User taps "Yes, I am 17+" | Video loads | +3.4s | **HIGH** |
| **Total: Homepage → video** | | **~13s** | |

---

## Where Users Bounce (Ranked by Impact)

### 1. THE AGE GATE IS THE PRIMARY BOUNCE POINT

Every detail page — the exact page all ads link to — hits users with a full-screen age verification modal before they see any content. On mobile, this modal covers the entire viewport.

**Why it causes bounces:**
- Users clicking a social ad expect **instant content** (TikTok trained them for 0-1s to content)
- Instead they get a branded modal asking them to confirm their age
- Every extra tap = 20-30% drop-off (industry standard for interstitial friction)
- The age gate takes **3.5-4s** to even appear, so users stare at a black screen first
- **No preview of the content behind the gate** — on iPhone 15 Pro, the background is completely black. On some devices, a faint video frame is visible behind the modal, but it's not compelling

**What this looks like per device:**
- iPhone 15 Pro: Black background + age gate modal
- Galaxy S24: Black background + age gate modal  
- iPhone SE: Black background + age gate modal (smaller screen, modal takes even more space)
- Galaxy A54: Black background + age gate modal

**This is NOT removable** — age verification is required for the content. But it can be **dramatically less friction** (see recommendations).

### 2. ALL 7 MUX PLAYERS SET TO `preload="auto"` — NOT TRULY LAZY

**Devs say they lazy-load ~10 episodes. Here's what actually happens:**

Karma in Heels has **7 `<mux-player>` elements** on the page. Every single one has `preload="auto"` and no `loading` attribute:

```
[0] <mux-player> playback-id=HB7Vvpk... IN VIEWPORT  | preload=auto | loading=not set
[1] <mux-player> playback-id=9Tt025v... off-screen (922px)  | preload=auto | loading=not set
[2] <mux-player> playback-id=Tr0091J... off-screen (1784px) | preload=auto | loading=not set
[3] <mux-player> playback-id=F7Mb2GM... off-screen (2646px) | preload=auto | loading=not set
[4] <mux-player> playback-id=qm00xHg... off-screen (3508px) | preload=auto | loading=not set
[5] <mux-player> playback-id=dI3YOQG... off-screen (4370px) | preload=auto | loading=not set
[6] <mux-player> playback-id=RanjHey... off-screen (5232px) | preload=auto | loading=not set
```

**`preload="auto"` tells the browser to eagerly download the full video.** With 7 players all set to `auto`, ALL 7 episodes start downloading immediately on page load — even the ones 5,000+ pixels off-screen.

**Timeline of media requests:**
```
  2s-4s:  68 requests ████████████████████████████████████████████████████████████
  4s-6s:  33 requests █████████████████████████████████
 10s-12s: 17 requests █████████████████
 12s-14s:  4 requests ████
 20s-22s: 14 requests ██████████████
```

**101 media requests fire BEFORE the user even clicks the age gate.** The videos are preloading behind a modal the user hasn't interacted with yet.

**Total: 136 media requests, 151 Mux requests, 10 unique stream IDs (7 episodes + quality variants).**

The page weight breakdown:

| Resource Type | Requests | Size | Notes |
|--------------|----------|------|-------|
| **Video segments (Mux)** | 99+ | 26.4MB | All 7 episodes, `preload="auto"` |
| JavaScript | 35 | 1.45MB | Including Mux player loaded **twice** (556KB) |
| Fonts | 4 | 149KB | Material Icons (125KB) |
| Images | 10 | 124KB | Show art, social icons |
| Facebook Pixel | 1 | 96KB | |
| Other (fetch/xhr) | 40+ | ~43KB | API calls, analytics |
| **TOTAL** | **189** | **27.6MB** | |

**What "lazy load" should actually mean:**
- `preload="none"` or `preload="metadata"` for all off-screen players
- Only the CURRENT episode (player [0]) should have `preload="auto"`
- Use IntersectionObserver or `loading="lazy"` to trigger preload when user scrolls near an episode
- This would cut initial media requests from 101 → ~15 (just episode 1)

### 3. 569KB OF RENDER-BLOCKING RESOURCES IN FIRST 500ms

Before the user sees ANYTHING, the browser must download and parse:

| Resource | Size | Why it's there |
|----------|------|---------------|
| Mux Player (CDN) | 278KB | Video player library |
| Mux Player (CDN) — **duplicate** | 278KB | Loaded a second time |
| Material Icons font | 125KB | UI icons |
| Google Tag Manager | 112KB | Analytics |
| AdSense | 54KB | Ads |
| Swiper CSS | 5KB | Carousel library |

That's **852KB of render-blocking JS/CSS/fonts** (counting the duplicate Mux load). The duplicate Mux player alone wastes 278KB and ~400ms.

### 4. NO CONTENT CONTEXT ON THE VIDEO PAGE

After the age gate, users see:
- Fullscreen vertical video (TikTok-style)
- Small engagement icons on the right (comments: 0, shares: 12)
- Play/pause + volume controls
- Bottom nav: What's New | Categories | My List
- A tiny progress bar at the bottom

**What's missing:**
- **No show title** anywhere on screen
- **No episode number** ("Episode 1 of 7")
- **No show description** or logline
- **No "what is VURT"** context for first-time visitors from ads
- **No CTA** telling users they can swipe for more episodes

A user arriving from an Instagram ad has zero context about what they're watching, what VURT is, or what else is available. If the first 3 seconds of video don't hook them, they have no reason to stay.

### 5. MISSING THUMBNAIL TOKENS — ALL 7 EPISODES AFFECTED

Console logs show 14 instances (2 per mux-player, for all 7 episodes):
```
[mux-player 3.11.7] Missing expected thumbnail token. No poster image will be shown
```

**Where this shows up:** When a user scrolls down in the vertical feed, each upcoming episode should show a poster/preview frame before the video loads. Instead, they see either a black rectangle or a loading spinner. The Mux player needs a signed thumbnail token to generate poster images — these tokens are not being passed.

**What users see vs what they should see:**
- **Current:** Black screen → age gate → video plays → scroll down → black rectangle → next video slowly loads
- **Should be:** Show poster frame → age gate → video plays → scroll down → poster frame of next episode visible immediately → tap to play

This matters because the poster frame is what makes users want to watch the next episode. Without it, scrolling feels like entering a void.

### 6. THIRD-PARTY BLOAT: 163 OF 189 REQUESTS ARE EXTERNAL

| Domain | Requests | Size |
|--------|----------|------|
| Mux (video CDN) | 113 | 26.4MB |
| Google (GTM + Ads + Analytics) | 13 | 667KB |
| Facebook (Pixel) | 1 | 96KB |
| jsdelivr (Mux player CDN) | 3 | 561KB |
| Firebase | 2 | ~0KB |
| Enveu (CMS images) | 8 | 126KB |

Only **26 of 189 requests** go to myvurt.com itself. The page is almost entirely dependent on third-party services.

### 7. CONSOLE ERRORS

| Error | Count | Impact |
|-------|-------|--------|
| Content-Security-Policy invalid directive '*' | 5 | Broken CSP — security headers misconfigured |
| Firebase messaging not initialized | 1 | Push notifications broken |
| Missing thumbnail token (Mux) | 14 | No episode previews |
| **Total console errors/warnings** | **79-80** | |

---

## Device-by-Device Performance

### Detail Page (Ad Landing)

| Device | LCP | FCP | Load Time | Issues |
|--------|-----|-----|-----------|--------|
| iPhone 15 Pro | 4.8s | 348ms | 3.6s | Age gate on black bg |
| iPhone 15 Pro Max | 5.3s | 500ms | 3.8s | Slowest LCP |
| iPhone SE | 5.5s | 312ms | 3.8s | Smallest screen, modal dominates |
| iPhone 14 | — | — | — | Same as 15 Pro |
| Galaxy S24 | 3.5s | 412ms | 3.6s | Best Android perf |
| Galaxy A54 | 4.5s | 456ms | 3.7s | Mid-range, slower |
| Pixel 7 | 3.5s | 412ms | 3.6s | Similar to S24 |

### Homepage (Browse)

| Device | LCP | FCP | Load Time | Issues |
|--------|-----|-----|-----------|--------|
| iPhone 15 Pro | 1.2s | 312ms | 3.5s | Clean, no gate |
| iPhone SE | 1.1s | 284ms | 3.5s | Fast |
| Galaxy S24 | 1.5s | 452ms | 3.8s | Acceptable |
| Galaxy A54 | 1.2s | 304ms | 3.6s | Good |

**Homepage LCP is 3-4x faster than detail page LCP.** The detail page's LCP is slow because it waits for the Mux video player + video segments to start rendering.

---

## Recommendations for Dev Team

### Priority 1: Fix `preload="auto"` on Off-Screen Mux Players (Biggest Impact)
**Current:** All 7 `<mux-player>` elements have `preload="auto"`, causing 101 media requests before the user even interacts with the age gate. 68 requests fire in the first 2-4 seconds.
**Fix:** Set `preload="none"` for players [1]-[6] (off-screen). Only player [0] (the current episode) should have `preload="auto"`. Use IntersectionObserver to set `preload="auto"` when a player enters the viewport.
**Expected impact:** Initial media requests drop from 101 → ~15. Page weight drops from 27.6MB → ~4MB. Current episode loads 3-5x faster because it's not competing for bandwidth with 6 other videos.

### Priority 2: Fix Duplicate Mux Player Load
**Current:** `@mux/mux-player` loads twice from CDN (556KB total)
**Fix:** Deduplicate the import — single load, cached.
**Expected impact:** 278KB less render-blocking JS, ~400ms faster initial paint.

### Priority 3: Generate Mux Thumbnail Tokens
**Current:** 14 "Missing expected thumbnail token" warnings. No poster images for episodes.
**Fix:** Generate signed thumbnail tokens when creating Mux playback IDs.
**Expected impact:** Users see preview frames when scrolling episodes instead of blank/loading states.

### Priority 4: Defer Non-Critical Third-Party Scripts
**Current:** AdSense (54KB), GTM (112KB), and Facebook Pixel (96KB) all load render-blocking.
**Fix:** Load these async/deferred, after video is playing.
**Expected impact:** ~260KB less render-blocking, faster first paint.

### Priority 5: Add Content Context to Detail Page
**Current:** After age gate, user sees fullscreen video with no title, description, or context.
**Suggestion:** Overlay show title + episode info ("Karma in Heels · Ep 1") as a semi-transparent bar that fades after 3-5 seconds. Add a subtle swipe indicator ("Swipe up for next episode").
**Expected impact:** Users understand what they're watching and know there's more content.

### Priority 6: Optimize the Age Gate UX
**Can't remove it**, but can reduce friction:
- **Show a video preview frame BEHIND the gate** (currently black on most devices) — let users see a compelling frame from the show
- **Auto-dismiss after tap** — currently takes 3-4s to process. Should be instant.
- **Remember the choice** via cookie/localStorage so returning users skip it
- **Pre-render the video** behind the gate so it plays instantly on dismiss (currently takes 2-3s after gate)

### Priority 7: Fix Content-Security-Policy
**Current:** CSP directive uses '*' which is invalid, generating 5 errors per page load.
**Fix:** Set proper CSP directives in server config.

---

## Summary

### The Data Story

- **Homepage bounce: 33.5%** (2,458 sessions) -- healthy, working well
- **Detail page bounce: 69-98%** depending on the show
- **Paid Social: 13,475 sessions (84% of all traffic), 88% bounce** -- drives almost entirely to show detail pages (only 58 sessions to homepage)
- **Direct traffic: 1,797 sessions, 45% bounce, 7m 52s avg duration** -- genuine returning/direct users with real engagement
- **Some shows prove the platform works:** Fatal Lust (23.5% bounce, 29min avg), Favorite Son (43.2%, 17min), The Parking Lot (46.3%, 13min)

### The Technical Story

1. **All 7 `<mux-player>` elements have `preload="auto"`.** This is NOT lazy loading. 101 media requests fire before the user clicks the age gate. 68 of those in the first 2-4 seconds. The devs may think they're lazy-loading because they render 7 players (not all episodes at once), but `preload="auto"` negates that — the browser eagerly downloads all 7 simultaneously.

2. **The age gate covers a black screen** on every device tested. No preview frame, no show context, no reason to click "yes" other than curiosity. Every extra tap = 20-30% drop-off.

3. **Missing Mux thumbnail tokens** means no poster images for any episode across the entire platform.

4. **Mux player JS loaded twice from CDN** — 556KB of duplicate render-blocking JavaScript.

### What to Tell the Dev Team

> "The mux-players have `preload="auto"` on all 7 episodes, even the ones 5,000px off-screen. This fires 101 media requests before the user even clicks the age gate. Suggested approach: player [0] keeps `preload="auto"`, player [1] uses `preload="metadata"` (prevents buffering on scroll), players [2-6] use `preload="none"` with IntersectionObserver to flip to `metadata` when ~1 viewport away. Also generate thumbnail tokens for poster images -- all 7 episodes show the 'Missing expected thumbnail token' warning. And the Mux player CDN import is duplicated (loads twice, 278KB each)."

### Priority Order

1. **`preload="none"` on off-screen mux-players** → cuts page weight from 27.6MB to ~4MB
2. **Generate Mux thumbnail tokens** → poster images for all episodes
3. **Deduplicate Mux player CDN import** → saves 278KB render-blocking JS
4. **Show a preview frame behind the age gate** → gives users a reason to tap "yes"
5. **Add show title overlay for 3-5s after video starts** → context for ad-click users
6. **Defer AdSense + GTM + Facebook Pixel** → 260KB less render-blocking
7. **Use `preload="metadata"` on next-up player** → prevents buffering on scroll while avoiding full preload of all episodes

# VURT Pixel & Tracking Plan

**Date:** March 19, 2026
**Prepared by:** Dioni Vasquez
**For:** Internal Team + Paid Ads Team

---

## Critical Technical Context

**myvurt.com runs on Enveu (Angular SPA).** URL structure:
- **Series pages DO have unique URLs** — e.g., `myvurt.com/series/come-back-dad`. Standard page-load pixels work at the series level. The paid ads team can deep link campaigns directly to specific show pages.
- **Episode pages do NOT have unique URLs** — individual episodes load within the series page without a URL change. Episode-level tracking (play, watch duration, specific episode clicks) requires **event-based pixels** firing on DOM events.
- Static pages (About, FAQ, Contact, Submit) also have unique URLs and can use standard page-load pixels.

**Enveu Share Links (Linkly):** The built-in share button on series generates Enveu deep links (e.g., `https://vurt.enveu.link/ocjfpfvnwz`). These are short links that route users to the correct content across web, app, and app store. The paid ads team should be aware these exist — they may be usable for campaign landing links, and tracking clicks on the share button itself is a pixel event (see #11).

---

## Phase 1: Foundation Pixels (Start Here)

These are the highest-value touchpoints. Get these live first.

### 1. Landing / Entry Pixel
**What:** Fires when a user lands on the site (any page)
**Pages:** `myvurt.com/` (homepage), series pages (e.g., `myvurt.com/series/come-back-dad`), `myvurt.com/about-us`, `myvurt.com/contact-us`
**Why:** Baseline for all attribution. Tells you which ad/source drove the visit.
**Data to capture:**
- Referral source (UTM params: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`)
- Device type (mobile/desktop/tablet)
- Timestamp
- Session ID (for stitching the full journey)

### 2. Age Gate Completion Pixel
**What:** Fires when user confirms they're 17+ and enters the site
**Page:** Homepage age gate modal
**Why:** First real engagement signal. Measures drop-off between landing and actually entering. If 60% of paid traffic bounces at the age gate, that's critical intel.
**Data to capture:**
- Time from landing to age gate completion
- Whether they bounced or proceeded

### 3. Play Button Pixel (PRIORITY)
**What:** Fires when a user clicks play on any series/episode
**Page:** Player component on series page (episode selection is within the series URL — fires on click event, not page load)
**Why:** The money metric. Tells you: "Did the person we paid to bring here actually watch something?"
**Data to capture:**
- Series title / Series ID
- Episode number
- Source (which ad/campaign drove them)
- Time from landing to first play
- Device type

### 4. View Duration / Watch Time Pixel
**What:** Fires at intervals during playback (25%, 50%, 75%, 100% completion)
**Page:** Player component
**Why:** A click isn't a watch. Someone who watches 10 seconds vs. the full episode are completely different signals. This is what tells you which content is actually sticky.
**Data to capture:**
- Series title / Episode number
- Percentage completed (25/50/75/100)
- Total seconds watched
- Whether they skipped/scrubbed forward
- Whether they watched the next episode (binge signal)

### 5. Registration / Sign-Up Pixel (PRIORITY)
**What:** Fires when the registration gate appears AND when user completes sign-up
**Page:** Registration modal (appears after X number of watches)
**Why:** This is your primary conversion event. The full funnel is: Ad → Land → Watch → Register. Two separate pixels needed:
- **Gate Shown:** How many users hit the registration prompt
- **Registration Complete:** How many actually signed up
**Data to capture:**
- Number of episodes watched before gate triggered
- Time on site before gate triggered
- Which series they were watching when gate appeared
- Registration method (email, Google, Apple, etc.)
- Conversion rate (gate shown → registered)

### 6. App Download Pixel (PRIORITY)
**What:** Fires when user clicks iOS App Store or Google Play download links
**Pages:** Any page with app download CTAs
**Why:** Measures cross-platform conversion. Did your web traffic convert to app installs?
**Data to capture:**
- Platform clicked (iOS vs. Android)
- Source page / referral campaign
- Whether user was registered or anonymous
**Note:** Pair with App Store attribution (Apple SKAdNetwork / Google Install Referrer) for full install tracking

---

## Phase 2: Behavior & Navigation Pixels

After foundation pixels are live, add these for deeper user intelligence.

### 7. Categories Page Pixel
**What:** Fires when user navigates to Categories section
**Page:** Categories view
**Why:** When you drive paid traffic to a specific show, this tells you what else those users explore. If everyone who watches "Come Back Dad" then browses Drama, that's targeting gold.
**Data to capture:**
- Which categories browsed
- Time spent in categories
- Which category they clicked into
- Previous content viewed (what show brought them here)

### 8. Series Browse / Thumbnail Click Pixel
**What:** Fires when a user clicks on a series thumbnail (before hitting play)
**Page:** Homepage carousels, category pages, "What's New"
**Why:** Interest signal before commitment. Which thumbnails get clicks vs. which get skipped tells you about creative effectiveness.
**Data to capture:**
- Series title clicked
- Position in carousel/rail (was it slot 1 or slot 15?)
- Which rail/section (Top 10, Break The Boredom, What's New)
- Whether they ultimately played it or bounced back

### 9. "My List" Add Pixel
**What:** Fires when user adds a series to their watchlist
**Page:** Any page with "Add to My List" functionality
**Why:** Intent signal. This is someone planning to come back. High-value retargeting audience.
**Data to capture:**
- Series added
- Number of items already in list
- Whether user is registered

### 10. Submit Your Series Page Pixel
**What:** Fires on page load + form submission
**Page:** `myvurt.com/submit-your-series` (or equivalent CTA)
**Why:** Creator acquisition funnel. If you run creator-facing ads, this is the conversion.
**Data to capture:**
- Page view (interest)
- Form submission (conversion)
- Referral source

### 11. Share / Social Action Pixel
**What:** Fires when user shares content via social share buttons
**Page:** Player component, series detail views
**Why:** Organic amplification signal. Which content do people share? That's your best-performing creative for future ads.
**Note:** The share button currently generates Enveu deep links (e.g., `https://vurt.enveu.link/ocjfpfvnwz`). These route users to the correct content across web and app. The pixel should capture when the share action is triggered and which link is generated.
**Data to capture:**
- Series/episode shared
- Enveu share link generated
- Platform shared to (IG, X, WhatsApp, SMS, copy link)
- Whether sharer is registered

---

## Phase 3: Advanced Tracking (After Foundation Is Solid)

### 12. Scroll Depth Pixel
**What:** Fires at scroll milestones (25%, 50%, 75%, 100%) on homepage
**Page:** Homepage
**Why:** Are users scrolling past the first carousel? If 80% never scroll to "Break The Boredom" rail, that content is invisible.

### 13. Session Replay / Heatmap Integration
**What:** Visual recording of user sessions
**Why:** See exactly what users do. Where they click, where they hesitate, where they leave. Tools like Hotjar or FullStory.

### 14. Return Visit Pixel
**What:** Fires when a previously-seen user returns
**Why:** Retention signal. Did the paid traffic come back organically? That's the real ROI.

### 15. Individual Show Pixels (1,000+ Titles)
**What:** Unique pixel/event per series
**Why:** Per-title attribution for content you're actively promoting
**Approach:** Don't pixel all 1,000 at once. Start with the 10-15 titles you're actively pushing via paid. Use a dynamic pixel that captures the series ID as a parameter rather than deploying 1,000 separate pixels.

---

## Recommended Pixel Architecture

### Don't Deploy 1,000 Pixels — Deploy 1 Smart Pixel

Since series pages have unique URLs but episodes do not, a hybrid approach works best:

1. **One base pixel** on every page (handles landing, session, device, UTM capture) — fires on standard page load for the homepage, series pages, and static pages
2. **Event listeners** for episode-level and in-player actions that fire the same pixel with different event parameters:
   - `event: play` + `series_id: xyz` + `episode: 3`
   - `event: register_gate_shown`
   - `event: register_complete`
   - `event: category_browse` + `category: drama`
   - `event: app_download` + `platform: ios`
   - `event: share` + `series_id: xyz` + `enveu_link: vurt.enveu.link/abc123`
3. **UTM parameter persistence** — UTMs from the landing URL must be captured on entry and stored in session/local storage, then passed with every subsequent event (important for episode-level events where the URL doesn't change)

### UTM Structure for Campaigns

```
?utm_source=[platform]&utm_medium=[paid|organic]&utm_campaign=[campaign_name]&utm_content=[creative_variant]
```

Examples:
- `?utm_source=instagram&utm_medium=paid&utm_campaign=come_back_dad_launch&utm_content=trailer_v2`
- `?utm_source=tiktok&utm_medium=paid&utm_campaign=top10_awareness&utm_content=kevin_hart_clip`

---

## Google Analytics (GA4) Setup — Parallel Track

Alongside custom pixels, GA4 should be set up to capture organic + paid traffic holistically:

| GA4 Event | Maps To | Purpose |
|-----------|---------|---------|
| `page_view` | Landing pixel | Traffic source attribution |
| `play_content` | Play button pixel | Content engagement |
| `watch_progress` | View duration pixel | Watch depth |
| `sign_up` | Registration pixel | Conversion |
| `app_cta_click` | App download pixel | Cross-platform |
| `share_content` | Share pixel | Virality |
| `add_to_list` | My List pixel | Retention intent |

GA4 custom dimensions needed:
- `series_title`
- `episode_number`
- `content_category`
- `user_type` (anonymous / registered)

---

## Priority Summary

| Priority | Pixel | Why It's Critical |
|----------|-------|-------------------|
| 🔴 P0 | Landing / Entry | Can't attribute anything without this |
| 🔴 P0 | Play Button | Core engagement metric |
| 🔴 P0 | Registration Complete | Primary conversion |
| 🟠 P1 | View Duration | Quality of engagement |
| 🟠 P1 | App Download Click | Cross-platform conversion |
| 🟠 P1 | Age Gate Completion | Funnel drop-off diagnosis |
| 🟡 P2 | Categories Browse | Audience interest mapping |
| 🟡 P2 | Thumbnail Clicks | Creative/content testing |
| 🟡 P2 | Registration Gate Shown | Funnel optimization |
| 🟢 P3 | My List, Share, Scroll | Behavioral depth |
| 🟢 P3 | Per-show dynamic pixels | Content-level attribution |

---

## User Journey Map (Point A → Point Z)

```
[Ad / Social Post / Organic Search]
        │
        ▼
   ① LAND on myvurt.com ←── Landing Pixel
        │
        ▼
   ② AGE GATE (17+ confirm) ←── Age Gate Pixel
        │
        ▼
   ③ BROWSE homepage ←── Scroll Depth Pixel
     (carousels, Top 10, What's New)
        │
        ├──→ Categories ←── Categories Pixel
        │
        ▼
   ④ CLICK series thumbnail ←── Thumbnail Click Pixel
        │
        ▼
   ⑤ PLAY episode ←── Play Button Pixel
        │
        ▼
   ⑥ WATCH content ←── View Duration Pixel (25/50/75/100%)
        │
        ├──→ Watch next episode (binge) ←── Sequential Play Pixel
        │
        ├──→ Share ←── Share Pixel
        │
        ├──→ Add to My List ←── My List Pixel
        │
        ▼
   ⑦ REGISTRATION GATE appears ←── Gate Shown Pixel
     (after X watches)
        │
        ▼
   ⑧ REGISTER (free) ←── Registration Pixel
        │
        ├──→ Download App ←── App Download Pixel
        │
        ▼
   ⑨ RETURN VISIT ←── Return Visit Pixel
```

---

## What the Paid Ads Team Needs From VURT Dev/Enveu

1. **Access to inject JavaScript** on the site (for pixel code + event listeners)
2. **DOM element identifiers** — CSS selectors or data attributes for: play button, registration form, age gate, category nav, share buttons, app download links
3. **Player API access** — Does Enveu's video player expose playback events (play, pause, progress, complete)? The paid team needs to hook into these.
4. **Confirmation of registration gate logic** — After how many watches does it appear? Is it configurable? Does it vary by user?
5. **GTM (Google Tag Manager) container** — Easiest way to deploy and manage all pixels from one place without touching site code repeatedly

---

## Email Draft for Paid Ads Team

*(See below — ready to send or edit)*

---

**Subject: VURT Pixel Plan — Pages, Events & Technical Context**

Hey team,

Following up on our call. Here's the breakdown of our site and what we want to track. Important technical context first:

**Our site (myvurt.com) runs on Enveu (Angular SPA).** Here's the URL situation:

**Pages with unique URLs (standard page-load pixels work):**
- Homepage: `myvurt.com/`
- Series pages: e.g., `myvurt.com/series/come-back-dad` (each series has its own URL)
- About: `myvurt.com/about-us`
- Contact: `myvurt.com/contact-us`
- Submit Your Series: `myvurt.com/submit-your-series`
- FAQ, Privacy Policy, Terms of Service

**What does NOT have unique URLs:** Individual episodes within a series. Episode selection happens on the series page without a URL change. So episode-level tracking needs event-based pixels.

**Also worth knowing:** The site has a built-in share feature that generates Enveu deep links (e.g., `https://vurt.enveu.link/ocjfpfvnwz`). These route to the right content across web and app. However, we're working with the dev team to redirect these to myvurt.com URLs — the Enveu links build authority for their domain, not ours. Until that's fixed, prefer direct myvurt.com URLs for campaigns where possible.

**Events we need custom pixels for (fire on user action, not page load):**

1. **Play button click** — When someone clicks play on any episode. We want to know: did the person we drove from social actually watch? Capture the series title and episode number with each fire.

2. **Watch completion** — Fire at 25%, 50%, 75%, 100% of episode. This tells us watch quality, not just clicks.

3. **Registration** — Two events: (a) when our registration gate appears (it shows up after users watch a certain number of episodes), and (b) when they complete sign-up. This is our primary conversion.

4. **App download clicks** — When users click our App Store or Google Play links. We want to know if web traffic converts to app installs.

5. **Category browsing** — When users navigate to our categories section. Especially important when we're driving traffic to a specific show — we want to see what else those users look for.

6. **Thumbnail clicks** — When users click on a series from the homepage carousels or category pages. Interest signal before play.

**User journey (A to Z):**
Ad/Social → Land on site → Age gate (17+) → Browse homepage → Click series → Watch episodes → Registration gate appears → Register for free → Download app / Return visits

**What we want to answer:**
- Which campaigns drive people who actually WATCH (not just land)?
- How long from first visit to registration?
- Which shows have the highest watch-through rates from paid traffic?
- Are users driven by paid ads downloading the app?
- After watching a promoted show, what categories/content do they explore next?

**Start with:** Landing pixel, play button pixel, registration pixel, app download pixel. Then layer in watch duration and category tracking.

**UTM structure we'll use:**
`?utm_source=[platform]&utm_medium=paid&utm_campaign=[campaign_name]&utm_content=[creative_id]`

Let me know what you need from our dev team (Enveu) to get the event listeners set up — DOM selectors, player API access, GTM container, etc. Happy to set up a call with them.

Talk soon,
Dioni

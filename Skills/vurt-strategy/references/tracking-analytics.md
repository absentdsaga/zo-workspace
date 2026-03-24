# VURT Tracking, Pixels & Analytics Infrastructure

## Critical Technical Context

**myvurt.com runs on Enveu (Angular SPA).** This has major implications for tracking:

### URL Structure
- **Series pages HAVE unique URLs** — e.g., `myvurt.com/detail/micro_series/the-love-letter`. Standard page-load pixels work at series level. Paid ads team can deep link campaigns directly to specific show pages.
- **Episode pages do NOT have unique URLs** — individual episodes load within the series page without a URL change. Episode-level tracking (play, watch duration, specific episode clicks) requires **event-based pixels** firing on DOM events.
- **Static pages** (About, FAQ, Contact, Submit) have unique URLs — standard page-load pixels work.

### Enveu Share Links (Linkly)
- Share button generates `https://vurt.enveu.link/{random-hash}` — these route users to correct content across web, app, and app store.
- **SEO problem:** All link equity goes to enveu.link, not myvurt.com.
- **Deep link problem:** Shared links open app to show page, NOT specific episode.
- Paid ads team should know these exist — may be usable for campaign landing links.

---

## Pixel Architecture

### One Smart Pixel, Not 1,000 Separate Pixels

Since series pages have unique URLs but episodes do not, use a hybrid approach:

1. **One base pixel** on every page — handles landing, session, device, UTM capture. Fires on standard page load for homepage, series pages, and static pages.
2. **Event listeners** for episode-level and in-player actions that fire the same pixel with different event parameters:
   - `event: play` + `series_id: xyz` + `episode: 3`
   - `event: watch_progress` + `percent: 50`
   - `event: register_gate_shown`
   - `event: register_complete`
   - `event: category_browse` + `category: drama`
   - `event: app_download` + `platform: ios`
   - `event: share` + `series_id: xyz` + `enveu_link: vurt.enveu.link/abc123`
3. **UTM parameter persistence** — UTMs from landing URL must be captured on entry and stored in session/local storage, then passed with every subsequent event (critical for episode-level events where URL doesn't change).

### UTM Structure for Campaigns
```
?utm_source=[platform]&utm_medium=[paid|organic]&utm_campaign=[campaign_name]&utm_content=[creative_variant]
```
Examples:
- `?utm_source=instagram&utm_medium=paid&utm_campaign=come_back_dad_launch&utm_content=trailer_v2`
- `?utm_source=tiktok&utm_medium=paid&utm_campaign=top10_awareness&utm_content=kevin_hart_clip`

---

## Pixel Implementation — 3 Phases

### Phase 1: Foundation (P0 — Start Here)

| # | Pixel | Trigger | Data Captured |
|---|-------|---------|---------------|
| 1 | **Landing / Entry** | Any page load | UTM params, device type, timestamp, session ID |
| 2 | **Age Gate Completion** | User confirms 17+ | Time from landing to completion, bounce vs proceed |
| 3 | **Play Button** (PRIORITY) | Click play on any episode | Series title, series ID, episode number, source campaign, time-to-first-play, device |
| 4 | **View Duration** | Playback milestones 25/50/75/100% | Series/episode, percent completed, total seconds, skip/scrub detection, binge signal (watched next episode) |
| 5 | **Registration** (PRIORITY) | Gate appears + user completes sign-up | Episodes watched before gate, time on site, series being watched, registration method, conversion rate |
| 6 | **App Download** (PRIORITY) | Click iOS/Android download link | Platform (iOS vs Android), source page/campaign, registered vs anonymous |

### Phase 2: Behavior & Navigation (P1-P2)

| # | Pixel | Trigger | Data Captured |
|---|-------|---------|---------------|
| 7 | **Categories Browse** | Navigate to categories | Categories browsed, time spent, category clicked, previous content viewed |
| 8 | **Thumbnail Click** | Click series thumbnail | Series title, carousel position, rail/section name, whether they ultimately played |
| 9 | **My List Add** | Add series to watchlist | Series added, list size, registered status |
| 10 | **Submit Your Series** | Page load + form submission | Page view (interest), form submit (conversion), referral source |
| 11 | **Share Action** | Share button clicked | Series/episode, enveu link generated, platform shared to, registered status |

### Phase 3: Advanced (P3 — After Foundation Solid)

| # | Pixel | Purpose |
|---|-------|---------|
| 12 | **Scroll Depth** | Homepage scroll milestones (25/50/75/100%) — are users seeing content below fold? |
| 13 | **Session Replay / Heatmap** | Visual session recording (Hotjar/FullStory) — see exactly where users click, hesitate, leave |
| 14 | **Return Visit** | Previously-seen user returns — organic retention signal, true paid ROI |
| 15 | **Per-Show Dynamic Pixels** | Unique event per promoted series (use series_id parameter, don't deploy 1,000 separate pixels). Start with 10-15 actively promoted titles. |

---

## User Journey (Full Funnel)

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

## GA4 Setup (Parallel Track)

### GA4 Property
- Property ID: `518738893`
- Firebase project: `vurt-bd356`
- Status: ⚠️ Blocked — need GA4 access/credentials configured

### Custom Events to Configure

| GA4 Event | Maps To | Purpose |
|-----------|---------|---------|
| `page_view` | Landing pixel | Traffic source attribution |
| `play_content` | Play button pixel | Content engagement |
| `watch_progress` | View duration pixel | Watch depth |
| `sign_up` | Registration pixel | Conversion |
| `app_cta_click` | App download pixel | Cross-platform |
| `share_content` | Share pixel | Virality |
| `add_to_list` | My List pixel | Retention intent |

### Custom Dimensions Needed
- `series_title`
- `episode_number`
- `content_category`
- `user_type` (anonymous / registered)

---

## What the Paid Ads Team Needs From Enveu Dev Team

1. **Access to inject JavaScript** on the site (for pixel code + event listeners)
2. **DOM element identifiers** — CSS selectors or data attributes for: play button, registration form, age gate, category nav, share buttons, app download links
3. **Player API access** — Does Enveu's video player expose playback events (play, pause, progress, complete)? Paid team needs to hook into these.
4. **Confirmation of registration gate logic** — After how many watches does it appear? Configurable? Varies by user?
5. **GTM (Google Tag Manager) container** — Easiest way to deploy and manage all pixels without touching site code repeatedly

---

## Key Questions the Pixel Data Answers

- Which campaigns drive people who actually **WATCH** (not just land)?
- How long from first visit to registration?
- Which shows have the highest watch-through rates from paid traffic?
- Are users driven by paid ads downloading the app?
- After watching a promoted show, what categories/content do they explore next?
- What's the drop-off rate at the age gate? (If 60% bounce there, that's critical)
- Which thumbnails/carousels get clicks vs. get skipped?
- What's the binge rate (users who watch multiple episodes in one session)?

---

## App Store Attribution (Complement to Web Pixels)

- **iOS:** Apple SKAdNetwork for install attribution
- **Google Play:** Install Referrer API for campaign tracking
- Pair with web app download pixel for full cross-platform funnel

---

## Priority Summary

| Priority | Pixel | Why Critical |
|----------|-------|-------------|
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

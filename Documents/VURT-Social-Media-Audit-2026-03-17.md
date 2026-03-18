# VURT Social Media & Web Presence Audit
**Date:** March 17, 2026

---

## Executive Summary

VURT soft-launched ~4 weeks ago (Feb 19) and just landed a **TechCrunch feature** today (March 17). The platform has 100+ titles live, a functioning iOS/Android app (4.7 stars, 11 ratings), and press from Yahoo Tech and Real Reel/Medium. Social presence is early-stage across all platforms with significant room to grow. There are some immediate issues to fix.

---

## Verification Methodology & Limitations
Technical findings were checked using **curl** (raw HTML source) and **Playwright headless Chromium** (390x844 iPhone viewport). However, headless browser testing proved **unreliable for this Angular SPA** — the app requires full client-side hydration that headless Chrome doesn't replicate faithfully. Several rendering/behavior findings were invalidated by manual testing on a real device.

**Confidence levels:**
- **High confidence:** DOM attribute values (URLs, meta tags, image sources) — these are data strings, not rendering behavior
- **Low confidence:** Anything about visual rendering, scroll behavior, or page functionality — headless Chrome cannot reliably test this Angular app. Manual device testing is required.

**Corrections made during audit:**
- ~~Privacy policy redirects to Twitch~~ → Works correctly
- ~~Submit page redirects to Vimeo 404~~ → Works correctly (has contact form)
- ~~About page blank~~ → Has 3 blocks of content
- ~~Mobile scrolling broken~~ → Works on real devices
- ~~Gold overlay rendering bug~~ → Not reproducible on real devices
- ~~Submit Your Series redirects to homepage~~ → Has a working contact form
- ~~Help/support placeholder~~ → Has content on mobile
- ~~What's New placeholder~~ → Navigates to top of page (functions as intended)

---

## Platform-by-Platform Breakdown

### Website — myvurt.com
**Status:** Live, functional
- Powered by Enveu (white-label OTT platform)
- Age gate (17+) on entry
- Nav: What's New, Categories, My List, Submit Your Series
- Footer links to all socials + App Store + Google Play
- **Content library visible:** Top 10 Micro Series rail + "Break The Boredom" rail with 20+ titles
- **Notable titles:** 35 & Ticking, Lord All Men Can't Be Dogs, Lil Duval - Living My Best Life, Girl In The Closet, Miami Kingpins, Miami Confidential, Favorite Son (ft. Rotimi & Serayah)
- About page (`/about-us`) has mission statement and 3 content blocks

### Google Play Store
**Status:** Live, recently updated (March 15, 2026)
- **Downloads:** 10+ (very early stage — no star rating displayed yet)
- **Reviews:** None visible
- **Content rating:** Everyone
- **Price:** Free with in-app purchases
- **Category:** Entertainment
- **Developer:** VURT (links to vurt.com)
- 5 screenshots showing dark-themed, gold-accented streaming UI
- **Issue:** Data safety section claims "no data collected" but also lists data shared with third parties — inconsistency worth cleaning up
- **Compared to iOS:** Significantly behind — iOS has 11 ratings at 4.7★ while Google Play has zero reviews and only 10+ downloads

### iOS App Store
**Status:** Live, v1.0.5 (updated today)
- **Rating:** 4.7/5 (11 ratings)
- **Reviews are positive:**
  - "A Promising Platform" — praises emerging filmmaker support
  - "Saved me $" — found free content that costs money on Prime
  - "Finally... an app for Black Audiences!" — highlights content + smooth player
  - "Great idea and smooth app"
- **Developer:** VURT Corporation
- **Size:** 60.8 MB
- **Age:** 16+
- **Languages:** English + 7 more (Arabic, Dutch, Hungarian, Indonesian, Portuguese, Russian, Spanish)
- **Platforms:** iPhone, iPad, Mac (M1+), Apple Vision
- App description is solid — covers micro-series, short films, docs, and creator submission pitch

### Instagram — @myvurt
**Status:** Active, growing
- **324 followers / 10 following / 21 posts**
- Bio: "Home Of The Vertical Creators. Vertical Micro Series. Built For The Culture. Welcome to VURT. Submit your series"
- Links to myvurt.com + 3 more
- **Content mix:** Launch announcements, TechCrunch feature carousel, Ted Lucas/Real Reel feature, title promos (Come Back Dad, Favorite Son), Liberty City history reel, culture-forward messaging
- **Third-party amplification:** @chadsand reposted the TechCrunch piece, @officialslipnslidemedia posted Miami Kingpins promo
- Posts are well-designed with consistent branding
- **Engagement:** Appears low relative to follower count — typical for early-stage accounts

### Instagram — @VURT_Official
**Status: DEAD — Page returns "Sorry, this page isn't available"**
- This handle is either deactivated, banned, or never existed
- **Action needed:** Remove any references to this handle, or reclaim/redirect it

### TikTok — @myvurt
**Status:** Active but very early
- **1 follower / 0 following / 1 like**
- Bio: "Vertical cinema. Built for the culture."
- **4 videos posted:**
  1. "THIS IS VURT" launch video — **103 views**
  2. Liberty City history — **1 view**
  3. Overtown/Black Miami history — **84 views**
  4. "VURT is live today" launch — **136 views**
- Content is being cross-posted from Instagram
- **Critically underdeveloped** — TikTok should be VURT's strongest channel given the vertical-first positioning

### TikTok — @VURT_Official
**Status: DEAD — "Couldn't find this account"**
- Handle doesn't exist on TikTok
- **Action needed:** Same as IG — remove references or register the handle as a redirect

### Facebook — /myvurt
**Status:** Active but minimal
- **24 followers / 0 following**
- Page type: Media/news company
- Contact: (786) 748-2517 / submissions@myvurt.com
- **0 reviews**
- Photos uploaded (7 total)
- Latest post: "THIS IS VURT" reel (8 hours ago)
- Tagging Swirl Films distribution partner
- **Very early stage** — needs consistent posting schedule

### Snapchat — @myvurt
**Status:** Active, content posting
- Display name: MYVURT
- Last updated: March 16, 2026 (yesterday)
- Bio: "The home for new Black cinema. Discover the stories, creators, and culture shaping the future of film."
- Has VURT logo as profile picture
- At least 3 visible video posts (Stories/Spotlight)
- Follower count not publicly visible on Snapchat
- **This is a hidden gem** — actively maintained but not mentioned prominently anywhere

### Twitch — myvurt
**Status:** Handle claimed, dormant
- Channel exists but is offline with no visible content
- Has a branded banner with "myvurt" watermark pattern
- No custom avatar, no bio, no past VODs
- **Appears to be a name reservation only**

### Kick — vurt
**Status:** Unconfirmed (likely does not exist)
- Kick blocks automated access; web search found zero results
- Handle likely not registered

### Discord — myvurt
**Status:** Invalid/broken invite
- discord.com/invite/myvurt returns "Invite Invalid"
- No accessible VURT Discord server exists

### Vimeo — myvurt
**Status:** Does not exist
- vimeo.com/myvurt returns 404
- Handle not registered

### YouTube — @myVURT1
**Status:** Active but minimal
- **7 subscribers / 4 videos (all Shorts)**
- Bio: "Serialized micro-dramas in vertical. Stories first. Creators first."
- **Videos:**
  1. "THIS IS VURT" — 34 views
  2. Liberty City — 244 views
  3. Overtown/Black Miami — **1.1K views** (best performer)
  4. "VURT is live today" — 101 views
- Same content cross-posted from TikTok/IG
- The Overtown short hit 1.1K which shows YouTube Shorts can work for cultural content

---

## Press & Media Coverage

| Outlet | Piece | Date | Notes |
|--------|-------|------|-------|
| **TechCrunch** (via Yahoo Tech) | "Meet Vurt, the mobile-first streaming platform for indie filmmakers embracing vertical video" | March 17, 2026 | Major feature by Lauren Forristal. Covers launch, 100+ titles, AVOD model, 50/50 rev split, Ted Lucas background, founding team (Tomosunas, Samuels, Sorey, Brooks) |
| **Real Reel / Medium** | "R:ID x Ted Lucas — The Old Way Is Over" | Recent | In-depth Q&A with Ted. Strong quotes about music-to-film pipeline, distribution pain points, generational shift to mobile |

**Key narrative from press:**
- VURT positioned against ReelShort ($1.2B), DramaBox ($276M), Watch Club, and TikTok's PineDrama
- Differentiator: direct creator submission (48-72hr turnaround), non-exclusive licensing, 50/50 rev split
- Founding team credibility: Slip-N-Slide Records, Swirl Films, Hilmon Sorey (angel), Tarik Brooks (BET/REVOLT)
- Competitor context: Disney+, Peacock, Netflix all exploring vertical/short-form

---

## Social Media Tracker Spreadsheet
The Google Sheets tracker has 5 tabs:
1. **Title Assignment & Status** — tracking content pipeline
2. **Metadata Tracker** — metadata for titles
3. **MetaData** — additional metadata
4. **Movies and Actors** — cast/title database
5. **Social Assets Tracker** — social content assets

*(Spreadsheet didn't fully render — recommend reviewing directly in Google Sheets)*

---

## Website Deep Pages Audit

| Page | Status | Notes |
|------|--------|-------|
| `/about-us` | **Functional** | Mission statement + 3 content blocks |
| `/privacy-policy` | **Functional** | Full privacy policy content loads correctly. References VURT Corporation, describes data collection practices. |
| `/terms-and-conditions` | Functional | Full, professional ToS. Florida law, AAA arbitration, 50/50 rev split terms. **Typo: "SUBISSION" instead of "SUBMISSION" in Section 7 heading.** Links to broken /privacy-policy twice. Physical address: 8004 NW 154th Street, Suite 349, Miami Lakes, FL 33016 |
| `/faq` | Functional | 7 solid Q&As covering what VURT is, pricing (free/ad-supported), device compatibility, submissions (email submissions@myvurt.com), content rating (mature audiences) |
| `/contact-us` | Functional (thin) | Just an email (contact@myvurt.com) and bullet list. No form, no phone, no address. Introduces a 4th email address alongside info@, support@, and submissions@ |
| `/help-support` | **Functional** | Has help content on mobile |
| `/what-new` | **Functional** | Navigates to content at top of page |
| `/submit-your-series` | **Functional** | Has contact form for submissions |

**Email address sprawl across the site:**
- info@myvurt.com (Terms page)
- support@myvurt.com (Terms + FAQ)
- contact@myvurt.com (Contact page)
- submissions@myvurt.com (Facebook + FAQ)

---

## Google Drive Assets
4 logo files available:
- VURT_V_SOLO.png
- VURT_horizontal logo.png
- white background VURT logo.png
- black background VURT logo.png

---

## Issues & Action Items

### Confirmed Technical Issues (High Confidence — from DOM data)
1. **iOS App Store link uses India region** — link in DOM is `https://apps.apple.com/in/app/vurt/id6757593810`. The `/in/` means India. Should be regionless: `https://apps.apple.com/app/vurt/id6757593810`. *Verify yourself: scroll to footer on desktop, right-click the App Store badge, copy link.*
2. **All 7 footer images served from another client's QA CDN** — social icons (Facebook, Instagram, Twitter/X, LinkedIn, YouTube) and app badges (Apple Store, Google Play) all load from `resources-qa.enveu.tv/PowerNews/`. "PowerNews" is a different Enveu customer. These images work today but are hosted on someone else's QA server — fragile. *Verify yourself: right-click any social icon in the footer → Inspect → check the `src` attribute.*
3. **No Apple Smart App Banner** — the `<meta name="apple-itunes-app">` tag is missing from page source. This is what makes Safari on iPhone show a "VURT — Open" banner at the top. One line of HTML: `<meta name="apple-itunes-app" content="app-id=6757593810">`. *Verify yourself: open myvurt.com in Safari on iPhone — no app banner appears at top.*
4. **Footer social link URLs have issues** — `tiktok.com/myvurt` (missing `@`, should be `tiktok.com/@myvurt`), `twitter.com/myvurt` (should be `x.com/myvurt`), `youtube.com/vurticals` (may be different channel than `@myVURT1`). *Verify yourself: click each social icon in the footer and check where it goes.*

### Confirmed Social Issues (from platform data)
5. **@VURT_Official is dead on both Instagram AND TikTok** — IG returns "Sorry, this page isn't available", TikTok returns "Couldn't find this account". Either reclaim or scrub all references.
6. **TikTok @myvurt has 1 follower and 4 videos** — for a vertical-first platform, this is the single biggest social gap. Cross-posting IG content isn't enough. Need native TikTok strategy.
7. **Google Play Store has 10+ downloads and zero reviews** — iOS is way ahead (11 ratings, 4.7★). Need to drive Android installs and reviews.
8. **YouTube Shorts showing promise** — the Overtown piece hit 1.1K views organically. Double down on cultural/historical content as a discovery funnel.
9. **Fix Terms of Service typo** — "SUBISSION" should be "SUBMISSION" in Section 7 heading.

### Confirmed Mobile Issues (DOM analysis + user verification)
10. **No social links anywhere on mobile web** — Footer has social links but renders at `height: 0` (invisible). Hamburger menu has a social section container but Angular renders it EMPTY (no icons). User confirmed: social icons are not in the hamburger. There is zero way to find VURT's social accounts from mobile web.
11. **App store download badges invisible on mobile** — Same footer that's `height: 0`. Apple Store and Google Play badges are in the footer DOM but the footer doesn't render on mobile. User confirmed: no store links visible. Mobile web visitors have zero path to install the native app.

### Growth Opportunities (This Month)
12. **Consistent posting cadence** — IG has 21 posts in ~4 weeks which is decent. TikTok/YouTube/Facebook need to match.
13. **Snapchat is a hidden asset** — @myvurt on Snapchat is actively posting but isn't promoted anywhere. Add to website footer and bio links.
14. **Consolidate email addresses** — 4 different contact emails (info@, support@, contact@, submissions@) with no clear routing.
15. **Google Play data safety** — claims "no data collected" but lists data shared with third parties. Inconsistency worth cleaning up.
16. **App Store ratings** — 11 iOS ratings at 4.7 is great quality but low volume. Push in-app review prompts.
17. **Claim unclaimed handles** — Vimeo (myvurt), Kick (vurt) are available. Discord needs a fresh server setup. Twitch handle is claimed but dormant.
18. **Creator testimonials** — get filmmakers who've submitted content to post about their experience.
19. **Leverage the TechCrunch piece** — reshare across all channels, pin it, add to website, use in creator outreach.

---

## Follower Snapshot (March 17, 2026)

| Platform | Handle | Followers | Posts/Videos | Status |
|----------|--------|-----------|-------------|--------|
| Instagram | @myvurt | 324 | 21 | Active |
| Instagram | @VURT_Official | — | — | **DEAD** |
| TikTok | @myvurt | 1 | 4 | Active (barely) |
| TikTok | @VURT_Official | — | — | **DEAD** |
| Facebook | /myvurt | 24 | ~5 | Active (minimal) |
| YouTube | @myVURT1 | 7 | 4 | Active (minimal) |
| Snapchat | @myvurt | N/A (not public) | 3+ | **Active** (hidden gem) |
| Twitch | myvurt | — | 0 | Claimed, dormant |
| Kick | vurt | — | — | Likely unclaimed |
| Discord | myvurt | — | — | Invite invalid |
| Vimeo | myvurt | — | — | Not registered |
| iOS App Store | VURT | 11 ratings (4.7★) | — | Active |
| Google Play | VURT | 10+ downloads (no rating) | — | Active |

**Total social reach: ~356 followers across active platforms** (excludes Snapchat where count isn't public)

### Website Health

| Page | Status |
|------|--------|
| Homepage | Working |
| /about-us | Working |
| /privacy-policy | **Working** |
| /terms-and-conditions | Working (has typo) |
| /faq | Working |
| /contact-us | Working (thin) |
| /help-support | Working |
| /what-new | Working |
| /submit-your-series | Working (contact form) |

---

## Mobile Experience Audit (390x844 / iPhone 14 Pro viewport)

### myvurt.com — Mobile Web

**The Good:**
- Fully responsive at 390px width, no horizontal overflow
- Hero carousel works with swipe and dot indicators
- Full-screen vertical video player is the strongest design decision — matches TikTok/Reels UX with heart/comment/share overlay on the right
- Bottom tab bar (What's New / Categories / My List) is fixed and app-like
- Touch targets are properly sized (44px+), text is readable (12px+)
- Angular SPA framework with lazy loading

**Confirmed Technical Issues (from DOM data — high confidence):**
1. **No Apple Smart App Banner** — `<meta name="apple-itunes-app">` tag missing from source. Safari on iPhone won't show an "Open in App" banner.
2. **iOS App Store link uses India region** — `apps.apple.com/in/app/vurt/id6757593810` (the `/in/` = India)
3. **All 7 footer images from another client's QA CDN** — social icons + app badges load from `resources-qa.enveu.tv/PowerNews/`
4. **Footer social link URLs have issues** — `tiktok.com/myvurt` (missing `@`), `twitter.com/myvurt` (should be `x.com`)

**Confirmed mobile issues (DOM + user verified):**
5. **No social links anywhere on mobile** — footer is `height: 0` (social links invisible). Hamburger menu has social section container but Angular renders it empty (no icons inside). User confirmed not in hamburger. Zero way to find VURT social accounts from mobile web.
6. **App store badges invisible on mobile** — same `height: 0` footer. User confirmed: no store links visible. Zero path to install the native app from mobile web.

**NOTE:** Several previously reported mobile issues (broken scrolling, gold overlay bug, empty search, broken pages) were headless browser artifacts and have been removed. The Angular SPA does not render faithfully in headless Chrome for behavior testing, but DOM data analysis (URLs, meta tags, element structure) is reliable.

### Social Profiles — Mobile View

| Platform | Mobile Rendering | Notes |
|----------|-----------------|-------|
| Instagram @myvurt | **Login wall** | IG blocks all mobile web profile views without auth. Standard behavior, not VURT-specific. Can only verify in-app. |
| TikTok @myvurt | **Visible but gated** | Profile pic (gold V) renders crisp. Bio visible: "Vertical cinema. Built for the culture." Stats show 1 follower. "Open TikTok" modal covers most of page (platform standard). Feed area appears empty. |
| Facebook /myvurt | **Login wall** | Same as IG — requires auth for mobile web. Verify in-app only. |
| YouTube @myVURT1 | **Best mobile presence** | Banner looks professional at mobile width ("Ready to go vertical?"). Bio is clear with myvurt.com link. Shorts grid renders beautifully in 3-column layout. Thumbnails are compelling. Liberty City short showing 244 views = organic discovery happening. |
| Snapchat @myvurt | **Clean** | Gold V logo renders well on white background. Bio fully readable. 3 Spotlight thumbnails visible. Green "Add" button prominent. "Better on the app" banner is standard Snap behavior. |

### App Store Listings — Mobile View

| Store | Mobile Experience | Issues |
|-------|------------------|--------|
| iOS App Store | Solid | 4.7★, 11 ratings, screenshots properly sized, description well-structured. Shows "Designed for iPad" prominently. |
| Google Play | Clean | Gold V icon, "10+" downloads, screenshots carousel works, data safety section present. Install button prominent. |

### Mobile Verdict

The mobile web experience works on real devices (scrolling, pages, content all functional). The full-screen vertical player and bottom nav feel app-native. The confirmed issues are under-the-hood: missing Smart App Banner, India-region App Store link, QA CDN dependencies, and incorrect social link URLs. These are easy fixes. The strongest mobile social presence is YouTube, followed by Snapchat. Instagram and Facebook can't be assessed on mobile web due to login walls.

---

## Bottom Line

VURT has a real product, real content (100+ titles with recognizable talent), legitimate press coverage, and strong investor/advisor backing. The platform is functional on mobile and well-received by early users. The social presence is early-stage across all platforms — expected at 4 weeks post-launch, but needs acceleration given the TechCrunch moment.

**Priority stack:**
1. Fix mobile footer / social links — footer renders at 0px on mobile, all social links and app download badges are invisible. Hamburger menu social section is empty. This is the most impactful fix.
2. Add Apple Smart App Banner — one line of HTML, highest-converting iOS install mechanism
3. Fix iOS App Store link region — `/in/` (India) → regionless
4. Replace QA CDN assets — 7 footer images depend on another Enveu client's QA server (`PowerNews`)
5. Fix footer social link URLs — TikTok missing `@`, Twitter should be X
6. Kill dead handles — @VURT_Official on IG + TikTok
7. Build real TikTok presence — 1 follower on the platform that should be VURT's strongest channel
8. Leverage TechCrunch coverage across all channels
9. Drive Google Play installs + reviews to match iOS

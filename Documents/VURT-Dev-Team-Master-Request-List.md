# VURT — Complete Dev Team Request List
**Date:** March 31, 2026  
**From:** Dioni Vasquez, VURT Co-Lead  
**To:** Andrew / Zupstream-Enveu Engineering Team  
**Context:** This is a comprehensive, itemized list of every outstanding technical task, bug fix, feature request, and platform improvement needed for VURT. Items are organized by priority tier. We need all of this addressed.

---

## STATUS: RECENTLY COMPLETED (For Reference)
These items are DONE and do not need work:
- [x] GTM container (`GTM-MN8TR3CR`) installed on myvurt.com
- [x] GA4 Consent Mode v2 fix deployed (was defaulting to "deny," suppressing engaged sessions)
- [x] Meta Pixel (`659791066496981`) live via GTM, firing on all pages
- [x] Enveu dev team added to Meta Business Portfolio
- [x] Alex Akimov (paid ads) has full Meta Business access
- [x] Security header issue fixed (per dev team 3/31)
- [x] Axios dependency vulnerability patched and deployed
- [x] Series-level GA4 tracking working

---

## TIER 0: CRITICAL / BLOCKING REVENUE & GROWTH (Do Tonight)

### 0.1 — Buffering / CDN Quality Crisis
**Impact:** 90%+ user drop from peak. Users are leaving because content won't play.
- Fastly CDN showing **76.9% buffer ratio** (should be under 2%). CloudFlare at 2.6% is fine — the problem is Fastly.
- Specific ISP issue: Comcast Cable at **49.3% buffer ratio** (2,918 views affected)
- US viewers overall: **20.5% buffer ratio** (60% of total traffic)
- Intermittent spikes: buffer ratio hits 100% during certain hours (confirmed 7 PM ET on 3/31)
- Specific titles severely affected: Come Back Dad Eps 3-5 (30-41% buffer), Love Regardless multiple episodes at 100%
- **Action:** Escalate with Fastly immediately. Investigate CDN configuration, origin shield settings, and cache hit ratios. Consider Fastly region-specific routing issues. Provide a root cause analysis report.

### 0.2 — Episodes Have No Unique URLs
**Impact:** Blocks ALL episode-level SEO, sharing, deep linking, and paid ad targeting.
- When a user switches episodes, the URL stays at the series level (e.g., `/detail/micro_series/the-love-letter`)
- Episodes cannot be indexed by Google, cannot be shared as individual links, cannot be deep-linked from ads
- **Action:** Every episode must get a unique URL that updates in the browser address bar. Format: `/detail/micro_series/{show-slug}/episode-{n}` or equivalent. URL must change when user navigates between episodes.

### 0.3 — Share Links Go to enveu.link, Not myvurt.com
**Impact:** All SEO equity, social shares, and word-of-mouth link value accrues to Enveu's domain instead of VURT's.
- Share button generates `https://vurt.enveu.link/{random-hash}` instead of `myvurt.com` URLs
- The random hash carries zero keyword signal for search engines
- Every time a user shares content, they're building Enveu's domain authority, not VURT's
- **Action:** Share links must generate `myvurt.com` URLs with human-readable paths (e.g., `myvurt.com/watch/the-love-letter/episode-2`)

### 0.4 — Deep Links Broken at Episode Level
**Impact:** Every shared link and every ad click that's supposed to take users to a specific episode instead dumps them at the show page.
- App deep link handler only resolves to the show page, not the specific episode
- The short link likely carries the episode ID but the app doesn't parse it
- **Action:** App deep link handler must parse episode ID from the link and route to the specific episode, not just the show page. Must work on both iOS and Android.

### 0.5 — Series Page Deep Link Bounce
**Impact:** Paid acquisition dollars wasted — users bounce instantly from deep-linked series pages.
- Paid sessions are bouncing instantly when landing on series pages via deep links
- **Action:** Debug session needed to identify the cause. Fix whatever is causing the immediate bounce (could be redirect loop, age gate blocking, loading state, or content not rendering).

### 0.6 — Mobile Footer Completely Broken
**Impact:** Every mobile visitor (majority of traffic) cannot see social links, App Store badge, or Google Play badge.
- `<app-footer>` renders at `height: 0` on mobile
- Hamburger menu has a social section container but Angular renders it empty (no icons)
- This has been broken since at least March 18
- **Action:** Fix the CSS collapse on `<app-footer>` for mobile viewports. Alternatively, move social links and app download badges into the hamburger menu where they'll actually render.

### 0.7 — Sitemap.xml is Empty
**Impact:** Google and all search engines cannot discover any VURT content. Zero organic discovery.
- `myvurt.com/sitemap.xml` returns HTTP 200 but contains **zero URLs**
- **Action:** Auto-generate sitemap with ALL pages: homepage, static pages (About, FAQ, Contact, Help, Privacy, Terms), every series page, every episode page (once unique URLs exist), every category/genre page. Must auto-update whenever new content is published.

### 0.8 — All Meta Tags Are Empty/Null
**Impact:** Social shares show blank previews. Search results show generic text. Zero click-through from search or social.
- Homepage: `og:title`, `og:description`, `og:type`, `twitter:title`, `twitter:description`, `twitter:image` are ALL null/empty
- Series pages and subpages have NO meta tags at all
- **Action:** Implement per-page dynamic meta tags. Detailed templates below:

**Homepage:**
```html
<title>VURT — Free Vertical Drama & Micro-Series | Built for the Culture</title>
<meta name="description" content="Watch 100+ vertical micro-series, dramas, and originals free on VURT. No paywall. Black creators, bold stories, designed for your phone." />
<meta property="og:title" content="VURT — Free Vertical Drama & Micro-Series" />
<meta property="og:description" content="Watch 100+ vertical micro-series and dramas free. No paywall. Built for the culture." />
<meta property="og:image" content="https://www.myvurt.com/images/vurt-og-share-card.jpg" />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://www.myvurt.com/" />
<meta property="og:site_name" content="VURT" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@myvurt" />
<meta name="twitter:title" content="VURT — Free Vertical Drama & Micro-Series" />
<meta name="twitter:description" content="100+ vertical micro-series free. No paywall. Built for the culture." />
<meta name="twitter:image" content="https://www.myvurt.com/images/vurt-og-share-card.jpg" />
<link rel="canonical" href="https://www.myvurt.com/" />
```

**Each Series Page (dynamic):**
```html
<title>{Series Name} | VURT — Watch Free</title>
<meta name="description" content="{Series synopsis, first 155 chars}" />
<meta property="og:title" content="{Series Name} | VURT" />
<meta property="og:description" content="{Series synopsis}" />
<meta property="og:image" content="{Series poster/thumbnail URL}" />
<meta property="og:type" content="video.tv_show" />
<meta property="og:url" content="https://www.myvurt.com/series/{slug}" />
<link rel="canonical" href="https://www.myvurt.com/series/{slug}" />
```

**Each Episode Page (dynamic):**
```html
<title>{Series Name} Ep. {#}: {Episode Title} | VURT</title>
<meta name="description" content="Watch {Series Name} Episode {#} free on VURT. {Episode description, first 120 chars}" />
```

### 0.9 — Episode-Level Tracking Still Incomplete
**Impact:** Cannot measure per-episode performance, which episodes retain users, which cause drop-off.
- Dev team confirmed series-level tracking works but episode numbers are not yet captured
- **Action:** Complete episode-level tracking. Every GA4 event must include `episode_number` as a parameter alongside `series_title`.

---

## TIER 1: HIGH PRIORITY (This Week)

### 1.1 — Angular SPA Blocks Search Engines (SSR / Pre-rendering)
- VURT is an Angular SPA. Crawlers see a blank JavaScript shell, not rendered HTML
- AI search engines (ChatGPT, Perplexity, Google AI Overviews) cannot parse the content at all
- Only 12 HTML pages are indexable out of a 100+ title platform
- **Action:** Implement one of:
  1. **Angular Universal SSR** (preferred — renders pages server-side)
  2. **Prerender.io middleware** (detects bot user agents, serves pre-rendered HTML, minimal code changes)
  3. **Static Site Generation** for fixed pages (About, FAQ, Contact, Help)

### 1.2 — Zero Canonical Tags on Any Page
- 100% of pages (12/12 crawled) missing canonical tags
- Causes duplicate content issues and diluted search rankings
- **Action:** Every page needs `<link rel="canonical" href="https://www.myvurt.com/{page-path}" />`

### 1.3 — Implement JSON-LD Structured Data
- Zero structured data on any page (no JSON-LD, no Microdata, no RDFa)
- No rich results possible in Google (ratings, episode counts, "free" badge)
- **Action:** Add `<script type="application/ld+json">` to:
  - **Homepage:** Organization schema (name, url, logo, sameAs social profiles, contactPoint)
  - **FAQ page:** FAQPage schema with Q&A pairs
  - **Each series page:** TVSeries schema (name, description, genre[], numberOfEpisodes, Offer with price "0")
  - **Each episode page:** TVEpisode schema (name, description, partOfSeries, episodeNumber, duration)

### 1.4 — Fix Broken Internal URLs
- Malformed doubled-domain URLs in production:
  - `myvurt.com/www.myvurt.com/privacy-policy`
  - `myvurt.com/www.myvurt.com/terms-and-conditions`
- Cause: absolute URL placed in an href expecting a relative path
- Internal settings path `/settings/terms-and-conditions` is publicly accessible
- **Action:** Fix the href values. Block `/settings/` paths from public access.

### 1.5 — robots.txt Updates
- **Action:** Add the following:
  ```
  Sitemap: https://www.myvurt.com/sitemap.xml
  Disallow: /settings/
  ```

### 1.6 — Add Apple Smart App Banner
- No `<meta name="apple-itunes-app">` tag on the site
- This is the highest-converting iOS install mechanism — one line of code, completely free
- **Action:** Add to `<head>` of index.html:
  ```html
  <meta name="apple-itunes-app" content="app-id=6757593810">
  ```

### 1.7 — Fix iOS App Store Link Region
- Footer link points to `apps.apple.com/in/app/vurt/id6757593810` — the `/in/` is India
- **Action:** Change to regionless: `https://apps.apple.com/app/vurt/id6757593810`

### 1.8 — Replace QA CDN Assets in Production
- All 7 footer images (5 social icons + 2 app store badges) served from `resources-qa.enveu.tv/PowerNews/` — a **different Enveu customer's QA environment**
- These assets will break without warning if that client's QA environment is recycled
- **Action:** Upload VURT's own icons to VURT's production CDN (`resources-us1.enveu.tv/VURT_...`)

### 1.9 — Fix Footer Social Link URLs
- `tiktok.com/myvurt` should be `tiktok.com/@myvurt` (missing @)
- `twitter.com/myvurt` should be `x.com/myvurt` (platform rebrand)
- `youtube.com/vurticals` — confirm if correct or should be `youtube.com/@myVURT1`
- **Action:** Update all three URLs.

### 1.10 — Fix Terms of Service Typo
- Section 7 heading says **"SUBISSION"** instead of **"SUBMISSION"**
- **Action:** Fix the typo.

### 1.11 — Image SEO: Alt Text and Dimensions
- 100% of images missing alt attributes
- All filenames are hashed CDN URLs with zero SEO value
- Logo image on subpages missing alt text entirely
- No explicit `width`/`height` on `<img>` tags (causes layout shift / poor Core Web Vitals)
- **Action:** Add descriptive alt text to every image. Add explicit width/height attributes. If possible, use descriptive filenames (e.g., `vurt-karma-in-heels-poster.jpg` instead of CDN hash).

### 1.12 — Fix Homepage H1
- Currently dynamically set to the featured series name, changes with carousel
- **Action:** Set a persistent H1: "VURT — Free Vertical Micro-Series & Drama Streaming" (or equivalent keyword-rich heading)

### 1.13 — GA4 Custom Events Configuration
- **Action:** Configure these custom events in GA4:
  - `play_content` (series_title, episode_number, content_category)
  - `watch_progress` (series_title, episode_number, percentage: 25/50/75/100)
  - `sign_up` (method: email/Google/Apple, episodes_watched_before_gate)
  - `app_cta_click` (platform: ios/android, source_page)
  - `share_content` (series_title, episode_number, share_platform)
  - `add_to_list` (series_title)
- **Custom dimensions needed:** `series_title`, `episode_number`, `content_category`, `user_type` (anonymous/registered)

### 1.14 — GA4: New vs. Returning User Distinction
- Cannot currently distinguish new vs. returning users in analytics
- Retention measurement is impossible without this
- **Action:** Configure GA4 user properties and reporting to separate new vs. returning users

### 1.15 — UTM Parameter Persistence
- UTM parameters from landing URLs must be captured on entry and stored in session/local storage
- Must be passed with every subsequent GA4 event (critical because episode-level events happen without URL changes in the current architecture)
- **Action:** Implement UTM capture on page load, store in sessionStorage, attach to all outbound events

### 1.16 — Google Search Console Registration
- VURT is not registered with Google Search Console
- Cannot submit sitemap, monitor indexing, or see search performance
- **Action:** Verify domain ownership and register at search.google.com/search-console

### 1.17 — Bing Webmaster Tools Registration
- ChatGPT uses Bing's index. If VURT isn't in Bing, it doesn't exist for AI search.
- **Action:** Register at bing.com/webmasters, submit sitemap

---

## TIER 2: IMPORTANT (Within 1 Week)

### 2.1 — Provide Root Cause Analysis for User Drop
- 99% web user drop (9,143 to 81 daily users) starting March 29
- Need an autopsy report: what changed, what broke, what traffic source dried up
- **Action:** Investigate and provide a written report on what caused the massive drop.

### 2.2 — Expose Player API Events
- Does Enveu's video player expose playback events (play, pause, progress, complete)?
- Paid ads team needs to hook into these for watch duration tracking
- **Action:** Document available player events and provide access. If not exposed, expose them.

### 2.3 — Provide DOM Element Identifiers
- Paid ads team needs CSS selectors or data attributes for: play button, registration form, age gate modal, category navigation, share buttons, app download links
- **Action:** Add `data-track` attributes to key interactive elements and document them.

### 2.4 — Document Registration Gate Logic
- After how many watches does the registration gate appear? Is it configurable? Does it vary by user type?
- **Action:** Document the current logic and make it configurable.

### 2.5 — Fill Empty Placeholder Pages
- "What's New" page: placeholder with no content
- "Help/Support" page: lists categories but has no articles
- Empty pages damage site-wide quality signals
- **Action:** Populate with real content or add `<meta name="robots" content="noindex">` tags

### 2.6 — Add Security Headers
- 100% of pages missing: Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- 2 pages have unsafe cross-origin links (need `rel="noopener noreferrer"`)
- **Action:** Add all four headers at the server/CDN config level.

### 2.7 — Add Meta Keywords to All Pages
- Bing uses meta keywords, and Bing powers ChatGPT search
- Low effort, meaningful for AI discoverability
- **Action:** Add `<meta name="keywords" content="...">` with relevant terms per page

### 2.8 — Fix Internal Linking Architecture
- 33% of pages have zero internal outlinks (dead-end pages)
- Homepage has only 1 inlink (critically low)
- Legal/support pages get the most internal links — content pages get almost none (inverted priority)
- **Action:** Add prominent internal links from homepage and navigation to top series, genre categories, and featured content.

### 2.9 — Add Press/Social Proof to Homepage
- TechCrunch featured VURT — that logo should be on the homepage
- Talent names (Kevin Hart, Vivica A. Fox) should be visible
- App store ratings, download counts
- **Action:** Add a social proof / press section to the homepage.

### 2.10 — Duplicate Content Cleanup
- 42% duplicate content detected across crawled pages (Angular serving same JS shell)
- 42% duplicate page titles ("Video Detail" repeated)
- 58% of titles under 30 characters
- **Action:** Ensure every page has a unique `<title>` and unique rendered content.

---

## TIER 3: APP STORE OPTIMIZATION (Within 2 Weeks)

### 3.1 — Google Play Title Optimization
- Change from "VURT" to **"VURT - Free Vertical Drama & Micro-Series"**
- Add keywords to description: "free streaming", "micro-drama", "vertical cinema", "Black culture", "short-form drama"

### 3.2 — Google Play "What's New" Text
- Replace generic "Small updates, same big vision" with keyword-rich update notes

### 3.3 — Google Play Data Safety Fix
- Currently contradicts itself: claims "no data collected" but also says "may share data types with third parties" (personal info, device IDs) and "data isn't encrypted"
- **Action:** Review and correct data safety declaration in Google Play Console to be accurate and consistent

### 3.4 — Google Play Developer Website
- Developer page links to `vurt.com` not `myvurt.com`
- **Action:** Update to `myvurt.com`

### 3.5 — iOS App Store Keyword Optimization
- Title/subtitle should include target keywords
- Keyword field should include all Tier 1-3 search terms
- Same optimization as Google Play listing

### 3.6 — In-App Review Prompts
- iOS: Implement `SKStoreReviewController` to prompt ratings after positive engagement (finishing a title, 3rd session, adding to My List)
- Android: Implement equivalent in-app review prompt
- Google Play has 10+ downloads and ZERO reviews vs iOS at 4.7 stars from 11 ratings

### 3.7 — Google Play Install Campaign Support
- Google Play installs far behind iOS — need infrastructure to support targeted install campaigns

---

## TIER 4: TRACKING & PIXEL INFRASTRUCTURE (Within 2 Weeks)

### 4.1 — Event-Based Pixel Architecture
- Because episodes currently have no unique URLs, episode-level tracking MUST use event-based pixels, not page load triggers
- One smart base pixel + event listeners for in-player actions with dynamic parameters

### 4.2 — Foundation Event Pixels (P0/P1)
Implement the following event tracking (via GTM or direct):

| Pixel | Fires On | Captures |
|-------|----------|----------|
| Landing/Entry | Any page load | UTM params, device, session ID, timestamp |
| Age Gate | User confirms 17+ | Time from landing to completion, bounce vs proceed |
| Play Button | Click play on any episode | series_id, episode_number, source campaign, time to first play |
| View Duration | 25/50/75/100% completion | Series, episode, % completed, seconds watched, skip/scrub behavior, binge signal (watched next ep) |
| Registration Gate Shown | Gate appears | Episodes watched before trigger, time on site, series playing |
| Registration Complete | User signs up | Method (email/Google/Apple), conversion rate |
| App Download Click | Click iOS/Android link | Platform, source page, registered vs anonymous |

### 4.3 — Behavior & Navigation Pixels (P2)

| Pixel | Fires On | Captures |
|-------|----------|----------|
| Category Browse | Navigate to categories | Categories browsed, time spent, category clicked |
| Thumbnail Click | Click series thumbnail | Series title, position in carousel, which rail/section, played or bounced |
| My List Add | Add to watchlist | Series, items in list, user registered status |
| Share Action | Click share button | Series/episode, platform shared to, share link generated |
| Submit Your Series | Page load + form submit | Page view (interest), form submission (conversion) |
| Scroll Depth | 25/50/75/100% scroll | Homepage scroll engagement |

### 4.4 — App Store Attribution
- iOS: Apple SKAdNetwork for install attribution
- Android: Google Install Referrer API for campaign tracking
- Pair with web app download click pixel for full cross-platform funnel

### 4.5 — Web-to-App Conversion Tracking
- Need mechanism to measure conversion rate from myvurt.com visit to app install
- Currently no way to track this critical funnel step

---

## TIER 5: API & INTEGRATION ACCESS (Within 1 Week)

### 5.1 — Enable YouTube Analytics API
- API not enabled in GCP console — blocks daily views, watch time, demographics, retention curves, traffic source data
- **Action:** Enable "YouTube Analytics API" at `console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com` on the VURT GCP project

### 5.2 — YouTube Data API Access
- Blocked pending `developer@myvurt.com` enabling it on Google Cloud project `522377718476`
- **Action:** Enable YouTube Data API v3 on the GCP project and grant access

### 5.3 — Frame.io Write Access
- Currently read-only. Cannot tag/label assets, set thumbnails, or add comments via API
- v4 API has no asset-level PUT/PATCH route
- **Action:** Provide v2 developer token or upgrade Adobe OAuth scopes for write operations

### 5.4 — Mux Data Add-on Verification
- Getting 404 on `/data/v1` endpoint — viewer-level analytics may require Data add-on
- **Action:** Check if Mux Data add-on is enabled. If not, enable it.

### 5.5 — Meta Ads API Access
- Need `ads_read` scope for campaign performance data
- **Action:** Upgrade Meta token via Meta Business Suite to include `ads_read`

### 5.6 — TikTok Official API
- Currently scraping TikTok HTML for metrics (fragile, rate-limited)
- **Action:** Set up official TikTok API integration for reliable metrics

### 5.7 — Clarify GA4 Properties
- Three GA4 properties exist under the account (`vurt-bd356`, `vurt-790c4`, `vurt-9e1c5`)
- Only `518738893` appears to be active production
- **Action:** Explain what the other two properties are for. Confirm which is production. Decommission unused ones.

---

## TIER 6: CONTENT DELIVERY & SUBTITLE SYSTEM

### 6.1 — SRT Upload Mechanism
- We have generated SRT files for titles (via Frame.io + AssemblyAI pipeline)
- **Action:** What is the process for uploading/attaching SRT files to content in Enveu? Is there an API or CMS mechanism? We need a documented workflow.

### 6.2 — Subtitle Display Support
- Platform content standards require "clear subtitles or closed captions" on all content
- **Action:** Confirm the player supports SRT/VTT subtitle rendering and provide the upload path

---

## TIER 7: PRODUCT & PLATFORM FEATURES (Roadmap)

### 7.1 — Culture-Based Content Categorization
- Content is currently organized by genre (Drama, Comedy, Thriller)
- VURT's differentiator is organizing by CULTURE (Black Cinema, Horror Culture, Hip Hop Culture, Anime Culture, Gaming Culture)
- **Action:** Implement culture-based categories as the primary content organization. Genre becomes secondary.

### 7.2 — In-App Community Features (Phase 1)
- Comments on episodes + basic chat
- Without community features, VURT is just a content library with no reason to return
- **Action:** Implement episode-level comments and basic social interaction

### 7.3 — Creator Revenue Transparency Dashboard
- Creators need to see how they earn (50/50 rev split model)
- **Action:** Build a creator-facing dashboard showing views, revenue share, and payout status

### 7.4 — Open Submissions Portal
- Currently submission happens via email — needs a proper portal/pipeline
- **Action:** Build a content submission system accessible from the platform

### 7.5 — Shareable Clips from App
- Users must be able to share clips/screenshots from within the app
- Quibi died partly because it blocked sharing — VURT must enable it
- **Action:** Implement native sharing of clips/screenshots from the app

### 7.6 — Auto-Play on Deep Link Landing
- When ads deep-link to a series page, content should auto-play immediately
- **Action:** Implement auto-play behavior for deep-linked content

### 7.7 — Watch Parties (Phase 2)
- Social viewing with real-time chat — no microdrama platform has this
- **Action:** Build synchronized viewing + real-time chat feature

### 7.8 — Interactive Features (Phase 3)
- Polls, predictions, fan voting, leaderboards during episodes
- This is VURT's whitespace — no competitor has interactive features
- **Action:** Build participation mechanics tied to episode viewing

### 7.9 — Audience-Influenced Storylines (Phase 4)
- Community-driven content where audience votes influence plot decisions
- **Action:** Build voting/polling infrastructure that feeds back to content production

### 7.10 — Bullet Comments (Bilibili Model)
- Comments that float across the screen during playback
- Popular in Asian streaming — novel for Western/Black culture audiences
- **Action:** Evaluate and build real-time on-screen comment overlay

### 7.11 — Email Consolidation
- 4 email addresses across the site (`info@`, `support@`, `contact@`, `submissions@`) with no routing guide
- **Action:** Consolidate to 2 max with clear purposes and proper routing

---

## TIER 8: INFRASTRUCTURE QUESTIONS REQUIRING ANSWERS

These are open questions that have been asked but never answered. We need answers to proceed:

1. **What can be customized in Enveu?** (meta tags, schema markup, URL structure, sitemap, image alt text, filenames, robots.txt)
2. **Does Enveu support Angular Universal (SSR)?** If not, can Prerender.io be added as middleware?
3. **Why don't episodes have unique URLs?** Is this an Enveu platform limitation or a configuration issue?
4. **Can share links be configured to use myvurt.com instead of vurt.enveu.link?**
5. **Can custom JSON-LD `<script>` tags be injected per page?**
6. **Who controls robots.txt and sitemap.xml?** Can they be edited directly?
7. **Does Enveu's video player expose playback events?** (play, pause, progress, complete)
8. **Where in Enveu CMS can image alt text be set per content item?**
9. **How does the deep link handler work?** What would it take to fix episode-level routing?
10. **Can JavaScript be injected on specific pages?** (for pixel code and event listeners beyond GTM)
11. **What is the registration gate trigger logic?** (number of watches, configurable?)
12. **What caused the 99% user drop starting March 29?** Root cause analysis needed.
13. **Is Mux Data add-on enabled?** (getting 404 on data endpoints)

---

## SUMMARY COUNT

| Tier | Items | Description |
|------|-------|-------------|
| Tier 0 | 9 | Critical / Blocking Revenue (Tonight) |
| Tier 1 | 17 | High Priority (This Week) |
| Tier 2 | 10 | Important (Within 1 Week) |
| Tier 3 | 7 | App Store Optimization (2 Weeks) |
| Tier 4 | 5 | Tracking & Pixel Infrastructure (2 Weeks) |
| Tier 5 | 7 | API & Integration Access (1 Week) |
| Tier 6 | 2 | Subtitle/Content Delivery |
| Tier 7 | 11 | Product & Platform Features (Roadmap) |
| Tier 8 | 13 | Open Questions Needing Answers |
| **TOTAL** | **81** | |

---

*This document consolidates findings from: SEO Master Plan, SEO Dev Team Brief, Pixel Tracking Plan, API Capabilities Audit, Google Play Store Audit, Site Audit Action Items, Dev Call Talking Points, NPAW analytics data, GA4 analytics data, daily analytics reports, and all ongoing VURT operational conversations.*

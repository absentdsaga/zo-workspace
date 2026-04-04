# VURT — Dev Team Operations List (v2)
**Date:** March 31, 2026
**From:** Dioni Vasquez, VURT Co-Lead
**To:** Andrew Rivers / Zupstream-Enveu Engineering Team
**CC:** Hilmon Sorey, Ted Lucas, Mark Samuels
**Context:** This is everything we need from the dev team. Every item is required. Items are numbered and sequenced into three buckets — **NOW** (before anything else), **THIS SPRINT** (this week), and **BEFORE NEXT PUSH** (within 2 weeks). The buckets are sequencing, not importance. Everything on this list matters.

---

## DONE (For Reference — No Action Needed)
- [x] GTM container (`GTM-MN8TR3CR`) installed on myvurt.com
- [x] GA4 Consent Mode v2 fix deployed (was defaulting to "deny," killing engaged sessions)
- [x] Meta Pixel (`659791066496981`) live via GTM, firing on all pages
- [x] Enveu dev team added to Meta Business Portfolio
- [x] Alex Akimov (paid ads) has full Meta Business access
- [x] Security header issue fixed
- [x] Axios dependency vulnerability patched and deployed
- [x] Series-level GA4 tracking working
- [x] Dioni has full Frame.io permissions
- [x] Dioni has full Meta Business Portfolio control (Admin)

---

## NOW

### 1. Fix the buffering — Fastly CDN is broken
`ENVEU`

When someone presses play, the video stutters, freezes, or won't load. Your Fastly CDN is failing — it has a 77% buffer ratio when it should be under 2%. Your CloudFlare CDN works fine at 2.6%, so the problem is specifically Fastly. This is the #1 reason users leave. A viewer who buffers for more than 3 seconds is gone. Comcast users alone have a 49% buffer ratio across nearly 3,000 views.

**What needs to happen:** Escalate with Fastly. Investigate CDN configuration, origin shield settings, cache hit ratios, and region-specific routing. Provide a root cause analysis.

**What we need from you:** Written report on what's wrong and what you did to fix it.

**Status on your tracker:** Not listed. Needs to be added immediately.

---

### 2. Give every episode its own URL
`ENVEU`

Right now, when a user watches Episode 3 of a show, the browser still says `/detail/micro_series/the-love-letter` — the same URL for every episode. It's like if YouTube showed the same URL whether you're watching a 2-minute clip or a 2-hour documentary. This breaks everything downstream: Google can't index individual episodes, you can't share a link to a specific episode, ads can't target specific episodes, and analytics can't tell which episodes perform.

**What needs to happen:** When a user navigates between episodes, the URL in the browser must change. Format: `/detail/micro_series/{show-slug}/episode-{n}` or equivalent.

**What we need from you:** Nothing — this is entirely your codebase.

**Status on your tracker:** Row 46, In-Progress, P1. Keep pressure — this has been "in progress" for a while.

---

### 3. Share links must use myvurt.com, not enveu.link
`ENVEU`

When someone shares a VURT show, the link says `vurt.enveu.link/random-letters` instead of `myvurt.com/show-name`. Every share, every backlink, every social post is building Enveu's domain authority in Google instead of ours. This is like paying rent on someone else's storefront sign. Every day this stays broken, we lose SEO equity we can never get back.

**What needs to happen:** Share links must generate `myvurt.com` URLs with human-readable paths (e.g., `myvurt.com/watch/the-love-letter/episode-2`).

**What we need from you:** Nothing.

**Status on your tracker:** Row 42, Waiting, P1. "Waiting" means you haven't started. Start.

---

### 4. Deep links must go to the specific episode, not the show page
`ENVEU`

When someone clicks a shared link or an ad that's supposed to take them to Episode 5, the app opens to the show page instead. The link probably carries the episode ID but the app ignores it. Every ad dollar targeting a specific episode is wasted because the user lands somewhere generic.

**What needs to happen:** Deep link handler must parse the episode ID and route to the specific episode. Must work on iOS, Android, and web.

**What we need from you:** Nothing.

---

### 5. Figure out why series pages bounce from ads
`ENVEU`

Paid traffic bounces instantly when landing on series pages via deep links. We tested loading a series page from our end and it timed out — couldn't even load the page. If automated tools can't load it, real users clicking from ads are getting the same experience. Every ad click that bounces is money burned.

**What needs to happen:** Debug session to identify the cause — could be a redirect loop, the age gate blocking content, a loading spinner that never resolves, or the page simply taking too long to render. Fix whatever it is.

**What we need from you:** Nothing.

---

### 6. Mobile footer is completely broken
`ENVEU`

On mobile (where most of your traffic is), the footer renders at zero height. Nobody can see the social links, App Store badge, or Google Play badge. The hamburger menu has a social section container but Angular renders it empty — no icons appear. This has been broken since at least March 18.

**What needs to happen:** Fix the CSS collapse on `<app-footer>` for mobile viewports. Or move social links and app download badges into the hamburger menu where they'll actually render.

**What we need from you:** Nothing.

---

### 7. Sitemap.xml is empty
`ENVEU`

`myvurt.com/sitemap.xml` returns HTTP 200 but contains zero URLs. Google and every search engine look at the sitemap to discover your content. An empty sitemap means Google has no map of what exists on VURT. Zero organic discovery.

**What needs to happen:** Auto-generate a sitemap with ALL pages: homepage, static pages (About, FAQ, Contact, Help, Privacy, Terms), every series page, every episode page (once unique URLs exist from item #2), every genre/category page. Must auto-update whenever new content is published via the CMS.

**What we need from you:** Nothing.

**Status on your tracker:** Row 43, Waiting, P0. Marked P0 but never started.

---

### 8. All meta tags are empty
`ENVEU`

When someone shares a VURT link on social media, the preview card shows nothing — no title, no image, no description. Same in Google search results — generic or missing text. The HTML tags that control these previews (`og:title`, `og:image`, `og:description`, etc.) are ALL null on every page. This means every share on Instagram, Twitter, WhatsApp, iMessage, Slack — anywhere — shows a blank card. Nobody clicks a blank card.

**What needs to happen:** Implement per-page dynamic meta tags. Here are the exact templates:

**Homepage:**
```html
<title>VURT — Free Vertical Drama & Micro-Series | Stream Now</title>
<meta name="description" content="Watch 100+ vertical micro-series, dramas, and originals free on VURT. No paywall. Bold stories, designed for your phone." />
<meta property="og:title" content="VURT — Free Vertical Drama & Micro-Series" />
<meta property="og:description" content="Watch 100+ vertical micro-series and dramas free. No paywall. Stream now." />
<meta property="og:image" content="https://www.myvurt.com/images/vurt-og-share-card.jpg" />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://www.myvurt.com/" />
<meta property="og:site_name" content="VURT" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@myvurt" />
<meta name="twitter:title" content="VURT — Free Vertical Drama & Micro-Series" />
<meta name="twitter:description" content="100+ vertical micro-series free. No paywall. Stream now." />
<meta name="twitter:image" content="https://www.myvurt.com/images/vurt-og-share-card.jpg" />
<link rel="canonical" href="https://www.myvurt.com/" />
```

**Each Series Page (dynamic per title):**
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

**What we need from you:** We will provide the OG share card image (1200x630 jpg) for the homepage. All other images/text should pull dynamically from the CMS data you already have.

---

### 9. Implement Server-Side Rendering (SSR)
`ENVEU`

This is the prerequisite that makes half the other items on this list actually work. VURT is currently running as an Angular SPA (Single Page Application). That means when a browser loads a page, it first gets an empty HTML shell, then JavaScript builds the page content. The problem: Google, social media crawlers, ChatGPT, and every other bot sees the empty shell. They can't read the JavaScript. So even if you add perfect meta tags, a perfect sitemap, and perfect structured data — crawlers will still see an empty page.

The industry standard for content platforms (Netflix, YouTube, every major streaming app) is SSR — the server builds the full HTML before sending it to the browser. Crawlers get complete content. Users get faster initial page loads.

You told us you're using "a mix of SSR and SPA" and that "SPA is the newer way." That's the wrong direction. SPA is newer in your codebase, but the industry trend is the opposite — everyone moved to SSR because Google demands it. We need full SSR.

**What needs to happen:** Implement Angular Universal for server-side rendering across all pages. If that's not feasible on your platform, implement Prerender.io middleware as the minimum — it detects bot user agents and serves pre-rendered HTML to crawlers while humans get the SPA. Minimal code change for the middleware route.

**This is not optional.** Without SSR or pre-rendering, items 7 (sitemap), 8 (meta tags), 11 (JSON-LD), 12 (canonical tags), and 16 (H1 fix) are all cosmetic — crawlers still see empty HTML regardless.

**What we need from you:** A written plan for how you will implement SSR or pre-rendering, with a timeline.

---

### 10. Episode-level tracking
`ENVEU`

You confirmed series-level GA4 tracking works, but episode numbers aren't captured yet. Without this we can't measure which episodes retain users, which cause drop-off, or which are worth promoting.

**What needs to happen:** Every GA4 event must include `episode_number` as a parameter alongside `series_title`.

**What we need from you:** Nothing.

**Status on your tracker:** Row 45, Waiting, P0.

---

## THIS SPRINT

### 11. Add JSON-LD structured data to every page
`ENVEU`

Zero structured data exists on any page. This means Google can't show rich results — no star ratings, no episode counts, no "Free" badge, no series info cards in search. Structured data is what makes your listing stand out vs plain blue links.

**What needs to happen:** Add `<script type="application/ld+json">` blocks to:
- **Homepage:** Organization schema (name, url, logo, sameAs for social profiles)
- **FAQ page:** FAQPage schema with Q&A pairs
- **Each series page:** TVSeries schema (name, description, genre, numberOfEpisodes, Offer with price "0")
- **Each episode page:** TVEpisode schema (name, description, partOfSeries, episodeNumber, duration)

**What we need from you:** Confirm the correct social profile URLs (TikTok, YouTube, X/Twitter, Instagram, Facebook).

---

### 12. Add canonical tags to every page
`ENVEU`

100% of pages are missing canonical tags. This means Google doesn't know which version of a page is the "real" one, which causes duplicate content penalties and diluted search rankings.

**What needs to happen:** Every page needs `<link rel="canonical" href="https://www.myvurt.com/{page-path}" />`

**What we need from you:** Nothing.

---

### 13. Fix broken internal URLs
`ENVEU`

There are malformed doubled-domain URLs in production:
- `myvurt.com/www.myvurt.com/privacy-policy`
- `myvurt.com/www.myvurt.com/terms-and-conditions`

Someone put an absolute URL in an href that expects a relative path. Also, `/settings/terms-and-conditions` is publicly accessible — internal settings paths should not be exposed.

**What needs to happen:** Fix the href values. Block `/settings/` paths from public access.

**What we need from you:** Nothing.

---

### 14. Update robots.txt
`ENVEU`

**What needs to happen:** Add:
```
Sitemap: https://www.myvurt.com/sitemap.xml
Disallow: /settings/
```

**What we need from you:** Nothing.

---

### 15. Fix iOS App Store link region
`ENVEU`

The footer link points to `apps.apple.com/in/app/vurt/id6757593810` — the `/in/` means India. Your users are in the US.

**What needs to happen:** Change to regionless: `https://apps.apple.com/app/vurt/id6757593810`

**What we need from you:** Nothing.

---

### 16. Fix homepage H1
`ENVEU`

The main heading on the homepage dynamically changes to whatever series is featured in the carousel. Search engines use the H1 to understand what the page is about. A changing H1 confuses Google.

**What needs to happen:** Set a persistent H1 like "Watch Free Vertical Drama & Micro-Series on VURT." The carousel can still rotate featured titles visually — the H1 and the hero carousel are separate elements. The H1 can sit above the carousel or be visually hidden (still readable by search engines) while the carousel stays the main visual. The H1 doesn't need to be the biggest element on the page.

**What we need from you:** We'll confirm the exact wording. Use the above as placeholder until then.

---

### 17. Replace QA CDN assets in production
`ENVEU`

All 7 footer images (5 social icons + 2 app store badges) are served from `resources-qa.enveu.tv/PowerNews/` — a different Enveu customer's QA environment. These assets will break without warning if that client's QA environment is recycled.

**What needs to happen:** Upload VURT's own icons to VURT's production CDN (`resources-us1.enveu.tv/VURT_...`).

**What we need from you:** Nothing.

---

### 18. Fix footer social link URLs
`ENVEU`

- `tiktok.com/myvurt` should be `tiktok.com/@myvurt` (missing @)
- `twitter.com/myvurt` should be `x.com/myvurt` (platform rebrand)
- `youtube.com/vurticals` — needs confirmation if this is correct or should be `youtube.com/@myVURT1`

**What we need from you:** We'll confirm the correct YouTube handle.

---

### 19. Fix Terms of Service typo
`ENVEU`

Section 7 heading says **"SUBISSION"** instead of **"SUBMISSION"**.

**What we need from you:** Nothing.

---

### 20. GA4 custom events
`ENVEU`

Beyond basic page tracking, we need these custom events configured so the paid ads team can optimize campaigns and we can measure what actually matters:

| Event | Parameters |
|-------|-----------|
| `play_content` | series_title, episode_number, content_category |
| `watch_progress` | series_title, episode_number, percentage (25/50/75/100) |
| `sign_up` | method (email/Google/Apple), episodes_watched_before_gate |
| `app_cta_click` | platform (ios/android), source_page |
| `share_content` | series_title, episode_number, share_platform |
| `add_to_list` | series_title |

**Custom dimensions needed:** `series_title`, `episode_number`, `content_category`, `user_type` (anonymous/registered)

**What we need from you:** Nothing — event names and parameters are defined above.

---

### 21. New vs. returning user distinction in GA4
`ENVEU`

We can't currently tell new users from returning users. Without this, measuring retention is impossible.

**What needs to happen:** Configure GA4 user properties and reporting to separate new vs. returning users.

**What we need from you:** Nothing.

---

### 22. UTM parameter persistence
`ENVEU`

When someone clicks an ad with UTM tracking parameters in the URL, those parameters need to stick around for the whole session. Right now, because episodes don't change the URL (item #2), the UTM data is lost after the landing page. The paid ads team can't attribute conversions without this.

**What needs to happen:** Capture UTM parameters on page load, store in sessionStorage, attach to all outbound GA4 events.

**What we need from you:** Nothing.

---

### 23. Register with Google Search Console
`ENVEU` + `VURT INTERNAL`

VURT is not registered with Google Search Console. We can't submit our sitemap, monitor indexing, or see search performance data.

**What needs to happen:** Verify domain ownership at search.google.com/search-console and register.

**What we need from you:** We may need to add a DNS TXT record or HTML file depending on the verification method. We'll coordinate.

---

### 24. Register with Bing Webmaster Tools
`ENVEU` + `VURT INTERNAL`

ChatGPT uses Bing's index. If VURT isn't in Bing, it doesn't exist for AI search engines.

**What needs to happen:** Register at bing.com/webmasters and submit sitemap.

**What we need from you:** Same as above — may need DNS/HTML verification.

---

### 25. Image SEO: alt text and dimensions
`ENVEU`

100% of images are missing alt attributes. All filenames are hashed CDN URLs with zero SEO value. No explicit width/height on `<img>` tags, which causes layout shift and hurts Core Web Vitals scores.

**What needs to happen:** Add descriptive alt text to every image. Add explicit width/height attributes. If possible, use descriptive filenames instead of CDN hashes.

**What we need from you:** Nothing.

---

### 26. Expose player API events
`ENVEU`

The paid ads team needs to hook into video player events (play, pause, progress percentages, completion) to track watch duration for ad conversion optimization. Does your player expose these events? If so, document them. If not, expose them.

**What we need from you:** Documentation of available player events, or implement them if they don't exist.

---

### 27. Provide DOM element identifiers for tracking
`ENVEU`

The paid ads team needs CSS selectors or data attributes on key interactive elements so they can set up event tracking in GTM: play button, registration form, age gate modal, category navigation, share buttons, app download links.

**What needs to happen:** Add `data-track` attributes to these elements and document them.

**What we need from you:** Nothing.

---

### 28. Document the registration gate logic
`ENVEU`

After how many watches does the registration gate appear? Is it configurable? Does it vary by user type? We need this documented so the paid ads team can set expectations and we can optimize the conversion funnel.

**What we need from you:** Nothing — just document what already exists and tell us.

---

### 29. Provide root cause analysis for user drop
`ENVEU`

Web users dropped 99% — from 9,143 daily to 81 — starting March 29. We need to know what changed, what broke, what traffic source dried up. This was requested on 3/31 and you said you'd have an update by tomorrow (April 1).

**What we need from you:** Nothing — this is your infrastructure.

---

### 30. Fill empty placeholder pages
`ENVEU`

"What's New" page is a placeholder with no content. "Help/Support" lists categories but has no articles. Empty pages damage site-wide quality signals that affect how Google ranks every other page.

**What needs to happen:** Populate with real content or add `<meta name="robots" content="noindex">` to prevent Google from indexing empty pages.

**What we need from you:** We can provide copy for these pages if needed.

---

### 31. Add security headers
`ENVEU`

100% of pages missing: Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, Referrer-Policy. Two pages have unsafe cross-origin links missing `rel="noopener noreferrer"`. (Note: you said security headers were fixed on 3/31 but they were not present when we last checked — please verify.)

**What we need from you:** Nothing.

---

### 32. Fix internal linking architecture
`ENVEU`

33% of pages are dead ends — no links going out to other content. The homepage has only 1 inlink. Legal/support pages get the most internal links while content pages get almost none. This is backwards — content should be the most linked-to thing on the site.

**What needs to happen:** Add prominent internal links from homepage and navigation to top series, genre categories, and featured content.

**What we need from you:** Nothing.

---

### 33. Add press/social proof to homepage
`ENVEU`

TechCrunch featured VURT. Kevin Hart and Vivica A. Fox are attached to content. App Store ratings exist. None of this is visible on the homepage. Social proof is what converts a visitor into someone who presses play.

**What needs to happen:** Add a social proof / press logos section to the homepage.

**What we need from you:** We'll provide the list of press logos, talent names, and quotes to feature.

---

### 34. Duplicate content cleanup
`ENVEU`

42% duplicate content across pages (Angular serving the same JS shell). 42% of pages have the same title ("Video Detail" repeated). 58% of titles are under 30 characters. Every page needs a unique `<title>` and unique rendered content.

**What we need from you:** Nothing.

---

### 35. Add meta keywords
`ENVEU`

Bing uses meta keywords, and Bing powers ChatGPT search. Low effort, meaningful for AI discoverability.

**What needs to happen:** Add `<meta name="keywords" content="...">` with relevant terms per page.

**What we need from you:** We'll provide keyword lists per page type.

---

## BEFORE NEXT PUSH

### 36. Clarify all three GA4 properties
`ENVEU`

Three GA4 properties exist: `vurt-bd356`, `vurt-790c4`, `vurt-9e1c5`. Only property `518738893` appears active. What are the other two? Test environments? Abandoned setups? If data is being split across properties, we're losing visibility.

**What we need from you:** Nothing — just tell us what each one is.

---

### 37. Event-based pixel architecture
`ENVEU` + `PAID ADS TEAM`

Because episodes currently share a URL (item #2), all episode-level tracking MUST use event-based pixels, not page load triggers. This is a temporary architecture until unique episode URLs exist, but it needs to work now.

**What needs to happen:** One smart base pixel + event listeners for in-player actions with dynamic parameters (series_id, episode_number, % watched, etc.).

**What we need from you:** Nothing — paid ads team will configure in GTM once player events are exposed (item #26).

---

### 38. Foundation event pixels
`ENVEU` + `PAID ADS TEAM`

These are the core tracking events the paid ads team needs:

| Event | Fires On | Captures |
|-------|----------|----------|
| Landing/Entry | Any page load | UTM params, device, session ID |
| Age Gate | User confirms 17+ | Time from landing to completion |
| Play Button | Click play | series_id, episode_number, time to first play |
| View Duration | 25/50/75/100% | Series, episode, % completed, seconds watched, binge signal |
| Registration Gate Shown | Gate appears | Episodes watched before trigger |
| Registration Complete | User signs up | Method, conversion rate |
| App Download Click | Click iOS/Android | Platform, source page |

**What we need from you:** Player events exposed (item #26) and DOM identifiers (item #27). Paid ads team handles the GTM configuration.

---

### 39. Behavior and navigation pixels
`ENVEU` + `PAID ADS TEAM`

| Event | Fires On | Captures |
|-------|----------|----------|
| Category Browse | Navigate categories | Categories browsed, time spent |
| Thumbnail Click | Click series thumbnail | Series title, position in carousel |
| My List Add | Add to watchlist | Series, user registered status |
| Share Action | Click share | Series/episode, platform shared to |
| Submit Your Series | Form submit | Interest (page view) + conversion (form submit) |
| Scroll Depth | 25/50/75/100% | Homepage scroll engagement |

**What we need from you:** Same as above.

---

### 40. Google Play Store title optimization
`ENVEU`

Change from "VURT" to **"VURT - Free Vertical Drama & Micro-Series"**. Add keywords to description: "free streaming", "micro-drama", "vertical cinema", "short-form drama", "mobile-first entertainment".

**What we need from you:** We'll provide the exact copy.

---

### 41. Google Play "What's New" text
`ENVEU`

Replace generic "Small updates, same big vision" with keyword-rich update notes that actually describe what changed.

**What we need from you:** We'll provide copy for each update.

---

### 42. Google Play Data Safety fix
`ENVEU`

Currently contradicts itself: claims "no data collected" but also says "may share data types with third parties" (personal info, device IDs) and "data isn't encrypted." This confuses users and could trigger a review.

**What needs to happen:** Review and correct the data safety declaration in Google Play Console.

**What we need from you:** Nothing.

---

### 43. Google Play developer website
`ENVEU`

Developer page links to `vurt.com` instead of `myvurt.com`.

**What we need from you:** Nothing — just update it.

---

### 44. iOS App Store keyword optimization
`ENVEU`

Title/subtitle should include target keywords. Keyword field should include all priority search terms.

**What we need from you:** We'll provide the keyword list.

---

### 45. In-app review prompts
`ENVEU`

Google Play has 10+ downloads and ZERO reviews. iOS has 4.7 stars from 11 ratings. Prompting users for reviews after positive engagement (finishing a title, 3rd session, adding to My List) is free and dramatically increases ratings.

**What needs to happen:** iOS: `SKStoreReviewController`. Android: equivalent in-app review prompt.

**What we need from you:** Nothing.

---

### 46. SRT subtitle upload workflow
`ENVEU`

We have generated SRT files for titles via our subtitle pipeline. We need to know: what is the process for uploading/attaching SRT files to content in Enveu? Is there an API? A CMS upload? We need a documented workflow.

**What we need from you:** Nothing — just document the process and tell us.

---

### 47. Subtitle display in player
`ENVEU`

All content needs clear subtitles or closed captions. Does the player support SRT/VTT rendering? If yes, point us to the upload path. If no, this needs to be built.

**What we need from you:** Nothing.

---

### 48. Web-to-app conversion tracking
`ENVEU` + `PAID ADS TEAM`

No mechanism currently exists to measure the conversion rate from myvurt.com visit to app install. This is a critical funnel step we're flying blind on.

**What we need from you:** Paid ads team to design the tracking; devs to implement the event hooks.

---

### 49. App store install attribution
`ENVEU`

- iOS: Apple SKAdNetwork for install attribution
- Android: Google Install Referrer API for campaign tracking

These let the paid ads team know which ad campaigns actually drive installs.

**What we need from you:** Nothing.

---

### 50. Email consolidation
`ENVEU`

4 email addresses across the site (`info@`, `support@`, `contact@`, `submissions@`) with no routing guide. Consolidate to 2 max with clear purposes.

**What we need from you:** We'll define which emails to keep and what routes where.

---

---

## OPEN QUESTIONS (Answers Required Before Certain Items Can Start)

These have been asked before and never answered. We need answers now:

1. **What can we customize in Enveu without a code deploy?** (meta tags, schema markup, URL structure, sitemap, image alt text, robots.txt — which of these can be edited from the CMS vs requiring engineering?)
2. **Can share links be configured to use myvurt.com instead of vurt.enveu.link?** Is this a configuration setting or a code change?
3. **Can custom JSON-LD script tags be injected per page from the CMS?**
4. **Who controls robots.txt and sitemap.xml?** Can they be edited directly or do they require a code deploy?
5. **Where in the CMS can image alt text be set per content item?**
6. **How does the deep link handler work technically?** What's the actual code path and what would it take to add episode-level routing?
7. **What is the registration gate trigger logic?** How many watches before it fires? Is it configurable?
8. **Is the Mux Data add-on enabled?** We're getting 404s on `/data/v1` endpoints.
9. **Why do three GA4 properties exist?** Which is production? What are the other two?
10. **Does your platform support Angular Universal (SSR)?** If not, what is your plan for pre-rendering? We need a written answer.

---

## API & INTEGRATION ACCESS

These are access issues we can often resolve ourselves, but some require Enveu action:

| Item | Status | Owner | What's Needed |
|------|--------|-------|---------------|
| YouTube Analytics API | Blocked — not enabled in GCP | `VURT INTERNAL` | 1-click enable in GCP console |
| YouTube Data API | Working | — | No action |
| Frame.io write access | Retesting with new perms | `VURT INTERNAL` | Retest with Dioni's new full permissions |
| Mux Data API | 404 on endpoints | `ENVEU` | Confirm if Data add-on is enabled |
| Meta Ads API | Blocked — needs ads_read scope | `PAID ADS TEAM` | Alex upgrades token scope in Meta Business Suite |
| TikTok API | Scraping (fragile) | `VURT INTERNAL` | Low priority, scraping works for now |

---

## PRODUCT ROADMAP (Not Blocking — Future Development)

These are features for VURT's next phase. They're listed here so the dev team knows the direction, not because they're needed this sprint:

1. **Culture-based content categories** — Organize by culture (Black Cinema, Horror Culture, Hip Hop Culture, Anime Culture, Gaming Culture) as primary, genre as secondary. This is VURT's differentiator.
2. **In-app community features (Phase 1)** — Episode-level comments + basic chat. Without community, it's just a content library.
3. **Creator revenue transparency dashboard** — Creators see views, revenue share, payout status (50/50 model).
4. **Open submissions portal** — Proper intake system replacing email submissions.
5. **Shareable clips from app** — Users must be able to share clips/screenshots. Quibi died partly because it blocked sharing.
6. **Auto-play on deep link landing** — When ads deep-link to a series, content auto-plays immediately.
7. **Watch parties** — Social viewing with real-time chat.
8. **Interactive features** — Polls, predictions, fan voting during episodes. No competitor has this.
9. **Audience-influenced storylines** — Community votes influence plot decisions.
10. **Bullet comments (Bilibili model)** — Comments floating across screen during playback.

---

## SUMMARY

| Bucket | Items | What It Covers |
|--------|-------|----------------|
| NOW | 1–10 | Buffering, URLs, sharing, deep links, SSR, tracking |
| THIS SPRINT | 11–35 | SEO infrastructure, GA4 events, search console, content fixes |
| BEFORE NEXT PUSH | 36–50 | Pixels, app store, subtitles, attribution |
| Open Questions | 10 | Platform capabilities we need answers on |
| API Access | 6 | Integration access items |
| Product Roadmap | 10 | Future features |
| **TOTAL** | **81** | |

---

*This document consolidates findings from: SEO Master Plan, SEO Dev Team Brief, Pixel Tracking Plan, API Capabilities Audit, Google Play Store Audit, Site Audit, NPAW analytics data, GA4/Firebase analytics data, daily analytics reports, Enveu task tracker review, and all operational conversations to date.*

*Version 2 — March 31, 2026*

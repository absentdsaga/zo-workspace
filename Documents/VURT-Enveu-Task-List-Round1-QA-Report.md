# VURT - Enveu Task List Round 1: QA Verification Report

**Date:** April 9, 2026
**Prepared by:** Dioni Vasquez / VURT Operations
**Source:** Enveu Task List Round 1 PDF (response to Dev Team Operations List v2)

---

## Summary

Of 50 items sent to the dev team, Enveu's responses break down as follows:

| Category | Count |
|----------|-------|
| Claims "already implemented" | 16 |
| "In progress / reviewing" | 6 |
| "Provide more details" (despite clear specs) | 21 |
| Answered with useful info | 2 |
| No response / missing | 5 |

**Of the 16 items they claim are done, our live site verification found:**
- Fully fixed: **5**
- Partially fixed (issues remain): **6**
- NOT actually done: **5**

---

## SECTION 1: Items They Claim Are Done - Verified Against Live Site

### ACTUALLY FIXED (5 items)

| # | Item | Verification |
|---|------|-------------|
| 15 | iOS App Store link region | Link is now `apps.apple.com/app/vurt/id6757593810` (no `/in/`). Confirmed fixed. |
| 17 | Replace QA CDN assets | Footer images now served from `resources-us1.enveu.tv/VURT_...` (production CDN). No `resources-qa.enveu.tv/PowerNews/` found. **However:** `<link rel="preconnect" href="https://frontend-api-qa.enveu.tv">` still in HTML head (QA API endpoint leaking into production). |
| 18 | Footer social links | TikTok has `@`, Twitter is `x.com/myvurt`, YouTube is `@myVURT1`. Mostly correct. Minor: TikTok icon alt text says "toktok" (typo). YouTube handle has "1" at end - confirm if intentional. |
| 19 | ToS typo | Section 7 now reads "SUBMISSION" not "SUBISSION". Fixed. |
| 9 | SSR | `ng-server-context="ssr"` confirmed. Page returns real rendered HTML content via curl. SSR is working. **CRITICAL CAVEAT:** This SSR deploy (April 6) broke GA4 engagement tracking - gtag.js event listeners don't re-register after SSR hydration, causing 99.6% bounce rate in analytics. SSR itself works, but it broke analytics. |

### PARTIALLY FIXED (6 items)

| # | Item | What's Done | What's Still Broken |
|---|------|------------|-------------------|
| 8 | Meta tags | og:title, og:description, og:image exist on homepage and series pages | `og:url` is EMPTY on homepage. `og:url` uses HTTP (not HTTPS) on series pages. `og:sitename` is empty. `twitter:card` and `twitter:site` are empty. `<meta name="title">` is empty. |
| 14 | robots.txt | Has `Disallow: /settings` and `Disallow: /user` and `Disallow: /search*` | **Missing `Sitemap:` directive.** No `Sitemap: https://www.myvurt.com/sitemap.xml` line. This defeats half the purpose of robots.txt. |
| 16 | Homepage H1 | Persistent SEO H1 added: "Watch Free Vertical Drama & Micro-Series on VURT" (visually hidden, readable by crawlers) | **Two H1 tags on the page.** The carousel titles are also wrapped in H1 tags. Having multiple H1s confuses Google. Carousel should use H2. |
| 31 | Security headers | `referrer-policy`, `x-frame-options`, `x-content-type-options`, `strict-transport-security` all present | `content-security-policy` is set to `*` (wildcard) which allows everything and provides zero actual protection. Effectively useless. |
| 13 | Broken internal URLs | Unknown if the doubled URLs were fixed in navigation | `myvurt.com/www.myvurt.com/privacy-policy` still returns HTTP 200 (renders homepage instead of 404). `/settings/terms-and-conditions` returns 200 but shows homepage content. No proper 404 handling. |
| 35 | Meta keywords | `<meta name="keywords">` tag exists in HTML | The `content` attribute is **empty**. No keywords populated. Tag is there but has no value. |

### NOT ACTUALLY DONE (5 items)

| # | Item | Enveu Claim | Reality |
|---|------|------------|---------|
| 11 | JSON-LD structured data | "Already implemented, check website" | **ZERO `application/ld+json` blocks found** on homepage or any series page. Not implemented at all. |
| 7 | Sitemap.xml | "I will provide a demo" (not claiming done, but said CMS can handle it) | `/sitemap.xml` returns the homepage HTML, not XML. Zero URLs in sitemap. Completely non-functional. |
| 12 | Canonical tags | No response in PDF | Could not verify separately but likely not done given state of other items. |
| 34 | Duplicate content | "Provide more details" | Not done. Pages still serve same Angular shell. |
| 25 | Image alt text | "Provide more details" | Not done. |

---

## SECTION 2: Items Still In Progress (No Action Needed From Us)

| # | Item | Enveu Response | Our Assessment |
|---|------|---------------|---------------|
| 1 | Buffering / Fastly CDN | "Reviewing, will share update soon" | Still unresolved. Buffer rates remain high (42% as of Apr 8). They also admitted staging traffic pollutes production NPAW data. We asked for filtering identifiers and never got them. |
| 2 | Episode URLs | "In progress, will provide update" | Was "in progress" since before our list. Has been sitting at Row 46 P1 on their tracker for weeks. |
| 3 | Share links (myvurt.com not enveu.link) | "In progress, will keep you posted" | Same - been waiting. Every day this stays broken = lost SEO equity. |
| 4 | Deep links to episodes | "In progress, will provide update" | Blocked by #2 (episode URLs). |
| 6 | Mobile footer | "In progress, will provide update" | You confirmed this is still broken (sent screenshot of collapsed footer on mobile). |
| 22 | UTM persistence | "Will review and update shortly" | Not started. |

---

## SECTION 3: Items Where They're Asking US for Details

This is the biggest category (21 items). Some of these requests are legitimate (they need copy/assets from us). Others are concerning because the original doc already had clear specs.

### Legitimate - They Need Content From Us

| # | Item | What They Need | What We Should Provide |
|---|------|---------------|----------------------|
| 40 | Google Play title optimization | Exact keywords for Play Store | Title: "VURT - Free Vertical Drama & Micro-Series". Keywords: "free streaming", "micro-drama", "vertical cinema", "short-form drama", "mobile-first entertainment" |
| 41 | Google Play "What's New" | Copy for update notes | We write the release notes copy |
| 44 | iOS App Store keywords | Keyword list | We provide keyword list |
| 33 | Social proof on homepage | Press logos, talent names, quotes | We provide: TechCrunch logo, Kevin Hart, Vivica A. Fox names + quotes |
| 50 | Email consolidation | Which emails to keep | We define: keep `info@` (general) and `submissions@` (creators). Retire `support@` and `contact@` (redirect to info@). |

### Concerning - Specs Were Already Clear

These items had detailed specs in the original doc. "Provide more details" means they either didn't read the doc carefully or are stalling.

| # | Item | Why This Is Concerning |
|---|------|----------------------|
| 10 | Episode-level tracking | We said: "Every GA4 event must include `episode_number` as a parameter alongside `series_title`." That IS the detail. |
| 20 | GA4 custom events | We provided a full table of 6 events with exact parameter names. What more details do they need? |
| 21 | New vs returning users | Standard GA4 configuration. No "details" needed - this is a checkbox in GA4 admin. |
| 25 | Image alt text | We said: "Add descriptive alt text to every image. Add width/height attributes." What's unclear? |
| 26 | Player API events | We asked: "Does your player expose these events? If so, document them. If not, expose them." The question is TO them, not from them. |
| 27 | DOM identifiers | We said: "Add `data-track` attributes to play button, registration form, age gate, etc." Clear spec. |
| 29 | Root cause for user drop | We asked THEM to investigate their own infrastructure. This is a question TO them, not from them. |
| 30 | Empty placeholder pages | We said: "Populate with content or add noindex." Clear instruction. |
| 32 | Internal linking | We said: "Add prominent internal links from homepage to top series." Clear instruction. |
| 36 | Clarify GA4 properties | We asked THEM: "What are the other two GA4 properties?" This is a question they should answer, not ask us for details on. |
| 42 | Google Play Data Safety | We said: "Review and correct the data safety declaration." They have Google Play Console access. This is their action. |
| 43 | Google Play developer website | We said: "Change vurt.com to myvurt.com." One field change. |
| 45 | In-app review prompts | We said: "iOS: SKStoreReviewController. Android: equivalent." Standard implementation, no details needed. |
| 48 | Web-to-app conversion | We said: "Devs implement event hooks." They need to tell us what hooks exist. |
| 49 | App store install attribution | Standard SDK implementations (SKAdNetwork, Install Referrer API). Well-documented. |

---

## SECTION 4: Useful Answers They Provided

| # | Item | Their Answer | Value |
|---|------|-------------|-------|
| 46 | SRT upload workflow | "CMS -> Content Manager -> Open any Micro Episode -> Subtitle option -> add SRT file" | This is actionable. We can now upload SRTs ourselves through the CMS. |
| 47 | Subtitle display in player | "Already available in the CMS. Upload SRT/VTT via CMS -> Content Manager -> Micro Episode -> Subtitle option" | Player supports subtitles. Same upload path as #46. We can start uploading our generated SRTs immediately. |

---

## SECTION 5: Bonus Issues Found During Verification

| Issue | Details |
|-------|---------|
| QA API in production | `<link rel="preconnect" href="https://frontend-api-qa.enveu.tv">` in HTML head. QA/staging API endpoint leaking into production code. |
| Beta API in production | `href="https://experience-manager-fe-api.beta.enveu.com"` - non-production endpoint in source. |
| India AWS region | `ap-south-1.amazonaws.com` endpoint in page source. May cause latency for US users. |
| Build info exposed | `VERSION_NUMBER = 'v-26.04.08.3'` and `BRANCH:feature/player-enhancements-rishabh` visible in page source. Internal build info and developer names public. |
| No 404 page | ALL invalid URLs return HTTP 200 and render the homepage. No proper 404 handling exists. |
| SSR broke GA4 engagement | Their SSR deploy (Apr 6) caused gtag.js event listeners to not re-register after hydration. Result: `user_engagement` events stopped firing, bounce rate went from ~70% to 99.6%. This is verified with console testing. They need to fix their gtag initialization to work with SSR hydration. |

---

## SECTION 6: What YOU Need To Do (VURT Internal Actions)

Based on their responses, here's what's actually on your plate:

1. **Provide Google Play Store copy** (items 40, 41) - title, keywords, What's New text
2. **Provide iOS keyword list** (item 44)
3. **Provide social proof assets** (item 33) - press logos, talent names, quotes
4. **Define email routing** (item 50) - which addresses to keep
5. **Provide OG share card image** (item 8) - 1200x630 jpg for homepage
6. **Confirm YouTube handle** - is `@myVURT1` correct or should it be something else?
7. **Register Google Search Console** (item 23) - you can do this yourself at search.google.com/search-console with dioni@myvurt.com. May need DNS verification from Enveu.
8. **Register Bing Webmaster Tools** (item 24) - same, bing.com/webmasters
9. **Start uploading SRTs** (items 46-47) - path confirmed: CMS -> Content Manager -> Episode -> Subtitle option
10. **Push back on items 10, 20, 21, 26, 27, 29, 36** - these had clear specs or were questions TO them. They should not be asking us for details.

---

## SECTION 7: Recommended Response to Dev Team

**Items to push back on (they claim done but aren't):**
- #11 JSON-LD: "You said this is implemented. We checked - zero `ld+json` blocks on any page. Please implement."
- #35 Meta keywords: "Tag exists but content is empty. Please populate with actual keywords."
- #8 Meta tags: "Partially done. og:url is empty on homepage, uses HTTP on series pages, og:sitename empty, twitter cards empty. Please complete."
- #13 Internal URLs: "Doubled URLs still return 200. Need proper 404 handling."
- #14 robots.txt: "Missing Sitemap directive. Add `Sitemap: https://www.myvurt.com/sitemap.xml`"
- #16 H1: "Good that SEO H1 is added, but carousel titles are also H1. Change carousel to H2."
- #31 CSP: "Content-Security-Policy is set to `*` which does nothing. Implement a real policy."

**Items to push back on (asking for details that were already provided):**
- #10, #20, #21, #25, #26, #27, #29, #30, #32, #36, #42, #43, #45: "All specs were in the original document. Please re-read items 10, 20, 21, etc. The details you're asking for are already there."

**Critical unresolved item:**
- #9 SSR broke GA4: "Your SSR implementation broke GA4 engagement tracking. gtag.js event listeners don't re-register after Angular hydration. This caused bounce rate to spike from ~70% to 99.6% on April 6. This needs an immediate fix - the engagement timer is dead."

---

*This report was generated by cross-referencing Enveu's PDF responses against live site verification on myvurt.com as of April 9, 2026.*

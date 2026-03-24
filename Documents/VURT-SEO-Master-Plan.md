# VURT SEO MASTER PLAN
### Comprehensive Technical Audit + Strategic Roadmap
### Date: March 18, 2026 (Updated: March 19, 2026)
### Prepared by: Dioni Vasquez + SEO Analyst (External Audit)
### Crawl Date: March 17, 2026

---

## EXECUTIVE SUMMARY

VURT (www.myvurt.com) is a free vertical drama and micro-series streaming platform built on the enveu CMS. The site was professionally crawled on March 17, 2026, and cross-referenced with the internal dev team brief.

**The Bottom Line:** VURT is currently invisible to both traditional search engines and AI search platforms. Zero SEO work has been done to date. With 100+ titles, TechCrunch press coverage, and talent like Kevin Hart and Vivica A. Fox, VURT has exceptional raw material being completely wasted due to fundamental technical failures.

When someone searches "free vertical drama app" or "micro drama like ReelShort but free," VURT does not appear anywhere — not on Google, not in ChatGPT, not in Perplexity, not in Google AI Overviews.

---

## OVERALL HEALTH SCORE

| Category | Score | Summary |
|---|---|---|
| Crawlability & Indexation | **FAIL** | Empty sitemap, no canonical tags, Angular SPA blocks crawlers |
| On-Page SEO | **FAIL** | 58% missing meta descriptions, 42% duplicate titles, 42% missing H1s |
| Technical Infrastructure | **FAIL** | No SSR/pre-rendering; AI crawlers see blank page |
| Content Quality | **FAIL** | 83% low-content pages, 42% exact duplicates detected |
| Structured Data | **FAIL** | Zero schema markup on any page — no rich results possible |
| Security Headers | **WARN** | HTTPS present but missing CSP, X-Content-Type, X-Frame-Options |
| Internal Linking | **WARN** | 33% of pages have zero internal outlinks; broken URL patterns found |
| Image SEO | **FAIL** | 100% missing alt attributes; hashed CDN filenames with zero SEO value |
| Mobile Readiness | **PASS** | Viewport set, font sizes legible, no unsupported plugins |
| Off-Site / Backlinks | **WARN** | TechCrunch coverage exists but no strategic link-building in place |

---

## PART 1: CRAWL DATA & TECHNICAL FINDINGS

### 1.1 Crawl Summary

| Metric | Value | Status |
|---|---|---|
| Total URLs Encountered | 20 | Very Low |
| Internal URLs | 16 (80%) | Extremely Low |
| External URLs | 4 (20%) | — |
| HTML Pages | 12 | Thin Site |
| JavaScript Files | 3 (18.75%) | Angular SPA Confirmed |
| CSS Files | 1 | — |
| Images Crawled | 0 internal / 1 external | Critical Image Gap |
| Success Responses (2xx) | 19 (95%) | Good |
| Redirections (3xx) | 1 (5%) | Acceptable |
| Client/Server Errors | 0 | Good |
| Average Response Time | < 1 second | Fast |

**Key findings:**
- Only 20 URLs discovered for a platform with 100+ titles — the crawler couldn't find series/episode pages through navigation
- **UPDATE (Mar 19):** Manual testing confirms series DO have unique URLs (e.g., `myvurt.com/detail/micro_series/the-love-letter`) — but episodes do NOT. The URL does not change when switching episodes. The crawler missed series URLs because the Angular SPA doesn't expose them through standard links.
- Zero internal images crawled — all loaded via JavaScript or served from external CDN with hashed filenames
- 12 HTML pages = the entire indexable footprint of VURT

### 1.2 URL Structure

URLs that exist are clean: no uppercase, no parameters, no spaces. URL hygiene is sound for existing pages.

**UPDATED URL Findings (Mar 19 — Manual Testing):**

Series pages DO have unique URLs. Example: `https://www.myvurt.com/detail/micro_series/the-love-letter`. The initial crawl missed these because the Angular SPA doesn't expose them through standard HTML links — the crawler couldn't discover them through navigation.

**However, three critical URL problems remain:**

**Problem 1: Episodes have NO unique URLs.** When a user clicks from one episode to another within a series, the URL in the address bar does NOT change — it stays at the show-level URL (e.g., `myvurt.com/detail/micro_series/the-love-letter`). This means:
- Individual episodes cannot be indexed by any search engine
- Episode-level sharing is impossible via web URL
- Deep links from app → web cannot route to a specific episode

**Problem 2: Share links go to enveu's domain, not VURT's.** When a user clicks "Share" on an episode, the generated link is `https://vurt.enveu.link/dmqdikktzy` — a short link on enveu's domain with a random hash. This means:
- Every share builds SEO authority for `enveu.link`, NOT `myvurt.com`
- The "vurt" subdomain provides zero SEO benefit — authority accrues to the root domain (`enveu.link`)
- The random hash (`dmqdikktzy`) carries no keyword signal — search engines can't tell what content lives at that URL
- All social sharing, backlinks, and word-of-mouth link equity is being given away to a third-party domain

**Problem 3: Deep links are broken at the episode level.** The enveu short link triggers a browser → app handoff, but the app only resolves to the show page, not the specific episode. The short link likely carries the episode ID, but the app's deep link handler doesn't parse it.

**What share links SHOULD look like:** `https://www.myvurt.com/detail/micro_series/the-love-letter/episode-2` — keyword-rich, on VURT's domain, directly linkable and indexable.

**Broken Internal URLs Detected (Bug)**

The crawl found malformed URLs where the domain is doubled:
- `https://www.myvurt.com/www.myvurt.com` — domain prepended as path
- `https://www.myvurt.com/www.myvurt.com/terms-and-conditions`
- `https://www.myvurt.com/www.myvurt.com/privacy-policy`
- `https://www.myvurt.com/settings/terms-and-conditions` — internal settings path exposed

**Cause:** Absolute URL placed in an href expecting a relative path. Immediate code fix required.

### 1.3 Crawl Depth

| Depth (Clicks from Home) | Pages | % of Total |
|---|---|---|
| 0 (Homepage) | 1 | 8.33% |
| 1 click | 7 | 58.33% |
| 2 clicks | 4 | 33.33% |

All pages within 2 clicks — good. When unique series/episode URLs are created, keep content within 3 clicks through proper navigation.

---

## PART 2: ON-PAGE SEO ANALYSIS

### 2.1 Page Titles

| Issue | Count | % of Pages | Severity |
|---|---|---|---|
| Missing Titles | 0 | 0% | PASS |
| Duplicate Titles | 5 | 41.67% | CRITICAL |
| Over 60 Characters | 5 | 41.67% | MEDIUM |
| Below 30 Characters | 7 | 58.33% | HIGH |
| Over 561 Pixels | 5 | 41.67% | MEDIUM |
| Below 200 Pixels | 6 | 50.00% | HIGH |
| Same as H1 | 0 | 0% | PASS |

5 duplicate titles on a 12-page site = the Angular app is serving generic titles like "Video Detail" across multiple pages. 58% of titles are too short for meaningful keywords.

**Recommended Title Templates:**
- **Homepage:** VURT — Free Vertical Drama & Micro-Series | Built for the Culture
- **Series Pages:** {Series Name} | VURT — Watch Free
- **Episode Pages:** {Series Name} Ep. {#}: {Episode Title} | VURT
- **About:** About VURT | Free Streaming for Black Creators & Culture
- **FAQ:** FAQ | VURT — Free Vertical Drama & Micro-Series
- **Contact:** Contact Us | VURT Streaming Support

### 2.2 Meta Descriptions

| Issue | Count | % of Pages | Severity |
|---|---|---|---|
| Missing Meta Descriptions | 7 | 58.33% | CRITICAL |
| Duplicate Meta Descriptions | 5 | 41.67% | CRITICAL |

58% missing, and the remaining 42% are all duplicates. Effectively **0% of pages have a proper, unique meta description.**

**Recommended Templates:**
- **Homepage:** "Watch 100+ vertical micro-series, dramas, and originals free on VURT. No paywall. Black creators, bold stories, designed for your phone."
- **Series Pages:** "{Series synopsis, first 155 characters}" — dynamically pulled from CMS
- **Static Pages:** Unique, keyword-rich description per page

### 2.3 Heading Tags

| Issue | Count | % of Pages | Severity |
|---|---|---|---|
| Missing H1 | 5 | 41.67% | CRITICAL |
| Missing H2 | 5 | 41.67% | HIGH |
| Multiple H2s (OK) | 3 | 25.00% | PASS |

Homepage H1 is dynamically set to the featured series name and changes with the carousel. Should be persistent: **"VURT — Free Vertical Micro-Series & Drama Streaming"**

### 2.4 Meta Keywords

All 12 pages missing meta keywords. Google doesn't use them, but **Bing does — and Bing powers ChatGPT search.** Low-effort optimization worth adding.

### 2.5 Content Quality

| Issue | Count | % of Pages | Severity |
|---|---|---|---|
| Exact Duplicate Content | 5 | 41.67% | CRITICAL |
| Low Content Pages | 10 | 83.33% | CRITICAL |

83% flagged as "low content" because the crawler sees the Angular JS shell, not the rendered content. Two specific empty pages identified:
- **"What's New"** — placeholder with no actual content
- **"Help/Support"** — lists categories but has no articles

**Recommendation:** Populate with real content or add noindex tags. Empty pages damage site-wide quality signals.

---

## PART 3: TECHNICAL SEO

### 3.1 Canonical Tags

| Issue | Count | Severity |
|---|---|---|
| Missing Canonical Tags | 12 (100%) | CRITICAL |
| Self-Referencing Canonicals | 0 | CRITICAL |

Zero pages have a canonical tag. Every page must have:
```html
<link rel="canonical" href="https://www.myvurt.com/{page-slug}" />
```

### 3.2 Sitemap

`myvurt.com/sitemap.xml` returns HTTP 200 but contains **zero URLs**. Google has no roadmap to discover pages.

**Required sitemap contents:**
- Homepage URL
- All static pages (About, FAQ, Contact, Help, Privacy, Terms, What's New)
- Every series page: `/series/{slug}`
- Every episode page: `/series/{slug}/episode-{n}`
- Every category/genre page

Must be auto-generated by the CMS and updated on publish. Add `Sitemap: https://www.myvurt.com/sitemap.xml` to robots.txt.

### 3.3 Structured Data (Schema.org)

Zero structured data on any page. No JSON-LD, no Microdata, no RDFa.

**Required Schema Implementations:**

**Homepage — Organization:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "VURT",
  "url": "https://www.myvurt.com",
  "logo": "https://www.myvurt.com/images/vurt-logo.png",
  "description": "Vertical-first streaming platform for micro-series, dramas, and originals. Free, ad-supported, built for the culture.",
  "sameAs": [
    "https://www.instagram.com/myvurt",
    "https://www.tiktok.com/@myvurt",
    "https://www.youtube.com/@myVurt1",
    "https://www.facebook.com/myvurt"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "contact@myvurt.com",
    "contactType": "customer service"
  }
}
```

**FAQ Page — FAQPage:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is VURT?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "VURT is the ultimate streaming destination for premium vertical cinema. We provide a mobile first viewing experience across all platforms, delivering quality content for FREE."
      }
    },
    {
      "@type": "Question",
      "name": "Is VURT free?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, VURT is a free and legal video streaming service. To keep our service free, we include advertising."
      }
    },
    {
      "@type": "Question",
      "name": "Where can I watch VURT?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "You can watch VURT anytime, anywhere for free at www.myvurt.com or on the VURT app on iOS, Android, smart TVs, tablets, and streaming devices."
      }
    },
    {
      "@type": "Question",
      "name": "Can I submit my film or show to VURT?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, VURT supports independent creators. Email submissions@myvurt.com for more information."
      }
    }
  ]
}
```

**Series Pages — TVSeries:**
```json
{
  "@context": "https://schema.org",
  "@type": "TVSeries",
  "name": "{Series Name}",
  "description": "{Synopsis}",
  "genre": ["{Genre1}", "{Genre2}"],
  "numberOfSeasons": 1,
  "numberOfEpisodes": "{count}",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
```

**Episode Pages — TVEpisode:**
Each episode should have TVEpisode schema nested within TVSeries for relationship clarity: episode name, description, part of series, episode number, duration.

### 3.4 Server-Side Rendering / Pre-Rendering

**The Core Problem:** VURT is an Angular SPA. Crawlers receive a JavaScript shell, not rendered HTML. Googlebot can execute JS (slowly), but AI crawlers (ChatGPT, Perplexity) **cannot** — they see a blank page.

**Options (ranked by preference):**
1. **Angular Universal SSR** — Best option. Server renders full HTML per request. Gold standard.
2. **Prerender.io or similar** — Good fallback. Middleware detects bot user agents and serves pre-rendered static HTML. No Angular code changes needed.
3. **Static Site Generation** for fixed pages (About, FAQ, Contact, Help, Privacy, Terms)

**This is the single most important technical fix for AI search visibility.** Without SSR or pre-rendering, VURT will never appear in ChatGPT, Perplexity, or Google AI Overviews — regardless of how good the on-page SEO is.

### 3.5 Meta Tags (Current State)

**Homepage (all null/empty):**
```
og:title = null
og:description = null
og:type = null
twitter:title = null
twitter:description = empty
twitter:image = null
```

**What We Need — Homepage:**
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

**What We Need — Each Series Page (dynamic):**
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

### 3.6 Security Headers

| Issue | Affected | Severity |
|---|---|---|
| Missing Content-Security-Policy | 16 (100%) | MEDIUM |
| Missing X-Content-Type-Options | 16 (100%) | MEDIUM |
| Missing X-Frame-Options | 16 (100%) | MEDIUM |
| Missing Secure Referrer-Policy | 16 (100%) | MEDIUM |
| Unsafe Cross-Origin Links | 2 (12.5%) | LOW |
| HTTPS Enabled | 16 (100%) | PASS |
| HSTS Header Present | 16 (100%) | PASS |

Not direct ranking factors, but Google increasingly signals that security contributes to trust. Straightforward server-config fixes at CDN/hosting level.

### 3.7 Robots.txt

No noindex or nofollow directives — fine for now. Updates needed:
- Add: `Sitemap: https://www.myvurt.com/sitemap.xml`
- Ensure crawlers aren't blocked from content pages
- Block `/settings/` paths (crawl found internal settings exposed)

---

## PART 4: INTERNAL LINKING & ARCHITECTURE

### 4.1 Dead-End Pages

| Issue | Count | Severity |
|---|---|---|
| Pages Without Internal Outlinks | 4 (33.33%) | HIGH |

1/3 of pages have zero outlinks — trapping users and crawlers. Every page should link to at least 2-3 relevant internal pages.

### 4.2 Inverted Link Priority

| URL | Inlinks | Notes |
|---|---|---|
| /privacy-policy | 6 (highest) | Footer link on every page |
| /help-support | 5 | Footer link |
| /what-new | 5 | Footer link |
| /faq | 5 | Footer link |
| /terms-and-conditions | 5 | Footer link |
| /about-us | 5 | Footer link |
| /contact-us | 5 | Footer link |
| / (homepage) | 1 | Critically low |

**The problem:** Legal/support pages get the most links. Content pages get almost none. This is inverted — content (series, episodes) should receive the most internal links.

Once unique series URLs exist, navigation and homepage should prominently link to top series, genre categories, and featured content.

---

## PART 5: IMAGE SEO

Only 1 image was discovered by the crawler (external CDN). Missing both alt attribute and explicit dimensions. All other images loaded via JavaScript — invisible to crawlers.

**Standards:**

| Element | Standard |
|---|---|
| **Filename** | `vurt-[series-name]-[descriptor]-[optional-episode].jpg` (e.g., `vurt-karma-in-heels-poster-s1.jpg`) |
| **Alt Text** | Unique per image, describes what you see, includes keywords naturally |
| **EXIF Title** | Series/asset name |
| **EXIF Description** | What the image shows + context |
| **EXIF Copyright** | © 2026 VURT Corporation |
| **EXIF Keywords** | Series name, talent, genre, "VURT", "vertical cinema", "micro-drama" |
| **EXIF Author** | VURT |
| **EXIF Source** | myvurt.com |
| **Dimensions** | Every `<img>` must include explicit `width` and `height` attributes (CLS / Core Web Vitals) |

**Good alt text:** "Tatyana Ali and Charles S. Dutton in Come Back Dad, a VURT micro-series about family reconciliation."

**Bad alt text:** "come-back-dad image" or keyword-stuffed spam

---

## PART 6: AI SEARCH OPTIMIZATION (GEO)

Generative Engine Optimization — optimizing for ChatGPT, Perplexity, Google AI Overviews. ~70% of AI search queries flow through ChatGPT.

### 6.1 Current AI Visibility: Zero

VURT does not appear in any AI search results. Compounding reasons:
1. Angular SPA serves blank JS shell to AI crawlers
2. No structured data for AI systems to parse
3. No canonical URLs for AI to reference or cite
4. No entity presence on platforms AI systems trust (Wikipedia, Crunchbase, Product Hunt)
5. Content freshness — AI citation drops sharply after 3 months without updates

### 6.2 GEO Strategy

**Entity Building — get VURT mentioned on pages AI already cites:**
- Crunchbase company profile
- Product Hunt launch
- AlternativeTo listing (as alternative to ReelShort/DramaBox/Tubi)
- Wikipedia article (TechCrunch coverage establishes notability)
- Reddit threads in r/streaming, r/BlackFilm, r/filmmakers, r/shortfilm, r/cordcutters
- Medium publication (backlink engine + AI-citable source)

**Unlinked brand mentions** carry weight with AI systems even without links.

**Answer-first content structure:**
- Bullet points and clear headers
- Direct answers before context/explanation
- Factual, encyclopedic tone AI can quote

**Monthly AI search testing:**
- Test 10-20 VURT-relevant queries across ChatGPT, Perplexity, Google AI Overviews
- Track "share of voice" — brand appearance frequency across AI responses
- Content freshness: refresh key content quarterly

**Bing Webmaster Tools registration:**
ChatGPT uses Bing's index. Submitting sitemap to Bing is essential for AI search visibility.

**Technical dependency:** AI crawlers cannot execute JavaScript — SSR/pre-rendering is the blocker here.

---

## PART 7: OFF-SITE SEO & BACKLINK STRATEGY

### 7.1 Current State
TechCrunch coverage is an exceptional starting point. No systematic backlink strategy in place. Referring domain count is minimal and domain authority is likely very low.

### 7.2 Backlink Strategy (4 Tiers)

**Tier 1: Editorial/Press**
- Leverage TechCrunch to pitch: Variety, Deadline, Shadow and Act, The Root, Black Enterprise, Essence
- Creator spotlight articles timed with each new series launch
- Milestone press releases (download counts, partnerships, talent announcements)

**Tier 2: Directory & Listing Sites**
- Crunchbase, AngelList, Product Hunt launch
- AlternativeTo (as free alternative to ReelShort/DramaBox/Tubi)
- Wikipedia article (TechCrunch establishes notability threshold)

**Tier 3: Content Backlinks**
- **Medium publication:** 2-3 articles/week for first 90 days
  - Article types: industry analysis, competitor comparisons, creator spotlights, cultural essays, how-tos
  - Example titles:
    - "The $14B Micro-Drama Market Has a Diversity Problem"
    - "ReelShort Charges $30/Month. VURT Is Free. Here's Why."
    - "How [Creator Name] Made a Micro-Series in 72 Hours on VURT"
  - Every article links to myvurt.com at least twice (contextual, not forced)
  - Contextual backlinks outperform profile bio links 5-10x (Google Jan 2026 "Authenticity Update" values first-hand experience)
- **LinkedIn articles:** market reports, creator economy analysis (B2B visibility)
- Guest posts on creator/filmmaker blogs

**Tier 4: Community**
- **Reddit:** r/streaming, r/BlackFilm, r/filmmakers, r/shortfilm, r/cordcutters (genuine engagement first, max 1 self-promo per sub per month)
- **X / Twitter threads:** "The VURT thesis," competitor comparisons, creator spotlights, behind-the-series
  - X is now a ranking signal — Grok pulls from X data, Google counts social mentions for E-E-A-T
- Quora answers about micro-drama and vertical streaming
- Discord communities, film festival partnerships

---

## PART 8: KEYWORD STRATEGY

### 8.1 Four-Tier Framework

**Tier 1 — Brand (Must Own)**
VURT, VURT app, VURT streaming, myvurt, myvurt.com
Should rank #1 with zero competition. Currently may not rank at all.

**Tier 2 — Category (Compete)**
Micro drama app, short drama series, vertical video streaming, free drama streaming app
Moderate competition but VURT's "free" positioning is a strong differentiator.

**Tier 3 — Long-Tail (Win These — Low Competition, High Intent)**
- "free Black drama series app"
- "micro drama app like ReelShort but free"
- "vertical drama series for phone"
- "Black indie filmmaker streaming platform"
- "micro drama app no paywall"
- "free alternative to ReelShort" / "free alternative to DramaBox"
- "vertical cinema platform"

**Tier 4 — Cultural/Contextual (Authority Building)**
Black micro-drama, vertical filmmaking, micro-drama industry 2026, AVOD vs pay-per-episode, creator-owned streaming
Content marketing keywords for Medium articles and blog posts.

### 8.2 Open Territory — Nobody Ranks for These

These represent an immediate opportunity:
- "free vertical drama streaming"
- "Black micro drama app"
- "indie filmmaker streaming submit"
- "culture-driven streaming app"
- "AVOD micro drama"

With proper technical SEO, VURT can own these within 60-90 days by being the first credible result.

---

## PART 9: APP STORE OPTIMIZATION (ASO)

Unified with web SEO for maximum keyword convergence.

### Google Play
- **Title:** Change from "VURT" to "VURT - Free Vertical Drama & Micro-Series"
- **Description:** Add keywords: "free streaming", "micro-drama", "vertical cinema", "Black culture", "short drama series"
- **What's New:** Keyword-rich update notes, not "Small updates, same big vision"

### iOS App Store
Same keyword optimization. Title/subtitle should mirror Google Play keywords. Keyword field should include all Tier 1-3 terms.

---

## PART 10: PRIORITIZED ACTION PLAN

### PRIORITY 1: CRITICAL — Do This Week
*Blocking ALL organic discovery. Nothing else works until these are fixed.*

| # | Action Item | Owner | Impact |
|---|---|---|---|
| 1A | **Create unique URLs for every episode** — series URLs exist (e.g., `/detail/micro_series/the-love-letter`) but episodes have none. Need `/detail/micro_series/{show-slug}/episode-{n}` or similar. URL must update in address bar when user switches episodes. | Dev Team | Unlocks all SEO |
| 1A2 | **Redirect share links to myvurt.com** — share button currently generates `vurt.enveu.link` short links, giving all SEO equity to enveu's domain. Share must generate `myvurt.com` URLs. | Dev Team | Stops SEO value leak |
| 1A3 | **Fix deep links to episode level** — app currently opens to show page, not specific episode, when opening shared link. App link handler must parse episode-level routing. | Dev Team | Fixes sharing UX |
| 1B | Populate sitemap.xml with all page URLs | Dev Team | Enables discovery |
| 1C | Add meta tags (title, desc, OG, Twitter, canonical) to every page | Dev + SEO | On-page foundation |
| 1D | Fix broken internal URLs (www.myvurt.com doubled paths) | Dev Team | Stops crawl errors |
| 1E | Add Sitemap reference to robots.txt | Dev Team | Crawler guidance |

### PRIORITY 2: HIGH — Do Within 2 Weeks

| # | Action Item | Owner | Impact |
|---|---|---|---|
| 2A | Implement Schema.org structured data (JSON-LD) on all pages | Dev Team | Rich results + AI |
| 2B | Implement SSR or pre-rendering (Angular Universal / Prerender.io) | Dev Team | AI search visibility |
| 2C | Fix image SEO: alt text, filenames, EXIF metadata | Dev + Content | Image search traffic |

### PRIORITY 3: MEDIUM — Do Within 30 Days

| # | Action Item | Owner | Impact |
|---|---|---|---|
| 3A | Fix homepage H1 to persistent keyword-rich heading | Dev Team | Homepage SEO |
| 3B | Fill empty pages (What's New, Help/Support) with real content | Content Team | Quality signals |
| 3C | Add press/social proof to homepage (TechCrunch, talent) | Dev + Content | Trust & conversion |
| 3D | Register with Google Search Console & Bing Webmaster Tools | SEO Lead | Monitoring & AI index |
| 3E | Optimize App Store listings (Google Play title, description) | Marketing | ASO traffic |
| 3F | Add security headers (CSP, X-Content-Type, X-Frame-Options) | Dev Team | Trust signals |
| 3G | Add meta keywords to all pages (Bing/ChatGPT optimization) | Dev Team | AI search (Bing-powered) |

### PRIORITY 4: ONGOING — Content & Authority Building

| # | Action Item | Owner | Impact |
|---|---|---|---|
| 4A | Launch Medium publication (2-3 articles/week) | Content/SEO | Backlinks + authority |
| 4B | Begin Reddit/community engagement strategy | Marketing | Community links + AI citation |
| 4C | Pitch press (Variety, Deadline, Shadow and Act, etc.) | PR/Marketing | High-DA backlinks |
| 4D | Create directory listings (Crunchbase, Product Hunt, AlternativeTo) | Marketing | Entity building |
| 4E | Launch X/Twitter thread strategy with keyword hooks | Social/Content | Social signals + Grok |
| 4F | Monthly AI search testing across ChatGPT/Perplexity/Google AI | SEO Lead | GEO measurement |

---

## PART 11: QUESTIONS FOR DEV TEAM

These must be answered before implementation:

1. **What can we customize in enveu?** Meta tags, schema markup, URL structure, sitemap, image alt text, filenames?
2. **Does enveu support Angular Universal (SSR)?** If not, can we add Prerender.io as middleware?
3. **Why don't episodes have unique URLs?** Series have them (`/detail/micro_series/{slug}`) but the URL doesn't change when switching episodes. Is this an enveu limitation or a configuration issue?
4. **Can share links point to myvurt.com instead of vurt.enveu.link?** Currently every share generates a link on enveu's domain — all SEO equity goes to them, not us. Is this configurable in enveu, or do we need a custom solution?
5. **Can we inject custom scripts (JSON-LD) per page?** Or do we need Google Tag Manager?
6. **Who controls robots.txt and sitemap.xml?** Can we edit them directly?
7. **What's the timeline?** How quickly can Priority 1 items be implemented?
8. **Can we get Google Search Console / Bing Webmaster Tools access?** Need to verify domain ownership.
9. **How does the deep link handler work?** Shared links open the app to the show page but not the specific episode — is the episode ID passed in the link? What would it take to fix episode-level routing in the app?

---

## PART 12: MEASUREMENT & KPIs

| Metric | Frequency | Tool |
|---|---|---|
| Referring domains (new backlinks) | Weekly | Ahrefs / SEMrush |
| Keyword rankings (Tier 2-3) | Weekly | Ahrefs / SEMrush |
| AI search results appearance | Monthly | Manual testing |
| Organic traffic (sessions) | Weekly | Google Analytics |
| Pages indexed in Google | Weekly | Google Search Console |
| Pages indexed in Bing | Monthly | Bing Webmaster Tools |
| Medium views + referral traffic | Weekly | Medium Analytics + GA |
| X thread impressions + link clicks | Weekly | X Analytics |
| Dead link audit | Monthly | Screaming Frog / Ahrefs |
| Core Web Vitals scores | Monthly | PageSpeed Insights |
| App store rankings | Weekly | App Annie / Sensor Tower |

---

## PART 13: CONTENT CALENDAR — First 30 Days

| Week | Medium | X Threads | Other |
|---|---|---|---|
| 1 | Launch article + industry piece | "The VURT thesis" thread | Reddit intros (r/streaming, r/BlackFilm) |
| 2 | Competitor comparison + creator spotlight | Creator spotlight thread | LinkedIn, Product Hunt, Crunchbase |
| 3 | Submission how-to + market analysis | Comparison thread | Reddit organic engagement |
| 4 | Cultural essay + future of vertical | Behind-the-series thread | LinkedIn market report, AlternativeTo |

---

## WHAT DIONI OWNS (Content & Strategy)

*Dev team doesn't need to focus on these. Sharing for alignment and expert review.*

1. **Off-site SEO & backlink strategy** — Medium, X, LinkedIn, Reddit, press, community
2. **Keyword strategy** — 4-tier framework, open territory identification
3. **App store copy** — I write, dev team publishes
4. **AI search optimization (GEO)** — Entity building, answer-first content, monthly testing
5. **Image EXIF & asset SEO** — Filename conventions, metadata embedding before upload
6. **Press & authority building** — TechCrunch leverage, editorial pitching
7. **Content calendar execution** — Medium articles, X threads, Reddit engagement
8. **Measurement** — Weekly/monthly tracking across all KPI channels

---

## THE BOTTOM LINE

Right now, if someone searches "free vertical drama app" or "micro drama like ReelShort but free" — VURT doesn't appear. Not on Google, not in AI search, nowhere. 100+ titles are completely invisible to the internet.

**The share link problem makes this worse.** Every time a user shares an episode, the link (`vurt.enveu.link/dmqdikktzy`) sends all SEO value to enveu's domain. VURT is actively generating backlinks — for someone else. The more users share, the more equity leaks. This needs to be fixed before any marketing push amplifies the problem.

The Priority 1 fixes (episode URLs, share link redirect, sitemap, meta tags, broken link fix) are the foundation. Without them, nothing else works. Every day without these is organic traffic left on the table — especially with TechCrunch coverage driving awareness that should be compounding, not wasting.

VURT has all the ingredients for SEO success: great content, notable talent, press coverage, and a free product in a growing market. The only thing missing is the technical foundation to let search engines see it. **Fix the foundation, and the organic traffic will follow.**

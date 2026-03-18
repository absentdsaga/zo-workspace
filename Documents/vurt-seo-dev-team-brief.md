# VURT SEO — Dev Team Brief
### For: Web & App Dev Team Call
### Date: March 18, 2026
### Prepared by: Dioni Vasquez

---

## Context
We've done zero SEO. The technical audit shows the site is currently invisible to search engines and AI search (ChatGPT, Perplexity, Google AI Overviews). Every fix below is something the dev team needs to implement in enveu or at the infrastructure level.

The good news: the content is there, the brand is strong, and we launched to TechCrunch. We just need the technical foundation to let search engines actually find us.

---

## PRIORITY 1: CRITICAL (Do This Week)
*These are blocking all organic discovery*

### 1A. Series Pages Need Unique URLs
**The Problem:** When a user clicks on "Karma In Heels" (or any series), the URL stays at `myvurt.com/` — it doesn't change. The page title becomes generic "Video Detail." There are no unique meta tags per series.

**Why It Matters:** Google and AI search engines cannot index what they can't see. Our 100+ titles are invisible to search. Nobody can find "Karma In Heels" or "Come Back Dad" by searching for them. Nobody can share a link to a specific series — it just links to the homepage.

**What We Need:**
- Every series needs a unique, clean URL: `myvurt.com/series/karma-in-heels`
- Every episode needs a unique URL: `myvurt.com/series/karma-in-heels/episode-1`
- Each URL must have its own title, meta description, and OG tags (see 1C below)
- URLs should use hyphens, lowercase, human-readable slugs

**Question for dev team:** Does enveu support unique routes per content item? Is this a configuration or a platform limitation?

---

### 1B. Sitemap Is Empty
**The Problem:** `myvurt.com/sitemap.xml` returns HTTP 200 but contains no content. Google doesn't know what pages exist.

**What We Need:**
- Auto-generated sitemap.xml listing every page: homepage, all static pages, every series page, every episode page, every category page
- Add `Sitemap: https://www.myvurt.com/sitemap.xml` to robots.txt
- Submit sitemap to Google Search Console once generated

**Question for dev team:** Does enveu auto-generate sitemaps? If not, can we configure one?

---

### 1C. Meta Tags Are Empty or Broken
**The Problem:** Open Graph and Twitter Card tags are present on the homepage but all have null/empty values. Subpages have NO meta tags at all. When someone shares VURT on social media or messaging, the preview shows nothing.

**Current state (homepage):**
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

**What We Need — Each Static Page (About, FAQ, Contact, etc.):**
- Unique meta description per page
- OG tags per page
- Canonical URL per page

**Question for dev team:** Where in enveu do we configure meta tags? Can we set them dynamically per content item?

---

## PRIORITY 2: HIGH (Do Within 2 Weeks)

### 2A. Add Schema.org Structured Data (JSON-LD)
**The Problem:** Zero structured data on any page. This means no rich results in Google (ratings, episode counts, "free" badge), and AI search engines can't parse our content.

**What We Need — Homepage:**
```json
<script type="application/ld+json">
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
</script>
```

**What We Need — FAQ Page:**
```json
<script type="application/ld+json">
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
</script>
```

**What We Need — Each Series Page:**
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TVSeries",
  "name": "{Series Name}",
  "description": "{Synopsis}",
  "genre": ["{Genre1}", "{Genre2}"],
  "numberOfSeasons": 1,
  "numberOfEpisodes": {count},
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

**Question for dev team:** Can we inject custom `<script>` tags per page in enveu? Or do we need a tag manager (Google Tag Manager)?

---

### 2B. Server-Side Rendering / Pre-Rendering
**The Problem:** VURT is an Angular SPA. Search engine crawlers and AI crawlers receive a JavaScript shell, not rendered HTML. Googlebot can execute JS (slowly), but AI crawlers (ChatGPT, Perplexity) generally cannot. This means AI search sees a blank page.

**Options (in order of preference):**
1. **Angular Universal SSR** — Best option. Server renders full HTML per request.
2. **Pre-rendering service (Prerender.io)** — Middleware that serves static HTML to bots. No code changes needed.
3. **Static site generation** for fixed pages (About, FAQ, etc.)

**Question for dev team:** Does enveu support Angular Universal? If not, can we add Prerender.io as middleware?

---

### 2C. Image SEO
**The Problem:** All image filenames are hashed CDN URLs with zero SEO value. Alt text exists but is minimal (just series titles). No EXIF metadata.

**What We Need:**
- Descriptive alt text on every image (not just the title — describe what's in the image)
- Logo image on subpages is missing alt text entirely — fix immediately
- If possible within enveu: descriptive image filenames

**Question for dev team:** Can we control alt text per content item in enveu's CMS? Can we set custom filenames for uploaded assets?

---

## PRIORITY 3: MEDIUM (Do Within 30 Days)

### 3A. Fix Homepage H1
Currently the h1 is the featured series name ("Karma In Heels"). It changes with the carousel. Should have a persistent h1: "VURT — Free Vertical Micro-Series & Drama Streaming" or similar.

### 3B. Fill Empty Pages
- "What's New" page is a placeholder with no actual content
- "Help/Support" page lists categories but has no articles
- These empty pages hurt credibility with crawlers

### 3C. Add Press/Social Proof to Homepage
- TechCrunch logo with link
- Talent names (Kevin Hart, Vivica A. Fox)
- App store ratings
- Download counts (when meaningful)

### 3D. Register with Search Consoles
- Google Search Console — verify ownership, submit sitemap
- Bing Webmaster Tools — important because ChatGPT uses Bing's index

### 3E. App Store Optimization
- **Google Play title**: Change from "VURT" to "VURT - Free Vertical Drama & Micro-Series"
- **Google Play description**: Add keywords: "free streaming", "micro-drama", "vertical cinema", "Black culture"
- **iOS title/subtitle**: Same keyword optimization
- **What's New text**: Use keyword-rich update notes, not "Small updates, same big vision"

---

## QUESTIONS TO ASK THE DEV TEAM

1. **What can we customize in enveu?** Meta tags, schema markup, URL structure, sitemap, image alt text, filenames?
2. **Does enveu support Angular Universal (SSR)?** If not, can we add Prerender.io?
3. **Why don't series have unique URLs?** Is this an enveu limitation or a configuration issue?
4. **Can we inject custom scripts (JSON-LD) per page?** Or do we need Google Tag Manager?
5. **Who controls robots.txt and sitemap.xml?** Can we edit them directly?
6. **What's the timeline?** How quickly can they implement Priority 1 items?
7. **Can we get Google Search Console / Bing Webmaster Tools access?** Need to verify domain ownership.

---

## WHAT I'LL OWN (Content & Strategy Side)
*Dev team does not need to focus on these — sharing the full plan for alignment and expert review.*

### 1. Off-Site SEO & Backlink Strategy

**Medium (Primary — high-DA backlink engine)**
- Creating a VURT publication on Medium
- 2-3 articles/week for first 90 days
- Article types: industry analysis, competitor comparisons, creator spotlights, cultural essays, how-tos
- Example titles:
  - "The $14B Micro-Drama Market Has a Diversity Problem"
  - "ReelShort Charges $30/Month. VURT Is Free. Here's Why."
  - "How [Creator Name] Made a Micro-Series in 72 Hours on VURT"
- Every article links to myvurt.com at least twice (contextual, not forced)
- Contextual backlinks outperform profile bio links 5-10x (Google Jan 2026 "Authenticity Update" values first-hand experience)

**X / Twitter Threads (social signal + Grok integration)**
- Thread types: "The VURT thesis," competitor comparisons, creator spotlights, industry news reactions, behind-the-series
- Structure: hook with primary keyword → value → CTA + link
- X is now a ranking signal — Grok pulls from X data, Google counts social mentions for E-E-A-T

**LinkedIn Articles (B2B visibility)**
- Business model thought leadership, market reports, creator economy analysis
- Targets: entertainment execs, investors, brand partners, creators

**Reddit (Google indexes heavily since 2024 deal, AI search cites frequently)**
- Target subs: r/streaming, r/BlackFilm, r/filmmakers, r/shortfilm, r/cordcutters
- Genuine engagement first — max 1 self-promo post per sub per month

**Backlink tiers:**
1. **Editorial/Press**: Already have TechCrunch. Targeting Variety, Deadline, Shadow and Act, The Root, Black Enterprise
2. **Directory**: Crunchbase, AngelList, Product Hunt launch, AlternativeTo (as alt to ReelShort/DramaBox/Tubi), Wikipedia (TechCrunch coverage establishes notability)
3. **Content**: Medium, X threads, LinkedIn, guest posts, creator blogs
4. **Community**: Reddit, Quora, Discord, film festival partnerships

### 2. Keyword Strategy

**4-tier approach — not competing head-on with ReelShort on "micro drama app." Owning the lanes they aren't in.**

**Tier 1 — Brand (must own):** VURT, VURT app, VURT streaming, myvurt

**Tier 2 — Category (compete):** micro drama app, short drama series, vertical video streaming, free drama streaming app

**Tier 3 — Long-tail (win these — low competition, high intent):**
- "free Black drama series app"
- "micro drama app like ReelShort but free"
- "vertical drama series for phone"
- "Black indie filmmaker streaming platform"
- "micro drama app no paywall"
- "free alternative to ReelShort" / "free alternative to DramaBox"
- "vertical cinema platform"

**Tier 4 — Cultural/Contextual (authority building):** Black micro-drama, vertical filmmaking, micro-drama industry 2026, AVOD vs pay-per-episode, creator-owned streaming

**Open territory nobody ranks for:**
- "free vertical drama streaming"
- "Black micro drama app"
- "indie filmmaker streaming submit"
- "culture-driven streaming app"
- "AVOD micro drama"

### 3. App Store Copy (I write, dev team publishes)
- **Google Play title**: "VURT - Free Vertical Drama & Micro-Series" (currently just "VURT")
- **Google Play description**: Adding "free streaming", "micro-drama", "vertical cinema", "Black culture"
- **iOS title/subtitle**: Same keyword optimization
- **What's New**: Keyword-rich update notes, not "Small updates, same big vision"
- Unified keyword strategy across web + app stores (ASO + SEO convergence)

### 4. AI Search Optimization (GEO)

70% of AI search runs through ChatGPT. Google/Microsoft confirmed (March 2025) they use schema markup for AI features.

- **Entity building**: Getting VURT mentioned on pages AI already cites — Crunchbase, Product Hunt, AlternativeTo, Wikipedia, Reddit, Medium
- **Unlinked brand mentions**: Carry weight with AI systems even without links
- **Answer-first content**: Structuring all content so AI can extract and cite it (bullet points, clear headers, direct answers before context)
- **Monthly AI search testing**: 10-20 VURT-relevant queries across ChatGPT, Perplexity, Google AI Overviews — tracking whether VURT appears
- **Share of voice**: Brand appearance frequency across AI responses (primary GEO metric)
- **Content freshness**: AI citation drops sharply after 3 months — refreshing key content quarterly
- **Technical dependency**: AI crawlers cannot execute JavaScript — SSR/pre-rendering (Priority 2B) is the dev team blocker here

### 5. Image EXIF & Asset SEO

**Filename convention:**
```
vurt-[series-name]-[descriptor]-[optional-episode].jpg
```
Examples: `vurt-karma-in-heels-poster-s1.jpg`, `vurt-come-back-dad-tatyana-ali-ep3-still.jpg`

**EXIF metadata embedded before upload:**
| Field | Value |
|-------|-------|
| Title | Series/asset name |
| Description | What the image shows + context |
| Copyright | © 2026 VURT Corporation |
| Keywords | Series name, talent, genre, "VURT", "vertical cinema", "micro-drama" |
| Author | VURT |
| Source | myvurt.com |

**Alt text standards:**
- Unique per image, describes what you see, includes keywords naturally
- GOOD: "Tatyana Ali and Charles S. Dutton in Come Back Dad, a VURT micro-series about family reconciliation"
- BAD: "come-back-dad image" / keyword-stuffed spam

### 6. Press & Authority Building
- TechCrunch coverage in hand — using for notability (Wikipedia, directory listings)
- Pitching follow-ups: Variety, Deadline, Shadow and Act, The Root, Black Enterprise, Essence
- Creator spotlights timed with each new series launch
- Milestone press releases (download counts, partnerships, talent announcements)

### 7. Content Calendar (First 30 Days)

| Week | Medium | X Threads | Other |
|------|--------|-----------|-------|
| 1 | Launch article + industry piece | "The VURT thesis" thread | Reddit intros (r/streaming, r/BlackFilm) |
| 2 | Competitor comparison + creator spotlight | Creator spotlight thread | LinkedIn AVOD piece, Product Hunt launch, Crunchbase/AngelList |
| 3 | Submission how-to + market analysis | Comparison thread | Reddit organic engagement |
| 4 | Cultural essay + future of vertical | Behind-the-series thread | LinkedIn market report, AlternativeTo listing |

### 8. Measurement
- Referring domains tracked weekly (new backlinks)
- Keyword rankings for Tier 2-3 keywords weekly
- AI search results tested monthly (ChatGPT, Perplexity, Google AI)
- Medium views + referral traffic to myvurt.com
- X thread impressions + link clicks
- Dead link audit monthly (AI crawlers abandon unreliable domains faster than Google)

---

## THE BOTTOM LINE
Right now, if someone searches "free vertical drama app" or "micro drama like ReelShort but free" — VURT doesn't appear. Not on Google, not in AI search, nowhere. We have 100+ titles that are completely invisible to the internet.

The Priority 1 fixes (unique URLs, sitemap, meta tags) are the foundation. Without them, nothing else works. Every day without these is organic traffic we're leaving on the table — especially with TechCrunch coverage driving initial awareness that we should be compounding, not wasting.

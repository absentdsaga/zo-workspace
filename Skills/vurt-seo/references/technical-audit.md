# VURT Technical SEO Audit — myvurt.com
## Audited: March 17, 2026

---

## Overall Grade: D+
The site is functional but has major SEO gaps. Almost no optimization for search engines or AI crawlers. The enveu white-label platform provides basic structure but critical SEO elements are missing or misconfigured.

---

## 1. Meta Tags

### Homepage
| Tag | Status | Current Value | Issue |
|-----|--------|---------------|-------|
| title | PRESENT but weak | "Home Of The Vertical Creators. Watch vertical micro series, documentaries, and culture driven stories" | Too long (100+ chars), no brand name "VURT", no primary keywords |
| meta description | PRESENT but weak | Same as title | Duplicate of title, generic, no CTA |
| og:title | EMPTY | null | Open Graph title is blank |
| og:description | EMPTY | null | Open Graph description is blank |
| og:image | PRESENT | enveu CDN URL | OK but filename is hashed (not descriptive) |
| og:type | EMPTY | null | Should be "website" |
| twitter:card | PRESENT | summary_large_image | OK |
| twitter:title | EMPTY | null | Blank |
| twitter:description | EMPTY | whitespace | Blank |
| twitter:image | EMPTY | null | Blank |
| canonical | MISSING | — | No canonical URL set |
| keywords | MISSING | — | No meta keywords (low priority but still matters for some crawlers) |

### Subpages (About, FAQ, Contact, What's New)
| Tag | Status |
|-----|--------|
| title | PRESENT, unique per page (good) |
| meta description | MISSING on all subpages |
| og:* tags | MISSING on all subpages |
| twitter:* tags | MISSING on all subpages |
| canonical | MISSING on all subpages |

### Verdict
**Homepage**: OG and Twitter tags exist but are empty/null — sharing the site on social media produces blank previews. This is a critical fix.
**Subpages**: No meta descriptions, no OG tags, no Twitter cards. Search engines and social shares get nothing.

### Recommended Fix — Homepage
```html
<title>VURT — Free Vertical Drama & Micro-Series | Built for the Culture</title>
<meta name="description" content="Watch 100+ vertical micro-series, dramas, and originals free on VURT. No paywall. Black creators, bold stories, designed for your phone. Download now." />
<link rel="canonical" href="https://www.myvurt.com/" />
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
```

---

## 2. Structured Data (Schema.org)

### Current: ZERO JSON-LD schemas on any page

This is a major miss. Schema markup is how you get:
- Rich snippets in Google (show ratings, episode counts, free pricing)
- AI search engine citations
- Google Knowledge Panel for VURT
- Video carousels in search results

### Required schemas:
| Page | Schema needed |
|------|--------------|
| Homepage | Organization, WebSite (with SearchAction) |
| Series pages | TVSeries, VideoObject |
| Episode pages | TVEpisode, VideoObject |
| FAQ page | FAQPage (AI search engines pull directly from this) |
| All pages | BreadcrumbList |

### Priority: FAQPage schema on /faq
This is the fastest win — the FAQ page already has great Q&A content. Adding FAQPage schema makes it eligible for Google's FAQ rich results AND makes AI search engines cite VURT directly when answering "what is VURT" or "is VURT free" queries.

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
        "text": "Yes, VURT is a free and legal video streaming service. To keep our service free, we include advertising to help pay for the awesome content available and technology costs of running our platform."
      }
    }
  ]
}
```

---

## 3. Heading Hierarchy

### Homepage
| Level | Content | Assessment |
|-------|---------|------------|
| h1 | "Karma In Heels" | BAD — h1 is the featured series, not the site/page identity. Should be "VURT — Free Vertical Micro-Series & Drama Streaming" |
| h2 | "Top 10 Micro Series", "Break The Boredom" | OK as rail/section headers |
| h3 | "Policy", "Other Links", "Connect with us", "Download App" | Footer sections — fine |
| h4 | Series titles (35 & Ticking, etc.) | OK |

**Issue**: The h1 changes with featured content. Should have a persistent, keyword-rich h1.

### Subpages
- About: h1="ABOUT VURT", h2="Our Mission" — OK structure
- FAQ: h1="FAQs", h2s for each question — GOOD structure
- Contact: h1="Contact Us" — OK
- What's New: h1="What's New", h2="What's New" — BAD: duplicate h1/h2

---

## 4. Images

### Homepage: 44 images
- **1 missing alt text** (logo image has no alt on subpages)
- Alt text is present on most images but uses series titles only (e.g., alt="35 & Ticking") — should be more descriptive
- **Filenames**: All hashed/CDN URLs via enveu — zero SEO value in filenames
  - Example: `https://images-cdn-us1.enveu.com/900x506/filters:format(webp):quality(60)/https%3A%2F%2Fresources-us1.enveu.tv%2FVURT_17...`
  - Should be: `vurt-35-and-ticking-series-poster.jpg`
- Lazy loading properly implemented (`loading="lazy"` on non-hero images, `loading="eager"` on hero)
- WebP format used via CDN — good for performance
- No srcset/responsive image attributes

### Subpages
- Logo image missing alt text on ALL subpages (About, FAQ, Contact, What's New)

### Verdict
Image alt text exists but is minimal. Filenames are all CDN-hashed (enveu limitation). EXIF data likely stripped by CDN. Need to work within enveu's constraints or find override points.

---

## 5. robots.txt

```
User-agent: *
Allow: /
Disallow: /user
Disallow: /search*
```

**Assessment**: Basic but functional. Correctly blocks user account pages and search pages. Missing:
- Sitemap directive (`Sitemap: https://www.myvurt.com/sitemap.xml`)
- No crawl-delay specified
- Could add specific blocks for bot types if needed

---

## 6. Sitemap

**Status**: sitemap.xml returns HTTP 200 but appears EMPTY.

This is critical — without a sitemap, Google doesn't know what pages exist. For a content platform with 100+ series, this means potentially hundreds of pages are invisible to search engines.

**Need**: Auto-generated sitemap including:
- Homepage
- All static pages (about, faq, contact, etc.)
- Every series page
- Every episode page
- Every genre/category page

---

## 7. Server-Side Rendering (SSR)

The site is an Angular SPA on enveu infrastructure. Key question: **Does the server return rendered HTML or just a JavaScript shell?**

Based on the audit:
- Meta tags ARE present in initial render (good — enveu likely handles basic meta tag injection)
- Content appears to be client-rendered (Angular components)
- Need to verify with Google's URL Inspection tool in Search Console

**If no SSR**: Googlebot can execute JavaScript, but with delays and limitations. AI crawlers generally cannot. This could mean AI search engines see a blank page.

---

## 8. Page Speed & Performance

- Images served via CDN with WebP optimization — good
- Lazy loading on non-hero images — good
- CACHE-CONTROL: NO-CACHE header set — BAD for performance, means nothing is cached
- No visible preconnect/prefetch hints for CDN domains
- Angular bundle size unknown — need Lighthouse audit

---

## SUMMARY: Top 10 Fixes (Priority Order)

| # | Fix | Impact | Effort |
|---|-----|--------|--------|
| 1 | Fill in OG + Twitter meta tags on homepage | HIGH — social shares currently show blank | LOW — config change |
| 2 | Add meta descriptions to ALL pages | HIGH — search result snippets | LOW |
| 3 | Add FAQPage schema to /faq | HIGH — AI search + Google rich results | LOW |
| 4 | Fix empty sitemap.xml (or generate one) | HIGH — pages aren't being indexed | MEDIUM |
| 5 | Add Organization + WebSite schema to homepage | HIGH — Knowledge Panel, AI citations | LOW |
| 6 | Add canonical URLs to all pages | MEDIUM — prevents duplicate content | LOW |
| 7 | Add Sitemap directive to robots.txt | MEDIUM — helps crawlers find sitemap | LOW |
| 8 | Fix homepage h1 (should be VURT, not featured series) | MEDIUM — page identity signal | LOW-MEDIUM |
| 9 | Add alt text to logo image on all subpages | LOW-MEDIUM — accessibility + SEO | LOW |
| 10 | Investigate SSR/pre-rendering for AI crawler support | HIGH — but depends on enveu capability | HIGH |

---

## Platform Constraint: enveu
VURT runs on enveu.com white-label streaming infrastructure. Many of these fixes require changes in enveu's CMS/config, not direct code access. Key questions for Mark/team:
1. Where do we configure meta tags in enveu?
2. Can we inject custom JSON-LD scripts?
3. Can we control the sitemap generation?
4. Does enveu support SSR or pre-rendering?
5. Can we customize image filenames or alt text per content item?

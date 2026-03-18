# VURT SEO Implementation Checklist

## Priority: CRITICAL (Do This Week)

### Technical SEO — myvurt.com
- [ ] **Fix page titles** — Homepage title is generic ("Home Of The Vertical Creators..."). Should be: "VURT — Free Vertical Drama & Micro-Series Streaming | Built for the Culture"
- [ ] **Unique meta descriptions per page** — Each page needs a distinct, keyword-rich meta description (under 160 chars)
- [ ] **Add Open Graph tags** — og:title, og:description, og:image, og:type, og:url on every page
- [ ] **Add Twitter Card tags** — twitter:card, twitter:site, twitter:title, twitter:description, twitter:image
- [ ] **Create/fix robots.txt** — Ensure crawlers can access all public pages
- [ ] **Create sitemap.xml** — Submit to Google Search Console
- [ ] **Register with Google Search Console** — Verify ownership, submit sitemap, monitor indexing
- [ ] **Register with Bing Webmaster Tools** — AI search engines (ChatGPT via Bing) use this
- [ ] **Dead link audit** — Scan entire site, fix any broken links immediately
- [ ] **Angular SSR or pre-rendering** — Critical: without this, Google may not index content properly. Check if enveu supports this.

### Schema Markup
- [ ] **Organization schema** on homepage (name, url, logo, social profiles, description)
- [ ] **WebSite schema** with SearchAction on homepage
- [ ] **TVSeries schema** on each series page
- [ ] **VideoObject schema** on each episode page
- [ ] **FAQPage schema** on FAQ page (AI search engines LOVE pulling from FAQ schema)
- [ ] **BreadcrumbList schema** for navigation

### Image SEO
- [ ] **Audit all image filenames** — Replace hashed/generic names with descriptive `vurt-[what-it-is].jpg` format
- [ ] **Add alt text to every image** — Unique, descriptive, keyword-natural
- [ ] **Add EXIF metadata** to key promotional images (posters, thumbnails, social assets)
- [ ] **Optimize image file sizes** — WebP format, under 200KB for web

---

## Priority: HIGH (Do Within 2 Weeks)

### Content SEO (Off-Site)
- [ ] **Create Medium publication** — "VURT" publication for all blog content
- [ ] **Publish first 3 Medium articles** — Launch announcement, industry analysis, comparison piece
- [ ] **Create X thread** — "The VURT thesis" thread explaining the platform
- [ ] **Create X thread** — Competitor comparison thread
- [ ] **Create Crunchbase profile** — Company, funding, team
- [ ] **Create AngelList profile**
- [ ] **Submit to Product Hunt** — Plan launch for maximum visibility
- [ ] **List on AlternativeTo** — As alternative to ReelShort, DramaBox, Tubi

### App Store Optimization
- [ ] **Optimize iOS App Store title** — Include "micro-drama" or "vertical drama" in subtitle
- [ ] **Optimize iOS App Store description** — Front-load with target keywords
- [ ] **Optimize Google Play listing** — Title, short description, full description with keywords
- [ ] **Add keyword-rich screenshot captions** in both stores
- [ ] **Implement app indexing** — Google App Indexing so series/episodes appear in search

### Keyword Targeting
- [ ] **Create landing pages** for top 5 long-tail keywords
- [ ] **Optimize FAQ page** for "People Also Ask" triggers
- [ ] **Add blog/articles section to myvurt.com** (if possible within enveu platform)

---

## Priority: MEDIUM (Do Within 30 Days)

### Authority Building
- [ ] **LinkedIn article** — Business model thought leadership
- [ ] **Reddit presence** — Establish in r/streaming, r/BlackFilm, r/filmmakers
- [ ] **Wikipedia** — Check if VURT meets notability requirements (TechCrunch coverage helps). If yes, create stub or add to relevant articles (micro-drama, vertical video)
- [ ] **Press outreach** — Pitch follow-up stories to Variety, Deadline, Shadow and Act, The Root, Black Enterprise
- [ ] **Creator blog posts** — Each creator who publishes on VURT writes/gets a spotlight post linking back

### Website Improvements
- [ ] **Fill "What's New" page** — Currently empty placeholder. Should be a live blog/changelog
- [ ] **Fill "Help/Support" page** — Currently empty. Add actual FAQ content, troubleshooting
- [ ] **Add press section** — Logo bar with TechCrunch, Yahoo Tech logos + links
- [ ] **Add talent highlights to homepage** — Kevin Hart, Vivica A. Fox, etc. as social proof
- [ ] **Series-level SEO pages** — Each series needs its own URL with unique title, description, schema

---

## Priority: ONGOING

### Content Cadence
- [ ] **2-3 Medium articles per week** (first 90 days)
- [ ] **2+ X threads per week**
- [ ] **1 LinkedIn article per week**
- [ ] **Monthly Reddit engagement**
- [ ] **Creator spotlight with every new series launch**

### Monitoring
- [ ] **Weekly**: Check Google Search Console for indexing issues, keyword rankings
- [ ] **Weekly**: Monitor backlink growth (new referring domains)
- [ ] **Monthly**: Search VURT-relevant queries in ChatGPT, Perplexity, Google AI Overviews — track whether VURT appears
- [ ] **Monthly**: Competitor keyword position tracking
- [ ] **Quarterly**: Full technical SEO re-audit

---

## Platform Limitations to Investigate
VURT uses enveu.com white-label streaming infrastructure. Key questions:
- [ ] Does enveu support server-side rendering (SSR) or pre-rendering for Angular?
- [ ] Can we customize meta tags per series/episode page?
- [ ] Can we add custom JSON-LD schema to pages?
- [ ] Can we control robots.txt and sitemap.xml?
- [ ] Can we add a blog section within the platform?
- [ ] Can we customize image filenames and alt text in the CMS?
- [ ] What URL structure does enveu use for series/episodes?

If enveu limits these capabilities, we may need:
- A separate blog subdomain (blog.myvurt.com) on a platform we control
- Custom meta tag injection via enveu's config or a tag manager
- A reverse proxy setup for SSR

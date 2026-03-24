# VURT Dev Team — Preliminary Call Talking Points

**Re: SEO & Technical Fixes**
**Date: March 19, 2026**

---

## URL & Linking Issues

- Series pages have unique URLs (e.g., `/detail/micro_series/the-love-letter`) — good
- **Episodes do NOT have unique URLs** — URL stays at the series level when switching episodes. Each episode needs its own URL for SEO indexing and sharing.
- **Share links point to `vurt.enveu.link` instead of `myvurt.com`** — every shared link builds SEO authority for enveu's domain, not ours. Need share links to generate `myvurt.com` URLs.
- **Deep links don't route to episodes** — shared link opens app to the show page, not the specific episode the user shared

## Crawlability & Indexing

- **Sitemap.xml is empty** — search engines can't discover our content. Needs to be auto-populated with all series and episode URLs.
- **Angular SPA rendering** — crawlers and AI search engines (ChatGPT, Perplexity) may see a blank page instead of content. Do we have SSR or pre-rendering enabled? If not, what are our options?
- Robots.txt needs a sitemap directive added

## Meta Tags & Structured Data

- Homepage has meta tags but **series pages appear to have none** (no title, description, OG tags, Twitter cards, canonical URL per page)
- **Zero schema markup (JSON-LD) on any page** — this is what gets us rich results in Google and citations in AI search
- Need per-page meta tags: unique title, description, OG image, canonical URL for every series and episode

## Broken Links

- Crawl found malformed URLs with doubled domain: `myvurt.com/www.myvurt.com/privacy-policy`
- Internal settings path exposed: `/settings/terms-and-conditions` is publicly accessible

## Analytics & Infrastructure — RESOLVED (for reference)

- GA4 property 518738893 access was blocked because it was set up under **developer@myvurt.com** (GA4 account 379620900). dioni@myvurt.com and mark@myvurt.com have now been added as Admins.
- The prod GCP project (vurt-bd356) is under thesourcegroups.com org — VURT owns it. All team members are Owners.
- **Note for dev team:** There are 3 GA4 properties under this account (vurt-790c4, vurt-9e1c5, vurt-bd356) — confirm only vurt-bd356 (518738893) is the active production property. What are the other two?

## Questions We Need Answered

1. ~~**Who owns GA4 property 518738893?**~~ RESOLVED — developer@myvurt.com. What are the other two GA4 properties (vurt-790c4, vurt-9e1c5) for?
2. What can we customize in enveu? (meta tags, schema, URL structure, sitemap, image alt text)
3. Is the episode URL issue an enveu limitation or a config issue?
4. Can share links be configured to use our domain instead of `vurt.enveu.link`?
5. Does enveu support SSR or pre-rendering for Angular?
6. Can we inject custom JSON-LD scripts per page?
7. Who controls robots.txt and sitemap.xml — can we edit them directly?
8. Can we get Google Search Console and Bing Webmaster Tools access? (need domain verification)

## Google Play Store

- Data safety section says "No data collected" but also "This app may share data types with third parties" — contradictory, needs cleanup
- No ratings yet (iOS has 11 ratings at 4.7 stars) — Android listing needs attention

---

*After this call, we'll have a direct line to the dev team for detailed implementation specs.*

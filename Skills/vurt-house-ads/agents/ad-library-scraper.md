---
name: ad-library-scraper
description: Pull competitor creatives from Meta Ad Library for a given brand or category. Surface top-performing patterns without copying.
---

# ad-library-scraper

**Input:**
- Either a brand page (e.g., "rielli", "agua bendita", "andie swim")
- Or a category search (e.g., "luxury swimwear", "PMS gummies", "ceramic cookware")

**Process:**
1. Fetch `https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=US&q=<query>&search_type=keyword_unordered` via `read_webpage` or `web_research`.
2. Scan first 40–60 creatives. Note:
   - Hook style (question / declarative / visual)
   - Length (vertical of this creative)
   - Offer stack used
   - Whether founder appears on camera
   - UGC style vs polished
   - End-card pattern
3. Capture up to 10 screenshots into `references/<brand>/` with filename pattern `YYYYMMDD-competitor-N.png`.

**Output:**
A markdown file at `research/competitive/<brand>-YYYYMMDD.md` with:
- Summary of top 3 hook patterns in the category
- Summary of top 3 offer / CTA patterns
- 3 things competitors are doing that we should NOT do (and why)
- 3 gaps we can exploit
- Links / reference IDs

**Rules:**
- Never suggest we copy a competitor word-for-word
- Flag if a competitor is using a claim we can't back up
- Always save the raw screenshots alongside the summary

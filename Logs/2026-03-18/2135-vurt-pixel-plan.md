# VURT Pixel Tracking Plan
**Time:** 2026-03-18 21:35 ET
**Task:** Create comprehensive pixel/tracking plan for VURT paid ads team

## Actions
1. Explored all VURT docs (master doc, SEO plan, social audit, app audits)
2. Identified critical technical constraint: myvurt.com is Angular SPA with no unique URLs per series/episode
3. Created phased pixel plan (Phase 1: Foundation, Phase 2: Behavior, Phase 3: Advanced)
4. Mapped full user journey A→Z with pixel placement at each touchpoint
5. Drafted email for paid ads team with technical context + event descriptions
6. Recommended smart pixel architecture (1 base pixel + event params vs 1000 separate pixels)

## Files Created
- `Documents/VURT-Pixel-Tracking-Plan.md` — Full plan + email draft

## Key Decisions
- Event-based pixels required (not page-load) due to SPA architecture
- P0 priorities: Landing, Play Button, Registration
- Recommended GTM container for centralized pixel management
- UTM structure standardized for all campaigns

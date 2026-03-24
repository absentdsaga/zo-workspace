# VURT Social Media Analytics Integration
**Date:** March 20, 2026 (9:45 PM ET)

## Objective
Integrate social media analytics into the VURT daily analytics report alongside existing Firebase/GA4 data.

## Actions Taken
1. **Created `social_client.py`** — Social media scraper module using `agent-browser` CLI
   - YouTube: subscribers, video count, total views, per-video breakdown
   - TikTok: followers, likes, following
   - X/Twitter: followers, posts, following
   - Instagram: Meta Graph API integration (requires token setup) with fallback to last-known data
   - JSON cache for day-over-day comparison tracking

2. **Integrated into `daily-report.py`** — Added social media section before insights

3. **Extended `insights_engine.py`** — New `_analyze_social()` function generates:
   - Cross-platform presence health check (social followers vs app users)
   - TikTok priority alerts (biggest gap in social strategy)
   - YouTube algorithm performance (views:subscriber ratio)
   - Day-over-day follower/subscriber changes

4. **Updated `SKILL.md`** — Documented new social capabilities and current status

## Data Sources & Reliability
- **YouTube:** Reliable via agent-browser snapshot (structured accessibility tree)
- **TikTok:** Reliable via agent-browser snapshot
- **X/Twitter:** Reliable via agent-browser snapshot
- **Instagram:** BLOCKED — all unauthenticated scraping methods fail (rate limited/login required). Needs Meta Graph API token (`VURT_INSTAGRAM_TOKEN` + `VURT_INSTAGRAM_USER_ID` as Zo secrets)

## Files Created/Modified
- Created: `Skills/vurt-analytics/scripts/social_client.py`
- Created: `Skills/vurt-analytics/scripts/.social-cache.json` (auto-generated cache)
- Modified: `Skills/vurt-analytics/scripts/daily-report.py` (added social section)
- Modified: `Skills/vurt-analytics/scripts/insights_engine.py` (added social analysis)
- Modified: `Skills/vurt-analytics/SKILL.md` (updated status and docs)

## Current VURT Social Metrics (Live Data)
| Platform | Handle | Followers/Subs | Activity |
|----------|--------|---------------|----------|
| YouTube | @myVURT1 | 11 | 6 videos, 2,365 total views |
| TikTok | @myvurt | 5 | 112 likes |
| Instagram | @myvurt | ~324* | 21 posts (manual) |
| X | @myvurt | 6 | 3 posts |

## Next Steps
1. Set up Instagram Meta Graph API access
2. Mark to upgrade Dioni to Editor on GA4 property 518738893
3. Create web data stream for myvurt.com in GA4

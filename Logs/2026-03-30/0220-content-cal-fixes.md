# Content Calendar Session - Fixes & Diagnostics
**Date:** 2026-03-30 02:20 ET

## Completed
1. **Renamed all Post Log titles** — "KIH" → "Karma in Heels" across 14 entries
2. **Fixed IG Views metric** — was returning 0 for everything because `impressions` metric (broken on v25.0) was in the batch request, causing a silent 400 error that zeroed out all metrics. Fix: split into working metric groups. Now pulling real views for all posts.
3. **Updated sync script** — pagination for IG posts (up to 100), separate reel-specific metric fetch, views logic uses `ig_reels_aggregated_all_plays_count` for reels and `views` insight for images

## Diagnostics
4. **YouTube Analytics API** — 403 Forbidden. Root cause: dioni@myvurt.com has no YouTube channel. The VURT YT channel (UCB7B5ifo5Pgfc-j_uJGQG1g, "VURT") is owned by a different Google account. YouTube Analytics requires OAuth from the channel OWNER. Need channel owner to authorize.
5. **Meta ads_read** — Current token is a PAGE token with scopes: read_insights, pages_show_list, instagram_basic, instagram_manage_insights, pages_read_engagement, pages_read_user_content, pages_manage_engagement. NO ads_read. Dioni has "Partial access / Basic" on myvurt business in Meta Business Suite — can't self-upgrade.
6. **Frame.io v3 token** — User on the token creation page. Needs: Accounts Read, Assets Read+Update, Projects Read.

## Files Modified
- Skills/vurt-post-log/scripts/sync.py (IG metrics fix, pagination, title logic)

# VURT API Capabilities Audit & Enhancements

**Date:** 2026-03-30 01:20 ET
**Task:** Full API audit, Frame.io write test, YouTube Analytics test, sync enhancements

## Actions Taken

1. **Tested all 13 API keys** for actual capabilities
2. **Frame.io** — READ works (592 assets crawled), WRITE blocked (v4 API lacks asset-level PUT endpoints with current Adobe OAuth token)
3. **YouTube Analytics** — OAuth token has correct scopes (youtube.readonly, yt-analytics.readonly) but Analytics API not enabled in GCP. Data API v3 works fine.
4. **Meta/IG** — Discovered additional metrics available: `total_interactions`, `reels_skip_rate`, `clips_replays_count`, `ig_reels_aggregated_all_plays_count`. Token scopes confirmed, no ads_read.
5. **NPAW** — Confirmed working with HMAC auth, rawdata endpoint needs specific request pattern
6. **Mux** — Video asset listing works (/video/v1/assets), Data API returns 404 (add-on may not be enabled)
7. **Notion** — Added 4 new columns: Engagement, Skip Rate (%), Replays, Total Plays
8. **Sync script updated** — Now pulls richer IG metrics, handles missing columns gracefully
9. **Created** Documents/VURT-API-Capabilities.md — comprehensive reference

## Files Modified
- Skills/vurt-post-log/scripts/sync.py (enhanced IG metrics, error handling)
- Documents/VURT-API-Capabilities.md (new)

## Key Findings
- IG Views=0 on older posts is a Meta API limitation (views metric only available for reels/video, not images; older reels may not return views)
- Frame.io tagging requires either a v2 developer token or upgraded Adobe OAuth scopes
- YouTube Analytics needs 1-click API enable in GCP
- Meta Ads data needs ads_read scope (token upgrade)
- Mux Data add-on status unknown — needs Enveu verification

# API Audit + Post Log Data Fix — 2026-03-30 02:15 UTC

## Task
1. Audit all API keys for untapped capabilities
2. Verify and fix Post Log data accuracy
3. Add asset links and relevant info to Content Calendar

## API Keys Audited

| Key | Status | What It Can Do |
|-----|--------|---------------|
| VURT_META_ACCESS_TOKEN | ✅ Active, enhanced | IG/FB post metrics + account demographics + best posting times |
| VURT_YOUTUBE_API_KEY | ✅ Active | YT Data API (views, likes, comments) — Analytics API needs OAuth upgrade |
| VURT_NOTION_API_KEY | ✅ Active | Full Notion CRUD for Post Log + Content Calendar |
| FRAMEIO_API_KEY | ⚠️ No project access | Token is personal (dioni.vasqu@gmail.com), no teams/projects found. Needs VURT workspace access. |
| VURT_MUX_TOKEN_ID/SECRET | ⚠️ Video only, no Data | 100 assets (IDs 3954-4069), but Mux Data (analytics) not available. Only 5 assets have public playback IDs. |
| VURT_ANALYTICS_REFRESH_TOKEN | ✅ Available | GA4/Firebase — not yet wired into content calendar |
| TRELLO_VURT_API_KEY | ✅ Available | Board/card management — not yet used |
| VURT_ADOBE_CLIENT_ID | ❓ Untested | Needs scope verification |
| GOOGLE_SHEETS_SERVICE_ACCOUNT | ✅ Available | Read/write sheets |

## Post Log Fixes

### 7 Mismatched Entries Found and Fixed
| Entry | Old Notion Views | Correct API Views | Root Cause |
|-------|-----------------|-------------------|------------|
| KIH Clip 3 - IG | 42 | 487 | Stale data (synced when brand new) |
| THIS IS VURT - IG | 1,078 | 2,678 | Not updated since initial sync |
| Industry Shifting - IG | 1,078 | 2,212 | Same |
| Come Back Dad - IG | 37,314 | 37,557 | Normal lag (+243) |
| My Brother's Wife - IG | 406 | 118 | Wrong post matched (date-only matching) |
| Miami Confidential - IG | 406 | 87 | Same issue |
| KIH Promo - IG | 894 | 795 | Had Parking Lot's number |

### Matching Fix
Changed from date-only matching to URL-first matching:
1. Priority 1: Match by permalink URL (exact)
2. Priority 2: Match by date + caption keyword overlap (fallback)

### New Columns Added to Post Log
- **Reach** — Unique accounts that saw the post
- **Avg Watch Time (s)** — Average watch time per view (Reels only)
- **Total Watch Time (min)** — Total cumulative watch time (Reels only)

## New Data Pulled

### Best Posting Times (from IG online_followers)
- Peak hours (UTC): 16:00-18:00 (~340-420 followers online)
- In ET: **12pm-2pm** is the sweet spot
- Secondary peak 8am-12pm UTC (4am-8am ET — early morning scrollers)

### Follower Demographics
- Age: 45-54 dominant (275), then 35-44 (214), then 55-64 (180)
- Gender: 57% Male, 36% Female, 15% Undisclosed
- Top cities: NYC (34), Houston (19), Miami Gardens (19), Jacksonville (16), LA (16)
- 90%+ US audience

### IG Views Accuracy
The API `views` insight metric IS the best available. `plays` field returns N/A on direct fields and errors on insights endpoint. The gap between API and in-app dashboard is a known Meta limitation (5-10% lag, updates every few hours).

## Files Modified
- Skills/vurt-post-log/scripts/sync.py — Enhanced IG matching + new metrics columns + FB reach
- Notion Post Log DB — Added Reach, Avg Watch Time (s), Total Watch Time (min) columns

## Blockers
- Frame.io: Token lacks project access — user needs to share VURT workspace with dioni.vasqu@gmail.com or get a team token
- Mux Data: Analytics addon not available — only video asset management works
- Content Calendar Asset Links: Can't auto-populate without Frame.io project access

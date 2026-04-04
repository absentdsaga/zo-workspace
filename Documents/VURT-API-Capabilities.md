# VURT API Capabilities Reference

*Last updated: 2026-03-30*

---

## 1. Meta (Instagram + Facebook)

**Token:** `VURT_META_ACCESS_TOKEN` (Page token, never expires)
**App:** Vurt Analytics (ID: 892877370386060)

### Granted Scopes
- `read_insights` — Page + IG insights
- `instagram_basic` — IG profile, media listing
- `instagram_manage_insights` — IG post-level + account-level analytics
- `pages_read_engagement` — FB page engagement data
- `pages_read_user_content` — FB user content on page
- `pages_manage_engagement` — Comment moderation on FB
- `pages_show_list` — List managed pages
- `public_profile`

### What We Can Pull
| Data | Endpoint | Status |
|------|----------|--------|
| IG post metrics (likes, comments, reach, shares, saves) | `/media?fields=insights` | **LIVE** |
| IG Reels metrics (views, avg watch time, skip rate, replays) | `insights.metric(views,ig_reels_avg_watch_time,reels_skip_rate,clips_replays_count)` | **LIVE** |
| IG total plays (aggregated) | `ig_reels_aggregated_all_plays_count` | **LIVE** |
| IG account-level insights (follower count, reach, impressions) | `/{IG_ID}/insights` | **LIVE** |
| IG audience demographics (age, gender, city, country) | `/{IG_ID}/insights?metric=follower_demographics` | **LIVE** |
| IG online followers (best posting times) | `/{IG_ID}/insights?metric=online_followers` | **LIVE** |
| FB Page post metrics (reactions, shares) | `/{PAGE_ID}/posts?fields=insights` | **LIVE** |
| FB video views | `post_video_views` via insights | **LIVE** |
| FB Page followers/fans | `/{PAGE_ID}?fields=followers_count,fan_count` | **LIVE** |
| IG post permalinks | `permalink` field | **LIVE** |
| IG media list (all posts) | `/{IG_ID}/media` | **LIVE** |

### NOT Available (would need additional scopes)
- `ads_read` — Meta Ads/campaign data (need Meta Business Suite access + token upgrade)
- `instagram_manage_comments` — Reply to IG comments programmatically
- `instagram_content_publish` — Auto-posting to IG (would need Business API approval)

### Key IDs
- IG Account: `17841479978232203`
- FB Page: `943789668811148`

---

## 2. YouTube

**Keys:** `VURT_YOUTUBE_API_KEY` (Data API), `VURT_YOUTUBE_REFRESH_TOKEN` (OAuth)
**OAuth Scopes:** `youtube.readonly`, `yt-analytics.readonly`

### YouTube Data API v3 (API Key) — LIVE
| Data | Status |
|------|--------|
| Channel stats (subs, views, video count) | **LIVE** |
| Video list with stats (views, likes, comments) | **LIVE** |
| Video details (title, description, tags, thumbnails) | **LIVE** |
| Search channel videos | **LIVE** |
| Playlist contents | **LIVE** |

### YouTube Analytics API (OAuth) — NEEDS ENABLING
| Data | Status |
|------|--------|
| Daily views, watch time, avg view duration | **BLOCKED** — API not enabled |
| Traffic sources (search, browse, external, etc.) | **BLOCKED** |
| Viewer demographics (age, gender, geography) | **BLOCKED** |
| Per-video retention curves | **BLOCKED** |
| Subscriber sources | **BLOCKED** |
| Revenue (if monetized) | **BLOCKED** |

**Action needed:** Enable "YouTube Analytics API" in GCP console (separate from Data API v3).
Link: https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com

### Key IDs
- Channel: `UCB7B5ifo5Pgfc-j_uJGQG1g` (VURT, 20 subs, 10 videos, 4687 views)

---

## 3. Frame.io (via Adobe OAuth)

**Keys:** `VURT_ADOBE_CLIENT_ID`, `VURT_ADOBE_CLIENT_SECRET`
**Token storage:** `/home/workspace/.secrets/adobe-tokens.json` (auto-refreshing)
**Account:** Mark's Account (dioni.vasqu@gmail.com as member)

### What Works
| Capability | Status |
|------------|--------|
| List all projects | **LIVE** |
| Browse folder structure | **LIVE** |
| List assets (videos, images, docs) | **LIVE** |
| Get asset metadata (name, size, type, status) | **LIVE** |
| Get asset view URLs (deep links to Frame.io player) | **LIVE** |
| Get version stacks | **LIVE** |
| Full inventory crawl (592 video files found) | **LIVE** |

### What Doesn't Work (Current Token)
| Capability | Status |
|------------|--------|
| Tag/label assets (write) | **BLOCKED** — v4 API has no asset-level PUT/PATCH route |
| Set custom thumbnails | **BLOCKED** — same issue |
| Add comments via API | **UNTESTED** — may need different endpoint |
| Download assets directly | **UNTESTED** — would need download URL from asset detail |

### Key IDs
- Account: `6c77dc3c-f088-486d-a8e3-678fc0fcbd70`
- Project: `6a0a9a57-379a-4d48-a7ba-f63982fa3acc`
- Root folder: `fea68d35-5ac3-4d96-9843-9257d0e06371`

### Library Structure
```
_Editing Assets/
Licensed Titles/
  1. SWIRL FILMS/ (Karma in Heels, Love Me Or Leave Me, The Last Stand, etc.)
  2. SLIP N SLIDE FILMS/ (Miami Kingpins)
  3. MBS MOVIES/
  4. FEAR PIX/
  5. CREATOR/FILMMAKER SUBMISSIONS/ (Parking Lot Series, Schemers, Chicago Boogie)
```

---

## 4. NPAW (Video Analytics for myvurt.com)

**Keys:** `NPAW_SYSTEM_CODE`, `NPAW_API_SECRET`
**Auth:** HMAC-MD5 signature

### What We Can Pull
| Data | Status |
|------|--------|
| Session-level viewing data (per viewer) | **LIVE** |
| Title-level play counts | **LIVE** |
| Device breakdown (brand, model, OS) | **LIVE** |
| Geographic data (country, city) | **LIVE** |
| Network info (ISP, CDN, connection type) | **LIVE** |
| Quality metrics (join time, buffer ratio, bitrate) | **LIVE** |
| Content metadata (title, duration, type) | **LIVE** |
| Real-time concurrent viewers | **AVAILABLE** (untested) |

### Key Findings
- 100% mobile viewers
- Samsung 47%, Huawei 22%, Apple 15%
- US 37% of traffic
- Top titles: Come Back Dad (16 plays), Girl In The Closet (9), Karma In Heels

---

## 5. Mux (Video Infrastructure)

**Keys:** `VURT_MUX_TOKEN_ID`, `VURT_MUX_TOKEN_SECRET`

### What Works
| Capability | Status |
|------------|--------|
| List video assets | **LIVE** |
| Get asset details (duration, resolution, status) | **LIVE** |
| Asset playback IDs | **LIVE** |
| Static renditions info | **LIVE** |

### What's Available But Untested
| Capability | Status |
|------------|--------|
| Mux Data (viewership analytics) | **NEEDS VERIFICATION** — got 404 on /data/v1, may need Data add-on enabled |
| Create new assets | Available with current token |
| Generate thumbnails from video | Available via Mux image API |
| Live streaming | Available but no live streams exist |

---

## 6. Google Analytics (GA4)

**Key:** `VURT_ANALYTICS_REFRESH_TOKEN`
**OAuth client:** `VURT_GOOGLE_OAUTH_CLIENT`

### What We Can Pull
| Data | Status |
|------|--------|
| Active users, sessions | **LIVE** |
| Page views by path | **LIVE** |
| Traffic sources | **LIVE** |
| Device/browser breakdown | **LIVE** |
| Geographic data | **LIVE** |
| Events (custom + standard) | **LIVE** |

### Known Issue
Consent Mode v2 is defaulting to "deny" — suppressing engaged session data. Needs Enveu dev team to fix.

---

## 7. Google Sheets (Service Account)

**Key:** `GOOGLE_SHEETS_SERVICE_ACCOUNT` (JSON)

### Capabilities
- Read/write any sheet shared with the service account email
- Currently used for: production tracker reads
- Can automate: status updates, color coding, data pulls

---

## 8. Notion

**Key:** `VURT_NOTION_API_KEY` (Internal integration)
**Capabilities:** Read, Update, Insert content

### Active Databases
- Content Calendar: within VURT Social Ops page
- Post Log: `c592ce58-b453-436f-b8e0-4510b2dcb412`

---

## 9. Trello

**Keys:** `TRELLO_VURT_API_KEY`, `TRELLO_VURT_API_TOKEN`

### Capabilities
- Read/write boards, lists, cards
- Move cards between lists
- Add labels, checklists, due dates
- Webhooks for automation
- Currently used for: content pipeline triage

---

## 10. Adobe (Creative Cloud)

**Keys:** `VURT_ADOBE_CLIENT_ID`, `VURT_ADOBE_CLIENT_SECRET`

### Capabilities
- Frame.io access (see #3 above)
- Potentially: Adobe Express API, Firefly (AI image gen)
- Untested: Creative Cloud asset access

---

## 11. Google AI (Gemini)

**Key:** `GOOGLE_AI_API_KEY`

### Capabilities
- Gemini API access for AI text/vision tasks
- Could be used for: auto-captioning, content analysis, thumbnail evaluation

---

## Cross-API Opportunities

### Currently Built
1. **Post Log Sync** — IG + FB + YT metrics → Notion (every 6 hours)
2. **Frame.io Inventory** — Full asset crawl with metadata
3. **NPAW Dashboard** — Platform viewing data

### Ready to Build (APIs confirmed working)
1. **Frame.io → Content Calendar** — Auto-populate calendar entries with asset links + view URLs when clips are ready
2. **NPAW + IG/YT → Title Intelligence** — Cross-reference platform views with social engagement per title
3. **GA4 + NPAW → Funnel Analysis** — Track social click → site visit → app open → video play
4. **Google Sheets → Notion** — Production tracker "green" status triggers content calendar entries
5. **Mux thumbnails → Notion** — Generate thumbnail images from Mux video timestamps

### Needs User Action
1. **YouTube Analytics API** — Enable in GCP console (1 click)
2. **Frame.io write access** — Need v2 developer token or upgraded Adobe OAuth scopes
3. **Meta Ads API** — Need `ads_read` scope (token upgrade via Meta Business Suite)
4. **Mux Data add-on** — Check with Enveu if enabled (for viewer-level analytics on platform)
5. **GA4 Consent Mode fix** — Enveu dev team needs to update consent defaults

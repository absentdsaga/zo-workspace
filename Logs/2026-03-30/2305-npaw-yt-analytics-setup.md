# NPAW + YouTube Analytics Setup Log
**Date:** 2026-03-30 ~23:05 ET

## NPAW Skill Built
- **Location:** Skills/vurt-npaw/scripts/npaw.py
- **Auth:** HMAC MD5 signing (path + query + secret + dateToken)
- **API:** api.youbora.com rawdata endpoint — gives session-level data
- **Tested:** Successfully pulled 40 sessions from last 7 days
- **Commands:** --top-content, --devices, --geo, --quality, --concurrent, --raw-sessions, --title-detail, --all

### Key Findings from NPAW (7-day snapshot):
- 40 total sessions
- Top titles: Come Back Dad (16 plays), Girl In The Closet (9), Karma In Heels (trailer+eps)
- 100% smartphone traffic (Samsung 47%, Huawei 22%, Apple 15%)
- 85% Android, 15% iOS
- US 37%, Tanzania 20%, South Africa 15%, Nigeria 10%
- Top cities: Dar es Salaam, Tacoma, Johannesburg, Atlanta
- 9.3/10 average happiness score
- 0 error sessions

## YouTube Analytics OAuth
- **Setup script:** Skills/vurt-post-log/scripts/yt-oauth-setup.py
- **Analytics script:** Skills/vurt-post-log/scripts/yt-analytics.py
- **OAuth:** access_type=offline, prompt=consent (forces long-lasting refresh token)
- **Status:** URL generated, waiting for user to authorize
- **Scopes:** yt-analytics.readonly, youtube.readonly
- **Features:** retention curves, traffic sources, demographics, top videos, geography

## User Feedback Applied
- Stop asking for API keys that are already in env — check first
- Spreadsheet (Google Sheets) is source of truth for edit readiness (green=ready)
- No auto-posting from Trello — human decides scheduling
- UTM tags already covered by pixel tracking plan + Enveu webdev team
- Frame.io: user needs to invite dioni.vasqu@gmail.com as collaborator

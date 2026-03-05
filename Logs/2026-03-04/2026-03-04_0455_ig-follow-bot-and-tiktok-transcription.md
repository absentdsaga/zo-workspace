# Task: Build IG Follow Bot + TikTok Transcription

**Date**: 2026-03-04 04:55 UTC  
**Objective**: Two tasks — (1) Add TikTok audio transcription to sentiment scanner, (2) Build Instagram follow automation skill

## Actions Taken

### 1. TikTok Transcription
- Explored sentiment-scanner project structure
- Found `transcribe_tiktok.py` already exists with yt-dlp + faster-whisper pipeline
- `scan_tiktok.py` already has `--transcribe` flag that invokes it
- **Status**: Already complete, no changes needed

### 2. IG Follow Bot
- Researched current IG automation landscape (instagrapi, rate limits, anti-detection)
- Installed `instagrapi` 2.3.0
- Created skill at `Skills/ig-follow-bot/`
- Built `scripts/follow.py` with:
  - Follower-of-target and hashtag-based targeting
  - 50/day hard cap with ±15% daily jitter
  - 45-120s randomized delays between follows
  - 15% profile-view-only actions (looks human)
  - Session persistence via `session.json`
  - Target quality filters (min posts, max followers, bot detection)
  - Rate limit detection and graceful backoff
  - Full JSONL logging + state tracking
  - Dry-run mode for previewing
- Verified: syntax OK, imports OK, --status and --help working

## Files Created/Modified
- `Skills/ig-follow-bot/SKILL.md` (new)
- `Skills/ig-follow-bot/scripts/follow.py` (new)
- `Skills/ig-follow-bot/data/` (new directory)

## Setup Required
- User must set `IG_USERNAME` and `IG_PASSWORD` in Settings > Advanced

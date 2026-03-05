# Sentiment Scanner Updates — TikTok Transcripts + IG Follow Bot

**Date:** 2026-03-04 ~04:45 UTC  
**Task:** Add TikTok video transcription + build IG follow automation

## Changes Made

### 1. TikTok Transcript Extraction (`transcribe_tiktok.py`)
- **New file:** `Skills/sentiment-scanner/scripts/transcribe_tiktok.py`
- Two-phase approach:
  - Phase 1: Extract existing auto-captions via `yt-dlp --write-subs` (free, ~1-2s/video)
  - Phase 2: Download audio + transcribe with `faster-whisper` base model on CPU (fallback for uncaptioned videos)
- Supports single URL, batch file, and `--from-scan` mode (processes top N from latest scan)
- Outputs to `data/transcripts/transcripts_YYYYMMDD_HHMMSS.json`
- Installed dependencies: `yt-dlp`, `faster-whisper`, `webvtt-py`

### 2. TikTok Scanner Updates (`scan_tiktok.py`)
- Added `video_url` and `video_id` fields to processed video output
- Added `--transcribe` flag: runs transcription on top 10 crypto-relevant videos after scanning
- Saves transcribed scan data separately

### 3. Aggregator Updates (`aggregate.py`)
- `extract_topics_from_tiktok()` now parses transcript text alongside captions
- Extracts $TOKEN mentions and topic keywords from both caption + transcript
- Cross-platform signal scoring now includes TikTok spoken content

### 4. IG Follow Bot (`ig_follow_bot.py`)
- **New file:** `Skills/sentiment-scanner/scripts/ig_follow_bot.py`
- Full growth automation for @loveofflinedating
- Features:
  - 14 seed accounts across 3 tiers (direct competitors, dating coaches, adjacent niches)
  - 11 target hashtags (#offlinedating, #deletedatingapps, etc.)
  - Progressive warm-up: 10/day → 20 → 35 → 50 over 4 weeks
  - Engage-then-follow protocol (like before following)
  - Unfollow non-followers after 4 days
  - State tracking in `data/ig/follow_state.json`
  - Action logging in `data/ig/follow_log.jsonl`
- Designed as plan generator for Zo scheduled agent (agent uses browser tools to execute)

### 5. Scheduled Agent Created
- Runs 3x daily: 10am, 2pm, 8pm ET
- Uses Sonnet 4.5 model
- Executes follow plan via Zo's browser (IG already logged in)
- Records results back to state file

## Files Created/Modified
- Created: `scripts/transcribe_tiktok.py`
- Created: `scripts/ig_follow_bot.py`
- Modified: `scripts/scan_tiktok.py` (video URL + transcribe flag)
- Modified: `scripts/aggregate.py` (transcript-aware topic extraction)

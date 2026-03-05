---
name: ig-follow-bot
description: Instagram follow automation bot. Follows users from target account follower lists with human-like behavior, rate limiting (max 50/day), and anti-detection measures. Uses instagrapi with session persistence and randomized delays.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: "1.0.0"
  created: "2026-03-04"
---

# IG Follow Bot

Automated Instagram follower growth via targeted follows. Finds followers of competitor/similar accounts and follows them with human-like timing patterns.

## Setup

1. Add IG credentials to [Settings > Advanced](/?t=settings&s=advanced):
   - `IG_USERNAME` — Instagram username (e.g. `loveofflinedating`)
   - `IG_PASSWORD` — Instagram password

2. First run will create a session file at `Skills/ig-follow-bot/session.json` — this persists login state to avoid re-auth.

## Usage

```bash
# Follow users from a target account's followers
python3 Skills/ig-follow-bot/scripts/follow.py --target <username> --count 50

# Follow from multiple target accounts
python3 Skills/ig-follow-bot/scripts/follow.py --targets <user1> <user2> <user3> --count 50

# Follow users posting with specific hashtags
python3 Skills/ig-follow-bot/scripts/follow.py --hashtags <tag1> <tag2> --count 50

# Check status / history
python3 Skills/ig-follow-bot/scripts/follow.py --status

# Dry run (no actual follows, just shows who would be followed)
python3 Skills/ig-follow-bot/scripts/follow.py --target <username> --count 10 --dry-run
```

## Safety

- **Max 50 follows/day** hard cap (configurable via `--max-daily`)
- **Randomized delays**: 45-120s between follows
- **Session-based batching**: Runs in 2-3 sessions with 3-4h gaps
- **Mixed actions**: Occasional profile views without follows to look human
- **Daily jitter**: Actual count varies ±15% from target
- **Skip filters**: Skips private accounts with 0 posts, accounts with 50k+ followers, and bot-looking accounts
- **Persistent session**: Reuses auth token — no repeated logins

## Logs

All follow activity is logged to `Skills/ig-follow-bot/data/follow_log.jsonl` with timestamps, usernames, and status.

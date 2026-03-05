#!/usr/bin/env python3
"""Instagram follow automation with human-like behavior patterns.

Usage:
  python3 follow.py --target <username> --count 50
  python3 follow.py --targets <user1> <user2> --count 50
  python3 follow.py --hashtags <tag1> <tag2> --count 50
  python3 follow.py --status
  python3 follow.py --target <username> --count 10 --dry-run
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, ChallengeRequired, FeedbackRequired,
    PleaseWaitFewMinutes, ClientError
)

SKILL_DIR = Path(__file__).resolve().parent.parent
SESSION_FILE = SKILL_DIR / "session.json"
LOG_FILE = SKILL_DIR / "data" / "follow_log.jsonl"
STATE_FILE = SKILL_DIR / "data" / "state.json"
DATA_DIR = SKILL_DIR / "data"

DEFAULT_MAX_DAILY = 50
MIN_DELAY = 45
MAX_DELAY = 120
PROFILE_VIEW_CHANCE = 0.15  # 15% chance of viewing profile without following

# Filters for target quality
MIN_POSTS = 1
MAX_FOLLOWERS = 50000
MIN_FOLLOWERS = 5
MAX_FOLLOWING_RATIO = 10  # following/followers ratio — skip likely bots


def get_client() -> Client:
    cl = Client()
    cl.delay_range = [1, 3]

    username = os.environ.get("IG_USERNAME")
    password = os.environ.get("IG_PASSWORD")

    if not username or not password:
        print("ERROR: Set IG_USERNAME and IG_PASSWORD in Settings > Advanced")
        sys.exit(1)

    if SESSION_FILE.exists():
        try:
            cl.load_settings(str(SESSION_FILE))
            cl.login(username, password)
            cl.get_timeline_feed()  # verify session is alive
            print(f"Logged in as @{username} (existing session)")
            return cl
        except Exception as e:
            print(f"Session expired, re-authenticating: {e}")

    try:
        cl.login(username, password)
        cl.dump_settings(str(SESSION_FILE))
        print(f"Logged in as @{username} (new session)")
    except ChallengeRequired:
        print("ERROR: Instagram requires challenge verification.")
        print("Log into Instagram on a real device, complete the challenge, then retry.")
        sys.exit(1)
    except Exception as e:
        print(f"Login failed: {e}")
        sys.exit(1)

    return cl


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"followed_ids": [], "daily_counts": {}, "last_run": None}


def save_state(state: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def log_action(action: str, username: str, user_id: str, details: dict = None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "username": username,
        "user_id": str(user_id),
    }
    if details:
        entry.update(details)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_today_count(state: dict) -> int:
    return state.get("daily_counts", {}).get(get_today_key(), 0)


def is_good_target(cl: Client, user_id: str, state: dict) -> bool:
    if str(user_id) in [str(uid) for uid in state.get("followed_ids", [])]:
        return False  # already followed

    try:
        info = cl.user_info(user_id)
    except Exception:
        return False

    if info.media_count < MIN_POSTS:
        return False
    if info.follower_count > MAX_FOLLOWERS:
        return False
    if info.follower_count < MIN_FOLLOWERS:
        return False
    if info.follower_count > 0 and info.following_count / info.follower_count > MAX_FOLLOWING_RATIO:
        return False

    return True


def human_delay():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"  Waiting {delay:.0f}s...")
    time.sleep(delay)


def get_followers_of(cl: Client, target_username: str, amount: int = 200) -> list:
    try:
        user_id = cl.user_id_from_username(target_username)
        followers = cl.user_followers(user_id, amount=amount)
        return list(followers.keys())
    except Exception as e:
        print(f"ERROR: Could not fetch followers of @{target_username}: {e}")
        return []


def get_hashtag_users(cl: Client, hashtag: str, amount: int = 50) -> list:
    try:
        medias = cl.hashtag_medias_recent(hashtag, amount=amount)
        user_ids = list(set(m.user.pk for m in medias))
        return user_ids
    except Exception as e:
        print(f"ERROR: Could not fetch hashtag #{hashtag}: {e}")
        return []


def follow_users(cl: Client, user_ids: list, max_count: int, dry_run: bool = False):
    state = load_state()
    today = get_today_key()
    today_count = get_today_count(state)
    max_daily = DEFAULT_MAX_DAILY

    # Apply jitter: ±15%
    jitter = random.uniform(-0.15, 0.15)
    effective_max = min(int(max_count * (1 + jitter)), max_daily - today_count)

    if effective_max <= 0:
        print(f"Daily limit reached ({today_count}/{max_daily} today). Try again tomorrow.")
        return

    print(f"\nTarget: {effective_max} follows (jittered from {max_count}, {today_count} done today)")

    random.shuffle(user_ids)  # don't follow sequentially
    followed = 0

    for user_id in user_ids:
        if followed >= effective_max:
            break

        # Occasional profile view without follow (looks human)
        if random.random() < PROFILE_VIEW_CHANCE:
            try:
                info = cl.user_info(user_id)
                print(f"  [view] @{info.username} (no follow, just browsing)")
                log_action("profile_view", info.username, user_id)
                time.sleep(random.uniform(5, 15))
            except Exception:
                pass
            continue

        if not is_good_target(cl, user_id, state):
            continue

        try:
            info = cl.user_info(user_id)
            username = info.username
        except Exception:
            continue

        if dry_run:
            print(f"  [dry-run] Would follow @{username} "
                  f"({info.follower_count} followers, {info.media_count} posts)")
            followed += 1
            continue

        try:
            cl.user_follow(user_id)
            followed += 1
            today_count += 1

            state.setdefault("followed_ids", []).append(str(user_id))
            state.setdefault("daily_counts", {})[today] = today_count
            state["last_run"] = datetime.now(timezone.utc).isoformat()
            save_state(state)

            log_action("follow", username, user_id, {
                "follower_count": info.follower_count,
                "following_count": info.following_count,
                "media_count": info.media_count,
                "daily_total": today_count,
            })

            print(f"  [{followed}/{effective_max}] Followed @{username} "
                  f"({info.follower_count} followers)")

            human_delay()

        except PleaseWaitFewMinutes:
            print("  ⚠ Rate limited — pausing 10 minutes")
            log_action("rate_limited", username, user_id)
            time.sleep(600)
        except FeedbackRequired as e:
            print(f"  ⚠ Action blocked: {e}")
            log_action("action_blocked", username, user_id, {"error": str(e)})
            print("  Stopping to avoid further blocks. Try again in 24h.")
            break
        except Exception as e:
            print(f"  Error following @{username}: {e}")
            log_action("error", username, user_id, {"error": str(e)})

    print(f"\nDone: {followed} follows today ({today_count} total today)")


def show_status():
    state = load_state()
    today = get_today_key()
    today_count = get_today_count(state)
    total_followed = len(state.get("followed_ids", []))
    last_run = state.get("last_run", "never")

    print(f"IG Follow Bot Status")
    print(f"  Today: {today_count}/{DEFAULT_MAX_DAILY} follows")
    print(f"  Total ever followed: {total_followed}")
    print(f"  Last run: {last_run}")

    # Recent log entries
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text().strip().split("\n")
        recent = lines[-10:] if len(lines) >= 10 else lines
        print(f"\n  Last {len(recent)} actions:")
        for line in recent:
            entry = json.loads(line)
            ts = entry["timestamp"][:16]
            action = entry["action"]
            user = entry.get("username", "?")
            print(f"    {ts} | {action:15s} | @{user}")


def main():
    parser = argparse.ArgumentParser(description="IG follow automation")
    parser.add_argument("--target", help="Target account whose followers to follow")
    parser.add_argument("--targets", nargs="+", help="Multiple target accounts")
    parser.add_argument("--hashtags", nargs="+", help="Hashtags to find users from")
    parser.add_argument("--count", type=int, default=50, help="Number of follows (max 50)")
    parser.add_argument("--max-daily", type=int, default=50, help="Daily follow cap")
    parser.add_argument("--dry-run", action="store_true", help="Preview without following")
    parser.add_argument("--status", action="store_true", help="Show bot status")
    args = parser.parse_args()

    global DEFAULT_MAX_DAILY
    DEFAULT_MAX_DAILY = min(args.max_daily, 50)  # hard cap at 50

    if args.status:
        show_status()
        return

    if not args.target and not args.targets and not args.hashtags:
        parser.print_help()
        return

    cl = get_client()
    all_user_ids = []

    if args.target:
        print(f"\nFetching followers of @{args.target}...")
        ids = get_followers_of(cl, args.target)
        print(f"  Got {len(ids)} followers")
        all_user_ids.extend(ids)

    if args.targets:
        for t in args.targets:
            print(f"\nFetching followers of @{t}...")
            ids = get_followers_of(cl, t)
            print(f"  Got {len(ids)} followers")
            all_user_ids.extend(ids)

    if args.hashtags:
        for h in args.hashtags:
            print(f"\nFetching users from #{h}...")
            ids = get_hashtag_users(cl, h)
            print(f"  Got {len(ids)} users")
            all_user_ids.extend(ids)

    # Deduplicate
    all_user_ids = list(set(all_user_ids))
    print(f"\nTotal unique targets: {len(all_user_ids)}")

    follow_users(cl, all_user_ids, args.count, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Instagram follow automation for @loveofflinedating.

Uses Playwright with existing browser session for safe, human-like following.
Implements the full growth strategy: engage-then-follow, smart targeting,
proper spacing, warm-up, and unfollow management.

Usage:
  python3 ig_follow_bot.py follow --seed @masterofflinedating --count 15
  python3 ig_follow_bot.py follow --hashtag offlinedating --count 10
  python3 ig_follow_bot.py unfollow --count 20
  python3 ig_follow_bot.py status
  python3 ig_follow_bot.py run-daily    # Full daily cycle (used by scheduled agent)
"""

import json
import os
import sys
import random
import time
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_DIR = "/home/workspace/Skills/sentiment-scanner/data/ig"
STATE_FILE = os.path.join(DATA_DIR, "follow_state.json")
LOG_FILE = os.path.join(DATA_DIR, "follow_log.jsonl")

# === STRATEGY CONFIG ===
DAILY_FOLLOW_LIMIT = 50
DAILY_UNFOLLOW_LIMIT = 35
UNFOLLOW_AFTER_DAYS = 4
MIN_DELAY_BETWEEN_FOLLOWS = 120  # 2 min
MAX_DELAY_BETWEEN_FOLLOWS = 240  # 4 min
LIKE_BEFORE_FOLLOW = True
LIKES_PER_TARGET = 2

# Seed accounts — followers/likers of these accounts are our targets
SEED_ACCOUNTS = {
    "tier1_direct_competitors": [
        "masterofflinedating",   # Camille Virginia — #1 offline dating coach
        "dating.intentionally",  # Intentional dating advice, 196K
        "alittlenudge",          # Erika Ettin — dating coach
        "damonahoffman",         # Damona Hoffman — certified dating coach
    ],
    "tier2_dating_coaches": [
        "datingbyblaine",        # Blaine Anderson — matchmaker, 697K
        "datingwithgracie",      # Dating advice, 519K
        "sweet2elite",           # High-value dating for women 30+
        "realevanmarckatz",      # Evan Marc Katz — 31K, very engaged
        "apollonia_ponti",       # Relationship coach for men
        "kelseywonderlin",       # Secure love, 176K
    ],
    "tier3_adjacent": [
        "theartofcharm",         # Social dynamics, 41K
        "canadasdatingcoach",    # Chantal Heide, 174K
        "elsamoreck",            # Confidence in dating, 246K
        "jamiedate",             # Self-improvement for dating, 160K
    ],
}

TARGET_HASHTAGS = [
    "offlinedating", "deletedatingapps", "datingoffline",
    "datingadvice", "datingcoach", "relationshipadvice",
    "datingtips", "singleslife", "datingover30",
    "meetpeopleinreallife", "slowdating",
]

# === STATE MANAGEMENT ===

def load_state() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "followed": {},       # username -> {followed_at, source, followed_back}
        "unfollowed": {},     # username -> {unfollowed_at}
        "daily_counts": {},   # date -> {follows, unfollows, likes}
        "total_follows": 0,
        "total_unfollows": 0,
        "warm_up_day": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def save_state(state: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def log_action(action: str, data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **data,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_daily_count(state: dict, action: str) -> int:
    today = get_today_key()
    return state.get("daily_counts", {}).get(today, {}).get(action, 0)


def increment_daily_count(state: dict, action: str):
    today = get_today_key()
    if today not in state["daily_counts"]:
        state["daily_counts"][today] = {"follows": 0, "unfollows": 0, "likes": 0}
    state["daily_counts"][today][action] = state["daily_counts"][today].get(action, 0) + 1


def get_warm_up_limit(state: dict) -> int:
    """Progressive warm-up: increase daily limit over first 4 weeks."""
    days_active = len(state.get("daily_counts", {}))
    if days_active < 7:
        return 10
    elif days_active < 14:
        return 20
    elif days_active < 21:
        return 35
    return DAILY_FOLLOW_LIMIT


def get_accounts_to_unfollow(state: dict) -> list[str]:
    """Find accounts that didn't follow back after UNFOLLOW_AFTER_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=UNFOLLOW_AFTER_DAYS)
    to_unfollow = []
    for username, data in state.get("followed", {}).items():
        if username in state.get("unfollowed", {}):
            continue
        if data.get("followed_back"):
            continue
        followed_at = datetime.fromisoformat(data["followed_at"])
        if followed_at < cutoff:
            to_unfollow.append(username)
    return to_unfollow


# === ACTION PLANNING ===
# This bot is designed to be called by a Zo scheduled agent.
# It generates action plans that the agent executes using Zo's browser tools.

def plan_daily_actions(state: dict) -> dict:
    """Generate the action plan for today's follow/unfollow cycle."""
    today = get_today_key()
    follows_today = get_daily_count(state, "follows")
    unfollows_today = get_daily_count(state, "unfollows")
    follow_limit = get_warm_up_limit(state)
    remaining_follows = max(0, follow_limit - follows_today)
    remaining_unfollows = max(0, DAILY_UNFOLLOW_LIMIT - unfollows_today)

    plan = {
        "date": today,
        "warm_up_day": len(state.get("daily_counts", {})) + 1,
        "follow_limit": follow_limit,
        "follows_remaining": remaining_follows,
        "unfollows_remaining": remaining_unfollows,
        "follow_actions": [],
        "unfollow_targets": [],
        "already_followed": list(state.get("followed", {}).keys()),
    }

    if remaining_follows > 0:
        seed_follows = int(remaining_follows * 0.5)
        hashtag_follows = remaining_follows - seed_follows

        all_seeds = []
        for tier, accounts in SEED_ACCOUNTS.items():
            all_seeds.extend(accounts)
        selected_seeds = random.sample(all_seeds, min(3, len(all_seeds)))
        per_seed = max(1, seed_follows // len(selected_seeds))

        for seed in selected_seeds:
            plan["follow_actions"].append({
                "type": "follow_from_seed",
                "seed_account": seed,
                "count": per_seed,
                "instruction": f"Go to https://www.instagram.com/{seed}/followers/. Scroll the followers dialog to load more. For each user shown that has a 'Follow' button (not 'Following'), like 1-2 of their recent posts, then follow them. Do {per_seed} follows, waiting 2-4 minutes between each. Skip accounts with 10K+ followers or no posts.",
            })

        selected_hashtags = random.sample(TARGET_HASHTAGS, min(2, len(TARGET_HASHTAGS)))
        per_hashtag = max(1, hashtag_follows // len(selected_hashtags))

        for tag in selected_hashtags:
            plan["follow_actions"].append({
                "type": "follow_from_hashtag",
                "hashtag": tag,
                "count": per_hashtag,
                "instruction": f"Go to https://www.instagram.com/explore/tags/{tag}/. Click on recent posts. For each post, like it, then visit the creator's profile. If they have under 10K followers and posted in the last 7 days, follow them. Do {per_hashtag} follows, waiting 2-4 minutes between each.",
            })

    # Unfollow targets
    to_unfollow = get_accounts_to_unfollow(state)
    if to_unfollow and remaining_unfollows > 0:
        batch = to_unfollow[:remaining_unfollows]
        plan["unfollow_targets"] = batch
        plan["unfollow_instruction"] = f"For each username in the unfollow list, go to their profile, click 'Following', then click 'Unfollow'. Wait 60-120 seconds between each. Unfollow these {len(batch)} accounts: {', '.join(batch[:10])}{'...' if len(batch) > 10 else ''}"

    return plan


def record_follows(usernames: list[str], source: str):
    """Record successful follows to state."""
    state = load_state()
    for username in usernames:
        state.setdefault("followed", {})[username] = {
            "followed_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "followed_back": False,
        }
        increment_daily_count(state, "follows")
        log_action("follow", {"username": username, "source": source, "success": True})
    save_state(state)
    print(f"Recorded {len(usernames)} follows from {source}")


def record_unfollows(usernames: list[str]):
    """Record successful unfollows to state."""
    state = load_state()
    for username in usernames:
        state.setdefault("unfollowed", {})[username] = {
            "unfollowed_at": datetime.now(timezone.utc).isoformat(),
        }
        increment_daily_count(state, "unfollows")
        log_action("unfollow", {"username": username, "success": True})
    save_state(state)
    print(f"Recorded {len(usernames)} unfollows")


# === DAILY CYCLE ===

def run_daily_cycle():
    """Generate and print the daily action plan for the Zo agent."""
    state = load_state()
    plan = plan_daily_actions(state)

    print(f"=== IG Follow Bot — {plan['date']} ===")
    print(f"Warm-up day: {plan['warm_up_day']}")
    print(f"Daily follow limit: {plan['follow_limit']}")
    print(f"Follows remaining: {plan['follows_remaining']}")
    print(f"Active following: {len(state.get('followed', {})) - len(state.get('unfollowed', {}))}")
    print(f"Pending unfollows: {len(plan['unfollow_targets'])}")

    if plan["follow_actions"]:
        print(f"\n--- Follow Plan ---")
        for action in plan["follow_actions"]:
            print(f"  {action['type']}: {action.get('seed_account', action.get('hashtag', '?'))} x{action['count']}")

    if plan["unfollow_targets"]:
        print(f"\n--- Unfollow Plan ---")
        print(f"  {len(plan['unfollow_targets'])} accounts to unfollow")

    # Output machine-readable plan
    plan_file = os.path.join(DATA_DIR, f"plan_{plan['date']}.json")
    with open(plan_file, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"\nPlan saved to {plan_file}")

    # Also output as JSON for agent consumption
    print(f"\n=== PLAN_JSON ===")
    print(json.dumps(plan, indent=2))

    return plan


def show_status():
    state = load_state()
    today = get_today_key()
    follow_limit = get_warm_up_limit(state)

    active_following = len(state.get("followed", {})) - len(state.get("unfollowed", {}))
    days_active = len(state.get("daily_counts", {}))

    print(f"=== @loveofflinedating Follow Bot Status ===")
    print(f"Days active: {days_active}")
    print(f"Current warm-up limit: {follow_limit}/day")
    print(f"Total followed: {len(state.get('followed', {}))}")
    print(f"Total unfollowed: {len(state.get('unfollowed', {}))}")
    print(f"Active following: {active_following}")
    print(f"Today's follows: {get_daily_count(state, 'follows')}")
    print(f"Today's unfollows: {get_daily_count(state, 'unfollows')}")
    print(f"Pending unfollows: {len(get_accounts_to_unfollow(state))}")

    # Recent daily stats
    print(f"\n--- Last 7 Days ---")
    for i in range(7):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        counts = state.get("daily_counts", {}).get(day, {})
        if counts:
            print(f"  {day}: {counts.get('follows', 0)} follows, "
                  f"{counts.get('unfollows', 0)} unfollows, "
                  f"{counts.get('likes', 0)} likes")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "run-daily":
        run_daily_cycle()
    elif cmd == "status":
        show_status()
    elif cmd == "record-follows":
        # Called by agent after completing follows
        # Usage: record-follows <source> <username1> <username2> ...
        source = sys.argv[2]
        usernames = sys.argv[3:]
        record_follows(usernames, source)
    elif cmd == "record-unfollows":
        # Called by agent after completing unfollows
        # Usage: record-unfollows <username1> <username2> ...
        usernames = sys.argv[2:]
        record_unfollows(usernames)
    else:
        print(__doc__)

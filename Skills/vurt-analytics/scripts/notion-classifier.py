#!/usr/bin/env python3
"""
VURT Post Classifier — Notion Auto-Tagger
Reads VURT Content Tracker from Notion, classifies each post at 72hr mark.

Run: python3 notion-classifier.py
Schedule: Daily (or after each posting day)
Requires: NOTION_API_KEY, VURT_NOTION_DATABASE_ID in environment

Classification thresholds (per platform):
  TikTok:   Winner >50K | Solid 10K-50K | Under <10K
  IG Reels: Winner >5K  | Solid 1K-5K  | Under <1K
  YT Shorts: Winner >10K | Solid 2K-10K | Under <2K
  FB Reels: Winner >2K  | Solid 500-2K | Under <500

Output: Updates Classification field in Notion for each post.
"""

import os
import requests
import time
from datetime import datetime, timedelta

NOTION_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("VURT_NOTION_DATABASE_ID", "c592ce58-b453-436f-b8e0-4510b2dcb412")

HEADERS = {
    "Authorization": f"Bearer {NOTION_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Thresholds by platform (views at 72hr = classification)
THRESHOLDS = {
    "TikTok":        {"winner": 50_000, "solid": 10_000},
    "Instagram":     {"winner": 5_000,  "solid": 1_000},
    "YouTube":       {"winner": 10_000, "solid": 2_000},
    "Facebook":      {"winner": 2_000,  "solid": 500},
}

def classify(platform, views):
    t = THRESHOLDS.get(platform, {"winner": 5_000, "solid": 1_000})
    if views is None:
        return "Unclassified"
    if views >= t["winner"]:
        return "Winner"
    if views >= t["solid"]:
        return "Solid"
    return "Underperformer"

def get_posts():
    """Query all pages in the database."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": 100}
    all_pages = []
    while True:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        all_pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data.get("next_cursor")
        time.sleep(0.5)
    return all_pages

def update_classification(page_id, classification):
    """Update the Classification select field on a Notion page."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Classification": {
                "select": {"name": classification}
            }
        }
    }
    resp = requests.patch(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()

def should_classify(post):
    """Only classify posts older than 72 hours with no existing Classification."""
    props = post.get("properties", {})

    # Check if already classified
    class_prop = props.get("Classification", {})
    if class_prop.get("select") and class_prop["select"].get("name") not in (None, ""):
        return False

    # Check date posted
    date_prop = props.get("Date Posted", {})
    date_val = date_prop.get("date")
    if not date_val or not date_val.get("start"):
        return False

    posted = datetime.fromisoformat(date_val["start"].replace("Z", "+00:00"))
    cutoff = datetime.now(posted.tzinfo) - timedelta(hours=72)
    return posted < cutoff

def get_views(post):
    props = post.get("properties", {})
    views = props.get("Views", {}).get("number")
    return views or 0

def get_platform(post):
    props = post.get("properties", {})
    plat = props.get("Platform", {}).get("select", {}).get("name", "Instagram")
    return plat

def get_title(post):
    props = post.get("properties", {})
    title = props.get("Post Title", {})
    name = title.get("title", [{}])[0].get("plain_text", "")
    return name or "Untitled"

def main():
    if not NOTION_KEY:
        print("ERROR: NOTION_API_KEY not set")
        return

    print(f"Fetching posts from Notion database...")
    posts = get_posts()
    to_classify = [p for p in posts if should_classify(p)]

    print(f"Found {len(posts)} total posts, {len(to_classify)} ready for classification")

    for post in to_classify:
        page_id = post["id"]
        views = get_views(post)
        platform = get_platform(post)
        title = get_title(post)
        classification = classify(platform, views)

        try:
            update_classification(page_id, classification)
            print(f"  [{classification}] {title} ({platform}) — {views:,} views")
        except Exception as e:
            print(f"  [ERROR] {title}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()

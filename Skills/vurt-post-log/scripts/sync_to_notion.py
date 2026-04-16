#!/usr/bin/env python3
"""
VURT Post Log → Notion Sync
Pulls data from the Google Sheets Post Log and syncs to Notion Content Tracker.
Run daily via cron: python3 sync_to_notion.py
"""

import os
import json
import requests
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────────────────────
NOTION_TOKEN = os.environ.get("VURT_NOTION_API_KEY")
NOTION_DATABASE_ID = "c592ce58-b453-436f-b1ab-0bf3d091b5a3"  # Content Tracker
SHEET_ID = "1WK2-Otebg2LMHkV9ysqKOo8WFEruOg61dJFc-oy-WF0"  # Production Tracker
SHEET_TAB = "Post Log"

# ─── Notion API helpers ────────────────────────────────────────────────────────
NOTION_HEADERS = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}

def notion_search(database_id, title_filter):
    """Find existing Notion page by title (platform + date + clip name)."""
    query = {
        "database_id": database_id,
        "filter": {
            "property": "Name",
            "title": {"contains": title_filter}
        }
    }
    r = requests.post("https://api.notion.com/v1/databases/query", headers=NOTION_HEADERS, json=query)
    r.raise_for_status()
    results = r.json().get("results", [])
    return results[0]["id"] if results else None

def notion_patch(page_id, properties):
    """Update an existing Notion page with new metrics."""
    payload = {"properties": properties}
    r = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=NOTION_HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

def notion_create(properties):
    """Create a new Notion page in the Content Tracker."""
    payload = {"parent": {"database_id": NOTION_DATABASE_ID}, "properties": properties}
    r = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

def parse_sheet():
    """Fetch Post Log from Google Sheets as CSV."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    r = requests.get(url)
    r.raise_for_status()
    lines = r.text.strip().split("\n")
    headers = lines[0].split(",")
    rows = []
    for line in lines[1:]:
        cols = line.split(",")
        row = dict(zip(headers, cols))
        rows.append(row)
    return rows

def get_views_tiktok(video_url):
    """Placeholder — use TikTok API or Phantombuster to get actual views."""
    return 0

def get_views_yt(video_url):
    """Use YouTube Data API to get view count from video URL."""
    import os
    import requests
    api_key = os.environ.get("VURT_YOUTUBE_REFRESH_TOKEN", "")  # token, not key
    # Would need to exchange refresh token for access token first
    return 0

def build_notion_properties(row):
    """Map a sheet row to Notion page properties."""
    return {
        "Name": {"title": [{"text": {"content": row.get("Clip Title", "Untitled")}}]},
        "Platform": {"select": {"name": row.get("Platform", "Unknown")}},
        "Date Posted": {"date": {"start": row.get("Date", datetime.today().strftime("%Y-%m-%d"))}},
        "Views": {"number": int(row.get("Views", 0) or 0)},
        "Likes": {"number": int(row.get("Likes", 0) or 0)},
        "Shares": {"number": int(row.get("Shares", 0) or 0)},
        "Reach": {"number": int(row.get("Reach", 0) or 0)},
        "Engagement Rate": {"formula": {"formula": f"({row.get('Likes',0)} + {row.get('Shares',0)}) / {row.get('Views',1) or 1}"}},
        "Notes": {"rich_text": [{"text": {"content": row.get("Notes", "")}}]},
    }

def main():
    print(f"[{datetime.now().isoformat()}] Starting Notion sync...")
    rows = parse_sheet()
    synced = 0
    for row in rows:
        title_filter = f"{row.get('Platform','')} {row.get('Clip Title','')} {row.get('Date','')}"
        existing = notion_search(NOTION_DATABASE_ID, row.get("Clip Title",""))
        props = build_notion_properties(row)
        if existing:
            notion_patch(existing, props)
            print(f"  Updated: {row.get('Clip Title')}")
        else:
            notion_create(props)
            print(f"  Created: {row.get('Clip Title')}")
        synced += 1
    print(f"Done. {synced} rows synced.")

if __name__ == "__main__":
    main()
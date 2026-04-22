#!/usr/bin/env python3 -u
"""TikTok-only Notion Post Log sync.

Pulls every entry where Platform = TikTok and a Post URL is set, scrapes
the public TikTok page for current views/likes/comments/shares/saves, and
writes them back to Notion. Useful when the full sync.py run is too slow
or when only TikTok needs refreshing.
"""

import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tiktok_scraper import scrape_video  # noqa: E402

NOTION_DB_ID = "c592ce58-b453-436f-b8e0-4510b2dcb412"
NOTION_BASE = "https://api.notion.com/v1"


def _notion(method, path, body=None):
    token = os.environ["VURT_NOTION_API_KEY"]
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{NOTION_BASE}/{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
    )
    return json.loads(urllib.request.urlopen(req).read())


def fetch_tiktok_entries():
    out = []
    payload = {"page_size": 100}
    while True:
        data = _notion("POST", f"databases/{NOTION_DB_ID}/query", payload)
        for p in data.get("results", []):
            props = p["properties"]
            plat = (props.get("Platform", {}).get("select") or {}).get("name", "")
            if plat != "TikTok":
                continue
            url = props.get("Post URL", {}).get("url") or ""
            title_parts = props.get("Post Title", {}).get("title", [])
            title = title_parts[0]["plain_text"] if title_parts else ""
            cap_parts = props.get("Caption", {}).get("rich_text", [])
            caption = cap_parts[0]["plain_text"] if cap_parts else ""
            out.append({"id": p["id"], "title": title, "url": url, "caption": caption})
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return out


def main(dry_run: bool):
    entries = fetch_tiktok_entries()
    has_url = [e for e in entries if e["url"] and "tiktok.com" in e["url"]]
    no_url = [e for e in entries if not e["url"]]
    print(f"TikTok entries: {len(entries)} total, {len(has_url)} scrapeable, {len(no_url)} missing URL")
    if no_url:
        print("Missing URLs (need manual entry):")
        for e in no_url:
            print(f"  - {e['title']}")

    updated = 0
    for i, e in enumerate(has_url):
        if i:
            time.sleep(1.5)
        data = scrape_video(e["url"])
        if not data:
            print(f"  [skip] {e['title']} — scrape failed")
            continue
        props = {
            "Views": {"number": data["views"]},
            "Likes": {"number": data["likes"]},
            "Comments Count": {"number": data["comments"]},
            "Shares": {"number": data["shares"]},
            "Saves": {"number": data["saves"]},
        }
        if data["caption"] and not e["caption"]:
            props["Caption"] = {"rich_text": [{"text": {"content": data["caption"][:2000]}}]}
        nums = ", ".join(f"{k}={v['number']}" for k, v in props.items() if isinstance(v, dict) and "number" in v)
        print(f"  [{'dry' if dry_run else 'live'}] {e['title']} → {nums}")
        if not dry_run:
            try:
                _notion("PATCH", f"pages/{e['id']}", {"properties": props})
                updated += 1
            except Exception as ex:
                print(f"    write failed: {ex}")
    print(f"\nDone. {updated} entries written.")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)

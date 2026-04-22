#!/usr/bin/env python3
"""Create bare Notion Post Log rows for newly-posted TikToks that don't yet have
BC screenshot data. Pulls from data/tiktok_user_url_scrape.json and only writes
URLs that aren't already in any TikTok row.
"""

import argparse
import json
import os
import sys
import time
import urllib.request

NOTION_DB = "c592ce58-b453-436f-b8e0-4510b2dcb412"
NOTION_BASE = "https://api.notion.com/v1"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SCRAPE_FILE = os.path.join(DATA_DIR, "tiktok_user_url_scrape.json")
BC_FILE = os.path.join(DATA_DIR, "tiktok_bc_screenshots.json")


def _notion(method, path, body=None):
    token = os.environ["VURT_NOTION_API_KEY"]
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{NOTION_BASE}/{path}",
        data=data, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
    )
    return json.loads(urllib.request.urlopen(req).read())


def fetch_existing_tiktok_urls():
    urls = set()
    payload = {"page_size": 100}
    while True:
        d = _notion("POST", f"databases/{NOTION_DB}/query", payload)
        for p in d.get("results", []):
            props = p["properties"]
            plat = (props.get("Platform", {}).get("select") or {}).get("name", "")
            if plat != "TikTok":
                continue
            url = props.get("Post URL", {}).get("url") or ""
            if url:
                urls.add(url)
        if not d.get("has_more"):
            break
        payload["start_cursor"] = d["next_cursor"]
    return urls


def infer_show_from_caption(caption: str) -> str:
    """Pull show name from caption — VURT uses '. <Show>. Streaming' or hashtag pattern."""
    c = caption or ""
    # Hashtag-based: #FavoriteSon, #BrideToBe, etc.
    known = {
        "favoriteson": "Favorite Son",
        "bridetobe": "Bride to Be",
        "loveandhiphop": "Love Network Jam",
        "lovenetworkjam": "Love Network Jam",
        "schemers": "Schemers",
        "theparkinglot": "The Parking Lot",
        "karmainheels": "Karma in Heels",
        "somethinglikeabusiness": "Something Like A Business",
        "35andticking": "35 & Ticking",
    }
    lc = c.lower()
    for tag, show in known.items():
        if "#" + tag in lc:
            return show
    return "Untitled"


def title_for(scraped):
    show = infer_show_from_caption(scraped["caption"])
    snippet = (scraped["caption"] or "")[:40].strip().strip('"').rstrip(".")
    return f"{show} - {snippet} - TikTok"


def build_props(scraped):
    from datetime import datetime, timezone
    posted = datetime.fromtimestamp(scraped["create_time"], tz=timezone.utc).strftime("%Y-%m-%d")
    return {
        "Platform": {"select": {"name": "TikTok"}},
        "Post Title": {"title": [{"text": {"content": title_for(scraped)}}]},
        "Caption": {"rich_text": [{"text": {"content": (scraped["caption"] or "")[:2000]}}]},
        "Post URL": {"url": scraped["url"]},
        "Date Posted": {"date": {"start": posted}},
        "Views": {"number": scraped["views"]},
        "Likes": {"number": scraped["likes"]},
        "Comments Count": {"number": scraped["comments"]},
        "Shares": {"number": scraped["shares"]},
        "Saves": {"number": scraped["saves"]},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    scraped = json.load(open(SCRAPE_FILE))
    bc = json.load(open(BC_FILE))
    bc_urls = {p.get("url") for p in bc["posts"] if p.get("url")}

    existing_urls = fetch_existing_tiktok_urls() if args.live else set()

    targets = []
    for s in scraped:
        if "error" in s:
            continue
        if s["url"] in bc_urls:
            continue  # already imported via BC pipeline
        if s["url"] in existing_urls:
            continue
        targets.append(s)

    print(f"New TikToks to create (not in BC, not in Notion): {len(targets)}")
    for s in targets:
        cap = s["caption"][:60].replace("\n", " ")
        print(f"  + {title_for(s)} | views={s['views']} url={s['url']}")
        print(f"      caption: {cap}")

    if not args.live:
        print("\n[dry-run] No writes.")
        return

    print("\nWriting...")
    for s in targets:
        try:
            _notion("POST", "pages", {
                "parent": {"database_id": NOTION_DB},
                "properties": build_props(s),
            })
            print(f"  created: {title_for(s)}")
            time.sleep(0.4)
        except Exception as e:
            print(f"  FAILED {s['url']}: {e}")


if __name__ == "__main__":
    main()

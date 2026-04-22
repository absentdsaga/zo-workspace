#!/usr/bin/env python3
"""Import TikTok metrics from Business Center screenshot data into Notion Post Log.

Reads /home/workspace/Skills/vurt-post-log/data/tiktok_bc_screenshots.json and
either updates existing TikTok entries (matched by caption) or creates new ones
mirroring the naming pattern used for IG/FB/YT entries.

Default is --dry-run. Pass --live to actually write.

Title pattern follows existing repo convention:
  "<Show> Clip <N> - TikTok"  when there's a clip number
  "<Show> Clip - TikTok"      otherwise
"""

import argparse
import json
import os
import sys
import urllib.request

NOTION_DB = "c592ce58-b453-436f-b8e0-4510b2dcb412"
NOTION_BASE = "https://api.notion.com/v1"
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tiktok_bc_screenshots.json")


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


def fetch_existing_tiktok():
    out = []
    payload = {"page_size": 100}
    while True:
        d = _notion("POST", f"databases/{NOTION_DB}/query", payload)
        for p in d.get("results", []):
            props = p["properties"]
            plat = (props.get("Platform", {}).get("select") or {}).get("name", "")
            if plat != "TikTok":
                continue
            title_p = props.get("Post Title", {}).get("title", [])
            cap_p = props.get("Caption", {}).get("rich_text", [])
            out.append({
                "id": p["id"],
                "title": title_p[0]["plain_text"] if title_p else "",
                "caption": cap_p[0]["plain_text"] if cap_p else "",
            })
        if not d.get("has_more"):
            break
        payload["start_cursor"] = d["next_cursor"]
    return out


def caption_match(post_caption, notion_caption, notion_title):
    """Loose match: first ~30 chars of post caption appear in either notion field."""
    if not post_caption:
        return False
    needle = post_caption[:30].lower().strip().strip('"')
    haystack = (notion_caption + " " + notion_title).lower()
    return needle in haystack


def find_match(post, existing):
    """Match by title first (exact), then by caption snippet."""
    proposed = title_for(post).lower().strip()
    for e in existing:
        if e["title"].lower().strip() == proposed:
            return e
    for e in existing:
        if caption_match(post["caption_snippet"], e["caption"], e["title"]):
            return e
    return None


def title_for(post):
    show = post.get("show", "Untitled")
    clip = post.get("clip")
    if clip:
        return f"{show} Clip {clip} - TikTok"
    # Use first ~40 chars of caption as disambiguator
    snippet = (post.get("caption_snippet") or "")[:40].strip().strip('"').rstrip(".")
    return f"{show} - {snippet} - TikTok"


def build_props(post, is_new):
    props = {
        "Platform": {"select": {"name": "TikTok"}},
        "Views": {"number": post["views"]},
        "Likes": {"number": post["likes"]},
        "Comments Count": {"number": post["comments"]},
        "Shares": {"number": post["shares"]},
        "Saves": {"number": post["saves"]},
    }
    if post.get("reach") is not None:
        props["Reach"] = {"number": post["reach"]}
    if post.get("avg_view_duration_s") is not None:
        props["Avg Watch Time (s)"] = {"number": post["avg_view_duration_s"]}
    if post.get("completion_rate_pct") is not None:
        props["Completion Rate"] = {"rich_text": [{"text": {"content": f"{post['completion_rate_pct']}%"}}]}
    if post.get("url"):
        props["Post URL"] = {"url": post["url"]}
    if is_new:
        props["Post Title"] = {"title": [{"text": {"content": title_for(post)}}]}
        if post.get("caption_snippet"):
            props["Caption"] = {"rich_text": [{"text": {"content": post["caption_snippet"][:2000]}}]}
        if post.get("last_updated"):
            props["Date Posted"] = {"date": {"start": post["last_updated"][:10]}}
    return props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="Actually write to Notion (default is dry-run)")
    args = ap.parse_args()
    dry = not args.live

    with open(DATA_FILE) as f:
        data = json.load(f)
    posts = data["posts"]
    existing = fetch_existing_tiktok()

    updates = []
    creates = []
    for post in posts:
        match = find_match(post, existing)
        if match:
            updates.append((match, post))
        else:
            creates.append(post)

    print(f"Screenshot posts: {len(posts)}")
    print(f"Existing TikTok rows in Notion: {len(existing)}")
    print(f"Will UPDATE: {len(updates)}")
    print(f"Will CREATE: {len(creates)}")
    print()

    print("=== UPDATES (matched by caption) ===")
    for match, post in updates:
        print(f"  [{match['title']}] ← views={post['views']} likes={post['likes']} reach={post.get('reach')}")
    print()
    print("=== CREATES (new rows) ===")
    for post in creates:
        print(f"  + {title_for(post)} (views={post['views']}, last_updated={post.get('last_updated')})")

    if dry:
        print("\n[dry-run] No writes performed. Re-run with --live to apply.")
        return

    print("\nWriting to Notion...")
    for match, post in updates:
        try:
            _notion("PATCH", f"pages/{match['id']}", {"properties": build_props(post, is_new=False)})
            print(f"  updated: {match['title']}")
        except Exception as e:
            print(f"  FAILED update {match['title']}: {e}")
    for post in creates:
        try:
            _notion("POST", "pages", {
                "parent": {"database_id": NOTION_DB},
                "properties": build_props(post, is_new=True),
            })
            print(f"  created: {title_for(post)}")
        except Exception as e:
            print(f"  FAILED create {title_for(post)}: {e}")


if __name__ == "__main__":
    main()

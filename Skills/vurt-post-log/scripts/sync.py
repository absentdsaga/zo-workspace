#!/usr/bin/env python3
"""Sync post URLs and metrics from IG/YT into the Notion Post Log."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# --- Constants ---
NOTION_DB_ID = "c592ce58-b453-436f-b8e0-4510b2dcb412"
IG_ACCOUNT_ID = "17841479978232203"
YT_CHANNEL_ID = "UCB7B5ifo5Pgfc-j_uJGQG1g"
META_BASE = "https://graph.facebook.com/v25.0"
YT_BASE = "https://www.googleapis.com/youtube/v3"
NOTION_BASE = "https://api.notion.com/v1"


def get_env(key):
    val = os.environ.get(key)
    if not val:
        print(f"Error: {key} not set. Add it in Settings > Advanced.", file=sys.stderr)
        sys.exit(1)
    return val


# --- Notion helpers ---
def notion_request(method, path, body=None):
    token = get_env("VURT_NOTION_API_KEY")
    url = f"{NOTION_BASE}/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def get_post_log_entries():
    results = []
    payload = {"page_size": 100}
    while True:
        data = notion_request("POST", f"databases/{NOTION_DB_ID}/query", payload)
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


def update_page(page_id, properties):
    return notion_request("PATCH", f"pages/{page_id}", {"properties": properties})


# --- Instagram ---
def get_ig_posts(limit=25):
    token = get_env("VURT_META_ACCESS_TOKEN")
    params = urllib.parse.urlencode({
        "fields": "id,caption,timestamp,like_count,comments_count,media_type,permalink",
        "limit": limit,
        "access_token": token,
    })
    url = f"{META_BASE}/{IG_ACCOUNT_ID}/media?{params}"
    resp = urllib.request.urlopen(url)
    posts = json.loads(resp.read()).get("data", [])

    enriched = []
    for post in posts:
        insights = {"reach": 0, "saved": 0, "shares": 0, "views": 0}
        try:
            params2 = urllib.parse.urlencode({
                "metric": "reach,saved,shares,views",
                "access_token": token,
            })
            url2 = f"{META_BASE}/{post['id']}/insights?{params2}"
            resp2 = urllib.request.urlopen(url2)
            for entry in json.loads(resp2.read()).get("data", []):
                insights[entry["name"]] = entry.get("values", [{}])[0].get("value", 0)
        except Exception:
            pass
        enriched.append({**post, **insights})
    return enriched


# --- YouTube ---
def get_yt_videos(days=60):
    api_key = os.environ.get("VURT_YOUTUBE_API_KEY")
    if not api_key:
        print("  VURT_YOUTUBE_API_KEY not set, skipping YT", file=sys.stderr)
        return []
    after = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    params = urllib.parse.urlencode({
        "part": "snippet", "channelId": YT_CHANNEL_ID, "type": "video",
        "order": "date", "publishedAfter": after, "maxResults": 50,
        "key": api_key,
    })
    resp = urllib.request.urlopen(f"{YT_BASE}/search?{params}")
    items = json.loads(resp.read()).get("items", [])
    if not items:
        return []
    video_ids = ",".join(i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId"))
    if not video_ids:
        return []
    params2 = urllib.parse.urlencode({
        "part": "snippet,statistics", "id": video_ids, "key": api_key,
    })
    resp2 = urllib.request.urlopen(f"{YT_BASE}/videos?{params2}")
    videos = []
    for v in json.loads(resp2.read()).get("items", []):
        s = v["statistics"]
        videos.append({
            "videoId": v["id"],
            "title": v["snippet"]["title"],
            "publishedAt": v["snippet"]["publishedAt"][:10],
            "url": f"https://youtube.com/shorts/{v['id']}",
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
        })
    return videos


# --- Matching + Sync ---
def extract_entry(page):
    props = page["properties"]
    title_parts = props.get("Post Title", {}).get("title", [])
    title = title_parts[0]["plain_text"] if title_parts else ""
    platform_sel = props.get("Platform", {}).get("select")
    platform = platform_sel["name"] if platform_sel else ""
    date_obj = props.get("Date Posted", {}).get("date")
    date = date_obj["start"] if date_obj else ""
    url = props.get("Post URL", {}).get("url")
    views = props.get("Views", {}).get("number")
    return {
        "id": page["id"],
        "title": title,
        "platform": platform,
        "date": date,
        "url": url,
        "views": views,
    }


def sync_urls(entries, ig_posts, yt_videos, dry_run=False):
    updates = []
    for entry in entries:
        if entry["url"]:
            continue

        if entry["platform"] == "Instagram":
            for post in ig_posts:
                post_date = post.get("timestamp", "")[:10]
                if post_date == entry["date"]:
                    caption_snip = (post.get("caption") or "")[:30].lower()
                    title_lower = entry["title"].lower()
                    if any(word in caption_snip for word in title_lower.split()[:3]) or post_date == entry["date"]:
                        updates.append({
                            "entry": entry,
                            "url": post["permalink"],
                            "source": "IG Graph API",
                        })
                        ig_posts.remove(post)
                        break

        elif entry["platform"] == "YT Shorts":
            for vid in yt_videos:
                if vid["publishedAt"] == entry["date"]:
                    updates.append({
                        "entry": entry,
                        "url": vid["url"],
                        "source": "YT Data API",
                    })
                    yt_videos.remove(vid)
                    break

    for u in updates:
        print(f"  URL: {u['entry']['title']} → {u['url']} (from {u['source']})")
        if not dry_run:
            update_page(u["entry"]["id"], {"Post URL": {"url": u["url"]}})
    return len(updates)


def sync_metrics(entries, ig_posts, yt_videos, dry_run=False):
    updates = 0
    for entry in entries:
        props_update = {}

        if entry["platform"] == "Instagram":
            for post in ig_posts:
                if post.get("permalink") == entry["url"] or post.get("timestamp", "")[:10] == entry["date"]:
                    props_update = {
                        "Views": {"number": post.get("views", 0) or 0},
                        "Likes": {"number": post.get("like_count", 0) or 0},
                        "Saves": {"number": post.get("saved", 0) or 0},
                        "Shares": {"number": post.get("shares", 0) or 0},
                        "Comments Count": {"number": post.get("comments_count", 0) or 0},
                    }
                    break

        elif entry["platform"] == "YT Shorts":
            for vid in yt_videos:
                if vid.get("url") == entry["url"] or vid["publishedAt"] == entry["date"]:
                    props_update = {
                        "Views": {"number": vid["views"]},
                        "Likes": {"number": vid["likes"]},
                        "Comments Count": {"number": vid["comments"]},
                    }
                    break

        if props_update:
            nums = ", ".join(f"{k}={v['number']}" for k, v in props_update.items())
            print(f"  Metrics: {entry['title']} → {nums}")
            if not dry_run:
                update_page(entry["id"], props_update)
            updates += 1

    return updates


def main():
    parser = argparse.ArgumentParser(description="Sync Post Log with platform data")
    parser.add_argument("--urls", action="store_true", help="Sync post URLs")
    parser.add_argument("--metrics", action="store_true", help="Sync post metrics")
    parser.add_argument("--all", action="store_true", help="Sync both URLs and metrics")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if not (args.urls or args.metrics or args.all):
        parser.print_help()
        sys.exit(1)

    do_urls = args.urls or args.all
    do_metrics = args.metrics or args.all

    print("Fetching Post Log from Notion...")
    pages = get_post_log_entries()
    entries = [extract_entry(p) for p in pages]
    print(f"  Found {len(entries)} entries")

    ig_posts, yt_videos = [], []

    if do_urls or do_metrics:
        print("\nFetching Instagram posts...")
        try:
            ig_posts = get_ig_posts()
            print(f"  Found {len(ig_posts)} IG posts")
        except Exception as e:
            print(f"  IG fetch failed: {e}", file=sys.stderr)

        print("Fetching YouTube videos...")
        try:
            yt_videos = get_yt_videos()
            print(f"  Found {len(yt_videos)} YT videos")
        except Exception as e:
            print(f"  YT fetch failed: {e}", file=sys.stderr)

    if do_urls:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Syncing URLs...")
        n = sync_urls(entries, list(ig_posts), list(yt_videos), args.dry_run)
        print(f"  {n} URLs {'would be ' if args.dry_run else ''}updated")
        # Re-fetch entries if we updated URLs and need metrics too
        if n and do_metrics and not args.dry_run:
            pages = get_post_log_entries()
            entries = [extract_entry(p) for p in pages]

    if do_metrics:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Syncing metrics...")
        n = sync_metrics(entries, ig_posts, yt_videos, args.dry_run)
        print(f"  {n} entries {'would be ' if args.dry_run else ''}updated with metrics")

    print("\nDone.")


if __name__ == "__main__":
    main()

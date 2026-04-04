#!/usr/bin/env python3 -u
"""Sync post URLs and metrics from IG/YT into the Notion Post Log."""

import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

SHOW_KEYWORDS = [
    ("karma", "Karma in Heels"),
    ("parking", "Parking Lot Series"),
    ("come back", "Come Back Dad"),
    ("comeback", "Come Back Dad"),
    ("killer stepdad", "Killer Stepdad"),
    ("baby mama", "Baby Mama"),
    ("fatal lust", "Fatal Lust"),
    ("miami kingpin", "Miami Kingpins"),
    ("schemers", "SCHEMERS"),
    ("nita k", "Nita K Spotlight"),
    ("ted lucas", "Ted Lucas Spotlight"),
    ("vurt 100", "THIS IS VURT"),
    ("vurt100", "THIS IS VURT"),
    ("this is vurt", "THIS IS VURT"),
    ("director", "Director Spotlight"),
    ("spotlight", "Director Spotlight"),
    ("filmmaker", "Director Spotlight"),
]


def detect_show(title):
    tl = title.lower()
    for keyword, show_name in SHOW_KEYWORDS:
        if keyword in tl:
            return show_name
    return None


# --- Constants ---
NOTION_DB_ID = "c592ce58-b453-436f-b8e0-4510b2dcb412"
IG_ACCOUNT_ID = "17841479978232203"
FB_PAGE_ID = "943789668811148"
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
    resp = urllib.request.urlopen(req, timeout=15)
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
def get_ig_posts(limit=100):
    token = get_env("VURT_META_ACCESS_TOKEN")
    posts = []
    params = urllib.parse.urlencode({
        "fields": "id,caption,timestamp,like_count,comments_count,media_type,permalink,media_product_type",
        "limit": min(limit, 100),
        "access_token": token,
    })
    url = f"{META_BASE}/{IG_ACCOUNT_ID}/media?{params}"
    while url and len(posts) < limit:
        resp = json.loads(urllib.request.urlopen(url, timeout=15).read())
        posts.extend(resp.get("data", []))
        url = resp.get("paging", {}).get("next")

    now = datetime.utcnow()
    enriched = []
    for post in posts:
        mtype = post.get("media_type", "")
        base_metrics = "views,reach,saved,shares,total_interactions,likes,comments"
        reel_metrics = "ig_reels_avg_watch_time"

        insights = {}
        # Fetch base metrics (work for all post types)
        try:
            params2 = urllib.parse.urlencode({"metric": base_metrics, "access_token": token})
            url2 = f"{META_BASE}/{post['id']}/insights?{params2}"
            resp2 = urllib.request.urlopen(url2, timeout=15)
            for entry in json.loads(resp2.read()).get("data", []):
                insights[entry["name"]] = entry.get("values", [{}])[0].get("value", 0)
        except Exception:
            pass
        # Fetch reel-specific metrics separately (only for VIDEO)
        if mtype == "VIDEO":
            try:
                params3 = urllib.parse.urlencode({"metric": reel_metrics, "access_token": token})
                url3 = f"{META_BASE}/{post['id']}/insights?{params3}"
                resp3 = urllib.request.urlopen(url3, timeout=15)
                for entry in json.loads(resp3.read()).get("data", []):
                    insights[entry["name"]] = entry.get("values", [{}])[0].get("value", 0)
            except Exception:
                pass

        post_time = datetime.strptime(post["timestamp"][:19], "%Y-%m-%dT%H:%M:%S")
        age_hours = (now - post_time).total_seconds() / 3600
        post["_views_preliminary"] = age_hours < 48

        enriched.append({**post, **insights})
    return enriched


# --- Facebook Page ---
def get_fb_posts(limit=50):
    token = get_env("VURT_META_ACCESS_TOKEN")
    posts = []
    params = urllib.parse.urlencode({
        "fields": "id,message,created_time,permalink_url,shares",
        "limit": min(limit, 100),
        "access_token": token,
    })
    url = f"{META_BASE}/{FB_PAGE_ID}/posts?{params}"
    while url and len(posts) < limit:
        resp = json.loads(urllib.request.urlopen(url, timeout=15).read())
        posts.extend(resp.get("data", []))
        url = resp.get("paging", {}).get("next")

    enriched = []
    for i, post in enumerate(posts):
        print(f"  FB enriching {i+1}/{len(posts)}...", flush=True)
        likes_url = f"{META_BASE}/{post['id']}?fields=likes.summary(true),comments.summary(true)&access_token={token}"
        try:
            lr = json.loads(urllib.request.urlopen(likes_url, timeout=15).read())
            post["like_count"] = lr.get("likes", {}).get("summary", {}).get("total_count", 0)
            post["comments_count"] = lr.get("comments", {}).get("summary", {}).get("total_count", 0)
        except Exception:
            post["like_count"] = 0
            post["comments_count"] = 0

        post["share_count"] = post.get("shares", {}).get("count", 0)
        post["video_views"] = 0
        try:
            vv_url = f"{META_BASE}/{post['id']}/insights/post_video_views/lifetime?access_token={token}"
            vv_resp = json.loads(urllib.request.urlopen(vv_url, timeout=15).read())
            for m in vv_resp.get("data", []):
                post["video_views"] = m.get("values", [{}])[0].get("value", 0)
        except Exception:
            pass

        post["reach"] = 0
        try:
            r_url = f"{META_BASE}/{post['id']}/insights/post_impressions_unique/lifetime?access_token={token}"
            r_resp = json.loads(urllib.request.urlopen(r_url, timeout=15).read())
            for m in r_resp.get("data", []):
                post["reach"] = m.get("values", [{}])[0].get("value", 0)
        except Exception:
            pass

        enriched.append(post)
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
    try:
        resp = urllib.request.urlopen(f"{YT_BASE}/search?{params}", timeout=15)
        items = json.loads(resp.read()).get("items", [])
    except Exception as e:
        print(f"  YT search failed: {e}", file=sys.stderr)
        return []
    if not items:
        return []
    video_ids = ",".join(i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId"))
    if not video_ids:
        return []
    params2 = urllib.parse.urlencode({
        "part": "snippet,statistics", "id": video_ids, "key": api_key,
    })
    resp2 = urllib.request.urlopen(f"{YT_BASE}/videos?{params2}", timeout=15)
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


# --- TikTok (scrape from page HTML, no API key needed) ---
def get_tiktok_stats(url):
    """Scrape TikTok video stats from page HTML."""
    import time
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="ignore")
        match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not match:
            return None
        s = match.group(1)
        stats = {}
        for metric in ["playCount", "diggCount", "shareCount", "commentCount", "collectCount"]:
            vals = re.findall(rf'"{metric}":\s*(\d+)', s)
            if vals:
                stats[metric] = int(vals[0])
        return stats
    except Exception:
        return None


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
    notes_parts = props.get("Notes", {}).get("rich_text", [])
    notes = notes_parts[0]["plain_text"] if notes_parts else ""
    caption_parts = props.get("Caption", {}).get("rich_text", [])
    caption = caption_parts[0]["plain_text"] if caption_parts else ""
    day_sel = props.get("Day", {}).get("select")
    day = day_sel["name"] if day_sel else ""
    show_sel = props.get("Show", {}).get("select")
    show = show_sel["name"] if show_sel else ""
    return {
        "id": page["id"],
        "title": title,
        "platform": platform,
        "date": date,
        "url": url,
        "views": views,
        "notes": notes,
        "caption": caption,
        "day": day,
        "show": show,
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


def sync_metrics(entries, ig_posts, yt_videos, fb_posts=None, dry_run=False):
    fb_posts = fb_posts or []
    updates = 0
    for entry in entries:
        props_update = {}
        preliminary = False

        if entry["platform"] == "Instagram":
            matched_post = None
            # Priority 1: match by URL (most reliable)
            if entry["url"]:
                for post in ig_posts:
                    if post.get("permalink") == entry["url"]:
                        matched_post = post
                        break
            # Priority 2: match by date + caption keywords (fallback)
            if not matched_post and entry["date"]:
                title_words = [w.lower() for w in entry["title"].split() if len(w) > 3]
                for post in ig_posts:
                    if post.get("timestamp", "")[:10] == entry["date"]:
                        caption = (post.get("caption") or "").lower()
                        if any(w in caption for w in title_words[:3]):
                            matched_post = post
                            break
            if matched_post:
                preliminary = matched_post.get("_views_preliminary", False)
                mtype = matched_post.get("media_type", "")
                # views metric works for both VIDEO and IMAGE on v25.0
                views_val = matched_post.get("views", 0) or 0
                props_update = {
                    "Views": {"number": views_val},
                    "Likes": {"number": matched_post.get("like_count", 0) or 0},
                    "Saves": {"number": matched_post.get("saved", 0) or 0},
                    "Shares": {"number": matched_post.get("shares", 0) or 0},
                    "Comments Count": {"number": matched_post.get("comments_count", 0) or 0},
                    "Reach": {"number": matched_post.get("reach", 0) or 0},
                }
                avg_watch_ms = matched_post.get("ig_reels_avg_watch_time", 0) or 0
                total_interactions = matched_post.get("total_interactions", 0) or 0
                if avg_watch_ms:
                    props_update["Avg Watch Time (s)"] = {"number": round(avg_watch_ms / 1000, 1)}
                if total_interactions:
                    props_update["Engagement"] = {"number": total_interactions}
                # Extract caption, collaborator tags (@mentions), and hashtags
                caption_text = matched_post.get("caption") or ""
                if not entry.get("caption") and caption_text:
                    props_update["Caption"] = {"rich_text": [{"text": {"content": caption_text[:2000]}}]}
                # Store caption data for calendar enrichment later
                matched_post["_extracted_mentions"] = []
                matched_post["_extracted_hashtags"] = []
                if caption_text:
                    matched_post["_extracted_mentions"] = re.findall(r"@(\w+)", caption_text)
                    matched_post["_extracted_hashtags"] = re.findall(r"#(\w+)", caption_text)
                if not entry["url"] and matched_post.get("permalink"):
                    props_update["Post URL"] = {"url": matched_post["permalink"]}

        elif entry["platform"] == "YT Shorts":
            for vid in yt_videos:
                if vid.get("url") == entry["url"] or vid["publishedAt"] == entry["date"]:
                    props_update = {
                        "Views": {"number": vid["views"]},
                        "Likes": {"number": vid["likes"]},
                        "Comments Count": {"number": vid["comments"]},
                    }
                    break

        elif entry["platform"] == "Facebook":
            matched_fb = None
            if entry["url"]:
                for post in fb_posts:
                    if post.get("permalink_url") == entry["url"]:
                        matched_fb = post
                        break
            if not matched_fb and entry["date"]:
                title_words = [w.lower() for w in entry["title"].split() if len(w) > 3]
                for post in fb_posts:
                    if post.get("created_time", "")[:10] == entry["date"]:
                        msg = (post.get("message") or "").lower()
                        if any(w in msg for w in title_words[:3]) or not entry["url"]:
                            matched_fb = post
                            break
            if matched_fb:
                props_update = {
                    "Views": {"number": matched_fb.get("video_views", 0)},
                    "Likes": {"number": matched_fb.get("like_count", 0)},
                    "Shares": {"number": matched_fb.get("share_count", 0)},
                    "Comments Count": {"number": matched_fb.get("comments_count", 0)},
                    "Reach": {"number": matched_fb.get("reach", 0)},
                }
                if not entry["url"] and matched_fb.get("permalink_url"):
                    props_update["Post URL"] = {"url": matched_fb["permalink_url"]}
                if not entry.get("caption") and matched_fb.get("message"):
                    props_update["Caption"] = {"rich_text": [{"text": {"content": matched_fb["message"][:2000]}}]}

        elif entry["platform"] == "TikTok":
            if entry["url"] and "tiktok.com" in entry["url"]:
                import time
                stats = get_tiktok_stats(entry["url"])
                if stats:
                    props_update = {
                        "Views": {"number": stats.get("playCount", 0)},
                        "Likes": {"number": stats.get("diggCount", 0)},
                        "Comments Count": {"number": stats.get("commentCount", 0)},
                        "Shares": {"number": stats.get("shareCount", 0)},
                        "Saves": {"number": stats.get("collectCount", 0)},
                    }
                time.sleep(1)

        if props_update:
            if preliminary:
                props_update["Notes"] = {"rich_text": [{"text": {"content": "⏳ Views updating (post < 48hrs old)"}}]}
            elif entry.get("notes", "").startswith("⏳"):
                props_update["Notes"] = {"rich_text": []}

            show = detect_show(entry.get("title", ""))
            if show and not entry.get("show"):
                props_update["Show"] = {"select": {"name": show}}

            if entry.get("date") and not entry.get("day"):
                try:
                    dt = datetime.strptime(entry["date"][:10], "%Y-%m-%d")
                    props_update["Day"] = {"select": {"name": DAYS[dt.weekday()]}}
                except Exception:
                    pass

            tag = " ⏳" if preliminary else ""
            nums = ", ".join(f"{k}={v['number']}" for k, v in props_update.items() if isinstance(v, dict) and "number" in v)
            print(f"  Metrics: {entry['title']} → {nums}{tag}")
            if not dry_run:
                try:
                    update_page(entry["id"], props_update)
                except Exception:
                    safe = {k: v for k, v in props_update.items() if k in (
                        "Views", "Likes", "Saves", "Shares", "Comments Count", "Reach",
                        "Avg Watch Time (s)", "Post URL", "Caption", "Day", "Notes",
                        "Collaborator Tags", "Hashtags", "Show",
                    )}
                    if safe:
                        update_page(entry["id"], safe)
            updates += 1

    return updates


CAL_DB_ID = "a7587d5d-8f14-490d-a494-664bd80d6256"

PLAT_ARROW = {
    "Instagram": "IG", "Facebook": "Facebook",
    "TikTok": "TikTok", "YT Shorts": "YT Shorts",
}


def reconcile_calendar(dry_run=False):
    print("\nReconciling Content Calendar with Post Log...")
    log_pages = get_post_log_entries()
    posted = {}
    for p in log_pages:
        props = p["properties"]
        title = "".join(t["plain_text"] for t in props.get("Post Title", {}).get("title", []))
        plat = (props.get("Platform", {}).get("select") or {}).get("name", "")
        date = (props.get("Date Posted", {}).get("date") or {}).get("start", "")
        url = props.get("Post URL", {}).get("url", "") or ""
        if not date:
            continue
        m = re.search(r"Clip\s*(\d+)", title)
        if not m:
            continue
        clip_num = int(m.group(1))
        show = detect_show(title)
        if not show:
            continue
        posted[(show, clip_num, plat)] = {"date": date, "url": url, "page_id": p["id"]}

    # Snap same-clip dates: if all platforms for a clip posted within 24hrs,
    # use the earliest date (user posts all platforms at once, APIs lag)
    from collections import defaultdict
    clip_dates = defaultdict(list)
    for (show, clip_num, plat), info in posted.items():
        clip_dates[(show, clip_num)].append((plat, info))
    for (show, clip_num), entries in clip_dates.items():
        dates = [e[1]["date"] for e in entries]
        if len(set(dates)) > 1:
            sorted_dates = sorted(dates)
            earliest = sorted_dates[0]
            latest = sorted_dates[-1]
            d1 = datetime.strptime(earliest, "%Y-%m-%d")
            d2 = datetime.strptime(latest, "%Y-%m-%d")
            if (d2 - d1).days <= 1:
                for plat, info in entries:
                    if info["date"] != earliest:
                        print(f"  Snap: {show} Clip {clip_num} {plat} {info['date']}→{earliest}")
                        info["date"] = earliest
                        if not dry_run and info.get("page_id"):
                            try:
                                update_page(info["page_id"], {"Date Posted": {"date": {"start": earliest}}})
                            except Exception:
                                pass

    cal_results = []
    payload = {"page_size": 100}
    while True:
        data = notion_request("POST", f"databases/{CAL_DB_ID}/query", payload)
        cal_results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    updated = 0
    for e in cal_results:
        props = e["properties"]
        cal_title = "".join(t["plain_text"] for t in props.get("Title", {}).get("title", []))
        cal_date = (props.get("Post Date", {}).get("date") or {}).get("start", "")
        clip_num = props.get("Clip #", {}).get("number")
        platforms = [s["name"] for s in props.get("Platform", {}).get("multi_select", [])]
        status = (props.get("Status", {}).get("select") or {}).get("name", "")

        if not clip_num or not platforms:
            continue

        show = detect_show(cal_title)
        if not show:
            continue

        for plat in platforms:
            key = (show, int(clip_num), plat)
            if key in posted:
                info = posted[key]
                needs_update = False
                patch = {}
                if info["date"] != cal_date:
                    patch["Post Date"] = {"date": {"start": info["date"]}}
                    needs_update = True
                if status != "Posted":
                    patch["Status"] = {"select": {"name": "Posted"}}
                    needs_update = True
                if needs_update:
                    tag = f" (date {cal_date}→{info['date']})" if info["date"] != cal_date else ""
                    print(f"  Calendar fix: {cal_title}{tag} → Posted")
                    if not dry_run:
                        try:
                            update_page(e["id"], patch)
                        except Exception as ex:
                            print(f"    Failed: {ex}")
                    updated += 1

    print(f"  {updated} calendar entries {'would be ' if dry_run else ''}reconciled")
    return updated


def enrich_calendar(ig_posts, dry_run=False):
    """Push collaborator tags, hashtags, and captions from IG data to Content Calendar entries."""
    print("\nEnriching Content Calendar with IG post data...")
    cal_results = []
    payload = {"page_size": 100}
    while True:
        data = notion_request("POST", f"databases/{CAL_DB_ID}/query", payload)
        cal_results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    # Build IG post lookup by caption keywords for matching to calendar entries
    # (only write to Instagram-platform entries; other platforms get their own captions later)
    ig_caption_data = {}
    for post in ig_posts:
        caption = post.get("caption") or ""
        if not caption:
            continue
        mentions = re.findall(r"@(\w+)", caption)
        hashtags = re.findall(r"#(\w+)", caption)
        ig_caption_data[post.get("permalink", "")] = {
            "caption": caption,
            "mentions": mentions,
            "hashtags": hashtags,
            "timestamp": post.get("timestamp", "")[:10],
            "caption_lower": caption.lower(),
        }

    # Get Post Log IG entries to map show+clip to IG post data
    log_pages = get_post_log_entries()
    clip_ig_data = {}
    for p in log_pages:
        props = p["properties"]
        title = "".join(t["plain_text"] for t in props.get("Post Title", {}).get("title", []))
        url = props.get("Post URL", {}).get("url", "") or ""
        plat = (props.get("Platform", {}).get("select") or {}).get("name", "")
        if plat != "Instagram" or not url:
            continue
        # Extract show + clip from title
        m = re.search(r"Clip\s*(\d+)", title)
        show = None
        tl = title.lower()
        show = detect_show(title)
        if show and m:
            clip_num = int(m.group(1))
            if url in ig_caption_data:
                clip_ig_data[(show, clip_num)] = ig_caption_data[url]
        # Also match non-clip entries by title keywords
        if url in ig_caption_data:
            clip_ig_data[("_title", tl)] = ig_caption_data[url]

    # Also match IG posts directly by date + caption keywords for non-clip entries
    ig_by_date = {}
    for url, data in ig_caption_data.items():
        d = data["timestamp"]
        if d:
            ig_by_date.setdefault(d, []).append(data)

    updated = 0
    for e in cal_results:
        props = e["properties"]
        cal_title = "".join(t["plain_text"] for t in props.get("Title", {}).get("title", []))
        cal_date = (props.get("Post Date", {}).get("date") or {}).get("start", "")
        clip_num = props.get("Clip #", {}).get("number")
        platforms = [s["name"] for s in props.get("Platform", {}).get("multi_select", [])]

        # Only enrich Instagram-specific entries; other platforms (TikTok,
        # YT Shorts, Facebook, LinkedIn) will get platform-specific captions later
        if platforms != ["Instagram"]:
            continue

        existing_collab = "".join(t["plain_text"] for t in props.get("Collaborator Tags", {}).get("rich_text", []))
        existing_hashtags = "".join(t["plain_text"] for t in props.get("Hashtags", {}).get("rich_text", []))
        existing_caption = "".join(t["plain_text"] for t in props.get("Caption", {}).get("rich_text", []))

        if existing_collab and existing_hashtags and existing_caption:
            continue

        show = detect_show(cal_title)

        matched_data = None
        # Match by show + clip number
        if show and clip_num and (show, clip_num) in clip_ig_data:
            matched_data = clip_ig_data[(show, clip_num)]
        # Fallback: match by date + caption keywords
        if not matched_data and cal_date in ig_by_date:
            title_words = [w.lower() for w in cal_title.split() if len(w) > 3]
            for data in ig_by_date[cal_date]:
                if any(w in data["caption_lower"] for w in title_words[:3]):
                    matched_data = data
                    break

        if not matched_data:
            continue

        patch = {}
        if not existing_collab and matched_data["mentions"]:
            patch["Collaborator Tags"] = {"rich_text": [{"text": {"content": ", ".join(f"@{m}" for m in matched_data["mentions"])[:2000]}}]}
        if not existing_hashtags and matched_data["hashtags"]:
            patch["Hashtags"] = {"rich_text": [{"text": {"content": ", ".join(f"#{h}" for h in matched_data["hashtags"])[:2000]}}]}
        if not existing_caption and matched_data["caption"]:
            patch["Caption"] = {"rich_text": [{"text": {"content": matched_data["caption"][:2000]}}]}

        if patch:
            fields = ", ".join(patch.keys())
            print(f"  Enrich: {cal_title} → {fields}")
            if not dry_run:
                try:
                    update_page(e["id"], patch)
                except Exception as ex:
                    print(f"    Failed: {ex}")
            updated += 1

    print(f"  {updated} calendar entries {'would be ' if dry_run else ''}enriched")
    return updated


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

    ig_posts, yt_videos, fb_posts = [], [], []

    if do_urls or do_metrics:
        print("\nFetching Instagram posts...")
        try:
            ig_posts = get_ig_posts()
            print(f"  Found {len(ig_posts)} IG posts")
        except Exception as e:
            print(f"  IG fetch failed: {e}", file=sys.stderr)

        print("Fetching Facebook posts...")
        try:
            fb_posts = get_fb_posts()
            print(f"  Found {len(fb_posts)} FB posts")
        except Exception as e:
            print(f"  FB fetch failed: {e}", file=sys.stderr)

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
        n = sync_metrics(entries, ig_posts, yt_videos, fb_posts, args.dry_run)
        print(f"  {n} entries {'would be ' if args.dry_run else ''}updated with metrics")

    if do_metrics or args.all:
        reconcile_calendar(args.dry_run)
        enrich_calendar(ig_posts, args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Profile-level TikTok scraper for @myvurt.

Two sources feed this:

1. **Static profile HTML** — gives follower/likes/video counts + nickname
   by parsing the __UNIVERSAL_DATA_FOR_REHYDRATION__ blob. Fast, no browser.

2. **Per-video cache** at ../data/tiktok_user_url_scrape.json — already
   populated + refreshed by `tiktok_url_harvest.py` + `tiktok_scraper.py`.
   We use it to compute top performers by views/engagement/save rate.

Callers (daily-report.py, social_client.py, birdseye/snapshot.py) should use
`get_profile_summary()` which combines both and never raises.

CLI:
    python3 tiktok_profile.py            # print summary JSON
    python3 tiktok_profile.py --refresh  # harvest URLs + scrape then summarize
"""

import argparse
import gzip
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

DATA_BLOB_RE = re.compile(
    r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
    re.DOTALL,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "tiktok_user_url_scrape.json")
URL_CACHE = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "tiktok_urls.json")


def _fetch_html(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    })
    resp = urllib.request.urlopen(req, timeout=timeout)
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="ignore")


def get_profile_stats(handle="myvurt"):
    """Fetch live profile stats (followers, likes, video_count, nickname)."""
    out = {
        "handle": f"@{handle}",
        "followers": None,
        "following": None,
        "likes": None,
        "video_count": None,
        "nickname": None,
        "user_id": None,
        "source": "tiktok-profile-html",
        "error": None,
    }
    try:
        html = _fetch_html(f"https://www.tiktok.com/@{handle}")
        m = DATA_BLOB_RE.search(html)
        if not m:
            out["error"] = "no data blob"
            return out
        data = json.loads(m.group(1))
        ui = data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {}).get("userInfo", {})
        user = ui.get("user", {}) or {}
        stats = ui.get("stats", {}) or {}
        out["nickname"] = user.get("nickname")
        out["user_id"] = user.get("id")
        out["followers"] = stats.get("followerCount")
        out["following"] = stats.get("followingCount")
        out["likes"] = stats.get("heartCount") or stats.get("heart")
        out["video_count"] = stats.get("videoCount")
    except Exception as e:
        out["error"] = repr(e)
    return out


def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return []
    try:
        with open(CACHE_FILE) as f:
            return json.load(f) or []
    except Exception:
        return []


def get_top_performers(limit=5, min_views=100):
    """Return top posts by views from the per-URL cache.

    Each record includes views/likes/comments/shares/saves/save_rate/like_rate
    plus caption + url, already filtered to posts that cleared min_views.
    """
    cache = _load_cache()
    ranked = []
    for p in cache:
        v = p.get("views") or 0
        if v < min_views:
            continue
        s = p.get("saves") or 0
        l = p.get("likes") or 0
        c = p.get("comments") or 0
        sh = p.get("shares") or 0
        ranked.append({
            "video_id": p.get("video_id", ""),
            "url": p.get("url", ""),
            "caption": (p.get("caption") or "").strip().split("\n")[0][:80],
            "create_time": p.get("create_time", 0),
            "duration": p.get("duration", 0),
            "views": v,
            "likes": l,
            "comments": c,
            "shares": sh,
            "saves": s,
            "save_rate": s / v if v else 0,
            "like_rate": l / v if v else 0,
            "engagement": l + c + sh + s,
        })
    ranked.sort(key=lambda r: r["views"], reverse=True)
    return {
        "count": len(ranked),
        "cache_age_hours": _cache_age_hours(cache),
        "top": ranked[:limit],
    }


def _cache_age_hours(cache):
    if not cache:
        return None
    latest = max((p.get("scraped_at") or 0) for p in cache)
    if not latest:
        return None
    return round((time.time() - latest) / 3600, 1)


def get_recent_posts(days=7):
    """Return posts scraped whose create_time falls in the last N days."""
    cache = _load_cache()
    cutoff = time.time() - days * 86400
    recent = [p for p in cache if (p.get("create_time") or 0) >= cutoff]
    total_views = sum((p.get("views") or 0) for p in recent)
    total_saves = sum((p.get("saves") or 0) for p in recent)
    total_likes = sum((p.get("likes") or 0) for p in recent)
    return {
        "days": days,
        "post_count": len(recent),
        "total_views": total_views,
        "total_likes": total_likes,
        "total_saves": total_saves,
        "avg_views": round(total_views / len(recent)) if recent else 0,
        "avg_save_rate": round((total_saves / total_views * 100), 2) if total_views else 0,
    }


def get_profile_summary(handle="myvurt", top_limit=5, recent_days=7):
    """Combined summary used by daily report + birdseye."""
    stats = get_profile_stats(handle=handle)
    top = get_top_performers(limit=top_limit)
    recent = get_recent_posts(days=recent_days)
    return {
        "stats": stats,
        "recent": recent,
        "top_performers": top,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def refresh_cache(handle="myvurt", max_scrolls=50):
    """Run the existing harvest + per-video scraper to refresh the cache.

    Reuses tiktok_url_harvest.py (Playwright, with stealth) and
    tiktok_scraper.py so we have one source of truth for scraping logic.
    """
    print(f"Refreshing TikTok cache for @{handle}...")
    print("  Step 1/2: harvesting URLs via Playwright stealth...")
    harvest_script = os.path.join(SCRIPT_DIR, "tiktok_url_harvest.py")
    r = subprocess.run(
        [sys.executable, harvest_script, "--handle", handle, "--scrolls", str(max_scrolls)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("  harvest failed:", r.stderr[-500:])
        return False

    if not os.path.exists(URL_CACHE):
        print("  no URL cache produced")
        return False

    urls_data = json.load(open(URL_CACHE))
    urls = [v["url"] for v in urls_data.get("videos", [])]
    print(f"  Step 2/2: scraping {len(urls)} video pages...")

    from tiktok_scraper import scrape_many
    results = scrape_many(urls)
    out = [v for v in results.values() if v]
    with open(CACHE_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  wrote {len(out)} videos to {CACHE_FILE}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", default="myvurt")
    ap.add_argument("--refresh", action="store_true",
                    help="Harvest + scrape before summarizing (slow: uses Playwright)")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    if args.refresh:
        refresh_cache(handle=args.handle)

    summary = get_profile_summary(handle=args.handle, top_limit=args.top)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

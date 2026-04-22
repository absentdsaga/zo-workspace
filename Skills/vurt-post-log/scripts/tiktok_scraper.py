#!/usr/bin/env python3
"""Public TikTok page scraper.

Pulls per-video metrics (views, likes, comments, shares, saves, caption,
duration, create time, author) by parsing the __UNIVERSAL_DATA_FOR_REHYDRATION__
JSON blob TikTok embeds in the rendered page HTML.

No login or API keys required. Use this when the TikTok Display API is
unavailable (sandbox-only, app awaiting review, etc.).
"""

import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
DATA_BLOB_RE = re.compile(
    r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
    re.DOTALL,
)
VIDEO_ID_RE = re.compile(r"/video/(\d+)")


def _fetch_html(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="ignore")


def _to_int(v) -> int:
    if v is None:
        return 0
    if isinstance(v, int):
        return v
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def scrape_video(url: str, retries: int = 2, sleep: float = 1.0) -> Optional[dict]:
    """Return per-video stats dict for a TikTok video URL, or None on failure."""
    last_err = None
    for attempt in range(retries + 1):
        try:
            html = _fetch_html(url)
            m = DATA_BLOB_RE.search(html)
            if not m:
                last_err = "no data blob"
            else:
                data = json.loads(m.group(1))
                scope = data.get("__DEFAULT_SCOPE__", {})
                detail = scope.get("webapp.video-detail", {})
                if detail.get("statusCode") not in (0, None):
                    last_err = f"statusCode={detail.get('statusCode')} msg={detail.get('statusMsg')}"
                else:
                    item = detail.get("itemInfo", {}).get("itemStruct", {})
                    if not item:
                        last_err = "empty itemStruct"
                    else:
                        stats = item.get("stats", {}) or {}
                        # statsV2 is sometimes fresher; merge with stats taking the larger value
                        statsv2 = item.get("statsV2", {}) or {}
                        author = item.get("author", {}) or {}
                        video = item.get("video", {}) or {}

                        def best(key_v1, key_v2=None):
                            a = _to_int(stats.get(key_v1))
                            b = _to_int(statsv2.get(key_v2 or key_v1))
                            return max(a, b)

                        return {
                            "video_id": item.get("id", ""),
                            "url": url,
                            "author_username": author.get("uniqueId", ""),
                            "author_id": author.get("id", ""),
                            "caption": item.get("desc", "") or "",
                            "create_time": _to_int(item.get("createTime")),
                            "duration": _to_int(video.get("duration")),
                            "views": best("playCount"),
                            "likes": best("diggCount"),
                            "comments": best("commentCount"),
                            "shares": best("shareCount"),
                            "saves": best("collectCount"),
                            "scraped_at": int(time.time()),
                        }
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code in (404, 410):
                return None
        except Exception as e:
            last_err = repr(e)
        if attempt < retries:
            time.sleep(sleep * (attempt + 1))
    sys.stderr.write(f"  scrape failed: {url} ({last_err})\n")
    return None


def scrape_many(urls, sleep: float = 1.5) -> dict:
    """Scrape a list of URLs, returning {url: result_dict_or_None}. Polite delay between requests."""
    out = {}
    for i, u in enumerate(urls):
        if i > 0:
            time.sleep(sleep)
        out[u] = scrape_video(u)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tiktok_scraper.py <url> [<url> ...]")
        sys.exit(1)
    results = scrape_many(sys.argv[1:])
    print(json.dumps(results, indent=2))

#!/usr/bin/env python3
"""Scrape captions + stats for each URL in data/tiktok_user_urls.txt.

Output: data/tiktok_user_url_scrape.json — list of {url, caption, views, likes, ...}.
Used to match user-provided URLs against the BC screenshot data by caption.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tiktok_scraper import scrape_video  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
URLS_FILE = os.path.join(DATA_DIR, "tiktok_user_urls.txt")
OUT_FILE = os.path.join(DATA_DIR, "tiktok_user_url_scrape.json")


def load_urls():
    urls = []
    with open(URLS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Lines may be "<n>\t<url>" or just url
            parts = line.split()
            url = parts[-1].strip()
            if url.startswith("http"):
                urls.append(url)
    # Dedupe (preserve order)
    seen = set()
    deduped = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        deduped.append(u)
    return deduped


def main():
    urls = load_urls()
    print(f"Loaded {len(urls)} URLs")
    results = []
    for i, u in enumerate(urls):
        if i:
            time.sleep(1.5)
        d = scrape_video(u)
        if not d:
            print(f"  [{i+1}/{len(urls)}] FAIL {u}")
            results.append({"url": u, "error": "scrape failed"})
            continue
        cap_preview = (d["caption"] or "")[:60].replace("\n", " ")
        print(f"  [{i+1}/{len(urls)}] {d['views']:>7,} views  {cap_preview}")
        results.append(d)
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {len(results)} entries to {OUT_FILE}")


if __name__ == "__main__":
    main()

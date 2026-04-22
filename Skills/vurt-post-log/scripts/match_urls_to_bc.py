#!/usr/bin/env python3
"""Match scraped TikTok URLs (data/tiktok_user_url_scrape.json) to BC screenshot
posts (data/tiktok_bc_screenshots.json) by caption substring, then write the
URL into each BC post entry.

Reports unmatched URLs and unmatched BC posts.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
BC_FILE = os.path.join(DATA_DIR, "tiktok_bc_screenshots.json")
SCRAPE_FILE = os.path.join(DATA_DIR, "tiktok_user_url_scrape.json")


def norm(s: str) -> str:
    if not s:
        return ""
    return "".join(ch.lower() for ch in s if ch.isalnum() or ch.isspace()).strip()


def match(scraped_caption: str, bc_snippet: str) -> bool:
    a = norm(scraped_caption)
    b = norm(bc_snippet)
    if not a or not b:
        return False
    # Use first 25 chars of the shorter caption
    needle = (a if len(a) <= len(b) else b)[:25]
    return needle in a and needle in b


def main():
    bc = json.load(open(BC_FILE))
    scraped = json.load(open(SCRAPE_FILE))

    posts = bc["posts"]
    matched_pairs = []
    unmatched_urls = []

    bc_used = [False] * len(posts)
    for s in scraped:
        if "error" in s:
            unmatched_urls.append({"url": s["url"], "reason": "scrape failed (likely archived)"})
            continue
        cap = s.get("caption", "")
        url = s.get("url", "")
        idx = None
        for i, p in enumerate(posts):
            if bc_used[i]:
                continue
            if match(cap, p.get("caption_snippet", "")):
                idx = i
                break
        if idx is None:
            unmatched_urls.append({"url": url, "caption": cap[:80]})
        else:
            bc_used[idx] = True
            matched_pairs.append((idx, s))

    print(f"Matched: {len(matched_pairs)} / {len(scraped)} scraped URLs")
    print(f"Unmatched URLs: {len(unmatched_urls)}")
    print(f"Unmatched BC posts: {sum(1 for u in bc_used if not u)}")
    print()
    print("=== MATCHES ===")
    for idx, s in matched_pairs:
        cap = (posts[idx].get("caption_snippet") or "")[:55].replace("\n", " ")
        print(f"  post#{idx+1:2d} ← {s['url']}  | {cap}")
    print()
    print("=== UNMATCHED SCRAPED URLS ===")
    for u in unmatched_urls:
        print(f"  {u['url']}  reason={u.get('reason','no caption match')}  cap={u.get('caption','')[:60]}")
    print()
    print("=== UNMATCHED BC POSTS (no URL found) ===")
    for i, used in enumerate(bc_used):
        if used:
            continue
        p = posts[i]
        cap = (p.get("caption_snippet") or "")[:60].replace("\n", " ")
        print(f"  post#{i+1:2d}  show={p.get('show','')}  views={p.get('views',0):,}  | {cap}")

    # Write URLs back into BC JSON
    for idx, s in matched_pairs:
        posts[idx]["url"] = s["url"]
        # Also fold in the fresher scraped stats? No — BC stats are reach-period truth.
        # But add scraped views as a separate field for cross-reference.
        posts[idx]["scraped_at_match"] = {
            "views": s.get("views"),
            "likes": s.get("likes"),
            "comments": s.get("comments"),
            "shares": s.get("shares"),
            "saves": s.get("saves"),
            "scraped_at": s.get("scraped_at"),
        }

    with open(BC_FILE, "w") as f:
        json.dump(bc, f, indent=2, ensure_ascii=False)
    print(f"\nWrote URLs into {BC_FILE}")


if __name__ == "__main__":
    main()

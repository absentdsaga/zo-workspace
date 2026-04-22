#!/usr/bin/env python3
"""Harvest TikTok video URLs + captions from @myvurt via stealth browser.

Uses playwright_stealth (same approach as Skills/ux-tester) to bypass TikTok's
anti-bot detection. Scrolls the profile until no new posts load, collects every
video href + the visible caption text, and writes the result to
data/tiktok_urls.json.

Run with `python3 tiktok_url_harvest.py [--scrolls 30] [--handle myvurt]`.
"""

import argparse
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

DEFAULT_HANDLE = "myvurt"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tiktok_urls.json")


def harvest(handle: str, max_scrolls: int = 50, scroll_pause: float = 1.8):
    url = f"https://www.tiktok.com/@{handle}"
    items = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            device_scale_factor=2,
            locale="en-US",
        )
        Stealth().apply_stealth_sync(ctx)
        page = ctx.new_page()
        print(f"Loading {url} ...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        for i in range(max_scrolls):
            page.mouse.wheel(0, 4000)
            time.sleep(scroll_pause)
            posts = page.query_selector_all('a[href*="/video/"]')
            for a in posts:
                href = a.get_attribute("href") or ""
                if "/video/" not in href:
                    continue
                # Caption is on the parent's sibling alt text or aria-label
                alt = ""
                try:
                    img = a.query_selector("img")
                    if img:
                        alt = img.get_attribute("alt") or ""
                except Exception:
                    pass
                items[href] = alt
            print(f"  scroll {i+1}/{max_scrolls}: {len(items)} unique URLs")

        browser.close()
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", default=DEFAULT_HANDLE)
    ap.add_argument("--scrolls", type=int, default=50)
    args = ap.parse_args()

    items = harvest(args.handle, max_scrolls=args.scrolls)
    if not items:
        print("No URLs harvested — TikTok likely blocked the session.")
        sys.exit(1)
    out = [{"url": u, "alt": a} for u, a in items.items()]
    with open(OUT, "w") as f:
        json.dump({"handle": args.handle, "harvested_at": int(time.time()), "videos": out}, f, indent=2)
    print(f"Wrote {len(out)} URLs to {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Scrape Instagram post engagement data from @myvurt"""

from playwright.sync_api import sync_playwright
import json, time, re, sys

POST_URLS = [
    # From grid, top row (pinned first, then recent)
    "https://www.instagram.com/myvurt/p/DV1nlbYEaec/",   # Ted Lucas / Real Reel (pinned)
    "https://www.instagram.com/myvurt/p/DV_jlh9kV6L/",   # TechCrunch exclusive (pinned)
    "https://www.instagram.com/myvurt/p/DWZ303UD79C/",   # "Turn your film into a series" graphic
    # Karma in Heels reel - already have data
    "https://www.instagram.com/myvurt/p/DWXJHqLEQtk/",   # Director spotlight - Steven Alan Davis / Parking Lot
    "https://www.instagram.com/myvurt/reel/DWWo3YzDSaA/", # Karma in Heels - Patricia Sandoval promo
    "https://www.instagram.com/myvurt/p/DWUuO4JD-8n/",   # "Watch it once, think about it twice"
    "https://www.instagram.com/myvurt/reel/DWUn9wCDcsf/", # SCHEMERS - Antwan Smith
    "https://www.instagram.com/myvurt/p/DWSH1GDkZV4/",   # Filmmaker Spotlight - Nita K
    "https://www.instagram.com/myvurt/reel/DWPkw_xEo-Z/", # Come Back Dad
    "https://www.instagram.com/myvurt/p/DWKbCuYke96/",   # "Great stories don't need dilution"
]

def scrape_post(page, url, idx):
    print(f"\n--- Post {idx+1}: {url} ---")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Get the full page text content
        content = page.content()
        text = page.inner_text("body")

        # Try to find likes
        likes = "unknown"
        # Look for like count patterns
        like_matches = re.findall(r'(\d[\d,]*)\s*(?:like|Like)', text)
        if like_matches:
            likes = like_matches[0]
        else:
            # Try aria labels
            like_elements = page.query_selector_all('[aria-label*="like"]')
            for el in like_elements:
                label = el.get_attribute("aria-label") or ""
                if "like" in label.lower():
                    nums = re.findall(r'(\d[\d,]*)', label)
                    if nums:
                        likes = nums[0]
                        break

        # Try views for reels
        views = "N/A"
        view_matches = re.findall(r'(\d[\d,]*)\s*(?:view|View|play|Play)', text)
        if view_matches:
            views = view_matches[0]

        # Comments count
        comments = "unknown"
        comment_matches = re.findall(r'View all (\d+) comments', text)
        if comment_matches:
            comments = comment_matches[0]
        elif "No comments" in text or "0 comments" in text.lower():
            comments = "0"

        # Post date
        date = "unknown"
        time_el = page.query_selector("time")
        if time_el:
            date = time_el.get_attribute("datetime") or time_el.get_attribute("title") or time_el.inner_text()

        # Caption snippet
        caption = "unknown"
        # Look for the caption in various ways
        cap_parts = re.findall(r'(?:myvurt|Slip N Slide Media)\s*(.*?)(?:more|\.\.\.|\n\n)', text[:3000], re.DOTALL)
        if cap_parts:
            caption = cap_parts[0][:150].strip()

        # Get visible comments/commenters
        commenters = []
        # Look for username + comment patterns in visible text

        print(f"  Likes: {likes}")
        print(f"  Views: {views}")
        print(f"  Comments: {comments}")
        print(f"  Date: {date}")
        print(f"  Caption: {caption[:100]}...")

        # Take screenshot
        ss_path = f"/home/workspace/ig_post_{idx+1}.png"
        page.screenshot(path=ss_path, full_page=False)
        print(f"  Screenshot: {ss_path}")

        # Dump some raw text for debugging
        lines = text.split('\n')
        relevant = [l.strip() for l in lines if l.strip() and len(l.strip()) > 2][:80]
        print(f"  --- Raw text excerpt (first 80 non-empty lines) ---")
        for l in relevant:
            print(f"    {l[:120]}")

        return {
            "url": url,
            "likes": likes,
            "views": views,
            "comments": comments,
            "date": date,
            "caption_snippet": caption[:150],
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"url": url, "error": str(e)}

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        results = []
        for i, url in enumerate(POST_URLS):
            r = scrape_post(page, url, i)
            results.append(r)

        browser.close()

    with open("/home/workspace/ig_scrape_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n\nDone. Results saved to ig_scrape_results.json")

if __name__ == "__main__":
    main()

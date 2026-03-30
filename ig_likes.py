#!/usr/bin/env python3
"""Get like counts from Instagram posts by dismissing cookie dialog"""

from playwright.sync_api import sync_playwright
import time, re

POST_URLS = [
    ("Ted Lucas / Real Reel (pinned)", "https://www.instagram.com/myvurt/p/DV1nlbYEaec/"),
    ("TechCrunch exclusive (pinned)", "https://www.instagram.com/myvurt/p/DV_jlh9kV6L/"),
    ("Turn your film into a series", "https://www.instagram.com/myvurt/p/DWZ303UD79C/"),
    ("Karma in Heels clip", "https://www.instagram.com/reel/DWZXh7DkYLi/"),
    ("Parking Lot Series teaser", "https://www.instagram.com/myvurt/p/DWXJHqLEQtk/"),
    ("KIH - Patricia Sandoval promo", "https://www.instagram.com/myvurt/reel/DWWo3YzDSaA/"),
    ("Watch once think twice", "https://www.instagram.com/myvurt/p/DWUuO4JD-8n/"),
    ("SCHEMERS reel", "https://www.instagram.com/myvurt/reel/DWUn9wCDcsf/"),
    ("Nita K Filmmaker Spotlight", "https://www.instagram.com/myvurt/p/DWSH1GDkZV4/"),
    ("Come Back Dad reel", "https://www.instagram.com/myvurt/reel/DWPkw_xEo-Z/"),
    ("Great stories distribution", "https://www.instagram.com/myvurt/p/DWKbCuYke96/"),
    ("Miami Kingpins (collab)", "https://www.instagram.com/officialslipnslidemedia/p/DWHK3HjADKf/"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/chromium",
        headless=True,
        args=["--no-sandbox", "--disable-gpu"]
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 1200},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    # First visit and dismiss cookies
    page.goto("https://www.instagram.com/myvurt/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    # Try to dismiss cookie dialog
    try:
        decline_btn = page.locator("text=Decline optional cookies")
        if decline_btn.count() > 0:
            decline_btn.click()
            print("Dismissed cookie dialog")
            time.sleep(1)
    except:
        print("No cookie dialog found or couldn't dismiss")

    # Try Allow all cookies button
    try:
        allow_btn = page.locator("text=Allow all cookies")
        if allow_btn.count() > 0:
            allow_btn.click()
            print("Clicked Allow all cookies")
            time.sleep(1)
    except:
        pass

    for name, url in POST_URLS:
        print(f"\n--- {name} ---")
        print(f"URL: {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            # Dismiss cookie dialog again if it appears
            try:
                decline_btn = page.locator("text=Decline optional cookies")
                if decline_btn.count() > 0:
                    decline_btn.click()
                    time.sleep(1)
            except:
                pass

            # Get page HTML for parsing
            html = page.content()
            text = page.inner_text("body")

            # Look for likes in various patterns
            likes = "?"

            # Pattern: "X likes" in text
            like_match = re.findall(r'(\d[\d,]*)\s*likes?', text)
            if like_match:
                likes = like_match[0]

            # Pattern: aria-label with likes
            if likes == "?":
                els = page.query_selector_all('section')
                for el in els:
                    try:
                        t = el.inner_text()
                        m = re.findall(r'(\d[\d,]*)\s*likes?', t)
                        if m:
                            likes = m[0]
                            break
                    except:
                        pass

            # Check for "liked by X and Y others" pattern
            if likes == "?":
                others_match = re.findall(r'and\s+(\d[\d,]*)\s+others?', text)
                if others_match:
                    likes = f"{others_match[0]}+ (and others)"

            # Views for reels
            views = "N/A"
            view_match = re.findall(r'(\d[\d,]*)\s*(?:views?|plays?)', text, re.IGNORECASE)
            if view_match:
                views = view_match[0]

            # Also check for standalone numbers near play icons in reels
            # The number "136" appeared in SCHEMERS and "591" in Come Back Dad raw text

            # Comments
            comments = "0"
            comment_match = re.findall(r'View all (\d+) comments', text)
            if comment_match:
                comments = comment_match[0]
            elif "No comments yet" in text:
                comments = "0"
            else:
                # Count visible comment usernames
                visible_comments = text.count("Like\nReply")
                if visible_comments > 0:
                    comments = f"{visible_comments}+"

            # Screenshot without cookie dialog
            ss_name = name.replace(" ", "_").replace("/", "-")[:30]
            page.screenshot(path=f"/home/workspace/ig_clean_{ss_name}.png", full_page=False)

            print(f"  Likes: {likes}")
            print(f"  Views: {views}")
            print(f"  Comments: {comments}")

        except Exception as e:
            print(f"  ERROR: {e}")

    browser.close()

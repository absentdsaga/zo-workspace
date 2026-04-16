#!/usr/bin/env python3
"""
Tracking Audit — captures all tracking/analytics telemetry on a page.
Uses stealth browser to get past bot walls + age gates.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.myvurt.com"
OUT_DIR = Path("/home/workspace/Skills/ux-tester/reports/tracking-audit")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Tracking-related domains/paths to flag
TRACKING_PATTERNS = {
    "GA4": ["google-analytics.com/g/collect", "googletagmanager.com/gtag/js"],
    "GTM": ["googletagmanager.com/gtm.js"],
    "Meta Pixel": ["facebook.com/tr", "connect.facebook.net"],
    "TikTok Pixel": ["analytics.tiktok.com", "analytics-sg.tiktok.com"],
    "Firebase Analytics": ["firebaselogging-pa.googleapis.com", "firebaseinstallations.googleapis.com"],
    "Firebase Auth": ["identitytoolkit.googleapis.com", "securetoken.googleapis.com"],
    "Firebase Core": ["firebaseio.com", "firebase.googleapis.com"],
    "NPAW/Nice People": ["nicepeopleatwork.com", "npaw.com"],
    "Mux": ["mux.com", "litix.io"],
    "Hotjar": ["hotjar.com", "static.hotjar.com"],
    "Segment": ["segment.com", "segment.io"],
    "LinkedIn": ["px.ads.linkedin.com", "snap.licdn.com"],
    "Pinterest": ["ct.pinterest.com"],
    "Twitter/X": ["static.ads-twitter.com", "t.co/i/adsct"],
    "Snapchat": ["sc-static.net", "tr.snapchat.com"],
}

def classify(url):
    matches = []
    for category, patterns in TRACKING_PATTERNS.items():
        for p in patterns:
            if p in url:
                matches.append(category)
                break
    return matches

def main():
    network_log = []
    script_srcs = []

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            device_scale_factor=2,
        )
        page = context.new_page()

        # Capture all network requests
        def on_request(request):
            network_log.append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
                "categories": classify(request.url),
            })

        page.on("request", on_request)

        print(f"[*] Navigating to {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)  # let scripts settle

        # Try to click past age gate
        print("[*] Looking for age gate / modal buttons")
        for selector in [
            "button:has-text('Yes')",
            "button:has-text('I am')",
            "button:has-text('Enter')",
            "button:has-text('Accept')",
            "button:has-text('Confirm')",
            "button:has-text('Continue')",
        ]:
            try:
                btn = page.query_selector(selector)
                if btn and btn.is_visible():
                    print(f"    clicking: {selector}")
                    btn.click()
                    time.sleep(3)
                    break
            except Exception:
                pass

        time.sleep(5)  # more events may fire after age gate

        # Capture window state
        print("[*] Dumping window.dataLayer")
        try:
            data_layer = page.evaluate("() => JSON.stringify(window.dataLayer || [], null, 2)")
        except Exception as e:
            data_layer = f"ERROR: {e}"

        print("[*] Checking window.firebase")
        try:
            firebase_info = page.evaluate("""() => {
                const result = { detected: false };
                if (typeof firebase !== 'undefined') {
                    result.detected = true;
                    try {
                        result.apps = firebase.apps.map(app => ({
                            name: app.name,
                            options: app.options
                        }));
                    } catch(e) { result.error = e.toString(); }
                }
                if (window.firebase_config) result.firebase_config = window.firebase_config;
                return result;
            }""")
        except Exception as e:
            firebase_info = {"error": str(e)}

        print("[*] Checking gtag / GA4")
        try:
            gtag_info = page.evaluate("""() => {
                return {
                    gtag_defined: typeof gtag === 'function',
                    google_tag_data: typeof google_tag_data !== 'undefined',
                    ga_cookies: document.cookie.split(';').filter(c => c.trim().startsWith('_ga')).map(c => c.trim())
                };
            }""")
        except Exception as e:
            gtag_info = {"error": str(e)}

        print("[*] Checking fbq / ttq")
        try:
            pixel_info = page.evaluate("""() => {
                return {
                    fbq_defined: typeof fbq === 'function',
                    ttq_defined: typeof ttq === 'object' || typeof ttq === 'function',
                    TiktokAnalyticsObject: window.TiktokAnalyticsObject || null
                };
            }""")
        except Exception as e:
            pixel_info = {"error": str(e)}

        print("[*] Capturing script src URLs")
        try:
            script_srcs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
            }""")
        except Exception as e:
            script_srcs = [f"ERROR: {e}"]

        print("[*] Capturing all cookies")
        cookies = context.cookies()

        print("[*] Getting final URL + HTML size")
        final_url = page.url
        html_size = page.evaluate("() => document.documentElement.outerHTML.length")

        print("[*] Saving screenshot")
        page.screenshot(path=str(OUT_DIR / "final-page.png"), full_page=False)

        # Also check meta verification tags in head
        print("[*] Looking for domain verification meta tags")
        meta_tags = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('meta')).map(m => ({
                name: m.getAttribute('name'),
                property: m.getAttribute('property'),
                content: m.getAttribute('content')
            })).filter(m => m.name || m.property);
        }""")

        browser.close()

    # Analyze network log
    tracking_by_category = {}
    for req in network_log:
        for cat in req["categories"]:
            tracking_by_category.setdefault(cat, []).append(req["url"])

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "requested_url": URL,
        "final_url": final_url,
        "html_size": html_size,
        "total_network_requests": len(network_log),
        "tracking_firing": {
            cat: {"count": len(urls), "sample_urls": urls[:5]}
            for cat, urls in tracking_by_category.items()
        },
        "window_state": {
            "dataLayer_raw": data_layer[:5000] if isinstance(data_layer, str) else data_layer,
            "firebase": firebase_info,
            "gtag_ga4": gtag_info,
            "fb_tt_pixels": pixel_info,
        },
        "script_srcs": script_srcs,
        "cookies": [{"name": c["name"], "domain": c["domain"]} for c in cookies],
        "meta_tags_head": [m for m in meta_tags if m.get("content")],
    }

    out_file = OUT_DIR / f"tracking-audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] Saved: {out_file}")
    print(f"\n=== TRACKING SUMMARY ===")
    for cat, data in tracking_by_category.items():
        print(f"  {cat}: {len(data)} requests")
    print(f"\n=== WINDOW GLOBALS ===")
    print(f"  gtag defined: {gtag_info.get('gtag_defined')}")
    print(f"  fbq defined: {pixel_info.get('fbq_defined')}")
    print(f"  ttq defined: {pixel_info.get('ttq_defined')}")
    print(f"  firebase detected: {firebase_info.get('detected')}")
    print(f"  GA cookies: {gtag_info.get('ga_cookies')}")

if __name__ == "__main__":
    main()

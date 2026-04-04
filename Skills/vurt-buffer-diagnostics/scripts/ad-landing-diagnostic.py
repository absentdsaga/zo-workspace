#!/usr/bin/env python3
"""Full diagnostic of the VURT ad landing experience.
Simulates real ad traffic, interacts with age gate, measures everything."""

import json, time, sys, os
from playwright.sync_api import sync_playwright

LANDING_PAGES = [
    "/detail/micro_series/come-back-dad?fbclid=PAZXh0bgNhZW0test",
    "/detail/micro_series/favorite-son?fbclid=PAZXh0bgNhZW0test",
    "/detail/micro_series/girl-in-the-closet?fbclid=PAZXh0bgNhZW0test",
    "/detail/micro_series/karma-in-heels?fbclid=PAZXh0bgNhZW0test",
    "/?fbclid=PAZXh0bgNhZW0test",
]

BASE = "https://www.myvurt.com"

def run_diagnostic(page_path, browser, run_id):
    url = BASE + page_path
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    page = context.new_page()

    # Track all network requests
    tracking_requests = []
    all_requests = []
    failed_requests = []
    
    def on_request(req):
        all_requests.append({"url": req.url[:150], "method": req.method, "type": req.resource_type})
        if any(x in req.url for x in ["facebook", "fbevents", "google-analytics", "googletagmanager", "gtm.js", "analytics.google", "connect.facebook"]):
            tracking_requests.append({"url": req.url[:150], "ts": time.time()})
    
    def on_response(resp):
        if resp.status >= 400:
            failed_requests.append({"url": resp.url[:120], "status": resp.status})
    
    def on_request_failed(req):
        failed_requests.append({"url": req.url[:120], "failure": req.failure})

    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)

    # Console errors
    console_errors = []
    def on_console(msg):
        if msg.type in ("error", "warning"):
            console_errors.append(msg.text[:200])
    page.on("console", on_console)

    result = {
        "url": page_path,
        "timestamps": {},
        "tracking": {},
        "content": {},
        "errors": [],
        "screenshots": []
    }

    # PHASE 1: Initial page load
    t0 = time.time()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        result["errors"].append(f"Navigation error: {e}")
        context.close()
        return result
    
    t_dom = time.time() - t0
    result["timestamps"]["dom_content_loaded"] = round(t_dom, 2)

    # Wait for network idle
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except:
        pass
    t_idle = time.time() - t0
    result["timestamps"]["network_idle"] = round(t_idle, 2)

    # Screenshot 1: What user sees on first load
    ss1 = f"/tmp/vurt-diag-{run_id}-phase1.png"
    page.screenshot(path=ss1, full_page=False)
    result["screenshots"].append(ss1)

    # What's visible?
    body_text = page.inner_text("body")[:500]
    result["content"]["initial_body_text"] = body_text
    result["content"]["initial_body_length"] = len(page.inner_text("body"))

    # Check for age gate / registration / modals
    age_gate_visible = False
    signup_visible = False
    video_visible = False
    
    # Look for age verification
    for selector in [".age-gate", ".age-verify", "[class*='parental']", "[class*='age']", "[class*='verify']"]:
        try:
            els = page.query_selector_all(selector)
            for el in els:
                if el.is_visible():
                    txt = el.inner_text()[:100]
                    if any(w in txt.lower() for w in ["age", "17", "18", "verify", "confirm", "born", "year"]):
                        age_gate_visible = True
                        result["content"]["age_gate_text"] = txt
        except:
            pass

    # Look for signup/registration modal
    for selector in ["[class*='signup']", "[class*='sign-up']", "[class*='register']", "[class*='modal']"]:
        try:
            els = page.query_selector_all(selector)
            for el in els:
                if el.is_visible():
                    txt = el.inner_text()[:200]
                    if any(w in txt.lower() for w in ["sign up", "register", "create account", "full name", "email", "password"]):
                        signup_visible = True
                        result["content"]["signup_text"] = txt[:200]
        except:
            pass

    # Look for video player
    for selector in ["video", "[class*='player']", "[class*='video']", "vjs-", ".vjs-tech"]:
        try:
            els = page.query_selector_all(selector)
            for el in els:
                if el.is_visible():
                    video_visible = True
        except:
            pass

    result["content"]["age_gate_visible"] = age_gate_visible
    result["content"]["signup_visible"] = signup_visible
    result["content"]["video_visible"] = video_visible

    # PHASE 2: Try to dismiss age gate if present
    dismissed = False
    if age_gate_visible or "age" in body_text.lower() or "17" in body_text or "verify" in body_text.lower():
        # Try common dismiss buttons
        for btn_text in ["Yes", "I am 17", "I'm 17", "Confirm", "Enter", "Continue", "I agree", "Yes, I am", "I am over"]:
            try:
                btn = page.get_by_text(btn_text, exact=False)
                if btn.is_visible():
                    btn.click()
                    dismissed = True
                    time.sleep(2)
                    break
            except:
                pass
        
        if not dismissed:
            # Try clicking any visible button in the gate area
            try:
                buttons = page.query_selector_all("button")
                for btn in buttons:
                    if btn.is_visible():
                        txt = btn.inner_text().lower()
                        if any(w in txt for w in ["yes", "confirm", "enter", "continue", "agree", "17", "18"]):
                            btn.click()
                            dismissed = True
                            time.sleep(2)
                            break
            except:
                pass

    result["content"]["age_gate_dismissed"] = dismissed

    # PHASE 3: After age gate - what do we see?
    if dismissed:
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        time.sleep(2)
        
        ss2 = f"/tmp/vurt-diag-{run_id}-phase2.png"
        page.screenshot(path=ss2, full_page=False)
        result["screenshots"].append(ss2)
        
        body_text2 = page.inner_text("body")[:500]
        result["content"]["post_gate_body_text"] = body_text2
        result["content"]["post_gate_body_length"] = len(page.inner_text("body"))
        
        # Check for video now
        for selector in ["video", ".vjs-tech", "[class*='player']"]:
            try:
                els = page.query_selector_all(selector)
                for el in els:
                    if el.is_visible():
                        result["content"]["video_visible_after_gate"] = True
            except:
                pass

        # Check for signup wall after age gate
        for selector in ["[class*='signup']", "[class*='sign-up']", "[class*='modal']"]:
            try:
                els = page.query_selector_all(selector)
                for el in els:
                    if el.is_visible():
                        txt = el.inner_text()[:200]
                        if any(w in txt.lower() for w in ["sign up", "register", "full name", "email", "password"]):
                            result["content"]["signup_after_gate"] = True
                            result["content"]["signup_after_gate_text"] = txt[:200]
            except:
                pass

    # Phase 4: Check if there's a SECOND gate (signup after age)
    if result["content"].get("signup_after_gate"):
        ss3 = f"/tmp/vurt-diag-{run_id}-phase3-signup.png"
        page.screenshot(path=ss3, full_page=False)
        result["screenshots"].append(ss3)

    # Performance metrics
    try:
        perf = page.evaluate("""() => {
            const nav = performance.getEntriesByType("navigation")[0];
            const resources = performance.getEntriesByType("resource");
            const totalTransfer = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
            const jsResources = resources.filter(r => r.initiatorType === "script" || r.name.includes(".js"));
            const jsTransfer = jsResources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
            return {
                domInteractive: Math.round(nav.domInteractive),
                domContentLoaded: Math.round(nav.domContentLoadedEventEnd),
                loadComplete: Math.round(nav.loadEventEnd),
                htmlTransfer: Math.round(nav.transferSize / 1024),
                totalResources: resources.length,
                totalTransferKB: Math.round(totalTransfer / 1024),
                jsTransferKB: Math.round(jsTransfer / 1024),
                jsFiles: jsResources.length
            }
        }""")
        result["performance"] = perf
    except Exception as e:
        result["errors"].append(f"Perf error: {e}")

    # Tracking summary
    result["tracking"]["total_requests"] = len(tracking_requests)
    result["tracking"]["ga4_fired"] = any("google-analytics" in r["url"] or "analytics.google" in r["url"] for r in tracking_requests)
    result["tracking"]["meta_pixel_fired"] = any("facebook" in r["url"] or "fbevents" in r["url"] for r in tracking_requests)
    result["tracking"]["gtm_loaded"] = any("googletagmanager" in r["url"] for r in tracking_requests)
    result["tracking"]["requests"] = [r["url"] for r in tracking_requests]
    
    result["errors"].extend([f"Failed: {r['url']} ({r.get('status', r.get('failure', '?'))})" for r in failed_requests[:10]])
    result["console_errors"] = console_errors[:10]
    result["network"] = {"total_requests": len(all_requests)}

    context.close()
    return result


def main():
    print("=" * 70)
    print("VURT AD LANDING DIAGNOSTIC")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        
        all_results = []
        for i, path in enumerate(LANDING_PAGES):
            print(f"\n--- Testing: {path[:60]} ---")
            result = run_diagnostic(path, browser, i)
            all_results.append(result)
            
            # Print summary
            print(f"  Load: DOM={result['timestamps'].get('dom_content_loaded','?')}s, Idle={result['timestamps'].get('network_idle','?')}s")
            print(f"  Tracking: GTM={result['tracking'].get('gtm_loaded')}, GA4={result['tracking'].get('ga4_fired')}, Pixel={result['tracking'].get('meta_pixel_fired')}")
            print(f"  Age gate visible: {result['content'].get('age_gate_visible')}")
            print(f"  Signup visible: {result['content'].get('signup_visible')}")
            print(f"  Video visible: {result['content'].get('video_visible')}")
            print(f"  Age gate dismissed: {result['content'].get('age_gate_dismissed')}")
            if result['content'].get('signup_after_gate'):
                print(f"  *** SIGNUP WALL AFTER AGE GATE ***")
                print(f"  Signup text: {result['content'].get('signup_after_gate_text','')[:100]}")
            if result['content'].get('video_visible_after_gate'):
                print(f"  Video visible after gate: True")
            if result.get('performance'):
                perf = result['performance']
                print(f"  Perf: DOMi={perf.get('domInteractive')}ms, Load={perf.get('loadComplete')}ms, JS={perf.get('jsTransferKB')}KB/{perf.get('jsFiles')} files, Total={perf.get('totalTransferKB')}KB")
            if result['errors']:
                print(f"  Errors: {result['errors'][:3]}")
            if result['console_errors']:
                print(f"  Console errors: {len(result['console_errors'])}")
                for e in result['console_errors'][:3]:
                    print(f"    {e[:120]}")
            print(f"  Screenshots: {result['screenshots']}")

        browser.close()
    
    # Save full results
    out = "/tmp/vurt-ad-diagnostic.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nFull results saved to {out}")


if __name__ == "__main__":
    main()

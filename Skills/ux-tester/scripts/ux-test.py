#!/usr/bin/env python3
"""
UX Tester — Stealth browser testing that sees what real users see.
Uses Playwright with anti-detection to bypass bot walls.
"""

import argparse
import json
import os
import sys
import time
import random
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

DEVICES = {
    "desktop": {
        "viewport": {"width": 1440, "height": 900},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "device_scale_factor": 2,
        "is_mobile": False,
        "has_touch": False,
    },
    "iphone-14": {
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "iphone-15-pro": {
        "viewport": {"width": 393, "height": 852},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "pixel-7": {
        "viewport": {"width": 412, "height": 915},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "device_scale_factor": 2.625,
        "is_mobile": True,
        "has_touch": True,
    },
    "ipad": {
        "viewport": {"width": 820, "height": 1180},
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
    },
    "galaxy-s24": {
        "viewport": {"width": 360, "height": 780},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "galaxy-a54": {
        "viewport": {"width": 412, "height": 915},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "device_scale_factor": 2.625,
        "is_mobile": True,
        "has_touch": True,
    },
    "iphone-se": {
        "viewport": {"width": 375, "height": 667},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
    },
    "iphone-15-pro-max": {
        "viewport": {"width": 430, "height": 932},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "galaxy-s23-fe": {
        "viewport": {"width": 360, "height": 780},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S711B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
}

COMMON_MODAL_SELECTORS = [
    # Close buttons
    'button[aria-label="Close"]',
    'button[aria-label="close"]',
    'button[class*="close"]',
    'button[class*="Close"]',
    '[class*="modal"] button[class*="close"]',
    '[class*="modal"] [class*="dismiss"]',
    '[class*="popup"] button[class*="close"]',
    '.modal-close',
    '#close-modal',
    'button.close',
    # X buttons (text content)
    'button:has-text("×")',
    'button:has-text("✕")',
    'button:has-text("X")',
    # Cookie/consent
    'button:has-text("Accept")',
    'button:has-text("Got it")',
    'button:has-text("I agree")',
    'button:has-text("OK")',
    'button:has-text("Continue")',
    '#onetrust-accept-btn-handler',
    '.cookie-consent-accept',
    # Age gates
    'button:has-text("Yes")',
    'button:has-text("I am 17")',
    'button:has-text("I am 18")',
    'button:has-text("Yes, I am")',
    'button:has-text("Enter")',
]


def human_delay(min_ms=500, max_ms=1500):
    """Random delay to mimic human behavior."""
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


def try_dismiss_overlays(page, step_log):
    """Try to dismiss modals, popups, cookie banners, age gates."""
    dismissed = []
    for selector in COMMON_MODAL_SELECTORS:
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=300):
                text = el.text_content() or selector
                el.click(timeout=1000)
                dismissed.append(text.strip()[:50])
                human_delay(800, 1500)
        except Exception:
            continue
    if dismissed:
        step_log.append(f"Dismissed overlays: {', '.join(dismissed)}")
    return dismissed


def measure_performance(page):
    """Extract Web Vitals and performance metrics."""
    metrics = {}
    try:
        timing = page.evaluate("""() => {
            const nav = performance.getEntriesByType('navigation')[0] || {};
            const paint = performance.getEntriesByType('paint') || [];
            const fcp = paint.find(e => e.name === 'first-contentful-paint');
            return {
                ttfb: nav.responseStart ? Math.round(nav.responseStart - nav.requestStart) : null,
                dom_content_loaded: nav.domContentLoadedEventEnd ? Math.round(nav.domContentLoadedEventEnd - nav.startTime) : null,
                load_complete: nav.loadEventEnd ? Math.round(nav.loadEventEnd - nav.startTime) : null,
                fcp: fcp ? Math.round(fcp.startTime) : null,
                dom_nodes: document.querySelectorAll('*').length,
                document_height: document.documentElement.scrollHeight,
                viewport_height: window.innerHeight,
                images_total: document.images.length,
                images_loaded: Array.from(document.images).filter(i => i.complete).length,
                scripts: document.scripts.length,
                stylesheets: document.styleSheets.length,
            };
        }""")
        metrics.update(timing)
    except Exception as e:
        metrics["error"] = str(e)

    # Try LCP via PerformanceObserver (may not be available)
    try:
        lcp = page.evaluate("""() => {
            return new Promise(resolve => {
                new PerformanceObserver(list => {
                    const entries = list.getEntries();
                    resolve(entries.length ? Math.round(entries[entries.length-1].startTime) : null);
                }).observe({type: 'largest-contentful-paint', buffered: true});
                setTimeout(() => resolve(null), 2000);
            });
        }""")
        metrics["lcp"] = lcp
    except Exception:
        pass

    return metrics


def capture_step(page, output_dir, step_num, name, full_page=False):
    """Capture a screenshot for a step."""
    filename = f"{step_num:02d}-{name}.png"
    filepath = output_dir / filename
    page.screenshot(path=str(filepath), full_page=full_page)
    return filename


def detect_page_elements(page):
    """Detect what's on the page — modals, videos, forms, etc."""
    elements = page.evaluate("""() => {
        const found = [];
        // Modals/overlays
        const modals = document.querySelectorAll('[class*="modal"], [class*="overlay"], [class*="popup"], [role="dialog"]');
        modals.forEach(m => {
            const style = window.getComputedStyle(m);
            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                found.push({type: 'modal', classes: m.className?.toString().slice(0, 100), visible: true});
            }
        });
        // Video players
        const videos = document.querySelectorAll('video, [class*="player"], iframe[src*="mux"], iframe[src*="youtube"], iframe[src*="vimeo"]');
        videos.forEach(v => found.push({type: 'video', tag: v.tagName, src: (v.src || v.getAttribute('src') || '').slice(0, 100)}));
        // Forms
        const forms = document.querySelectorAll('form, [class*="signup"], [class*="register"], [class*="login"]');
        forms.forEach(f => found.push({type: 'form', classes: f.className?.toString().slice(0, 100), action: f.action?.slice(0, 100)}));
        // Age gates
        const ageGate = document.querySelectorAll('[class*="age"], [class*="verify"], [class*="gate"]');
        ageGate.forEach(a => {
            const style = window.getComputedStyle(a);
            if (style.display !== 'none') found.push({type: 'age-gate', classes: a.className?.toString().slice(0, 100)});
        });
        // Images count
        found.push({type: 'stats', images: document.images.length, links: document.links.length, buttons: document.querySelectorAll('button').length});
        return found;
    }""")
    return elements


def run_ux_test(url, device_name, flow, output_dir, wait_time, click_selectors, full_page, measure):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_lines = []
    step_log = []
    step_num = 0
    screenshots = []
    perf_metrics = {}

    report_lines.append(f"# UX Test Report")
    report_lines.append(f"**URL:** {url}")
    report_lines.append(f"**Device:** {device_name}")
    report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    device = DEVICES.get(device_name, DEVICES["desktop"])

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--window-size=1440,900",
            ],
        )

        context = browser.new_context(
            viewport=device["viewport"],
            user_agent=device["user_agent"],
            device_scale_factor=device.get("device_scale_factor", 1),
            is_mobile=device.get("is_mobile", False),
            has_touch=device.get("has_touch", False),
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            color_scheme="dark",
        )

        # Extra stealth: override webdriver property
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        # Navigate
        print(f"[1] Navigating to {url}...")
        start_time = time.time()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(int(wait_time * 1000))
            load_time = round(time.time() - start_time, 2)
        except Exception as e:
            load_time = round(time.time() - start_time, 2)
            step_log.append(f"Navigation warning: {e}")

        step_num += 1
        fname = capture_step(page, output_dir, step_num, "initial-load", full_page)
        screenshots.append(fname)
        step_log.append(f"Page loaded in {load_time}s")
        print(f"    Loaded in {load_time}s")

        # Detect elements
        elements = detect_page_elements(page)
        visible_modals = [e for e in elements if e.get("type") == "modal" and e.get("visible")]
        videos = [e for e in elements if e.get("type") == "video"]
        forms = [e for e in elements if e.get("type") == "form"]
        age_gates = [e for e in elements if e.get("type") == "age-gate"]

        report_lines.append("## Initial Page State")
        report_lines.append(f"- Load time: **{load_time}s**")
        report_lines.append(f"- Visible modals: **{len(visible_modals)}**")
        report_lines.append(f"- Video players: **{len(videos)}**")
        report_lines.append(f"- Forms/signups: **{len(forms)}**")
        report_lines.append(f"- Age gates: **{len(age_gates)}**")
        report_lines.append(f"- Screenshot: `{fname}`")
        report_lines.append("")

        if visible_modals:
            report_lines.append("### Detected Modals")
            for m in visible_modals:
                report_lines.append(f"- `{m.get('classes', 'unknown')}`")
            report_lines.append("")

        # Flow mode: interact with the page
        if flow:
            report_lines.append("## UX Flow Steps")
            report_lines.append("")

            # Step: Try dismissing overlays
            print(f"[2] Checking for overlays/modals...")
            dismissed = try_dismiss_overlays(page, step_log)
            if dismissed:
                step_num += 1
                human_delay(1000, 2000)
                fname = capture_step(page, output_dir, step_num, "after-dismiss", full_page)
                screenshots.append(fname)
                report_lines.append(f"### Step {step_num}: Dismissed Overlays")
                report_lines.append(f"- Dismissed: {', '.join(dismissed)}")
                report_lines.append(f"- Screenshot: `{fname}`")
                report_lines.append("")
                print(f"    Dismissed: {', '.join(dismissed)}")

                # Check for more overlays after dismissal (age gate after signup modal, etc.)
                print(f"[{step_num+1}] Checking for secondary overlays...")
                dismissed2 = try_dismiss_overlays(page, step_log)
                if dismissed2:
                    step_num += 1
                    human_delay(1000, 2000)
                    fname = capture_step(page, output_dir, step_num, "after-dismiss-2", full_page)
                    screenshots.append(fname)
                    report_lines.append(f"### Step {step_num}: Dismissed Secondary Overlays")
                    report_lines.append(f"- Dismissed: {', '.join(dismissed2)}")
                    report_lines.append(f"- Screenshot: `{fname}`")
                    report_lines.append("")
                    print(f"    Dismissed: {', '.join(dismissed2)}")
            else:
                report_lines.append("### No overlays detected")
                report_lines.append("")
                print("    No overlays found")

            # Step: Scroll down to see more content
            print(f"[{step_num+1}] Scrolling page...")
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            human_delay(1500, 2500)
            step_num += 1
            fname = capture_step(page, output_dir, step_num, "after-scroll-1", full_page)
            screenshots.append(fname)
            report_lines.append(f"### Step {step_num}: Scrolled Down")
            report_lines.append(f"- Screenshot: `{fname}`")
            report_lines.append("")

            # Scroll more
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            human_delay(1000, 2000)
            step_num += 1
            fname = capture_step(page, output_dir, step_num, "after-scroll-2", full_page)
            screenshots.append(fname)

            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            human_delay(500, 1000)

            # Re-detect elements after flow
            elements_after = detect_page_elements(page)
            videos_after = [e for e in elements_after if e.get("type") == "video"]
            report_lines.append(f"### After Flow State")
            report_lines.append(f"- Video players visible: **{len(videos_after)}**")
            report_lines.append("")

        # Custom click selectors
        for selector in click_selectors:
            try:
                print(f"[click] Clicking: {selector}")
                page.click(selector, timeout=5000)
                human_delay(1000, 2000)
                step_num += 1
                safe_name = selector.replace(" ", "-").replace('"', "").replace("'", "")[:30]
                fname = capture_step(page, output_dir, step_num, f"click-{safe_name}", full_page)
                screenshots.append(fname)
                step_log.append(f"Clicked: {selector}")
            except Exception as e:
                step_log.append(f"Failed to click {selector}: {e}")
                print(f"    Failed: {e}")

        # Performance metrics
        if measure:
            print(f"[perf] Measuring performance...")
            perf_metrics = measure_performance(page)
            report_lines.append("## Performance Metrics")
            for k, v in perf_metrics.items():
                if v is not None:
                    label = k.replace("_", " ").title()
                    unit = "ms" if k in ("ttfb", "fcp", "lcp", "dom_content_loaded", "load_complete") else ""
                    unit = "px" if k in ("document_height", "viewport_height") else unit
                    report_lines.append(f"- **{label}:** {v}{unit}")
            report_lines.append("")

            # Save raw metrics
            with open(output_dir / "metrics.json", "w") as f:
                json.dump(perf_metrics, f, indent=2)

        # Final full-page screenshot
        step_num += 1
        fname = capture_step(page, output_dir, step_num, "final", True)
        screenshots.append(fname)
        report_lines.append("## Final State")
        report_lines.append(f"- Full-page screenshot: `{fname}`")
        report_lines.append(f"- Current URL: `{page.url}`")
        report_lines.append("")

        # Step log
        if step_log:
            report_lines.append("## Log")
            for entry in step_log:
                report_lines.append(f"- {entry}")
            report_lines.append("")

        browser.close()

    # Write report
    report_path = output_dir / "report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    print(f"\n✓ Report: {report_path}")
    print(f"✓ Screenshots: {len(screenshots)} captured in {output_dir}")
    if perf_metrics:
        ttfb = perf_metrics.get("ttfb")
        fcp = perf_metrics.get("fcp")
        lcp = perf_metrics.get("lcp")
        print(f"✓ TTFB: {ttfb}ms | FCP: {fcp}ms | LCP: {lcp}ms")

    return str(report_path)


def main():
    parser = argparse.ArgumentParser(description="UX Tester — See what real users see")
    parser.add_argument("url", help="URL to test")
    parser.add_argument("--device", default="desktop", choices=list(DEVICES.keys()), help="Device to simulate")
    parser.add_argument("--flow", action="store_true", help="Run full UX flow (dismiss modals, scroll, interact)")
    parser.add_argument("--output", default=None, help="Output directory for screenshots and report")
    parser.add_argument("--wait", type=float, default=3, help="Extra wait seconds after load")
    parser.add_argument("--click", action="append", default=[], help="CSS selector to click (can repeat)")
    parser.add_argument("--full-page", action="store_true", help="Full-page screenshots")
    parser.add_argument("--measure", action="store_true", help="Capture performance metrics")

    args = parser.parse_args()

    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = args.url.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")[:40]
        args.output = f"/home/workspace/Skills/ux-tester/reports/{slug}_{args.device}_{timestamp}"

    run_ux_test(
        url=args.url,
        device_name=args.device,
        flow=args.flow,
        output_dir=args.output,
        wait_time=args.wait,
        click_selectors=args.click,
        full_page=args.full_page,
        measure=args.measure,
    )


if __name__ == "__main__":
    main()

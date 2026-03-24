#!/usr/bin/env python3
"""
Grafana Dashboard Monitor for Saga DAO Validator

Captures screenshots of the Solana monitoring Grafana dashboard using Playwright.
Supports configurable time ranges, saves to dated directories, and extracts
visible metric values from panel titles/legends where possible.

Requirements:
  - playwright (pip-installed)
  - chromium at /usr/bin/chromium

Usage:
  python3 grafana-monitor.py --help
  python3 grafana-monitor.py --range 1h
  python3 grafana-monitor.py --range 6h --output /path/to/dir
  python3 grafana-monitor.py --snapshot          # capture + extract metrics
  python3 grafana-monitor.py --panels            # capture individual panels
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Constants ----------------------------------------------------------------

DASHBOARD_URL = (
    "https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring"
    "?orgId=2&var-cluster=mainnet-beta&var-server=saga-mainnet"
)

VALIDATOR_IDENTITY = "SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ"
VOTE_ACCOUNT = "sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw"

# Grafana displays in EDT (UTC-4)
GRAFANA_TZ_OFFSET_HOURS = -4

# Time range param mapping for Grafana URL
TIME_RANGES = {
    "5m":  "now-5m",
    "15m": "now-15m",
    "30m": "now-30m",
    "1h":  "now-1h",
    "3h":  "now-3h",
    "6h":  "now-6h",
    "12h": "now-12h",
    "24h": "now-24h",
    "2d":  "now-2d",
    "7d":  "now-7d",
    "30d": "now-30d",
}

# Key panels to look for (by partial panel title text)
KEY_PANELS = [
    "Last Vote Distance",
    "Root Slot Distance",
    "Credits",
    "UDP",
    "Load Average",
    "Skip",
    "Vote Latency",
    "Slot Processing",
    "Activated Stake",
    "Epoch",
]

DEFAULT_OUTPUT_BASE = "/home/workspace/Skills/validator-diagnostics/snapshots"

CHROMIUM_PATH = "/usr/bin/chromium"


# -- Helpers ------------------------------------------------------------------

def build_url(time_range="1h"):
    """Build Grafana URL with the given time range."""
    from_param = TIME_RANGES.get(time_range, f"now-{time_range}")
    return f"{DASHBOARD_URL}&from={from_param}&to=now"


def ensure_output_dir(base_path=None):
    """Create a dated output directory and return its path."""
    base = Path(base_path) if base_path else Path(DEFAULT_OUTPUT_BASE)
    now = datetime.now(timezone.utc)
    dated_dir = base / now.strftime("%Y-%m-%d")
    dated_dir.mkdir(parents=True, exist_ok=True)
    return dated_dir


def utc_now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def edt_now_str():
    edt = timezone(timedelta(hours=GRAFANA_TZ_OFFSET_HOURS))
    return datetime.now(edt).strftime("%Y-%m-%d %H:%M:%S EDT")


# -- Browser Automation -------------------------------------------------------

def launch_browser():
    """Launch a headless Chromium browser via Playwright."""
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        executable_path=CHROMIUM_PATH,
        headless=True,
        args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
    )
    return pw, browser


def capture_full_dashboard(page, output_dir, time_range, label=""):
    """Capture a full-page screenshot of the Grafana dashboard."""
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    suffix = f"-{label}" if label else ""
    filename = f"grafana-{time_range}{suffix}-{timestamp}.png"
    filepath = output_dir / filename

    page.screenshot(path=str(filepath), full_page=True)
    print(f"  Saved: {filepath}")
    return filepath


def capture_individual_panels(page, output_dir, time_range):
    """Attempt to capture screenshots of individual Grafana panels."""
    panels_found = []

    # Grafana panels are typically in .panel-container or [data-panelid] elements
    panel_selectors = [
        ".react-grid-item",
        "[data-panelid]",
        ".panel-container",
    ]

    panels = []
    for selector in panel_selectors:
        panels = page.query_selector_all(selector)
        if panels:
            break

    if not panels:
        print("  No individual panels found via DOM selectors.")
        return panels_found

    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")

    for i, panel in enumerate(panels):
        try:
            # Try to get panel title
            title_el = panel.query_selector(
                ".panel-title-text, [data-testid='header-container'] h2, "
                ".panel-header .panel-title, h6"
            )
            title = title_el.inner_text().strip() if title_el else f"panel-{i}"

            # Sanitize title for filename
            safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title)[:50].strip('_')
            if not safe_title:
                safe_title = f"panel-{i}"

            filename = f"panel-{safe_title}-{time_range}-{timestamp}.png"
            filepath = output_dir / filename

            panel.screenshot(path=str(filepath))
            panels_found.append({
                "title": title,
                "file": str(filepath),
                "index": i,
            })
            print(f"  Panel {i}: {title} -> {filepath}")
        except Exception as e:
            print(f"  Panel {i}: capture failed ({e})")

    return panels_found


def extract_visible_metrics(page):
    """
    Extract visible metric values from the Grafana dashboard.
    Looks for stat panels, gauge values, and text content in known panel types.
    Returns a dict of metric_name -> value.
    """
    metrics = {}

    # Strategy 1: Look for stat/gauge panel values (big numbers)
    value_selectors = [
        ".react-grid-item .css-1rv116u",      # Grafana stat value
        ".react-grid-item .singlestat-panel-value",
        "[data-testid='data-testid Panel header Last Vote Distance'] ~ div",
        ".panel-content .flot-text",
        ".react-grid-item [style*='font-size']",
    ]

    # Strategy 2: Get all text from panel containers and try to match known metrics
    panels = page.query_selector_all(".react-grid-item")
    for panel in panels:
        try:
            text = panel.inner_text()
            if not text.strip():
                continue

            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if not lines:
                continue

            # Check if this panel matches a key metric
            panel_text = ' '.join(lines).lower()

            for key in KEY_PANELS:
                if key.lower() in panel_text:
                    # Try to find numeric values
                    numbers = re.findall(r'[\d,]+\.?\d*', ' '.join(lines))
                    if numbers:
                        # Take the most prominent number (usually the largest displayed)
                        metrics[key] = {
                            "raw_text": lines[:5],  # First 5 lines
                            "numbers_found": numbers[:5],
                        }
                    else:
                        metrics[key] = {
                            "raw_text": lines[:5],
                            "numbers_found": [],
                        }
                    break
        except Exception:
            continue

    return metrics


def save_snapshot_data(output_dir, time_range, metrics, panels, screenshots):
    """Save a JSON snapshot with all captured data."""
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    snapshot = {
        "captured_at_utc": utc_now_str(),
        "captured_at_edt": edt_now_str(),
        "time_range": time_range,
        "dashboard_url": build_url(time_range),
        "validator": {
            "identity": VALIDATOR_IDENTITY,
            "vote_account": VOTE_ACCOUNT,
        },
        "metrics_extracted": metrics,
        "panels_captured": panels,
        "screenshots": [str(s) for s in screenshots],
    }

    filepath = output_dir / f"snapshot-{time_range}-{timestamp}.json"
    with open(filepath, 'w') as f:
        json.dump(snapshot, f, indent=2)
    print(f"  Snapshot data: {filepath}")
    return filepath


# -- Historical Tracking ------------------------------------------------------

def load_history(base_path=None):
    """Load all historical snapshots for trend analysis."""
    base = Path(base_path) if base_path else Path(DEFAULT_OUTPUT_BASE)
    history = []

    if not base.exists():
        return history

    for date_dir in sorted(base.iterdir()):
        if not date_dir.is_dir():
            continue
        for snapshot_file in sorted(date_dir.glob("snapshot-*.json")):
            try:
                with open(snapshot_file) as f:
                    data = json.load(f)
                    data["_file"] = str(snapshot_file)
                    history.append(data)
            except (json.JSONDecodeError, OSError):
                continue

    return history


def print_trend_report(history):
    """Print a trend analysis from historical snapshots."""
    if not history:
        print("No historical snapshots found.")
        return

    print(f"\n{'=' * 70}")
    print(f"  TREND ANALYSIS - {len(history)} snapshots")
    print(f"{'=' * 70}")

    if len(history) >= 2:
        print(f"  First snapshot: {history[0].get('captured_at_utc', 'unknown')}")
        print(f"  Last snapshot:  {history[-1].get('captured_at_utc', 'unknown')}")

    # Track metrics across snapshots
    for key in KEY_PANELS:
        values = []
        for snap in history:
            m = snap.get("metrics_extracted", {}).get(key, {})
            nums = m.get("numbers_found", [])
            if nums:
                try:
                    val = float(nums[0].replace(',', ''))
                    values.append({
                        "value": val,
                        "time": snap.get("captured_at_utc", ""),
                    })
                except ValueError:
                    pass

        if values:
            vals = [v["value"] for v in values]
            print(f"\n  {key}:")
            print(f"    Samples: {len(vals)}")
            print(f"    Latest:  {vals[-1]:.2f}")
            print(f"    Min:     {min(vals):.2f}")
            print(f"    Max:     {max(vals):.2f}")
            print(f"    Avg:     {sum(vals)/len(vals):.2f}")
            if len(vals) >= 2:
                trend = vals[-1] - vals[0]
                print(f"    Trend:   {trend:+.2f} (first to last)")

    print(f"\n{'=' * 70}")


# -- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Grafana Dashboard Monitor for Saga DAO Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Time ranges: 5m, 15m, 30m, 1h, 3h, 6h, 12h, 24h, 2d, 7d, 30d

Examples:
  %(prog)s --range 1h                 # Capture last 1 hour
  %(prog)s --range 6h --panels        # Capture + individual panels
  %(prog)s --snapshot --range 3h      # Full snapshot with metric extraction
  %(prog)s --trend                    # Show trend from historical snapshots
  %(prog)s --url-only --range 12h     # Just print the Grafana URL
        """,
    )
    parser.add_argument(
        "--range", "-r",
        default="1h",
        choices=list(TIME_RANGES.keys()),
        help="Time range to display (default: 1h)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help=f"Output directory (default: {DEFAULT_OUTPUT_BASE}/<date>/)",
    )
    parser.add_argument(
        "--panels", "-p",
        action="store_true",
        help="Also capture individual panels as separate screenshots",
    )
    parser.add_argument(
        "--snapshot", "-s",
        action="store_true",
        help="Full snapshot: capture screenshots + extract metrics + save JSON",
    )
    parser.add_argument(
        "--trend", "-t",
        action="store_true",
        help="Print trend analysis from historical snapshots (no browser needed)",
    )
    parser.add_argument(
        "--url-only",
        action="store_true",
        help="Just print the Grafana URL for the given time range",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=8,
        help="Seconds to wait for dashboard to load (default: 8)",
    )
    parser.add_argument(
        "--viewport-width",
        type=int,
        default=1920,
        help="Browser viewport width (default: 1920)",
    )
    parser.add_argument(
        "--viewport-height",
        type=int,
        default=1080,
        help="Browser viewport height (default: 1080)",
    )

    args = parser.parse_args()

    # URL-only mode
    if args.url_only:
        print(build_url(args.range))
        return

    # Trend-only mode (no browser)
    if args.trend:
        history = load_history(args.output)
        print_trend_report(history)
        return

    # Browser modes
    url = build_url(args.range)
    output_dir = ensure_output_dir(args.output)

    print(f"Grafana Dashboard Monitor")
    print(f"  Time:       {utc_now_str()} / {edt_now_str()}")
    print(f"  Range:      {args.range}")
    print(f"  URL:        {url}")
    print(f"  Output:     {output_dir}")
    print(f"  Wait:       {args.wait}s")
    print()

    pw, browser = launch_browser()

    try:
        context = browser.new_context(
            viewport={"width": args.viewport_width, "height": args.viewport_height},
            device_scale_factor=2,
        )
        page = context.new_page()

        print(f"Loading dashboard...")
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Wait for panels to render
        print(f"Waiting {args.wait}s for panels to render...")
        time.sleep(args.wait)

        # Sometimes Grafana has a loading spinner overlay
        try:
            page.wait_for_selector(".panel-loading", state="hidden", timeout=10000)
        except Exception:
            pass

        screenshots = []

        # Full dashboard screenshot
        print("Capturing full dashboard...")
        full_screenshot = capture_full_dashboard(page, output_dir, args.range)
        screenshots.append(full_screenshot)

        # Scroll down to capture any panels below the fold
        page_height = page.evaluate("document.body.scrollHeight")
        viewport_height = args.viewport_height
        if page_height > viewport_height * 1.5:
            # Multi-section capture
            scroll_positions = []
            pos = viewport_height
            while pos < page_height:
                scroll_positions.append(pos)
                pos += viewport_height

            for i, scroll_y in enumerate(scroll_positions):
                page.evaluate(f"window.scrollTo(0, {scroll_y})")
                time.sleep(1)
                sc = capture_full_dashboard(
                    page, output_dir, args.range, label=f"scroll-{i+1}"
                )
                screenshots.append(sc)

            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)

        # Individual panels
        panels_data = []
        if args.panels:
            print("Capturing individual panels...")
            panels_data = capture_individual_panels(page, output_dir, args.range)

        # Metric extraction
        metrics = {}
        if args.snapshot:
            print("Extracting visible metrics...")
            metrics = extract_visible_metrics(page)
            if metrics:
                print(f"  Found {len(metrics)} metric panels:")
                for key, val in metrics.items():
                    nums = val.get("numbers_found", [])
                    print(f"    {key}: {nums[0] if nums else 'no value'}")
            else:
                print("  No metrics extracted (dashboard may use canvas rendering)")

        # Save snapshot JSON
        if args.snapshot or metrics:
            save_snapshot_data(output_dir, args.range, metrics, panels_data, screenshots)

        print(f"\nDone. {len(screenshots)} screenshot(s) saved to {output_dir}")

    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    main()

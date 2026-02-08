#!/usr/bin/env python3
"""
Build Preview Tool - Capture and review web builds visually.
"""

import argparse
import subprocess
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Get conversation workspace from env or use default
CONV_WORKSPACE = os.environ.get('CONV_WORKSPACE', '/home/.z/workspaces/previews')
PREVIEW_DIR = Path(CONV_WORKSPACE) / 'previews'


def ensure_preview_dir():
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    return PREVIEW_DIR


def get_screenshot_name(url: str, suffix: str = "") -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '-').replace(':', '-')
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{domain}{suffix}-{timestamp}.png"
    return name


def capture_screenshot(url: str, output_path: Path, mobile: bool = False, full_page: bool = False) -> bool:
    """Capture screenshot using agent-browser CLI."""
    
    viewport = "375x812" if mobile else "1280x800"
    
    cmd = [
        "agent-browser",
        "screenshot",
        url,
        "--output", str(output_path),
        "--viewport", viewport
    ]
    
    if full_page:
        cmd.append("--full-page")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True
        else:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Error: Screenshot capture timed out", file=sys.stderr)
        return False
    except FileNotFoundError:
        # Fallback to curl + playwright if agent-browser not available
        return capture_with_playwright(url, output_path, mobile, full_page)


def capture_with_playwright(url: str, output_path: Path, mobile: bool = False, full_page: bool = False) -> bool:
    """Fallback screenshot capture using playwright."""
    
    script = f'''
import asyncio
from playwright.async_api import async_playwright

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={{"width": 375, "height": 812}} if {mobile} else {{"width": 1280, "height": 800}},
            device_scale_factor=2
        )
        page = await context.new_page()
        await page.goto("{url}", wait_until="networkidle", timeout=30000)
        await page.screenshot(path="{output_path}", full_page={full_page})
        await browser.close()
        print("Screenshot saved to {output_path}")

asyncio.run(capture())
'''
    
    try:
        result = subprocess.run(
            ["python3", "-c", script],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"Playwright error: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


def cmd_capture(args):
    """Capture a single screenshot."""
    ensure_preview_dir()
    
    suffix = "-mobile" if args.mobile else "-desktop"
    if args.name:
        filename = f"{args.name}{suffix}.png"
    else:
        filename = get_screenshot_name(args.url, suffix)
    
    output_path = PREVIEW_DIR / filename
    
    print(f"Capturing {'mobile' if args.mobile else 'desktop'} screenshot of {args.url}...")
    
    if capture_screenshot(args.url, output_path, mobile=args.mobile, full_page=args.full):
        print(f"✓ Screenshot saved: {output_path}")
        return str(output_path)
    else:
        print("✗ Failed to capture screenshot")
        return None


def cmd_review(args):
    """Capture desktop + mobile screenshots and output review checklist."""
    ensure_preview_dir()
    
    url = args.url
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '-').replace(':', '-')
    
    desktop_path = PREVIEW_DIR / f"{domain}-desktop-{timestamp}.png"
    mobile_path = PREVIEW_DIR / f"{domain}-mobile-{timestamp}.png"
    
    print(f"=== Build Review: {url} ===\n")
    
    # Capture desktop
    print("1. Capturing desktop view (1280x800)...")
    desktop_ok = capture_screenshot(url, desktop_path, mobile=False)
    if desktop_ok:
        print(f"   ✓ Saved: {desktop_path}")
    else:
        print("   ✗ Failed")
    
    # Capture mobile
    print("\n2. Capturing mobile view (375x812)...")
    mobile_ok = capture_screenshot(url, mobile_path, mobile=True)
    if mobile_ok:
        print(f"   ✓ Saved: {mobile_path}")
    else:
        print("   ✗ Failed")
    
    # Output checklist
    print("\n=== Review Checklist ===")
    print("□ Images load correctly (no broken images)")
    print("□ Text is readable and properly sized")
    print("□ Buttons/links are visible and tappable")
    print("□ Layout looks correct (no overlapping elements)")
    print("□ Colors and styling match design intent")
    print("□ Mobile layout is responsive and usable")
    print("□ No console errors visible")
    print("□ Interactive elements work (if applicable)")
    
    print(f"\n=== Screenshot Paths ===")
    if desktop_ok:
        print(f"Desktop: {desktop_path}")
    if mobile_ok:
        print(f"Mobile: {mobile_path}")
    
    print("\nUse read_file on these paths to visually inspect the build.")
    
    return {"desktop": str(desktop_path) if desktop_ok else None, 
            "mobile": str(mobile_path) if mobile_ok else None}


def cmd_list(args):
    """List recent preview screenshots."""
    ensure_preview_dir()
    
    screenshots = sorted(PREVIEW_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not screenshots:
        print("No preview screenshots found.")
        return
    
    print(f"=== Recent Previews ({len(screenshots)} total) ===\n")
    
    for i, path in enumerate(screenshots[:20]):
        mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        size_kb = path.stat().st_size / 1024
        print(f"{i+1}. {path.name}")
        print(f"   {mtime} | {size_kb:.1f} KB")
        print(f"   {path}")
        print()


def cmd_compare(args):
    """Compare two screenshots (basic diff info)."""
    before = Path(args.before)
    after = Path(args.after)
    
    if not before.exists():
        print(f"Error: Before image not found: {before}", file=sys.stderr)
        return
    if not after.exists():
        print(f"Error: After image not found: {after}", file=sys.stderr)
        return
    
    before_size = before.stat().st_size
    after_size = after.stat().st_size
    
    print(f"=== Comparison ===")
    print(f"Before: {before.name} ({before_size/1024:.1f} KB)")
    print(f"After:  {after.name} ({after_size/1024:.1f} KB)")
    print(f"Size change: {(after_size - before_size)/1024:+.1f} KB")
    print(f"\nVisually compare these files using read_file to check for differences.")


def main():
    parser = argparse.ArgumentParser(description="Build Preview Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # capture
    capture_parser = subparsers.add_parser("capture", help="Capture a screenshot")
    capture_parser.add_argument("url", help="URL to capture")
    capture_parser.add_argument("--name", help="Custom name for screenshot")
    capture_parser.add_argument("--mobile", action="store_true", help="Use mobile viewport")
    capture_parser.add_argument("--full", action="store_true", help="Capture full page")
    capture_parser.set_defaults(func=cmd_capture)
    
    # review
    review_parser = subparsers.add_parser("review", help="Review a build (desktop + mobile)")
    review_parser.add_argument("url", help="URL to review")
    review_parser.set_defaults(func=cmd_review)
    
    # list
    list_parser = subparsers.add_parser("list", help="List recent previews")
    list_parser.set_defaults(func=cmd_list)
    
    # compare
    compare_parser = subparsers.add_parser("compare", help="Compare two screenshots")
    compare_parser.add_argument("before", help="Before screenshot path")
    compare_parser.add_argument("after", help="After screenshot path")
    compare_parser.set_defaults(func=cmd_compare)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render billboard HTML mockups to PNG at 1680x800 (2x of 840x400)."""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

MOCKUPS_DIR = Path(__file__).parent
HTML_FILES = sorted(MOCKUPS_DIR.glob("*.html"))


async def render_one(browser, html_path):
    page = await browser.new_page(viewport={"width": 1680, "height": 800})
    await page.goto(f"file://{html_path}")
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(1.0)
    out = html_path.with_suffix(".png")
    await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1680, "height": 800})
    await page.close()
    print(f"rendered: {out.name}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for html in HTML_FILES:
            await render_one(browser, html)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

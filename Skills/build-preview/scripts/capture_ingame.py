import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 375, "height": 812})
        await page.goto("https://trump-crash-game-dioni.zocomputer.io")
        await asyncio.sleep(1)
        
        # Click the Launch button
        await page.click("#start-btn")
        
        # Wait for the game to run for a bit (rocket should be mid-flight)
        await asyncio.sleep(2)
        
        # Take screenshot while game is running
        await page.screenshot(path="/home/.z/workspaces/con_dgOwwqXU1pAvm4Px/previews/trump-ingame-zindex.png")
        print("Screenshot saved!")
        
        await browser.close()

asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright
import json, time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path='/usr/bin/chromium',
            args=['--no-sandbox']
        )

        # Test 1: Clean URL
        print("=== TEST 1: Clean URL ===")
        page = await browser.new_page()
        errors = []
        page.on('console', lambda msg: print(f"  CONSOLE [{msg.type}]: {msg.text}"))
        page.on('pageerror', lambda err: errors.append(str(err)))

        response = await page.goto('https://myvurt.com', wait_until='networkidle', timeout=30000)
        print(f"  Status: {response.status}")
        print(f"  URL after load: {page.url}")

        # Check Angular
        ng_version = await page.evaluate("document.querySelector('[ng-version]')?.getAttribute('ng-version') || 'NOT FOUND'")
        print(f"  Angular version: {ng_version}")

        # Check page title and content
        title = await page.title()
        print(f"  Title: {title}")

        # Check for age gate
        age_gate = await page.query_selector('[class*="age"], [id*="age"], [class*="verify"]')
        print(f"  Age gate element: {'FOUND' if age_gate else 'NOT FOUND'}")

        # Check body content length
        body_text = await page.evaluate("document.body?.innerText?.length || 0")
        print(f"  Body text length: {body_text}")

        # Screenshot
        await page.screenshot(path='/home/workspace/test-clean-url.png', full_page=False)

        if errors:
            print(f"  JS Errors: {json.dumps(errors, indent=2)}")

        await page.close()

        # Test 2: fbclid URL (simulating Facebook ad click)
        print("\n=== TEST 2: fbclid URL (Facebook ad traffic) ===")
        page = await browser.new_page()
        errors2 = []
        page.on('pageerror', lambda err: errors2.append(str(err)))

        response = await page.goto('https://myvurt.com/?fbclid=IwAR3test123abc456', wait_until='networkidle', timeout=30000)
        print(f"  Status: {response.status}")
        print(f"  URL after load: {page.url}")

        ng_version2 = await page.evaluate("document.querySelector('[ng-version]')?.getAttribute('ng-version') || 'NOT FOUND'")
        print(f"  Angular version: {ng_version2}")

        body_text2 = await page.evaluate("document.body?.innerText?.length || 0")
        print(f"  Body text length: {body_text2}")

        # Check if redirected to /signup
        print(f"  Final URL (check for /signup redirect): {page.url}")

        await page.screenshot(path='/home/workspace/test-fbclid-url.png', full_page=False)

        if errors2:
            print(f"  JS Errors: {json.dumps(errors2, indent=2)}")

        await page.close()

        # Test 3: /signup page directly
        print("\n=== TEST 3: /signup page ===")
        page = await browser.new_page()
        response = await page.goto('https://myvurt.com/signup', wait_until='networkidle', timeout=30000)
        print(f"  Status: {response.status}")
        print(f"  URL after load: {page.url}")

        body_text3 = await page.evaluate("document.body?.innerText?.length || 0")
        print(f"  Body text length: {body_text3}")

        await page.screenshot(path='/home/workspace/test-signup-page.png', full_page=False)
        await page.close()

        # Test 4: Check what GA4/gtag does
        print("\n=== TEST 4: GA4 tracking check ===")
        page = await browser.new_page()

        # Intercept GA4 requests
        ga4_requests = []
        async def handle_request(request):
            url = request.url
            if 'google-analytics' in url or 'gtag' in url or 'analytics' in url:
                ga4_requests.append(url[:200])

        page.on('request', handle_request)

        await page.goto('https://myvurt.com', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)  # Wait for delayed tracking

        print(f"  GA4/analytics requests captured: {len(ga4_requests)}")
        for req in ga4_requests[:10]:
            print(f"    {req}")

        # Check dataLayer
        dl = await page.evaluate("window.dataLayer ? JSON.stringify(window.dataLayer.slice(0,5)) : 'NO DATALAYER'")
        print(f"  dataLayer: {dl}")

        # Check gtag
        gtag_exists = await page.evaluate("typeof gtag === 'function'")
        print(f"  gtag function exists: {gtag_exists}")

        await page.close()

        # Test 5: Try to interact with age gate and play video
        print("\n=== TEST 5: Age gate + video play ===")
        page = await browser.new_page()
        await page.goto('https://myvurt.com', wait_until='networkidle', timeout=30000)

        # Try clicking through age gate
        buttons = await page.query_selector_all('button')
        print(f"  Buttons found: {len(buttons)}")
        for i, btn in enumerate(buttons[:5]):
            text = await btn.text_content()
            print(f"    Button {i}: '{text}'")

        # Try to find and click yes/enter/verify button
        for btn in buttons:
            text = (await btn.text_content() or '').lower()
            if any(w in text for w in ['yes', 'enter', 'verify', 'continue', 'confirm']):
                print(f"  Clicking: '{text}'")
                await btn.click()
                await asyncio.sleep(3)
                break

        print(f"  URL after age gate: {page.url}")
        await page.screenshot(path='/home/workspace/test-after-agegate.png', full_page=False)

        # Check for video elements
        videos = await page.query_selector_all('video')
        print(f"  Video elements: {len(videos)}")

        await page.close()
        await browser.close()

asyncio.run(main())

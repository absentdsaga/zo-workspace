#!/usr/bin/env python3
"""Simulate paid ad clicks on myvurt.com - capture everything a first-time user experiences."""

import asyncio
import json
import os
import time
from datetime import datetime

async def run():
    from playwright.async_api import async_playwright
    
    URLS = [
        ("homepage_fb", "https://www.myvurt.com/?utm_source=facebook&utm_medium=cpc&fbclid=PAZXh0bgNhZW0test"),
        ("comeback_dad_fb", "https://www.myvurt.com/detail/micro_series/come-back-dad?utm_source=facebook&utm_medium=cpc&fbclid=test123"),
        ("karma_heels_fb", "https://www.myvurt.com/detail/micro_series/karma-in-heels?utm_source=facebook&utm_medium=cpc&fbclid=test456"),
        ("love_letter_google", "https://www.myvurt.com/detail/micro_series/the-love-letter?utm_source=google&utm_medium=cpc&gclid=test789"),
    ]
    
    USER_AGENTS = {
        "fb_inapp": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/21A329 [FBAN/FBIOS;FBAV/430.0.0.0;FBBV/1;FBDV/iPhone15,2;FBMD/iPhone;FBSN/iOS;FBSV/17.0;FBSS/3;FBID/phone;FBLC/en_US;FBOP/5]",
        "mobile_chrome": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    }
    
    os.makedirs("/home/.z/workspaces/con_v55GP1lr46UmN5fa/screenshots", exist_ok=True)
    results = {}
    
    async with async_playwright() as p:
        for ua_name, ua_string in USER_AGENTS.items():
            for url_name, url in URLS:
                key = f"{url_name}__{ua_name}"
                print(f"\n{'='*60}")
                print(f"Testing: {key}")
                print(f"URL: {url}")
                print(f"UA: {ua_name}")
                print(f"{'='*60}")
                
                browser = await p.chromium.launch(
                    executable_path="/usr/bin/chromium",
                    args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
                    headless=True
                )
                
                context = await browser.new_context(
                    user_agent=ua_string,
                    viewport={"width": 390, "height": 844},
                    device_scale_factor=3,
                    is_mobile=True,
                    has_touch=True,
                )
                
                page = await context.new_page()
                
                # Collectors
                requests_log = []
                responses_log = []
                console_msgs = []
                js_errors = []
                redirects = []
                
                page.on("console", lambda msg: console_msgs.append({"type": msg.type, "text": msg.text[:500]}))
                page.on("pageerror", lambda err: js_errors.append(str(err)[:500]))
                
                async def on_response(resp):
                    try:
                        responses_log.append({
                            "url": resp.url[:200],
                            "status": resp.status,
                            "content_type": resp.headers.get("content-type", "")[:100],
                            "content_length": resp.headers.get("content-length", ""),
                            "cache_control": resp.headers.get("cache-control", "")[:100],
                            "x_cache": resp.headers.get("x-cache", ""),
                            "age": resp.headers.get("age", ""),
                            "server": resp.headers.get("server", "")[:50],
                        })
                        if 300 <= resp.status < 400:
                            redirects.append({
                                "from": resp.url[:200],
                                "to": resp.headers.get("location", "")[:200],
                                "status": resp.status
                            })
                    except:
                        pass
                
                async def on_request(req):
                    requests_log.append({
                        "url": req.url[:200],
                        "method": req.method,
                        "resource_type": req.resource_type,
                    })
                
                page.on("response", on_response)
                page.on("request", on_request)
                
                # Navigate
                start = time.time()
                try:
                    resp = await page.goto(url, wait_until="load", timeout=30000)
                    load_time = round(time.time() - start, 2)
                    final_url = page.url
                    status = resp.status if resp else "none"
                except Exception as e:
                    load_time = round(time.time() - start, 2)
                    final_url = page.url
                    status = f"error: {str(e)[:200]}"
                
                print(f"  Load time: {load_time}s")
                print(f"  Final URL: {final_url}")
                print(f"  Status: {status}")
                print(f"  Redirects: {len(redirects)}")
                
                # Screenshots at intervals
                screenshots = {}
                for delay_name, delay in [("1s", 1), ("3s", 3), ("5s", 5), ("10s", 10)]:
                    if delay > 1:
                        await asyncio.sleep(delay - (1 if delay == 3 else 3 if delay == 5 else 5))
                    else:
                        await asyncio.sleep(1)
                    
                    ss_path = f"/home/.z/workspaces/con_v55GP1lr46UmN5fa/screenshots/{key}_{delay_name}.png"
                    await page.screenshot(path=ss_path, full_page=False)
                    screenshots[delay_name] = ss_path
                
                # Check for modals/overlays/gates
                modal_check = await page.evaluate("""() => {
                    const selectors = [
                        '.modal', '[role="dialog"]', '.overlay', '.age-gate', 
                        '.signup', '.register', '[class*="modal"]', '[class*="gate"]',
                        '[class*="signup"]', '[class*="login"]', '[class*="register"]',
                        '[class*="verify"]', '[class*="age"]', 'mat-dialog-container',
                        '.cdk-overlay-container', '.cdk-overlay-pane',
                        '[class*="overlay"]', '[class*="consent"]'
                    ];
                    const found = [];
                    for (const sel of selectors) {
                        const els = document.querySelectorAll(sel);
                        for (const el of els) {
                            const rect = el.getBoundingClientRect();
                            const style = window.getComputedStyle(el);
                            if (rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden') {
                                found.push({
                                    selector: sel,
                                    tag: el.tagName,
                                    classes: el.className.toString().substring(0, 200),
                                    text: el.innerText?.substring(0, 300) || '',
                                    width: rect.width,
                                    height: rect.height,
                                    zIndex: style.zIndex
                                });
                            }
                        }
                    }
                    return found;
                }""")
                
                # Check page content
                page_analysis = await page.evaluate("""() => {
                    const body = document.body;
                    const scripts = document.querySelectorAll('script[src]');
                    const title = document.title;
                    const h1s = [...document.querySelectorAll('h1')].map(h => h.innerText?.substring(0, 100));
                    const videos = document.querySelectorAll('video');
                    const iframes = document.querySelectorAll('iframe');
                    const forms = document.querySelectorAll('form');
                    const inputs = document.querySelectorAll('input');
                    const bodyText = body?.innerText?.substring(0, 2000) || '';
                    
                    // Check for registration/signup elements
                    const signupIndicators = [];
                    const allText = bodyText.toLowerCase();
                    if (allText.includes('sign up') || allText.includes('signup')) signupIndicators.push('signup_text');
                    if (allText.includes('register')) signupIndicators.push('register_text');
                    if (allText.includes('create account')) signupIndicators.push('create_account_text');
                    if (allText.includes('log in') || allText.includes('login')) signupIndicators.push('login_text');
                    if (allText.includes('age') && allText.includes('verif')) signupIndicators.push('age_verify_text');
                    if (inputs.length > 0) signupIndicators.push(f'inputs_count_{inputs.length}');
                    if (forms.length > 0) signupIndicators.push(f'forms_count_{forms.length}');
                    
                    return {
                        title: title,
                        h1s: h1s,
                        script_count: scripts.length,
                        video_count: videos.length,
                        iframe_count: iframes.length,
                        form_count: forms.length,
                        input_count: inputs.length,
                        body_text_preview: bodyText.substring(0, 1000),
                        signup_indicators: signupIndicators,
                        url: window.location.href,
                    };
                }""")
                
                # Count total transfer
                total_js_size = 0
                total_size = 0
                for r in responses_log:
                    cl = int(r.get("content_length") or 0)
                    total_size += cl
                    if "javascript" in r.get("content_type", ""):
                        total_js_size += cl
                
                result = {
                    "url": url,
                    "ua": ua_name,
                    "load_time_s": load_time,
                    "final_url": final_url,
                    "url_changed": final_url != url,
                    "status": status,
                    "redirects": redirects,
                    "total_requests": len(requests_log),
                    "total_responses": len(responses_log),
                    "total_size_bytes": total_size,
                    "total_js_bytes": total_js_size,
                    "console_errors": [m for m in console_msgs if m["type"] == "error"],
                    "js_errors": js_errors,
                    "modals_found": modal_check,
                    "page_analysis": page_analysis,
                    "screenshots": screenshots,
                }
                
                results[key] = result
                
                # Print summary
                print(f"  Total requests: {len(requests_log)}")
                print(f"  Total size: {total_size/1024/1024:.1f} MB (JS: {total_js_size/1024/1024:.1f} MB)")
                print(f"  URL changed: {final_url != url}")
                if redirects:
                    for r in redirects:
                        print(f"  REDIRECT: {r['status']} {r['from'][:60]} -> {r['to'][:60]}")
                if modal_check:
                    print(f"  MODALS/OVERLAYS FOUND: {len(modal_check)}")
                    for m in modal_check[:3]:
                        print(f"    - {m['selector']}: {m['text'][:100]}")
                if page_analysis.get("signup_indicators"):
                    print(f"  SIGNUP INDICATORS: {page_analysis['signup_indicators']}")
                if js_errors:
                    print(f"  JS ERRORS: {len(js_errors)}")
                    for e in js_errors[:3]:
                        print(f"    - {e[:150]}")
                        
                await browser.close()
    
    # Save full report
    with open("/home/.z/workspaces/con_v55GP1lr46UmN5fa/ad-click-report.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print final summary
    print("\n\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    for key, r in results.items():
        print(f"\n{key}:")
        print(f"  Load: {r['load_time_s']}s | Size: {r['total_size_bytes']/1024/1024:.1f}MB | JS: {r['total_js_bytes']/1024/1024:.1f}MB")
        print(f"  URL changed: {r['url_changed']} | Redirects: {len(r['redirects'])}")
        print(f"  Modals: {len(r['modals_found'])} | JS errors: {len(r['js_errors'])}")
        if r['modals_found']:
            for m in r['modals_found'][:2]:
                txt = m['text'][:80].replace('\n', ' ')
                print(f"    MODAL: {txt}")
        if r['page_analysis'].get('signup_indicators'):
            print(f"    Signup signals: {r['page_analysis']['signup_indicators']}")

asyncio.run(run())

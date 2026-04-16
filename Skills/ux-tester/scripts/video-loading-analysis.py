#!/usr/bin/env python3
"""
Deep analysis of video loading behavior on detail pages.
Tracks exactly WHEN each video/media request fires to verify lazy loading.
"""
import json, time, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def analyze_video_loading(url, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(
            headless=True, executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=3, is_mobile=True, has_touch=True,
            locale="en-US", timezone_id="America/New_York", color_scheme="dark",
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        page = context.new_page()
        
        media_requests = []
        mux_requests = []
        start_time = time.time()
        
        def on_request(req):
            elapsed = round((time.time() - start_time) * 1000)
            if req.resource_type == "media":
                media_requests.append({"url": req.url[:300], "time_ms": elapsed})
            if "mux.com" in req.url:
                mux_requests.append({"url": req.url[:300], "time_ms": elapsed, "type": req.resource_type})
        
        page.on("request", on_request)
        
        # Phase 1: Initial load (before age gate)
        print("=== PHASE 1: Initial page load (before age gate) ===")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
        
        phase1_media = len(media_requests)
        phase1_mux = len(mux_requests)
        print(f"Media requests: {phase1_media}")
        print(f"Mux requests: {phase1_mux}")
        
        # Check mux-player elements
        mux_players = page.evaluate("""() => {
            const players = document.querySelectorAll('mux-player');
            return Array.from(players).map((p, i) => {
                const rect = p.getBoundingClientRect();
                return {
                    index: i,
                    playbackId: p.getAttribute('playback-id') || '',
                    inViewport: rect.top < window.innerHeight && rect.bottom > 0,
                    top: Math.round(rect.top),
                    height: Math.round(rect.height),
                    loading: p.getAttribute('loading') || 'not set',
                    preload: p.getAttribute('preload') || 'not set',
                    autoplay: p.hasAttribute('autoplay'),
                    streamType: p.getAttribute('stream-type') || '',
                };
            });
        }""")
        print(f"\n<mux-player> elements on page: {len(mux_players)}")
        for mp in mux_players:
            vp = "IN VIEWPORT" if mp["inViewport"] else f"off-screen (top={mp['top']}px)"
            print(f"  [{mp['index']}] id={mp['playbackId'][:25]}... {vp} | loading={mp['loading']} preload={mp['preload']} autoplay={mp['autoplay']}")
        
        # Phase 2: Click age gate
        print("\n=== PHASE 2: After age gate ===")
        pre_age = len(media_requests)
        try:
            page.locator('text="Yes, I am 17+"').first.click(timeout=3000)
            page.wait_for_timeout(5000)
        except:
            print("No age gate")
        print(f"NEW media requests after age gate: {len(media_requests) - pre_age}")
        print(f"Total media now: {len(media_requests)}")
        
        # Phase 3: Scroll and track
        print("\n=== PHASE 3: Scroll tracking ===")
        for i in range(1, 8):
            pre = len(media_requests)
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            page.wait_for_timeout(2000)
            new = len(media_requests) - pre
            
            vis = page.evaluate("""() => {
                const players = document.querySelectorAll('mux-player');
                const inView = Array.from(players).filter(p => {
                    const r = p.getBoundingClientRect();
                    return r.top < window.innerHeight && r.bottom > 0;
                });
                return { total: players.length, visible: inView.length, scrollY: Math.round(window.scrollY) };
            }""")
            print(f"  Scroll {i}: +{new} media reqs (total: {len(media_requests)}) | {vis['visible']}/{vis['total']} players visible | scrollY={vis['scrollY']}")
        
        # Timeline
        print(f"\n=== TIMELINE (2s buckets) ===")
        buckets = {}
        for r in media_requests:
            b = (r["time_ms"] // 2000) * 2
            buckets[b] = buckets.get(b, 0) + 1
        for t in sorted(buckets.keys()):
            bar = "█" * min(buckets[t], 60)
            print(f"  {t:>3}s-{t+2}s: {buckets[t]:>3} reqs {bar}")
        
        # Unique streams
        unique_ids = set()
        for r in mux_requests:
            parts = r["url"].split("/")
            for part in parts:
                if len(part) > 20 and "." not in part[:20]:
                    unique_ids.add(part[:40])
                    break
        print(f"\nUnique Mux stream IDs: {len(unique_ids)}")
        
        # Console warnings about thumbnails
        print(f"\nTotal media requests: {len(media_requests)}")
        print(f"Total Mux requests: {len(mux_requests)}")
        
        with open(output_dir / "video-loading.json", "w") as f:
            json.dump({
                "mux_players": mux_players,
                "media_request_count": len(media_requests),
                "mux_request_count": len(mux_requests),
                "timeline_buckets": {str(k): v for k, v in buckets.items()},
                "unique_stream_ids": list(unique_ids),
            }, f, indent=2, default=str)
        
        browser.close()
    print(f"\n✓ Saved to {output_dir}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.myvurt.com/detail/micro_series/karma-in-hells"
    out = sys.argv[2] if len(sys.argv) > 2 else "/home/.z/workspaces/con_pA7pbH3kvcuaZ1eq/ux-tests/video-loading"
    analyze_video_loading(url, out)

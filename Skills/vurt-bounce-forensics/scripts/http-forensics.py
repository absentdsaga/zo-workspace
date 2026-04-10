#!/usr/bin/env python3
"""Raw HTTP-level forensics on myvurt.com - redirects, headers, TTFB, content analysis."""

import json
import time
import urllib.request
import urllib.parse
import ssl
import re
from html.parser import HTMLParser

ctx = ssl.create_default_context()

URLS = [
    "https://www.myvurt.com/",
    "https://myvurt.com/",
    "https://www.myvurt.com/detail/micro_series/come-back-dad",
    "https://www.myvurt.com/detail/micro_series/karma-in-heels",
    "https://www.myvurt.com/detail/micro_series/the-love-letter",
    "https://www.myvurt.com/?utm_source=facebook&utm_medium=cpc&fbclid=test",
    "https://www.myvurt.com/detail/micro_series/come-back-dad?fbclid=test",
    "https://www.myvurt.com/nonexistent-page-test-404",
    "https://www.myvurt.com/detail/micro_series/nonexistent-show-test",
]

USER_AGENTS = {
    "chrome_desktop": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "mobile_chrome": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    "fb_inapp": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/21A329 [FBAN/FBIOS;FBAV/430.0.0.0;FBBV/1;FBDV/iPhone15,2;FBMD/iPhone;FBSN/iOS;FBSV/17.0;FBSS/3;FBID/phone;FBLC/en_US;FBOP/5]",
    "ig_inapp": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/21A329 Instagram 312.0.0.0",
    "googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
}

results = {}

def fetch_no_redirect(url, ua, timeout=15):
    """Fetch URL without following redirects, return status + headers + body."""
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    # Don't follow redirects
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener2 = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
    
    start = time.time()
    try:
        resp = opener2.open(req, timeout=timeout)
        ttfb = round(time.time() - start, 3)
        body = resp.read(500000)  # first 500KB
        total_time = round(time.time() - start, 3)
        headers = dict(resp.headers)
        return {
            "status": resp.status,
            "headers": headers,
            "body_size": len(body),
            "body_preview": body[:5000].decode("utf-8", errors="replace"),
            "ttfb": ttfb,
            "total_time": total_time,
            "final_url": resp.url,
        }
    except urllib.error.HTTPError as e:
        ttfb = round(time.time() - start, 3)
        body = e.read(500000) if e.fp else b""
        headers = dict(e.headers) if e.headers else {}
        return {
            "status": e.code,
            "headers": headers,
            "body_size": len(body),
            "body_preview": body[:5000].decode("utf-8", errors="replace"),
            "ttfb": ttfb,
            "total_time": round(time.time() - start, 3),
            "redirect_to": headers.get("Location", ""),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)[:300], "ttfb": round(time.time() - start, 3)}

def follow_redirects(url, ua, max_hops=10):
    """Follow full redirect chain."""
    chain = []
    current = url
    for _ in range(max_hops):
        result = fetch_no_redirect(current, ua)
        chain.append({"url": current, "status": result.get("status"), "redirect_to": result.get("redirect_to", "")})
        if result.get("status") in (301, 302, 303, 307, 308) and result.get("redirect_to"):
            next_url = result["redirect_to"]
            if not next_url.startswith("http"):
                from urllib.parse import urljoin
                next_url = urljoin(current, next_url)
            current = next_url
        else:
            break
    return chain

def analyze_html(html):
    """Analyze HTML content for redirect indicators and content."""
    analysis = {
        "meta_refresh": [],
        "js_redirects": [],
        "script_tags": 0,
        "script_src_tags": [],
        "total_html_size": len(html),
        "has_body_content": False,
        "title": "",
        "meta_tags": {},
        "age_gate_indicators": [],
        "signup_indicators": [],
        "angular_app": False,
        "app_root_empty": False,
    }
    
    # Meta refresh
    for m in re.finditer(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\']([^"\']*)["\']', html, re.I):
        analysis["meta_refresh"].append(m.group(1))
    
    # JS redirects
    for pattern in [r'window\.location\s*=', r'location\.href\s*=', r'location\.replace\s*\(', r'window\.location\.replace\s*\(', r'window\.location\.href\s*=']:
        for m in re.finditer(pattern, html):
            context = html[max(0, m.start()-50):m.end()+100]
            analysis["js_redirects"].append(context.strip())
    
    # Script tags
    analysis["script_tags"] = len(re.findall(r'<script', html, re.I))
    for m in re.finditer(r'<script[^>]*src=["\']([^"\']*)["\']', html, re.I):
        analysis["script_src_tags"].append(m.group(1)[:150])
    
    # Title
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
    if m:
        analysis["title"] = m.group(1).strip()[:200]
    
    # OG tags
    for m in re.finditer(r'<meta[^>]*property=["\']og:(\w+)["\'][^>]*content=["\']([^"\']*)["\']', html, re.I):
        analysis["meta_tags"][f"og:{m.group(1)}"] = m.group(2)[:200]
    
    # Check for Angular
    if "ng-version" in html or "app-root" in html or "angular" in html.lower():
        analysis["angular_app"] = True
    
    # Check if app-root is empty
    m = re.search(r'<app-root[^>]*>(.*?)</app-root>', html, re.I | re.S)
    if m:
        content = m.group(1).strip()
        analysis["app_root_empty"] = len(content) < 50
        analysis["app_root_content_length"] = len(content)
    
    # Age gate / signup
    lower = html.lower()
    if "age" in lower and ("verif" in lower or "gate" in lower or "confirm" in lower):
        analysis["age_gate_indicators"].append("age_verification_detected")
    if "sign up" in lower or "signup" in lower or "register" in lower or "create account" in lower:
        analysis["signup_indicators"].append("signup_form_detected")
    
    # Real content check
    # Strip all tags and check text length
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text).strip()
    analysis["visible_text_length"] = len(text)
    analysis["has_body_content"] = len(text) > 500
    
    return analysis

# Run all tests
print("="*70)
print("HTTP FORENSICS - myvurt.com")
print("="*70)

# 1. Redirect chains
print("\n\n### REDIRECT CHAIN ANALYSIS ###\n")
for url in URLS:
    for ua_name, ua in USER_AGENTS.items():
        chain = follow_redirects(url, ua)
        if len(chain) > 1 or chain[0]["status"] not in (200,):
            print(f"  {ua_name:15} | {url[:60]}")
            for hop in chain:
                print(f"    → {hop['status']} {hop['url'][:80]} {'→ '+hop['redirect_to'][:60] if hop['redirect_to'] else ''}")
            print()

# 2. Detailed response analysis for key pages
print("\n\n### DETAILED RESPONSE ANALYSIS ###\n")
key_urls = [
    "https://www.myvurt.com/",
    "https://www.myvurt.com/detail/micro_series/come-back-dad",
    "https://www.myvurt.com/detail/micro_series/come-back-dad?fbclid=test",
    "https://www.myvurt.com/nonexistent-page-test-404",
]

for url in key_urls:
    for ua_name in ["fb_inapp", "mobile_chrome", "googlebot"]:
        ua = USER_AGENTS[ua_name]
        chain = follow_redirects(url, ua)
        final_url = chain[-1]["url"] if chain else url
        result = fetch_no_redirect(final_url, ua)
        
        print(f"\n--- {ua_name} | {url[:70]} ---")
        print(f"  Status: {result.get('status')}")
        print(f"  TTFB: {result.get('ttfb')}s")
        print(f"  Body size: {result.get('body_size', 0)/1024:.1f} KB")
        
        headers = result.get("headers", {})
        for h in ["Cache-Control", "Content-Type", "Server", "X-Cache", "Age", "Via", 
                   "X-Amz-Cf-Id", "X-Amz-Cf-Pop", "CF-Cache-Status", "Content-Security-Policy",
                   "X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy",
                   "Strict-Transport-Security"]:
            val = headers.get(h, headers.get(h.lower(), ""))
            if val:
                print(f"  {h}: {str(val)[:100]}")
        
        # HTML analysis
        body = result.get("body_preview", "")
        if body and "text/html" in result.get("headers", {}).get("Content-Type", result.get("headers", {}).get("content-type", "")):
            analysis = analyze_html(body)
            print(f"  Title: {analysis['title']}")
            print(f"  Angular: {analysis['angular_app']} | App-root empty: {analysis.get('app_root_empty', 'N/A')}")
            print(f"  Script tags: {analysis['script_tags']} | External scripts: {len(analysis['script_src_tags'])}")
            print(f"  Visible text: {analysis['visible_text_length']} chars | Has content: {analysis['has_body_content']}")
            print(f"  OG tags: {json.dumps(analysis['meta_tags'])}")
            if analysis["meta_refresh"]:
                print(f"  *** META REFRESH: {analysis['meta_refresh']}")
            if analysis["js_redirects"]:
                print(f"  *** JS REDIRECTS: {analysis['js_redirects'][:3]}")
            if analysis["age_gate_indicators"]:
                print(f"  *** AGE GATE: {analysis['age_gate_indicators']}")
            if analysis["signup_indicators"]:
                print(f"  *** SIGNUP: {analysis['signup_indicators']}")
            
            results[f"{ua_name}__{url[:60]}"] = {
                "status": result.get("status"),
                "ttfb": result.get("ttfb"),
                "body_size": result.get("body_size"),
                "headers": {k: str(v)[:200] for k, v in headers.items()},
                "html_analysis": analysis,
            }

# 3. Special tests
print("\n\n### SPECIAL TESTS ###\n")

# robots.txt
print("--- robots.txt ---")
r = fetch_no_redirect("https://www.myvurt.com/robots.txt", USER_AGENTS["chrome_desktop"])
print(f"  Status: {r.get('status')}")
print(f"  Content: {r.get('body_preview', '')[:500]}")

# sitemap
print("\n--- sitemap.xml ---")
r = fetch_no_redirect("https://www.myvurt.com/sitemap.xml", USER_AGENTS["chrome_desktop"])
print(f"  Status: {r.get('status')}")
body = r.get('body_preview', '')
url_count = body.count('<url>')
print(f"  URLs in sitemap: {url_count}")
print(f"  Content preview: {body[:300]}")

# CloudFront caching test
print("\n--- CloudFront HTML Caching Check ---")
for url in ["https://www.myvurt.com/", "https://www.myvurt.com/detail/micro_series/come-back-dad"]:
    r = fetch_no_redirect(url, USER_AGENTS["mobile_chrome"])
    h = r.get("headers", {})
    age = h.get("Age", h.get("age", "none"))
    cc = h.get("Cache-Control", h.get("cache-control", "none"))
    xcache = h.get("X-Cache", h.get("x-cache", "none"))
    via = h.get("Via", h.get("via", "none"))
    print(f"  {url[:60]}")
    print(f"    Age: {age} | Cache-Control: {cc} | X-Cache: {xcache}")
    print(f"    Via: {via}")

# 4. TTFB comparison across all URLs
print("\n\n### TTFB COMPARISON ###\n")
print(f"{'URL':<65} {'TTFB':>6}")
print("-"*75)
for url in URLS[:6]:
    r = fetch_no_redirect(url, USER_AGENTS["mobile_chrome"])
    ttfb = r.get("ttfb", "err")
    status = r.get("status", "err")
    print(f"  {url[:63]:<65} {ttfb}s ({status})")

# Save
with open("/home/.z/workspaces/con_v55GP1lr46UmN5fa/http-forensics-data.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\n\nDone. Data saved to http-forensics-data.json")

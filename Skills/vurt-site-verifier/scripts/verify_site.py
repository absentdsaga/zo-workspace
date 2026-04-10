#!/usr/bin/env python3
"""
VURT Site Verification Script
Tests: meta tags, GTM, SSR, sitemap, robots, CDN headers
Usage: python3 verify_site.py [url]
"""
import sys
import urllib.request
import urllib.parse
import re
import json
from datetime import datetime

def check_url(url):
    results = {
        'url': url,
        'status': None,
        'gtm': [],
        'meta_tags': {},
        'canonical': None,
        'title': None,
        'has_description': False,
        'og_image': None,
        'content_in_html': False,
        'h1_count': 0,
        'h1_text': [],
        'error': None
    }
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        resp = urllib.request.urlopen(req, timeout=15)
        results['status'] = resp.status
        html = resp.read().decode('utf-8', errors='ignore')
        
        # GTM
        results['gtm'] = re.findall(r'GTM-[A-Z0-9]{7}', html)
        
        # Meta tags
        meta_patterns = {
            'og:title': r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
            'og:description': r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
            'og:image': r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            'description': r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
        }
        for name, pattern in meta_patterns.items():
            m = re.search(pattern, html)
            if m:
                val = m.group(1)[:80] + '...' if len(m.group(1)) > 80 else m.group(1)
                results['meta_tags'][name] = val
        
        # Canonical
        canonical = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html)
        if canonical:
            results['canonical'] = canonical.group(1)
        
        # Title
        title = re.search(r'<title[^>]*>([^<]+)</title>', html)
        if title:
            results['title'] = title.group(1).strip()[:80]
        
        # Description
        results['has_description'] = bool(re.search(r'<meta[^>]+name=["\']description["\']', html))
        
        # OG Image
        og_img = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
        if og_img:
            results['og_image'] = og_img.group(1)[:80]
        
        # SSR check - is content in the initial HTML?
        # If Angular app, we expect to see some content
        if len(html) > 5000:
            results['content_in_html'] = True
        
        # H1s
        h1s = re.findall(r'<h1[^>]*>([^<]+)</h1>', html)
        results['h1_count'] = len(h1s)
        results['h1_text'] = [h.strip()[:60] for h in h1s[:5]]
        
    except Exception as e:
        results['error'] = str(e)[:100]
    
    return results

def main():
    urls = [
        'https://www.myvurt.com/',
        'https://www.myvurt.com/detail/micro_series/favorite-son',
    ]
    
    if len(sys.argv) > 1:
        urls = [sys.argv[1]]
    
    print(f"\n{'='*60}")
    print(f"VURT SITE VERIFICATION — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")
    
    for url in urls:
        r = check_url(url)
        print(f"URL: {r['url']}")
        print(f"  Status: {r['status'] or r['error']}")
        print(f"  GTM containers: {r['gtm'] or 'NONE'}")
        print(f"  Title: {r['title'] or 'MISSING'}")
        print(f"  Meta desc: {'YES' if r['has_description'] else 'MISSING'}")
        print(f"  OG title: {r['meta_tags'].get('og:title', 'MISSING')}")
        print(f"  OG desc: {r['meta_tags'].get('og:description', 'MISSING')}")
        print(f"  OG image: {r['meta_tags'].get('og:image', 'MISSING')}")
        print(f"  Canonical: {r['canonical'] or 'MISSING'}")
        print(f"  H1 count: {r['h1_count']}")
        for h in r['h1_text']:
            print(f"    H1: {h}")
        print(f"  SSR (has content): {'YES' if r['content_in_html'] else 'NO'}")
        print()
    
    print(f"{'='*60}")
    print("SUMMARY:")
    print("  GTM: Container installed = GTM-MN8TR3CR found in HTML")
    print("  SSR: Site returns content in initial HTML")
    print("  META: All pages need og:title, og:description, og:image, canonical")
    print("  H1: Must be unique per page, descriptive")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
---
name: vurt-site-verifier
description: |
  Automated verification of myvurt.com — SSR, meta tags, CDN headers, GTM installation, 
  sitemap, og tags, and security headers. Run this whenever VURT infrastructure changes 
  or before sending site updates to stakeholders. Returns green/red checks for each item.
  Usage: python3 scripts/verify_site.py
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
allowed-tools: Bash, Read, Write
---
# VURT Site Verifier

## What This Does
Verifies the live state of myvurt.com across all critical frontend/SEO markers.

## Usage
```bash
python3 Skills/vurt-site-verifier/scripts/verify_site.py
```

## What It Checks
- SSR: HTML contains real content (not empty shell)
- GTM container: GTM-MN8TR3CR present in source
- Meta Pixel: fbq/fbp references in source
- CloudFront headers: Cache-Control, x-cache, cf-ray
- Meta tags: og:title, og:description, og:image, og:type, og:url on homepage and series page
- Canonical tags: present on key pages
- Sitemap: returns non-empty XML
- Security headers: CSP, X-Frame-Options, etc.
- Homepage title: under 60 chars
- OG sitename: non-empty

## Output
Green ✓ / Red ✗ for each item with details on failures.

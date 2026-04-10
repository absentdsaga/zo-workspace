---
name: vurt-bounce-forensics
description: Deep forensic analysis of VURT paid ads bounce rates. Simulates real ad-click user journeys, measures page load waterfall, checks redirect chains, tests age gate behavior, and correlates GA4 data with actual page behavior. Use when investigating why paid traffic bounces.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## Usage

Run any of the diagnostic scripts to investigate bounce issues:

### Quick Diagnostic
```bash
python3 scripts/ga4-paid-bounce.py
```
Pulls 7-day GA4 data for paid traffic: bounce by landing page, device, browser, campaign, country, hour, events.

### Full Browser Simulation
```bash
python3 scripts/simulate-ad-click.py
```
Uses Playwright to simulate ad clicks with Facebook/Instagram in-app browser user agents. Captures screenshots, redirect chains, modals, JS errors, and page load timing.

### HTTP-Level Forensics
```bash
python3 scripts/http-forensics.py
```
Raw HTTP analysis: redirect chains, CDN headers, TTFB, HTML content inspection, sitemap/robots check.

## Key Findings (April 5, 2026)

See `references/findings-2026-04-05.md` for the full forensic report.

**#1 Issue:** Users land on a BLACK video player + age gate modal. Zero visual payoff. Only 5 out of 10,566 paid sessions started a video (0.05%).

**Secondary:** 63% of paid traffic targeted outside US. Campaign `120245604984150029` bounces at 92%. 5MB JS payload prevents 72% of sessions from even rendering.

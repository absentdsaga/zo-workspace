---
name: ux-tester
description: Stealth browser UX testing that sees what real users see. Uses Playwright with anti-detection to bypass bot walls, capture screenshots, measure load times, and document the actual user experience flow. Use this skill whenever you need to verify how a website actually looks and behaves for real humans — not how it looks to a bot.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## Usage

Run the UX test script against any URL:

```bash
python3 /home/workspace/Skills/ux-tester/scripts/ux-test.py <url> [options]
```

### Options
- `--device <name>` — Simulate a device: `iphone-14`, `pixel-7`, `ipad`, `desktop` (default: `desktop`)
- `--flow` — Run full UX flow: navigate, interact with modals/popups, scroll, capture each step
- `--output <dir>` — Output directory for screenshots and report (default: `/home/workspace/Skills/ux-tester/reports/`)
- `--wait <seconds>` — Extra wait time after page load (default: 3)
- `--click <selector>` — Click a specific element after load (can be used multiple times)
- `--full-page` — Capture full-page screenshot instead of viewport only
- `--measure` — Include performance metrics (LCP, FCP, TTFB, DOM size)
- `--help` — Show help

### Examples

```bash
# Basic desktop UX check
python3 scripts/ux-test.py https://www.myvurt.com --flow --measure

# Mobile UX check (iPhone)
python3 scripts/ux-test.py https://www.myvurt.com --device iphone-14 --flow --measure

# Test a specific show page with full flow
python3 scripts/ux-test.py https://www.myvurt.com/detail/micro_series/karma-in-hells --flow --device iphone-14 --measure

# Just take a screenshot
python3 scripts/ux-test.py https://www.myvurt.com --full-page
```

### Output
- Screenshots at each step of the flow (numbered: `01-initial.png`, `02-after-modal.png`, etc.)
- `report.md` — Markdown report with findings, metrics, and embedded screenshot references
- `metrics.json` — Raw performance data

### How It Works
Uses Playwright with stealth patches to appear as a real browser:
- Real Chrome user agent and fingerprint
- No `navigator.webdriver` flag
- Real viewport, fonts, plugins
- Human-like delays between interactions
- Dismisses cookie banners, age gates, and signup modals automatically

This is NOT a scraper — it's a UX verification tool that sees exactly what your users see.

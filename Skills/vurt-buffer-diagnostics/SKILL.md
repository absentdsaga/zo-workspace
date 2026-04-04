---
name: vurt-buffer-diagnostics
description: Run NPAW + GA4 buffering diagnostics for VURT. Pull buffer ratios by CDN, device, ISP, and show. Compare against GA4 engagement. Generate dev team action items.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

## When to Use
- When checking current VURT buffering/quality metrics
- When preparing dev team communications about video performance
- When comparing CDN performance (Fastly vs CloudFlare)

## How to Run

### Quick Check (last 4 hours)
```bash
python3 scripts/buffer-check.py --hours 4
```

### Full Diagnostic (includes GA4 cross-reference)
```bash
python3 scripts/buffer-check.py --hours 24 --ga4
```

### CDN-Specific Deep Dive
```bash
python3 scripts/buffer-check.py --hours 4 --cdn-detail
```

## Key References
- `references/fastly-diagnosis-checklist.md` — Questions for Enveu about Fastly config
- `references/quick-wins.md` — Ordered list of fixes by impact

## Environment
Requires: `NPAW_API_SECRET`, `NPAW_SYSTEM_CODE`, `VURT_GOOGLE_OAUTH_CLIENT`, `VURT_ANALYTICS_REFRESH_TOKEN`

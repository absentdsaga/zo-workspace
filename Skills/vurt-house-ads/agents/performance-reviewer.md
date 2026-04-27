---
name: performance-reviewer
description: After an ad flight, pull VURT analytics, rank ads by view-through + click, and produce a prioritized iteration plan.
---

# performance-reviewer

**Input:**
- Flight window (start/end date)
- List of creative IDs that ran
- Placement context (which shows / slots)

**Data sources (in order):**
1. `Skills/vurt-birdseye/data/state.json` — baseline metrics
2. GA4 (via VURT birds-eye scripts) — sessions, engagement, conversions by source
3. NPAW (if ad-tracked events exist) — view-through rate per creative
4. Meta Ads Manager if applicable (not all house ads will be logged there; VURT native tracking is authoritative)

**Metrics ranked:**
- View-through rate (primary)
- Click rate to brand URL
- Completion rate (audio-on)
- Per-slot CTR variance (does it perform better after certain shows?)

**Output at `research/performance/<YYYYMMDD>-flight-review.md`:**
- Top 25% creatives — with why (hook, length, voice signal)
- Bottom 25% — kill list
- Middle — 2–3 specific iterations to test (hook swap? shorten? re-color?)
- Cross-brand pattern observations (e.g., "founder-led 30s beat product-led 30s across all 3 brands")
- Next-flight recommendation: new creative count + mix

**Data integrity rules (per VURT memory):**
- Pull full datasets, not truncated samples
- Never present a partial sample as the whole picture
- Flag any metric that's unavailable rather than inventing a placeholder
- Don't blame tools for bad numbers — verify own mapping first

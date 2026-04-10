# VURT Paid Ads Bounce Investigation — Full Timeline

**Last Updated:** April 7, 2026
**Prepared by:** Dioni (VURT)

---

## The Question

Why is paid social traffic bouncing at 99.6%? Is it the ads, the site, or both?

---

## Three Distinct Phases

| Phase | Dates | Bounce Rate | Daily Paid Sessions | What Changed |
|-------|-------|-------------|--------------------:|--------------|
| **Phase 1** — High Volume | Mar 18–30 | ~90–93% | 3,800–9,900 | Consent Mode broken (defaulting to deny), broad targeting, high spend (~$200+/day) |
| **Phase 2** — Post-Fix | Apr 1–5 | ~71–78% | 800–2,100 | Consent Mode fixed, GTM installed, reduced spend, geo-targeted campaigns |
| **Phase 3** — SSR Break | Apr 6–7 | ~99.6% | 650–1,600 | SSR deployed, expanded ad campaign same day |

---

## Day-by-Day Timeline

### March 2026

| Date | Ad Side | Tech Side | Bounce | Paid Sessions |
|------|---------|-----------|--------|---------------|
| **Mar 5** | Tarik introduces Simple Social to handle paid ads | — | — | — |
| **Mar 9** | Facebook page suspended | — | — | — |
| **Mar 14** | Facebook page restored | — | — | — |
| **Mar 17** | **Ads launch** (TechCrunch launch day). Broad targeting, mixed landing pages | — | — | — |
| **Mar 18** | First full day of ads | Consent Mode v2 broken — defaulting to `denied`, inflating bounce | 91.1% | 5,249 |
| **Mar 19** | | | 91.1% | 4,806 |
| **Mar 20** | | | 89.5% | 4,970 |
| **Mar 21** | | | 90.3% | 6,041 |
| **Mar 22** | | | 89.1% | 5,561 |
| **Mar 23** | **Tarik's strategy pivot:** stop broad targeting, specific cities only, 10%+ CTR ads only, ALL content ads → series pages not homepage | | 90.9% | 6,404 |
| **Mar 24** | New geo-targeting takes effect | | 90.8% | 5,773 |
| **Mar 25** | | | 92.2% | 7,062 |
| **Mar 26** | Spend ramping up | | 92.9% | 8,836 |
| **Mar 27** | Peak spend period | | 92.1% | 9,879 |
| **Mar 28** | | | 91.8% | 9,094 |
| **Mar 29** | Budget nearly exhausted | | 91.4% | 3,889 |
| **Mar 30** | **Budget spent** ($5,695 total). Tarik proposes new $5K for Apr 1–15 | | 93.4% | 412 |
| **Mar 31** | Almost no spend | **GTM installed, Consent Mode fixed, Meta Pixel added** | 100% | 8 (negligible) |

### April 2026

| Date | Ad Side | Tech Side | Bounce | Paid Sessions |
|------|---------|-----------|--------|---------------|
| **Apr 1** | **New campaign:** 6 videos, 3 geo ad sets (US Cities, African Cities, Europe/Canada/Caribbean), series page landing. Karma In Heels challenger ad | Consent Mode now working correctly | **71.5%** | 1,893 |
| **Apr 2** | | | **71.3%** | 2,078 |
| **Apr 3** | Ariella sends new "What is VURT" video versions | | **74.2%** | 1,506 |
| **Apr 4** | Reduced spend (bounce concerns from investors) | | **72.5%** | 797 |
| **Apr 5** | | | **78.3%** | 1,787 |
| **Apr 6** | **Christian expanded campaign:** +6 titles (Church Boy, My Baby Mama, Drops of Mercy, Something Like Business, Killer Step Dad, Karma In Heels) + 3 "What is VURT" versions → homepage | **Enveu deployed SSR (Angular Universal) ~6am EST** — `user_engagement` event stops firing | **99.6%** | 1,609 |
| **Apr 7** | Tarik changed ads again | SSR still breaking engagement tracking | **99.7%** | 646 |

---

## The Smoking Gun: Landing Page Comparison (Apr 5 vs Apr 6)

Same pages, same ads — overnight change proves SSR deploy is the cause, not the new ad creatives.

| Landing Page | Apr 5 Bounce | Apr 5 Sessions | Apr 6 Bounce | Apr 6 Sessions |
|-------------|-------------|----------------|-------------|----------------|
| /detail/micro_series/girl-in-the-closet | **79.2%** | 890 | **99.8%** | 458 |
| /detail/micro_series/baby-mama | **88.8%** | 349 | **99.6%** | 238 |
| /detail/micro_series/killer-stepdad | **78.0%** | 173 | **99.7%** | 724 |
| / (homepage) | **51.3%** | 156 | **100%** | 55 |
| /detail/micro_series/come-back-dad | **77.6%** | 85 | **100%** | 77 |
| /detail/micro_series/something-like-a-business | **80.6%** | 67 | **100%** | 7 |
| /detail/micro_series/church-boy | **72.7%** | 22 | **100%** | 34 |

**Every single page jumped from 72–89% to 99.6–100% overnight.** The new titles Christian added (Church Boy expansion, Drops of Mercy, etc.) aren't the problem — pages that were working on Apr 5 broke identically on Apr 6.

---

## Root Cause: SSR Broke GA4 Engagement Tracking

### What we proved:
1. **Playwright test** (Apr 6): Loaded myvurt.com, waited 30+ seconds, switched tabs — `user_engagement` event **never fired**. Only `page_view` and `screen_viewed` fired.
2. **Browser console test**: Same result — engagement events absent after SSR deploy.
3. **GA4 defines "bounce" as a session without engagement.** If `user_engagement` never fires, GA4 reports 100% bounce regardless of what the user actually does on the page.

### Why SSR likely broke it:
- GA4 is loaded via Firebase SDK, hardcoded in Enveu's HTML: `gtag('config', 'G-F13X2NV8D0', {origin: 'firebase', firebase_id: '...'})`
- Angular Universal SSR pre-renders on the server, then "hydrates" on the client
- If the engagement timer initialization runs during SSR (server-side, where there's no `visibilitychange` event), it may never properly attach client-side listeners
- The `user_engagement` event fires on `visibilitychange` or `pagehide` — both are browser-only events that don't exist in a Node.js SSR context

### What the dev team needs to investigate:
1. Does `gtag.js` initialize during SSR or only after client hydration?
2. Are `visibilitychange` and `pagehide` event listeners being registered after hydration?
3. Is `window.gtag` available and functional after hydration completes?
4. Simple test: open browser console on myvurt.com → `window.gtag('event', 'test_engagement', {})` — does it fire?

---

## What's Real vs What's Inflated

| Phase | Bounce Rate | Assessment |
|-------|-------------|------------|
| Mar 18–30: 90% | **Partially inflated** — Consent Mode was broken (defaulting to deny), which prevents GA4 from storing cookies and may drop engagement events. Real bounce was high but not necessarily 90%. |
| Apr 1–5: 72% | **Most accurate baseline we have** — Consent Mode fixed, tracking working, engagement events firing. But volume was only ~1,500/day vs ~7,000/day before. |
| Apr 6+: 99.6% | **Almost entirely inflated** — SSR broke `user_engagement` event. Real bounce is unknown but likely similar to Apr 1–5 baseline (~72–78%). |

**We have never had fully working tracking AND full ad volume at the same time.** Once SSR is fixed and ads scale back up, we'll see the true baseline for the first time.

---

## Recommended Action Plan

### Immediate (Dioni → Dev Team)
1. **Fix user_engagement in SSR** — This is the #1 priority. The dev team needs to ensure gtag.js event listeners attach properly after client-side hydration. Until this is fixed, all bounce data is useless.
2. **How to verify the fix:** After deploying, check GA4 Realtime → Events. `user_engagement` should appear within 10–15 seconds of someone visiting any page. Dioni can also verify in browser console.

### Short-Term (Once tracking is fixed)
3. **Run ads at Apr 1–5 volume for 3–5 days** with working tracking to establish true baseline bounce rate
4. **Compare series page bounce vs homepage bounce** — the Apr 5 data already suggests homepage (51.3%) dramatically outperforms series pages (72–89%)
5. **Address the 5 UX issues** from the [Bounce Forensics doc](VURT-Paid-Ads-Bounce-Forensics.md) — broken skeleton render, black video player, 84MB preload, 5MB JS bundle, age gate over black screen

### Medium-Term (Once baseline is established)
6. **Scale spend back up** in increments — $50/day → $100 → $200 — watching bounce at each level
7. **A/B test homepage vs series page landing** with equal budgets to settle the landing page question with data
8. **Factor in Tarik's frequent ad changes** — tag or timestamp every creative/targeting change so bounce shifts can be attributed to specific changes

---

## Key Contacts & Roles

| Person | Role | Relevant To |
|--------|------|-------------|
| **Dioni** | VURT co-lead, coordinating all teams | Everything — analytics, dev liaison, ads strategy |
| **Mark Samuels** | VURT co-lead, dev liaison | Dev team communication, SSR fix |
| **Christian Guzman** | Simple Social, campaign manager | Ad creative changes, targeting, spend |
| **Alex Akimov** | Simple Social, lead | Ads strategy, reporting |
| **Ariella Lafayette** | Simple Social, operations/creative | New video assets, "What is VURT" versions |
| **Tarik Brooks** | Investor, active in ads strategy | Frequent ad changes, budget decisions, targeting direction |
| **Ted Lucas** | Investor | Strategy oversight |
| **Hilmon Sorey** | Lead investor | Strategy oversight |
| **Enveu** | Dev team | SSR fix, site performance, tracking implementation |

# VURT Social Ops -- Live State
### Last Updated: 2026-04-16

---

## Active Platforms
| Platform | Handle | Status |
|----------|--------|--------|
| Instagram | @myvurt | ACTIVE (primary) |
| TikTok | @watchvurticals | ACTIVE (Business account, verified) |
| Facebook | VURT page | ACTIVE |
| YouTube Shorts | VURT channel | ACTIVE |
| LinkedIn | VURT company page | ACTIVE (B2B, filmmaker spotlights) |
| X | @myvurt | Not yet |

## CTA Direction
All CTAs drive to **myvurt.com** (web). NOT app stores.

## Content Priority Order
1. VURT Originals (full machine treatment)
2. Submissions
3. Backlog (previously released on other platforms)

---

## ACTIVE TITLES

### The Love Network Jam (CURRENT PUSH)
- **Type:** Original
- **Platforms:** Rolling out now
- **Active dates:** Apr 14 - (ONGOING)
- **Note:** Current primary title being pushed across platforms

### SCHEMERS (35 posts -- winding down)
- **Type:** Original (UGC handoff received)
- **Platforms:** IG (13), FB (12), YT Shorts (10)
- **Active dates:** Mar 25 - Apr 14
- **Top performer:** IG clips getting 1,600-4,400 views
- **Note:** Last posts went up from UGC handoff, not the active push anymore

### Come Back Dad (6 posts)
- **Type:** Licensed
- **Platforms:** IG (1), FB (2), YT Shorts (3)
- **Active dates:** Mar 4 - Apr 14 (ONGOING)
- **Note:** Had a viral moment (243K views on one IG post)

### 99 Jamz x VURT (5 posts)
- **Platforms:** IG (1), FB (2), YT Shorts (2)
- **Active dates:** Apr 2 - Apr 14 (ONGOING)

### Director Spotlight series (8 posts)
- **Type:** Filmmaker features
- **Platforms:** IG (4), FB (3), LinkedIn (1)
- **Active dates:** Mar 30 - Apr 11
- **Cadence:** Weekly features

---

## ARCHIVE (Completed Title Cycles)

### Karma in Heels (18 posts -- COMPLETE)
- **All platforms:** IG (5), FB (5), TikTok (4), YT Shorts (4)
- **Dates:** Mar 26 - Mar 30
- **Note:** First full title cycle

### Parking Lot Series (23 posts -- COMPLETE)
- **Platforms:** IG (8), FB (9), YT Shorts (6)
- **Dates:** Mar 26 - Apr 6

---

## PIPELINE (Frame.io -- 153 social clips ready across 25 shows)
Shows with social clips ready: Frenemies (10), The Love Network Jam (12), Something Like A Business (6), Soul Ties (6), She's Not Our Sister (7), Saving Grace (5), Saving Westbrook High (6), Through Thick and Thin (6), The Wrong Choice (6), and 15+ more.

---

## TIKTOK STATUS
- **Business Center:** Verified, active (URL verification complete Apr 15)
- **Ads Manager:** VURT_adv account approved, billing set up
- **Team access:** Alex (Simple Social) + Mark invited as members
- **Developer API:** App submitted for review Apr 16 (status: In Review on TikTok for Developers)
- **TikTok Pixel (Web):** ID `D7GJKJBC77UBV63HQDUG` -- LIVE via GTM (GTM-MN8TR3CR), tag name `TT-D7GJKJBC77UBV63HQDUG-Web-Tag-Pixel_Setup`, trigger: All Pages. AAM enabled (all 5 data types). GTM Version 3 published Apr 16. All 6 setup steps complete. **VERIFIED FIRING 2026-04-16:** TikTok Events Manager shows "You're all set" with 21 total events received on the VURT Web Pixel dataset. Pixel is live and ingesting traffic.
- **Posting:** No TikTok posts synced via API yet (manual only until dev app approved)

---

## WEB TRACKING STATE (myvurt.com)
### GTM Container `GTM-MN8TR3CR` -- 2 tags live (Apr 16):
1. `Meta Pixel - Base` (Custom HTML, installed ~Apr 1) -- All Pages trigger
2. `TT-D7GJKJBC77UBV63HQDUG-Web-Tag-Pixel_Setup` (Custom HTML, Apr 16) -- All Pages trigger

### NOT in GTM (needs investigation):
- GA4 -- either hardcoded by Enveu or missing entirely
- Firebase Analytics -- hardcoded in Angular (expected)
- Custom events (signup, video_play, age_gate_passed) -- unknown location

### Codebase migration prep
Handoff doc in progress: `Documents/VURT-Tracking-Migration-Handoff.md`. Audit request to Enveu pending. Key unknowns: GA4 install method, Firebase project ownership, DNS/CloudFlare account ownership, custom event inventory.

---

## PENDING
- TikTok API verification (dev team blocker)
- YouTube Analytics deep metrics (needs Ari's OAuth from ari@thesourcegroups.com)
- Full Frame.io <-> Calendar linking
- Chief Keef / Glo Navy (unscripted) -- in production, not yet in social pipeline

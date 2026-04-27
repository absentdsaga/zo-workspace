# VURT Social Ops -- Live State
### Last Updated: 2026-04-23 (verified live APIs: Meta Graph, YT Data, GA4, Mux)

> Companion: `data/channel-winners.md` (per-channel top performers from daily reports).
> Captions playbook: `Skills/vurt-captions/references/winning-patterns.md` (TikTok save-rate winners, IG clip reel patterns, FB double-drop, YT premiere strategy).
> Video editor guide: `Documents/VURT-Social-Video-Editor-Guide.md` (v1 2026-04-23) — cut rules with the WHY, per-platform specs, Frame.io tag workflow, paid/organic distinction.

---

## Active Platforms
| Platform | Handle | Status |
|----------|--------|--------|
| Instagram | @myvurt | ACTIVE (primary) |
| TikTok | @myvurt | ACTIVE (Business account, verified) |
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

---

## DATA-DRIVEN DIRECTIVES (as of 2026-04-23 live pull)

### Two material corrections from prior state

1. **FB is ~98% paid, not 98% "Recommended algo."** 14d FB page video views = 447,266 total → **439,260 paid / 8,006 organic** (verified via `page_video_views_paid` Graph API). The old script computed `(total − organic)` and labeled it Recommended; that bucket is ad spend, primarily Simple Social's campaigns.
2. **YT top 3 aren't full-episode premieres.** They're 56s–2:30 catalog clips labeled "Premiere" in title (none use YT's actual Premiere feature — zero `liveStreamingDetails` across 42 uploads). The "full episodes win" claim was wrong; we've never uploaded one to test.

### Cross-channel
- **Clone TikTok's 4 save-rate winners' structure (70%),** run adjacent hypothesis-driven experiments (20%), leave one wild slot per week (10%). Details in `Skills/vurt-captions/references/winning-patterns.md`.
- **Pull Girl in the Closet into social rotation NOW.** Mux 14d: Ep1 13,131 views @ 68% completion, Eps 2-7 at **91–93% completion** (highest on platform). Biggest untapped clip source. Still absent from posting.
- **Mine Come Back Dad deeper.** Tatyana Ali ("Spence") monologue is the #1 TikTok save winner (2.47%). Mux: 80–93% completion across all 7 episodes. Under-clipped relative to proven appetite.

### IG: clip reels with character voice
- 14d totals: 38,161 reach / 222 saves / 329 shares. Top posts are 2,600–5,985 reach on in-world character lines. Brand/feed plateau: 78–200 reach.
- Top save-rate IG Reel (14d): "The rule they swore they'd keep" (Favorite Son) 0.79%. IG save-rate runs lower than TikTok; use reach + watch-time (AvgWatch ms) as tiebreakers.
- Move director spotlights to LinkedIn or IG Stories.

### TikTok: save rate is the KPI, upper-third overlay every post
- 25 of 29 recent posts failed the 1% save threshold. The 4 winners share structure — clone it, run adjacent experiments with written hypotheses (see 70/20/10 framework).
- Save rate is the leading indicator because: saves = intent to return, algo re-surfaces high-save videos, shares/F2F too noisy at our volume, and it separates FYP blasts (high-view/low-save) from real appetite.
- Dev API still in review (submitted Apr 16). Manual posting until then. Share/view/like/comment/save counts ARE available via public scraper (`Skills/vurt-post-log/data/tiktok_user_url_scrape.json`, 41 posts); only F2F (follows-from-FYP) blocked on dev API.
- **TikTok Boost counts as paid social.** The two top TikTok posts by views — SLAB "He tried to stand up" (380K) and KIH "You did this" (189.6K) — were boosted in-app. Exclude them from organic pattern cloning; bucket them with Meta ads when accounting for paid-social reach.

### FB: treat as a paid-ads channel, not a content channel
- Organic FB reach is effectively dead at this page size (~570 organic video views/day across the whole page).
- `myvurt.com` clickable in line 1 still required (only surface where it routes in-feed).
- Posting continues for hygiene + ad attribution; don't set editorial targets against FB view totals — those move with ad spend, not content quality.

### YouTube: catalog clips, real premieres worth testing
- 42 uploads, 320,576 total channel views. Three breakouts (166K / 74K / 40K) are short catalog clips on named shows, not full episodes.
- Keep current cadence (catalog-AM / premiere-PM, per Dioni's flow).
- **Test YT's actual Premiere feature** for new originals — scheduled with countdown + live chat. Cheap A/B worth running this month.
- Full-episode uploads = untested, business-case-dependent. Decide cannibalization vs growth before testing.

### GA4 reality check (14d)
- **Paid Social = 87.2% of sessions, 5.9% engagement.** fb/paid_ads alone: 73,436 sessions at 4.9% eng. Not a quality stream.
- **Organic Search = 686 sessions, 74.5% engagement.** Tiny but gold — don't strip cast/director/show names from captions, they compound here.
- **Paid destination red flags:** karma-in-hells 53,609 sessions @ 2.0% eng; killer-stepdad 10,926 @ 3.8%; baby-mama 2,525 @ 3.5%. Flag to Simple Social — creative-page mismatch.

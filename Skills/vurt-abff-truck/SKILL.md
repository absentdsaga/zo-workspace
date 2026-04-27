---
name: vurt-abff-truck
description: Creative + production skill for the LPMG digital billboard truck that will run VURT ads at ABFF 2026 (Miami Beach). Covers truck specs, creative treatments for two variations (Launch Party at Gates Hotel on Fri May 29 + always-on downloads/submissions), stickiness mechanics, and production handoff notes. READ this before producing assets, and UPDATE as decisions land.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# VURT × ABFF Truck (LPMG digital billboard)

## What this is
LPMG (Lex Promotions Marketing Group, Miami) digital billboard truck circulating during ABFF week in Miami Beach. Two creative variations share rotation:
- **V1** — VURT Launch Party, **Friday May 29** (Gates Hotel South Beach, two-tier: open ground floor + invite-only rooftop)
- **V2** — General VURT (web watches + submissions)

Vendor contact: `info@lexpromotions.com` / (305) 974-4568.

## ABFF 2026 verified facts (use in all creative + planning)
- **Dates:** May 27 – May 31, 2026 (Wed–Sun). 30th anniversary; theme "Homecoming."
- **Opening Night:** May 27, 7 PM — *Strung* premiere at New World Center, Opening Night Party at The Bass Museum.
- **Core venues:** New World Center, Miami Beach Convention Center, O Cinema, The Bass Museum.
- **No single host hotel.** ABFF uses a partner-hotel discount list; festivalgoers are spread across Miami Beach.
- **Key sponsors / official partners:** Warner Bros. Discovery + HBO (founding), Amazon MGM, Comcast NBCUniversal, Ally Financial, Sony Pictures, Netflix, Hartbeat, STARZ, L'Oréal, American Airlines, Uber. New for 2026: **ABFF Sports** programming track.
- **Pre-events:** No in-Miami pre-events before May 27. LA Pop-Up already ran.
- **Implication:** VURT Launch Party is **Friday May 29** — peak ABFF night (mid-festival, most attendees on the ground, most programming running). Not opening night. Frame is "the VURT night of ABFF" — must pull people *off* other Friday ABFF parties, not land after them. Strongest competitive pressure is other Friday night activations (industry dinners, sponsor after-parties). Creative urgency must be higher than a 5/27 frame would have needed.

## Truck specs (verified from LPMG Dropbox)

### Static images
| Face | Dimensions | DPI | Notes |
|------|-----------|-----|-------|
| Side | 8"W × 4"H | 300 | 2:1 aspect. Will be shared across panel on a moving unit. |
| Rear | 5" × 5" | 300 | 1:1. Viewed from cars behind the truck. |

### Video
| Face | Resolution | Audio | Aspect |
|------|-----------|-------|--------|
| Side | 1920 × 1080 | WITH sound | 16:9 |
| Rear | 1080 × 1080 | NO sound | 1:1 |

### Hard production rules (from LPMG)
- **Submit JPEG for static, MP4 for video.** No need for 4K.
- **Designed at SCALE, not actual size.** Provided to LPMG; they up-res for panels.
- **No skinny fonts. No white-on-white. Bold fonts only.** LED bleeds whites and loses thin strokes.
- Rotation loop — ad plays among other advertisers. Each slot is short. Brand must stamp in <2s.
- For video: multiple images/cuts can be timed with audio.

## Creative principles (non-negotiable)

1. **Brand stamp in 2 seconds** — VURT logo/color must be legible from the first frame, not delayed for a reveal. The truck is in rotation with other ads; if a viewer glances for 2s and doesn't register "VURT," the spot failed.
2. **Rear = QR throne.** Rear face is viewed by drivers at red lights and in traffic — 10–60+ second dwell is common. This is the highest-converting surface. Treat it like a poster with a QR code big enough to scan from 15–20 ft.
3. **Side = silent mini-commercial.** Pedestrians and sidewalk crowds at Miami venues will catch 5–10s. **No audio** — Miami Beach §46-152 flatly prohibits loudspeakers/amplifiers on vehicles. The spot must carry on type, motion, and cuts. Treat audio as legally unavailable (see `references/research-notes.md` §8).
4. **No signup wall in the CTA.** VURT is AVOD; users don't see signup until the 10th video. Pitch "free to watch" directly — it's a real unlock not many competitors have.
5. **CTAs go to web, not app stores.** Per VURT rule: `myvurt.com` is the destination. A dedicated landing page handles ABFF traffic (see Stickiness).
6. **Color + type system matches VURT brand.** No improvising; pull the exact brand tokens from `Documents/VURT-master.md` / existing brand assets.
7. **Not generic "streaming" language.** Don't say "watch anything, anytime." Say what VURT is: culture-first, creator-driven, horror/hood/halo (or whatever pillars are cleared).
8. **Do NOT mention "ABFF" on-screen.** VURT is not an official ABFF sponsor. Use dates only ("Fri 5.29 · Miami Beach"). Mentioning ABFF creates trademark/association risk.

## Stickiness architecture

**Landing page:** `myvurt.com/abff` — **internal dev team building.** Must be date-aware AND split-flow for the two-tier party:
- Before **May 29** → Page splits into two CTAs:
  - **"Request rooftop invite"** → gated RSVP form (500-cap, invite-only). Captures email + phone; auto-reject/waitlist if not on pre-approved list.
  - **"Walk-in ground floor"** → venue address + hours + "open to public, rooftop separate." Lower-friction capture: email only, no gating.
- May 30 onward → Featured VURT content reel, auto-play, "Keep watching" CTA.

**QR keyword:** Use **`VURT`** (not "ABFF") — we're not sponsors, and the brand keyword is more valuable for recall anyway.

**QR codes:** Single QR per variation, each tracked with a distinct UTM (`utm_source=truck&utm_campaign=miami-2026&utm_content=v1-rsvp` / `v2-general`). Note `miami-2026` not `abff-2026` in public-facing strings to stay off trademark turf.

**SMS fallback — 10DLC only (if we do SMS at all).** Shared shortcodes are banned (2021+); dedicated shortcode takes 8–12 weeks (won't hit 5/29). 10DLC (Twilio + SimpleTexting) can stand up in ~2–3 weeks IF brand + campaign registered by **~2026-05-01** for a 5/29 launch. See `references/research-notes.md` §12 for stack and TCPA opt-in flow. **Recommendation: skip SMS for round 1.** Keep the truck simple — QR → landing page → Meta pixel builds a retarget Custom Audience at near-zero cost and no compliance surface area. Add SMS in a later campaign once the program has a dedicated owner.

**Geo-routing:** If LPMG supports route control, weight Lincoln Rd perimeter (the mall itself is pedestrian-only), Collins Ave (Gates Hotel to NWC corridor), Washington Ave (O Cinema), Convention Center loop during peak evening hours (Thu–Sat of ABFF week). **Brief driver on Miami Beach cruising ordinance (Ch. 106, Art. VII)** — repeated passes of same traffic point in Ocean/Collins/Washington = violation.

**Paid retargeting stack (LOCKED — run all three layers):**
- **Layer 1 — Geofence vendor (Simpli.fi or GroundTruth):** Polygon the truck's ABFF-week route; capture household-IP signals for phones that entered the zone (post-ATT, IDFA mostly dead). Retarget those households on Meta/display for 14 days. Budget **$6–10K total** ($5–9K media + $1K fees). Workhorse layer — reaches the ~95% of truck viewers who saw the panel but never scanned. Confirm vendor's Florida Digital Bill of Rights posture in writing.
- **Layer 2 — Meta pixel Custom Audience (scanners):** Meta pixel + CAPI on `myvurt.com/abff`. Everyone who scans the QR and lands auto-joins a retarget Custom Audience. $500–1K in Meta spend for 14 days. Small audience but ~10× higher intent.
- **Layer 3 — IG/TikTok geo-radius (broader awareness):** $500–1K in Meta + TikTok geo-radius ads to 33139 / 33140 / 33109 zips during truck week. Creative echoes the truck exactly (same hero frame, same shows, same QR as fallback). Catches ABFF-week foot traffic outside the truck's literal route (Wynwood, Design District, industry hotels outside SoBe core).
- **Total stack:** ~$7–12K on top of truck media. Expect 15–35% incremental return-visit lift vs. truck alone.
- **Why all three:** Truck viewers outside zip boundaries = Layer 1. Scanners with highest intent = Layer 2. Broader ABFF-week crowd that didn't see the truck but fits the profile = Layer 3. Each hits a different slice of the conversion funnel.

## Variations — high level

See `storyboards/v1-launch-party.md` and `storyboards/v2-general.md` for full treatments.

**V1 — "Tonight on the roof."**
Two-tier party at Gates Hotel. Ground floor = decked out VURT experience, open to walk-ins + invitees. Rooftop = 500-cap RSVP invite-only. Ground floor creates FOMO for rooftop. Truck creative must sell the **rooftop as the hero** (aspirational visual) with split CTA on the landing page — don't try to explain both tiers in 2 seconds of glance.

- Venue: **The Gates Hotel South Beach, 2360 Collins Ave, Miami Beach.** 2 blocks from The Bass Museum.
- **Ground floor:** VURT experience / walk-in layer. Open to public + invitees. Branded activation, content walls, photo moments, ID + bar gate for alcohol (hotel handles). Goal: capture walk-ins as future users, generate visible line/energy on the street.
- **Rooftop:** 500-cap **invite-only / accepted RSVP.** Industry, investors, press. Where the party "really is." *(Verify cap with hotel — Plunge Deck published cap is 110; 500 likely combines deck + adjacent rooftop spaces or a build-out.)*
- Dress code: **business casual.**
- Start time: **TBD** (Dioni to confirm).
- Date: **Friday May 29, 2026.**
- Truck keyword: "Request rooftop." Short, specific, aspirational. Ground-floor info lives on the landing page, not the panel.

**V2 — "Free. No sign-up. No ads. Just culture."**
VURT as the free, culture-first platform. Four objections removed in one line. Silent rotating content stills → VURT logo → QR → myvurt.com. Zero-friction — user scans, lands on auto-playing content within 3 seconds. Deferred signup (AVOD rule — KPI is video views).

## Success KPIs (must agree before production)

- **Awareness:** Impressions served (LPMG provides), geo-weighted coverage of ABFF zones.
- **Response:** Unique QR scans by variation (UTM tracked in GA4).
- **V1 conversion:** RSVP form submissions → Launch Party attendance.
- **V2 conversion:** Video plays per QR session (`ga4: videoStart` events after truck referral), 10-video completion cohort.
- **Residual:** Follower deltas on @myvurt IG/TT during ABFF week.

## Gaps blocking production

See `QUESTIONS.md` — do not start final production until these are answered.

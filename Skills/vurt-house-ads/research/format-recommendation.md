# Format Recommendation — 15s vs 30s Mix

## Placement specs (confirmed)
- **Length cap:** 30s
- **Skippable:** NO
- **Audio:** On
- **End-card:** Clickable

## TL;DR — Revised
**First wave: 1 × 30s + 1 × 15s per brand = 6 spots. + Spanish cuts for SinFiltros = 8 total.**

Production window: **~1 week.**

Default format weight: **30s is the hero, 15s is the retargeter.**

## Why 30s leads, not 15s

Non-skippable + audio-on + clickable = the VURT pre/mid-roll is closer to a **TV spot than a feed ad.**

- Viewer can't bail. The hook buys us 2s max, but after that we get the full 28s for payload.
- Audio carries VO, music, founder delivery. The ad can *talk.*
- End-card is the close. 30s has enough room to earn the click; 15s has to sprint.
- Our audience is already narrative-mode (vertical micro-drama). A founder telling a story is on-format.
- **Only reason to go 15s:** Frequency capping and retargeting after wave 1 has data.

## Revised week-one slate (6 + 2 SP = 8)

### RIELLI (2 spots)
- **30s hero — Founder story.** Arielle on camera. "I built Rielli one piece at a time. No factory. No permission." Worn-by moments (Kardashian, SI) woven in as proof. End-card → riellibrand.com.
- **15s cut — Craftsmanship x Identity.** Atelier hands + "not one of many" VO + body-in-swim cutaway. Re-uses footage from 30s shoot.

### SINFILTROS NUTRITION (2 EN + 2 ES = 4 spots)
- **30s hero (EN + ES) — Valentina founder story.** "Post-bariatric. My body changed. My supplements didn't work. So I made my own." MOODMIES + GLOWMIES product reveal. End-card → sinfiltrosnutrition.com.
- **15s cut (EN + ES) — Glow/PMS reality.** Close-up skin/hair beauty + "day 3 and I didn't cancel plans" hook. Re-uses 30s footage.

### TRICK DADDY POTS (2 spots)
- **30s hero — Trick on camera.** Bridge Sunday's Eatery → home kitchen → family dinner. "From my kitchen to yours." Massive unlock: Trick is already VURT cast, so we're introducing the pots through a face the audience already knows.
- **15s cut — Price/value.** Set of 15, $169.99 + Sunday dinner timelapse. Ends on Trick's "I got you."

## Production efficiency rule
Every 30s shoot must produce its matching 15s from the same session. One shoot day per brand = 2 spots. That's how we hit a week turnaround.

## Landing + tracking
- Rielli → https://riellibrand.com?utm_source=vurt&utm_medium=in-app&utm_campaign=wave1&utm_content=[15s|30s]
- SinFiltros → https://sinfiltrosnutrition.com (same UTM pattern, + &utm_term=en|es)
- Trick Daddy → https://trickdaddypots.com (same UTM pattern)
- No promo codes yet — once we have them, we unlock an offer-stack variant tier in wave 2.

## What goes live-action vs AI

Based on the AI stack (see `references/ai-video-stack-2026.md`):

**Must be live-action (founder on camera):**
- Rielli 30s founder (Arielle)
- SinFiltros 30s founder (Valentina, both languages)
- Trick Daddy 30s hero (Trick)

**Hybrid (live + AI b-roll):**
- All 15s cuts. Founder audio + real product moments + AI-gen lifestyle/texture b-roll via Veo 3.1 and Runway Gen-4.5 using brand reference stills as image conditioning.

**Performance extension (shoot once, multiply):**
- Runway Act-Two on founder footage to build variant dialogue takes in wave 2 without a reshoot.
- ElevenLabs v3 voice clone (with signed consent) for VO variants and Spanish pickup lines.

## Wave 2 (only after data)
Week 2, after 7 days of live performance, the `performance-reviewer` agent pulls winners + losers. Then we produce 6-8 variants targeting:
- Top-performing hook extended into new angles
- Offer/promo-code cuts (once codes exist)
- Retargeting 15s cuts pointing at shoppers who bounced from the landing page

## Fatigue math
VURT weekly users ≈ 14K (current GA4). Non-skippable means higher forced-impression rate per user. Expect frequency fatigue in **2-3 weeks, not 3-4.** Fresh creative cadence: every 2 weeks after wave 1 lands.

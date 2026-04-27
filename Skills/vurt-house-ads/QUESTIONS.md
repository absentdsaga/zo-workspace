# Open Questions — VURT House Ads (for Dioni)

## RESOLVED (2026-04-17)

### VURT ad slot spec — LOCKED
- Length cap: **30s**
- Skippable: **No**
- Audio: **On**
- End card: **Clickable**
- Mid + pre-roll assumed until told otherwise.
- Implication: **30s is the hero format. 15s is for retargeting once we have data.** Format doc updated.

### Landing URLs — use brand sites
- Rielli → https://riellibrand.com
- SinFiltros → https://sinfiltrosnutrition.com
- Trick Daddy Pots → https://trickdaddypots.com
- All ads will carry UTM tags: `utm_source=vurt&utm_medium=in-app&utm_campaign=wave1&utm_content=<creative-id>`
- Promo codes: **none yet.** Wave 2 unlocks offer-stack variants once codes arrive.

### Production capability
- Video guy: **live-action + edit**, Miami-based (aligned with all 3 brands).
- AI stack: **flexible** — doc at `references/ai-video-stack-2026.md` with recommended tools by task. Editor should onboard Runway + Veo + ElevenLabs first.

### Volume + cadence — REVISED
- 24 ads in a week is not realistic for live-action founder shoots. **Wave 1 = 8 creatives** (1×30s + 1×15s per brand, + Spanish cuts for SinFiltros). Wave 2 after 7 days of data.
- Format doc updated.

---

## STILL OPEN

### Founder availability (blocks wave 1 shoot schedule)
- Arielle on camera for Rielli 30s — when?
- Valentina on camera for SinFiltros (EN + ES take in same session) — when?
- Trick Daddy — he's already VURT cast, so scheduling might be coordinated via VURT production. Who owns the ask?

### Asset access
- **Dropbox pull:** brief links raw brand assets (logos, product PNGs, existing footage). If I pull them into `Skills/vurt-house-ads/assets/` the editor and AI tools have a local reference library (color grade, product angles, typography) — and AI-gen b-roll can use real product stills as image-to-video conditioning. Want me to proceed?
- Any existing brand raw footage we can recut for first-wave 15s cuts? (faster than generating from scratch)

### Legal / claims
- SinFiltros — FTC disclaimer requirements for supplement claims? Required superbars on testimonial cuts?
- Rielli — can creative say "worn by Kim and Kourtney Kardashian" or must we stay with editorial press visuals only?
- Trick Daddy — can we film inside Sunday's Eatery?

### Measurement
- Does VURT's ad layer log creative ID + view-through + click internally? If yes, we map our UTM tags to VURT creative IDs. If no, UTM + GA4 on brand sites is our only signal.

### Talent cross-promo
- Beyond Trick, any other VURT cast tied to these brands? Cameo opportunities?
- Want me to scope a separate "VURT original starring Trick, cooking with the pots" branded-content unit, independent of the ad plan?

---

## Assumptions still standing
- 9:16 vertical
- No real-celebrity likeness in AI gen (Kardashians stay in editorial press cuts only)
- End card = brand + URL (+ offer when we have codes)
- Price shown for Trick Daddy Pots ($169.99), hidden for Rielli (premium logic), shown for SinFiltros bundle only

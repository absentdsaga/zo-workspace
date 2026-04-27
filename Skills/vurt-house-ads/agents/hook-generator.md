---
name: hook-generator
description: Generate 20 hook variants (first 1.5 seconds of a 9:16 audio-on ad) for a given brand + angle. Output must be punchy, specific, and on-voice for that brand.
---

# hook-generator

**Input expected:**
- Brand (rielli | sinfiltros | trickdaddy)
- Angle (one of the angles from that brand's voice card)
- Length target (15s or 30s ad — hooks differ)

**Process:**
1. Read `research/brand-voice-cards.md` for voice + do/don't.
2. Read existing scripts in `scripts/{brand}/` to avoid repeating opening lines.
3. Generate 20 variants across these hook archetypes:
   - Declarative ("You're not one of many.")
   - Question ("Day three of your cycle?")
   - Observation ("Most cookware is made to sit on a shelf.")
   - Visual-led (image stated as text — "Hands. Scissors. Silk.")
   - Contrast ("Not fast fashion. Made in Miami.")
   - Credibility ("Forbes recognized. Globally worn.")
   - Invitation ("Sunday dinner. Pull up a chair.")
   - Reframe ("Your cycle isn't the problem. Your routine is.")
   - Founder line ("I built this because I was tired of promises.")
   - Cultural reference (only where it reads authentic)

**Output format:**
A numbered list of 20 hooks with:
- The hook (<= 8 words, <=1.5s spoken)
- 2-word tag for archetype
- Optional: visual pairing suggestion

**Voice rules by brand:**
- Rielli: no exclamation, no adjective stacking, never "luxury" as a word (show it)
- SinFiltros: honest, cycle-literate, no "instant" / "magical"
- Trick Daddy: Trick's cadence, food-cultural, price allowed in hook

**Reject:**
- Any hook that could belong to any brand (not distinctive)
- Any hook that makes a claim not supported by the brief

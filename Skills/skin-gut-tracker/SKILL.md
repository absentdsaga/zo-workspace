---
name: skin-gut-tracker
description: Track dyshidrotic eczema + SNAS (Systemic Nickel Allergy Syndrome) protocol. Log daily symptoms, food, hand photos, flare triggers, and lab results. Cross-references meals against high-nickel, high-histamine, and MRT-reactive food lists. Use whenever Dioni reports a flare, a new food reaction, wants a daily log entry, or asks for progress review.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# Skin-Gut Protocol Tracker

Single source of truth for Dioni's dyshidrotic eczema + nickel allergy + gut protocol.

## Context (do not lose this)

- Diagnosis: dyshidrotic eczema driven by Systemic Nickel Allergy Syndrome, histamine overlay
- Confirmed nickel contact allergy (childhood + adult reactions to jewelry/buckles)
- Onset: after COVID vaccine, escalated during GI crisis ~Aug 2025
- Rescue: Betaderm (betamethasone valerate) — mid-potency, short-term only
- Daily supplements: L-glutamine 5g, NAC 600mg 2x, (recommended add: zinc picolinate 30mg, quercetin 500mg 2x, D3 5000IU)
- MRT test: 09/18/2024 — full data at `data/mrt-reactives.md`
- Distribution: right hand > left hand (middle finger), now spreading to inner thighs near groin (SNAS "baboon" pattern)
- Reflux + throat mucus + lethargy + immediate post-meal headaches = histamine/mast cell layer
- Labs NOT yet done — see `data/labs-todo.md`

## Files in this skill

- `data/mrt-reactives.md` — Dioni's MRT results, sorted by reaction level
- `data/nickel-food-lists.md` — high/medium/low nickel foods
- `data/histamine-foods.md` — histamine liberators + DAO blockers
- `data/symptom-log.md` — daily symptom + food log (append-only)
- `data/labs-todo.md` — prioritized labs checklist with status
- `data/supplements.md` — current stack + doses
- `photos/` — dated hand photos for objective progress tracking
- `scripts/log-day.py` — quick CLI to append a day entry
- `scripts/check-meal.py` — check a meal against nickel/histamine/MRT lists

## When to activate

Activate this skill whenever Dioni:
- Reports a flare or new symptom
- Asks "is X food safe?"
- Uploads a hand photo
- Wants a weekly/monthly progress review
- Has new lab results to log
- Adds/removes a supplement

## Workflow: daily log entry

1. Read `data/symptom-log.md` to see recent trend
2. Ask Dioni (or infer from message): hand severity 0-10, new spots, headache/reflux/bloat ratings, meals today, supplements taken, steroid used y/n
3. Append entry via `scripts/log-day.py` OR write directly to `symptom-log.md`
4. If photo uploaded, save as `photos/YYYY-MM-DD.jpg` and note in the log

## Workflow: "is this food safe?"

Run `scripts/check-meal.py "<food or dish>"` — it flags nickel/histamine/MRT hits and gives a recommendation.

## Workflow: weekly review

1. Summarize last 7 days from `symptom-log.md`
2. Correlate flare days with food entries — look for repeated triggers
3. Compare latest photo to one from 1-2 weeks ago side by side
4. Update `labs-todo.md` status
5. Recommend adjustments

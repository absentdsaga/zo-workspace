# Playbook — OOH / Billboards for VURT

When you're given a billboard or out-of-home brief, this is the system. Cross-reference `Skills/vurt-billboard-miami/references/dooh-specs.md` and `references/fomo-mechanics.md` for the technical fundamentals; this playbook is the creative spine.

---

## Phase 0 — Spec lock (before sketching)

Block these before drawing anything. Half the rejected concepts in `Skills/vurt-billboard-miami/storyboards/` failed because the spec wasn't locked first.

- [ ] **Aspect ratio and resolution.** 840×400 is 2.1:1. That is a horizontal canvas. Phone-frame mockups (9:16) waste 60% of it.
- [ ] **Pixel pitch / viewing distance.** 10mm pitch + 65mph dwell = 1.5-second read. Three-faces-in-a-grid mushes at 10mm.
- [ ] **Driver-facing or pedestrian.** Driver-facing = no QR. Pedestrian = QR allowed.
- [ ] **Daylight ambient nits.** LED daylight makes #FFFFFF bloom. Use #EBEBEB.
- [ ] **Slot length and loop.** 8s in 60s loop = 13% share-of-attention. Concept must land in 1.5s, hold for 8s.
- [ ] **Window dates and audience profile.** ABFF industry-only week vs. general Miami change the voice.

If any spec is unknown, ask vendor first. Don't sketch on assumptions.

---

## Phase 1 — Voice pick

Per `voice/in-world-vs-out-world.md`:

- **Out-world (VURT speaks as itself)** — for brand awareness, range proofs, FOMO mechanics that don't depend on a single show. Examples: C1-E "BY INVITATION. ROOFTOP. 5.29." / C2-G "Vertical Cinema. Built for the Culture. Always free to watch."
- **In-world (the show speaks)** — for show-launch boards. Examples: a hypothetical Karma in Heels solo poster with just "I told you not to come back." and no genre tag.
- **Peer voice rarely fits OOH** — peer is for social. If you find yourself reaching for it on a billboard, you're probably designing for the wrong medium.

---

## Phase 2 — Mechanism pick

Pick the mechanism BEFORE picking the visual. Without a mechanism, OOH is decoration.

| Mechanism | Use when | Example |
|---|---|---|
| **Specific scarcity** (FOMO) | Driving RSVPs to an invite-only event | "BY INVITATION. ROOFTOP. 5.29." |
| **Single-hero recognition** | Brand awareness; building familiarity over slot rotations | C2-G one face, one tagline |
| **Show-IP escape** | Launch of a specific Original | A24 Charlie-doll-on-doorstep equivalent |
| **Negative pull** (anti-promise) | When VURT has cultural authority to push back | "Don't come here for content." |
| **Specific receipt** | Show-launch where a verbatim line carries | "I told you not to come back." (Karma in Heels) |
| **Anti-decoration** (typography only) | When the brand has earned the right to whisper | "VURT" in plain Inter Bold on black |

If you don't know which mechanism you're using, you don't have a concept yet.

---

## Phase 3 — Layout fundamentals (840×400)

Proven layouts from C1-E and C2-G:

### "Hero phrase + proof line" (out-world FOMO — C1-E pattern)

```
+-----------------------------------------------------------+
|                                                           |
|  HERO PHRASE.                              VURT [logo]    |
|  HERO PHRASE.                                             |
|                                                           |
|  ────                                                     |
|  Support line in title case · Three details · Middot      |
|  Names line in regular weight prefaced "Hosted by"        |
|  ────                                                     |
|                                                           |
|                                       myvurt.com/abff →   |
+-----------------------------------------------------------+
```

Type spec: hero ~120px Inter Bold, support ~28px Inter Medium, names ~24px Inter Regular #999, CTA ~32px IBM Plex Mono accent color. Black field #0B0B0B.

### "Single hero photo + type column" (out-world brand — C2-G pattern)

```
+------------------------+----------------------------------+
|                        |                                  |
|                        |  VURT                            |
|     [SINGLE FACE       |                                  |
|      eyes camera       |  Vertical Cinema.                |
|      cinematic         |  Built for the Culture.          |
|      lighting          |                                  |
|      head + shoulders] |  ────                            |
|                        |  ALWAYS FREE TO WATCH            |
|                        |                                  |
|                        |  myvurt.com →                    |
+------------------------+----------------------------------+
       55% width                  45% width
```

One face, full-bleed left half. Type column right. Photo cropped tight. Solid #0B0B0B with subtle gradient mask on right edge of photo.

### "Type-only" (when the brand has earned silence)

```
+-----------------------------------------------------------+
|                                                           |
|                                                           |
|                                                           |
|                  Built for the Culture.                   |
|                                                           |
|                       VURT                                |
|                                                           |
|                                                           |
|                                                           |
+-----------------------------------------------------------+
```

Massive single line. VURT wordmark only as signature. Use sparingly; works only when the line is iconic.

---

## Phase 4 — Failure modes (do NOT do these)

These are the patterns the rejected billboard concepts (C1-A through D, C2-A through F) fell into. Each is documented in storyboards/.

1. **Phone-frame on horizontal canvas.** Wastes 60% of the panel. ReelShort/DramaBox don't do this because their player is already vertical. (V2-D Phone Hijack also failed this. The mockup at the top of this critique is the failure mode being demonstrated.)
2. **Cast-grid / triptych.** Mush at 10mm pitch. Tubi/Netflix never run grids on outdoor.
3. **Cofounder names alone as headline.** Vampire effect. Names need scaffolding.
4. **Library-genre tagging.** "Vertical Cinema · Free." VURT does not organize by Netflix-shelf categories.
5. **QR on driver-facing.** Conversion near zero.
6. **App-store badges.** VURT drives to web, not stores.
7. **Pure white #FFFFFF.** Glares on LED.
8. **Em dashes.** Use periods.
9. **More than 7 hero words.** "VURT × ABFF Opening Night Rooftop Party Friday" — too many words. Fragment instead.
10. **Multiple CTAs.** One URL. One mechanism. Pick.

---

## Phase 5 — Pre-ship checks

Before sending to gfx guy:

- [ ] Hero phrase ≤7 words.
- [ ] One CTA only.
- [ ] No forbidden words (run `voice/forbidden.md`).
- [ ] No em dashes.
- [ ] Voice mode picked and held throughout.
- [ ] Mechanism is named (FOMO / single-hero / IP-escape / etc.).
- [ ] Logo doesn't exceed 12% of frame width.
- [ ] CTA doesn't exceed 6% of frame area.
- [ ] Black field #0B0B0B, soft white #EBEBEB (not #FFFFFF).
- [ ] Driver-facing or pedestrian confirmed; QR added only if pedestrian.
- [ ] Cofounder/talent clearance confirmed for any named person.
- [ ] Date format follows VURT pattern ("5.29" or "Fri 5.29 · Miami Beach").
- [ ] Run all four critic subagents (per `SKILL.md` Phase 3).
- [ ] Run the five questions from `critique-rubric.md`.

If anything fails, fix before delivering.

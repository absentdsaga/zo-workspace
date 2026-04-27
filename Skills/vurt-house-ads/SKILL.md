---
name: vurt-house-ads
description: Production system for VURT house ads — creative for Source Group umbrella brands (Rielli, SinFiltros Nutrition, Trick Daddy Pots) placed into VURT's own AVOD ad slots. Use when writing scripts, hooks, storyboards, or planning 15s/30s mixes for house ads.
compatibility: claude-code
metadata:
  author: dioni.zo.computer
  scope: vurt
---

# VURT House Ads

Production system for the house ad campaign: VURT's AVOD platform carries ads for Source Group (holding co.) umbrella brands. First wave: **Rielli**, **SinFiltros Nutrition**, **Trick Daddy Pots**.

## Read first (every session)
1. `briefs/source-group-brief.md` — brand briefs from Source Group (positioning, ad angles, tone, assets).
2. `references/audience-insights.md` — research-backed audience briefs per brand. **Every script written against this.**
3. `references/anti-slop-guide.md` — banned phrases, banned visual tropes, banned structural moves. Run every draft through this.
4. `research/brand-voice-cards.md` — distilled voice, audience, social footprint per brand (v1 — supplements the audience-insights doc).
5. `research/format-recommendation.md` — 15s vs 30s split + per-brand volume + rationale.
6. `references/ai-video-stack-2026.md` — tool stack for production (Veo 3.1, Runway Act-Two, ElevenLabs, Suno, Magnific, Topaz).
7. Latest scripts under `scripts/{rielli,sinfiltros,trickdaddy}/` — currently **v2**.

## Directory map
```
briefs/              Source-of-truth briefs + product specs per brand
research/            Voice cards, audience notes, format rec, competitive pulls
scripts/             Per-brand ad scripts (v1, v2, final) split 15s/30s
storyboards/         Shot lists + AI generation prompts per script
assets/              Stills, logo refs, talent lookbooks (copies of Dropbox)
references/          Screenshots of top-performing swim/supplement/cookware ads
QUESTIONS.md         Open clarifiers for Dioni before v2
```

## Core operating rules
- **VURT slot spec (confirmed):** 30s cap, non-skippable, audio-on, clickable VAST end card. This pushes 30s to the hero format — viewer cannot scroll past.
- **9:16 vertical only.** No landscape cutdowns for this wave.
- **Don't fabricate claims.** Use only claims present in the brief or on the live site. No invented stats, no made-up celebrity quotes. FTC/compliance discipline on SinFiltros — structure/function only.
- **Rielli is priority.** Ted Lucas flagged the swimwear brand as the most important to promote. Rielli gets the best shoot slot, the deepest creative pass, and first attention through the AI upscale stack.
- **Trick Daddy is already on VURT talent roster** — direct access, cross-promo leverage, shoot day is achievable fast.
- **SinFiltros ships EN primary with Spanglish code-switch + full ES hero versions.** Spanglish outperforms both straight English and straight Spanish for US Latinas 22-32 (see audience-insights.md).
- **Per-brand voice never bleeds.** Rielli = quiet confidence. SinFiltros = founder-honest, Spanglish, symptom-first. Trick Daddy = observational, Miami, one-liners.

## Format mix (revised — 1-week scope)
Shipping **8 spots** across three brands. Each 30s produces its matching 15s from the same shoot session — one shoot day per brand.

| Brand | 15s | 30s | Lang | Total |
|---|---|---|---|---|
| Rielli | 4 | 2 | EN | 6 |
| SinFiltros | 4 | 2 | EN (Spanglish) | 6 |
| SinFiltros | — | 2 | ES hero | 2 |
| Trick Daddy Pots | 4 | 2 | EN | 6 |
| **Total** | **12** | **8** | | **20** |

Per HexClad variant-factory model, one shoot day should also generate enough b-roll for 10+ additional cutdowns per brand post-wave-1 if needed. Original v1 "24 spots across 3 brands" was over-scoped — v2 above is the actual producible count for a 1-week turnaround. Rationale in `research/format-recommendation.md`.

## Sub-agents
Invoke with `Task` tool using `subagent_type` matching:
- `hook-generator` — take an angle, return 20 hook variants under 1.5s read-time.
- `script-polisher` — pass a draft + target seconds (15/30), get trimmed copy hitting exact spoken-word count.
- `storyboard-creator` — script → shot list + AI image/video prompts per shot.
- `ad-library-scraper` — pull competitor creatives from Meta Ad Library for a given brand/category.
- `creative-director` — run any draft through `references/anti-slop-guide.md` + `references/audience-insights.md`. Flags banned phrases, generic visuals, and structural mistakes. Always run before shipping a script.
- `performance-reviewer` — after flight, read which brand/format is pulling and flag focus for wave 2. With 8 spots live, this is not a variant-testing engine; it's a "double down on the winner" function.

Agent specs live in `agents/`.

## Workflow
1. Read `references/audience-insights.md` + `references/anti-slop-guide.md`. Non-negotiable.
2. Confirm brief is current.
3. Run `ad-library-scraper` for competitive context (skip if already pulled in last 30 days).
4. Generate hooks via `hook-generator` against the audience insights for each brand.
5. Write scripts. Pass each through `script-polisher` for length.
6. Run `creative-director` against each draft — it enforces the anti-slop guide.
7. Build storyboards via `storyboard-creator`.
8. Review with Dioni → hand to video guy / AI gen.
9. After flight, run `performance-reviewer`.

## Resolved constraints (as of v2)
- **VURT ad slot:** 30s cap, non-skippable, audio-on, clickable VAST end card ✓
- **Landing URLs:** riellibrand.com, sinfiltrosnutrition.com, trickdaddypots.com ✓ (UTM-tag per creative)
- **Promo codes:** none yet — will swap in when Dioni provides
- **Video guy:** Miami-based, live-action + edit, open to AI stack. Does NOT have Zo workspace access — keep all production assets downloadable from Dropbox, not Zo paths.
- **Dropbox access:** Skipped per Dioni (video guy can't access Zo workspace anyway).
- **FTC supplement compliance:** Structure/function claims only. Testimonial spots need "Individual results vary" superbar + `Seeded creator · compensated` disclosure. End card must show full DSHEA line on SinFiltros spots.

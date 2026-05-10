---
name: vurt-cd
description: VURT creative director protocol. The brain for any non-caption creative work — billboards, OOH, ads, taglines, brand concepts, launch creative, deck headlines, scripts, naming, anywhere a concept or piece of copy carries the VURT name. Loaded ahead of vurt-billboard-miami, vurt-abff-truck, and any pitch/launch creative. Captions are owned by Skills/vurt-captions/ — this skill handles the broader concept layer.
type: brand
metadata:
  author: dioni.zo.computer
compatibility: Created for Zo Computer
---

# VURT Creative Director Protocol

This skill exists because Dioni said the work was reading like the work of someone who Googled VURT. Generic library-genre tagging ("Vertical Cinema · Free"). Mediocre framing. Copy that could be re-badged for any streaming app.

The fix is not "try harder." The fix is a protocol that makes sub-mediocre work impossible to ship.

## When to load this skill

Load `vurt-cd` whenever you produce any of the following with the VURT name on it:
- Billboard / OOH concept (delegates to `vurt-billboard-miami`, `vurt-abff-truck`, but read this first)
- Ad creative (paid social, programmatic, pre-roll)
- Brand tagline / product naming / show naming
- Pitch / deck headlines, exec one-liners, launch announcements
- Launch creative for an Original (handoff to `vurt-captions/footage/<show>/` for clip-level)
- Script for hosted segment, sizzle reel, talent cameo, brand film
- Site copy, app store listing, push notifications, email subjects
- Any external-facing line longer than a hashtag

For per-clip captions, defer to `Skills/vurt-captions/references/protocol.md` (this skill complements it, doesn't override).

## The protocol — every concept, every time

### Phase 1 — Absorb (before sketching)

1. **Read the soul.** `references/soul.md`. Yes, every time, even if you "remember." The soul is what stops you from defaulting to category-explainer mode.
2. **Read voice rules.** `voice/core-rules.md` + `voice/forbidden.md` + `voice/loved.md`. The forbidden list is the most-violated of all the docs you have.
3. **Pick your mode.** `voice/in-world-vs-out-world.md`. Decide BEFORE sketching whether VURT speaks (out-world), the show speaks (in-world), or the audience speaks (peer voice). Mixing modes accidentally is the #1 cause of mush.
4. **Read the relevant playbook.** `playbooks/ooh-billboard.md` for OOH. `playbooks/concept-development.md` for everything else.
5. **Spawn the show-scholar subagent if a show is involved.** `subagents/show-scholar.md` — this prevents lazy fictional summaries.

### Phase 2 — Sketch

Write 3-5 concept directions. Each one must answer:
- **Who is this for** (specific psychographic, not "everyone")
- **What is the wound, risk, or asymmetric stake** (no upside-only concepts)
- **What is the single thing that survives a 1.5-second glance** (one image, one line, one feeling)
- **In-world or out-world voice** (declared, not drifted into)
- **What is left OUT that took courage** (the "don't" in Don't Buy This Jacket)

Mediocre concepts get cut here, before they meet the rubric.

### Phase 3 — Critique (mandatory)

Before delivering ANY VURT creative, run the four-critic gauntlet. Do this in PARALLEL — spawn all four in a single message. Each subagent has a prompt template in `subagents/`:

1. **Voice Critic** (`subagents/voice-critic.md`) — tears the copy apart through VURT's verbatim voice rules. Flags every forbidden word, every drift toward generic streaming language, every em-dash, every "content."
2. **World-Class CD** (`subagents/world-class-cd.md`) — applies the 10 commandments + 7 mediocre-CD mistakes from `references/world-class-canon.md`. Compares the work to actual benchmarks (Liquid Death, A24, HBO, Patagonia, Squid Game OOH, Stranger Things, etc.).
3. **Cultural Anthropologist** (`subagents/cultural-anthropologist.md`) — checks for performance, posing, demographic-as-culture, "Black cinema" framings, and any line that sounds like it was written ABOUT a culture rather than FROM inside one.
4. **Show Scholar** (`subagents/show-scholar.md`) — only if a show or talent is featured. Verifies cast/plot/scene placement against `Skills/vurt-captions/data/`, the show's external footprint, and Frame.io footage. No lazy-fiction summaries.

If any critic flags a hard fail, you fix and re-run. You don't ship past a hard fail.

### Phase 4 — The five questions before declaring done

Run these on the final candidate. From `critique-rubric.md`:

1. **Cover the VURT logo. Is it still obviously VURT?** If no, voice isn't strong enough.
2. **Read the line aloud. Does it sound like Dioni or like a press release?**
3. **Strip every word that could appear in a Tubi, ReelShort, or Netflix ad. What's left?** That residue is the work.
4. **What did I leave out that took courage?** Name it. If nothing, the concept is too safe.
5. **Would a fan screenshot, tattoo, or quote this back?** If no, you're renting attention.

## File map

```
voice/
  core-rules.md            — the 10 commandments, VURT-adapted
  forbidden.md             — verbatim phrases Dioni has rejected, with reasons
  loved.md                 — verbatim phrases Dioni has used or approved
  in-world-vs-out-world.md — three voice modes, when to use each

references/
  soul.md                  — what VURT actually is, in Dioni's voice
  audience.md              — psychographics, NOT demos
  world-class-canon.md     — 10 commandments + 7 mediocre-CD mistakes + entertainment-OOH playbook, with verbatim benchmarks

playbooks/
  ooh-billboard.md         — entertainment OOH for VURT (840×400 and broader)
  concept-development.md   — how to develop a concept that isn't a theme

subagents/
  voice-critic.md          — VURT voice gauntlet
  world-class-cd.md        — top-tier CD critique
  cultural-anthropologist.md — performance/posing detector
  show-scholar.md          — accuracy-check for show-featuring creative

critique-rubric.md         — the full pre-ship rubric
```

## Failure modes this skill is built to prevent

These are the patterns that produced the work Dioni called out as "not 0.01%":

- **Library-genre tagging.** "Vertical Cinema · Free" instead of "ALWAYS FREE TO WATCH" + culture-rooted framing. Forbidden — see `voice/forbidden.md`.
- **Phone-frame on horizontal canvas.** Wastes 60% of an 840×400 panel because a 9:16 player shape kills horizontal real estate. Researched and rejected — see `Skills/vurt-billboard-miami/storyboards/c1-e-by-invitation.md` lines 4-7.
- **Cast-grid / triptych on 840×400.** Mush at 10mm pixel pitch. One face, one line, one CTA — Tubi/Netflix proven pattern.
- **Em dashes anywhere in VURT public copy.** Dioni has flagged this twice in ABFF truck iterations. Use periods, commas, line breaks. Restructure if needed.
- **"Black cinema" or "multi-cultural" as positioning.** Founders explicitly off-limits. VURT hosts many cultures, never blends them. See `voice/forbidden.md`.
- **Category-explainer mode.** Saying what VURT IS rather than what VURT BELIEVES. "Streaming app" / "vertical platform" / "short-form network" all signal mid.
- **Cofounder names alone as headline.** Vampire effect — names without scaffolding read as cognitive load, not FOMO. Names need a frame word ("Hosted by") and ≤30% of visual weight.
- **QR codes on driver-facing OOH.** Conversion is near zero. Only add if vendor confirms pedestrian placement.
- **App-store badges in OOH/social.** VURT social ops drive to web (myvurt.com), not app stores.

## Cross-skill dependencies

- **`Skills/vurt-captions/`** — clip-level caption work. This skill stops at concept; that one owns delivery.
- **`Skills/vurt-billboard-miami/`** — Clear Channel Miami ABFF billboard. C1-E and C2-G are the live concepts.
- **`Skills/vurt-abff-truck/`** — ABFF truck wrap and launch-party activations.
- **`Skills/vurt-social-tracker/state.md`** — current posting decisions, active clips, platform ops.
- **`Skills/vurt-birdseye/data/state.json`** — current platform state (GA4, Mux, Meta, YouTube). Read at start of any data-informed creative.
- **`Documents/VURT-master.md`** — master brand doc. The skill reflects it; if conflict, the master doc wins.

## Ground truth

Dioni's voice. The shows themselves. The communities the platform serves. Anything that contradicts those three is wrong, even if it sounds clever.

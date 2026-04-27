# VURT Caption-Making Protocol

**This is the MANDATORY checklist for every caption brief.** Run pre-flight before writing a single line. Run output check before delivering. No exceptions — Dioni has flagged dropped platforms (YT, upper-thirds, FB titles) and unresearched captions repeatedly. This file exists to stop that.

Cross-reference: `references/winning-patterns.md` (data-backed structures), `references/interactive-engagement.md` (story-stack tier picker + per-platform engagement plays), and `Documents/VURT-Social-Video-Editor-Guide.md` (cut-side rules).

---

## PRE-FLIGHT (before writing anything)

If any answer below is "no" or "I don't know," stop and resolve it first. Do not write captions on missing context — that's the exact "you took my transcript and made captions" failure mode.

### 1. Show research — required every time
- [ ] Read the title's full entry in `Skills/vurt-captions/data/shows.yaml` and `data/titles.yaml`
- [ ] Pull the myvurt.com detail URL (e.g. `myvurt.com/detail/micro_series/<slug>`) and confirm the show exists
- [ ] Search IMDb/Letterboxd/Wikipedia for synopsis, year, original network, director, lead cast — **at least one external source beyond Dioni's description**
- [ ] If any prior clips for this title exist in `Skills/vurt-social-tracker/state.md` or `Skills/vurt-captions/footage/<show>/`, read them — know who's who and where this scene sits in the arc
- [ ] If the show is on Frame.io and footage hasn't been transcribed, pull + transcribe per `SKILL.md § Frame.io Footage Review Workflow` before writing

If research returns nothing usable (truly obscure title, no online footprint), say so explicitly to Dioni and ask before writing. Do not hallucinate plot.

### 2. Scene placement
- [ ] Which clip in the 5-arc is this — Hook / Escalation / Twist / Confrontation / Edge of Resolution?
- [ ] Who are the speakers (character names, not "Speaker 1")?
- [ ] What's the actual stake of THIS scene — not the dialogue, the underlying conflict?
- [ ] What does the audience know that a character doesn't, or vice versa? (Dramatic irony is usually the hook.)

### 3. Pattern declaration (70/20/10 split)
Per `references/winning-patterns.md § Clone vs Experiment`, every brief picks a slot:

- [ ] **CLONE (70%)** — Which of the 4 proven TikTok winners am I cloning?
  - Inner monologue / confession (CBD Tatyana)
  - Courtroom / professional reveal (SLAB judge)
  - Generational / family-legacy stakes (FS dinner)
  - Character-name-as-hook (SLAB Uncle 3D)
- [ ] **ADJACENT (20%)** — One-line written hypothesis. Example: "hypothesis: sibling-betrayal saves as well as father-announces-future because both tap family-legacy stakes."
- [ ] **WILD (10%)** — Outside known patterns. Note it. Expect to lose.

State the slot in the brief output so Dioni can audit later.

### 4. Brand guardrails — every brief
- [ ] No mention of competitors (Tubi, ReelShort, DramaBox, Netflix, BET+, etc. — even if it's where the show originally aired). It's a VURT Original on our platform.
- [ ] No "Black cinema" tag — VURT is culture-first, multi-genre, vertical-native. Boxes us in, kills algo spread.
- [ ] No em dashes anywhere in any caption (use periods, commas, line breaks).
- [ ] No cursing unless the dialogue itself is the hook.
- [ ] No giving away the twist.

---

## OUTPUT CHECKLIST — every brief delivers all 7 items unless explicitly told otherwise

Default deliverable count = **7**. If Dioni names specific platforms, follow that — but if he says "captions" without naming platforms, give all 7. Silently skipping is the failure mode.

### Required deliverables
1. [ ] **TikTok caption** + pinned comment (see pinned-comment rule below)
2. [ ] **TikTok upper-third overlay** — 2-6 words, burned into top third of video, visible in profile-grid square crop. NEVER skip this. The 4 winners all had one.
3. [ ] **TikTok Stories** — 2-stack, visual-only (no captions): Story 1 reshare post, Story 2 = tag card OR "Send to a friend" prompt sticker (alternate weekly to avoid pattern fatigue)
4. [ ] **Instagram Reels caption** — character-rooted opening line (not brand language). Tag exec producer + director + top 2 actors in caption body. Collaborator invite list.
5. [ ] **Instagram Stories** — 3-funnel: Story 1 caption tease (reshare), Story 2 = "Send to a friend" sticker with character-voice prompt (default) OR tag card (alternate), Story 3 link sticker (`myvurt.com`)
6. [ ] **Facebook Reel** — title (`<Show Name> | A VURT Original`) + caption with **clickable myvurt.com link in line 1**
7. [ ] **YouTube Shorts** — title (`<Show Name> | A VURT Original` or named-talent variant) + searchable description with show + cast + director + genre keywords + `myvurt.com`

### Conditional deliverable
8. [ ] **LinkedIn caption** — only if it's a director spotlight, founder content, industry milestone, or press moment. Don't include for clip drops.

### Per-deliverable structural rules (read before writing each one)
- **TikTok caption:** 1-2 sentences. Lead with character voice or specific receipt. **End with an open-loop hook** (question form — "What would you do?", "Would you forgive this?", "Who else saw this coming?") OR an unresolved stakes line ("Nobody saw it coming"). Then show name + "Streaming free on VURT." 5-7 hashtags max. Pinned comment is mandatory, not optional.
- **Pinned comment rule (TikTok + IG):** Default = character-voice share-bait question that invites reply ("Would you forgive him?" / "Who's wrong here?" / "Tell me she's not about to…"). Seeds replies, which the algo reads as share-worthy signal. The stream-free line (`Stream free at myvurt.com`) goes in the caption body or the second pinned comment, not the first. Alternate strategy weekly so the account doesn't feel bot-patterned.
- **TikTok upper-third:** Pull the most savable phrase from the dialogue or scene stake. Lead with the option that creates intrigue without spoiling.
- **TikTok / IG Reels — trending audio option:** For every clip brief, also note one trending-audio variant the editor can cut alongside the dialogue version. Trending audio under a scene clip is a cheap algorithm-breaker — the platform reads it as participation in the audio trend and surfaces it to a wider audio-graph audience. Pick audio whose mood matches the scene (tense → tense; flirty → flirty; reveal → drop-style sting). Keep the original dialogue available as a lower-bed if the scene only lands with the line. When recommending a trend, name the sound's vibe and what scene moment to sync the beat-drop to. If you cannot point to a specific current trend, say so — do not invent one.
- **IG Reels:** 2-4 sentences. Line breaks for scan. Tags in body, not just hashtags. Hashtags at end. **Every IG reel caption must include an open-loop hook (question or unresolved stakes) AND a share CTA** ("Send this to the friend who…", "Tag someone who's been here"). Captions that summarize dropped median comments 71% this week. The data: clip reels with in-world character lines beat brand posts 20-140× on reach.
- **IG Stories Story 1:** Caption tease, NOT just the post. Story 2: tag card only. Story 3: link sticker only.
- **FB:** Link in line 1, then 2-3 sentences setup, then hashtags. FB is mostly a paid channel now — link still works, but stop framing FB volume as "feed the algo."
- **YT Shorts title:** Format = `<Show Name> | A VURT Original`. Named talent variant for spotlight clips: `<Star Name> in <Show Name> | A VURT Original`. Title is the brand, not the scene. Compounds for organic search.
- **YT description:** Minimum 4 lines. Show name + premise + cast + director + `Stream free at myvurt.com` + hashtags. Searchable strings matter — google/organic + google-play/organic are our highest-engagement traffic (88.8% engagement on play store organic per 14d GA4).

### Open-loop hook library (paste-ready openers/closers)

Question form:
- "What would you do in her seat?"
- "Is she wrong for this?"
- "Would you forgive this?"
- "Who else saw this coming?"
- "Who's the real villain here?"
- "Have you ever had to say this to your own family?"

Unresolved-stakes form (declarative, but implies a question):
- "Nobody saw it coming."
- "He still doesn't know."
- "She has no idea what just happened."
- "The part she doesn't know yet…"
- "Watch what happens when she finds out."

Share-CTA form (mandatory on at least one surface per clip):
- "Send this to [the friend who swore she'd never / your sister / your group chat]."
- "Tag someone who'd lose it at this."
- "Share if you've seen this play out in real life."

Sharer-voice one-liner (write the DM for them — include on Reel caption or Story 2 sticker):
The line a sharer can paste-and-send without editing. One clean sentence in the character's or viewer's emotional voice. Examples:
- "This scene alone…"
- "When she finds out you're done."
- "You're going to want to see this play out."
- "She didn't say a word. That was the scariest part."

Rule: Shares double when the caption already writes the sharer's reply. Three sentences of setup is worth less than one quotable line.

Story 2 "Send to a friend" sticker prompts (pair one with a silent frame from the clip):
- "Send this to [her / your group chat / the friend who…]"
- "Who needs to see this?"
- "DM this to someone who'd scream at this scene."

IG's `send_to_friend` sticker converts shares at roughly 2× the rate of passive reshares. Use Story 2 as the default share slot on the ladder.

---

## TIMING — when to post (post 60-90 min before peak)

Per `references/winning-patterns.md § Peak posting windows`:
- 11AM ET (commute / lunch)
- 1AM ET (highest save rate window — late-night insomnia scroll)
- 9PM ET (prime evening)

If Dioni asks "when should I post," default to the next upcoming peak unless there's a release-day reason to ride a different hour.

---

## SUCCESS METRICS — what "good" looks like after posting

Track in `Skills/vurt-social-tracker/state.md` 72 hours after each post:

| Platform | Primary KPI | Threshold |
|----------|-------------|-----------|
| TikTok | Save rate | ≥1.0% = clone the structure. <0.5% = study the anti-pattern, don't repeat. |
| TikTok | Like rate | ≥6% is table stakes. Below = hook failed. |
| TikTok | Watch ratio | 0.9+ on <30s, 0.7+ on 30-60s |
| IG Reels | Reach | Compare against last 4 weeks median, not absolute |
| IG Reels | Saves + Shares | Saves = "this is me." Shares = "send it to someone." Both signal repost-worthy. |
| YT Shorts | Views (24h) + retention | Outliers (40K+) are Shorts-feed surges, not baseline. Median ~600-1500 is normal. |
| FB | Mostly paid signal — skip organic comparisons | — |

---

## ANTI-PATTERNS — Dioni-flagged failures, do not repeat

Logged from prior sessions. Each one cost a redo.

1. **"You just took my transcript and made captions."** Caused by: writing without reading shows.yaml, IMDb, or footage transcripts. Fix: pre-flight § 1 is non-negotiable.
2. **Skipping YT or upper-third overlay.** Caused by: defaulting to "the platforms Dioni mentioned" instead of all 7. Fix: output checklist runs every time.
3. **"Black cinema" hashtag.** Caused by: pattern-matching the cast demographic instead of the brand. Fix: brand guardrails § 4.
4. **Tubi / competitor mentions.** Caused by: pulling from IMDb or original-airing data without filtering. Fix: brand guardrails § 4.
5. **Em dashes.** Caused by: default writing style. Fix: brand guardrails § 4.
6. **Spoiling the ending in the caption.** ("Favorite Son" Clip 5 hook gave away the family arc.) Fix: scene placement § 2 — know what to withhold.
7. **Inventing causation chains** (e.g., "this clip drove the spotlight repost"). Fix: only state what's verified in data, not what feels narratively true.
8. **Repackaging the dialogue verbatim.** Fix: cite the line as receipt, but the caption hook is a NEW framing of the stake.

---

## When this protocol updates

After every weekly data refresh (vurt-daily-report), `references/winning-patterns.md` may add/retire winners. When that happens:
- Update the 4-winner list in pre-flight § 3
- Update the success-metrics thresholds if save-rate distribution shifts
- Re-version this protocol file with date

Last updated: 2026-04-23.

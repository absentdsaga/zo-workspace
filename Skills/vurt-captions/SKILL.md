---
name: vurt-captions
description: Expert social media caption writing for VURT micro-drama clips. Generates platform-native captions (TikTok, IG, FB, YouTube, LinkedIn) using the VURT brand voice and the 5-clip arc framework. Includes both manual guidance and automated draft generation via Notion API.
metadata:
  author: dioni.zo.computer
---

# VURT Captions Skill

## ⚠ Mandatory Protocol

**Every caption brief MUST follow `references/protocol.md`.** That file is the pre-flight + output checklist — no exceptions. It exists because Dioni has flagged dropped platforms (YT, upper-third overlays, FB titles) and unresearched captions repeatedly, and the protocol is what stops those failures.

Sequence for every brief:
1. Run pre-flight (research the show, place the scene, declare the 70/20/10 slot, check brand guardrails)
2. Write all 7 deliverables (TT caption + upper-third + TT Stories, IG Reels, IG Stories 3-funnel, FB w/ link + title, YT Shorts title + description) — only skip a platform if Dioni names a subset
3. Output check before delivering

Patterns we clone are in `references/winning-patterns.md` (refreshed weekly from daily-report data).

## Capabilities

### 1. Manual Caption Writing (Conversation-based)
When a user provides dialogue transcript or scene description, generate captions following the framework below.

### 2. Automated Draft Generation (Script)
`scripts/generate-captions.py` reads the Content Calendar Notion DB, identifies entries with empty Caption fields, and generates template-based draft captions using show profiles and hashtag config.

```bash
# Generate for all empty entries
python3 scripts/generate-captions.py --all

# Only for a specific show
python3 scripts/generate-captions.py --show karma

# Preview without writing to Notion
python3 scripts/generate-captions.py --dry-run

# Combine flags
python3 scripts/generate-captions.py --show parking-lot --dry-run
```

Requires: `VURT_NOTION_API_KEY` env var. Content Calendar DB: `a7587d5d-8f14-490d-a494-664bd80d6256`.

Generated captions are prefixed with `[DRAFT]` so the team knows to review before posting. Hashtags are also auto-filled if the Hashtags field is empty.

---

## Manual Caption Framework

### Step 1 -- Identify the Clip
From the dialogue/scene description, determine:
- Which clip in the 5-clip arc is this? (Hook / Escalation / Twist / Confrontation / Edge of Resolution)
- Who are the characters speaking?
- What's the emotional hook?

### Step 2 -- Pull Title Data
Check `data/shows.yaml` for:
- Title, premiere date, current status
- Cast and crew with social handles
- Caption hooks and tone
- Synopsis and themes

Check `data/titles.yaml` for:
- Exec producer + handles
- Director + handles
- Top 2 actors + handles
- Title-specific hashtag
- myvurt.com URL slug

### Step 3 -- Choose Platform Strategy
Each platform needs a different angle:

**TikTok** -- Shortest, boldest. 1-2 sentences max. Key dialogue line + one context sentence. Trending/provocative hook. Fewer hashtags (5-7). No @mentions in caption. Ends with "myvurt.com" in caption AND pinned comment. **Always include an on-video text overlay** (short hook phrase baked into the video itself) -- testing whether overlays increase engagement vs. caption-only.

**IG Reels** -- Slightly more polished. 2-4 sentences. Full hook setup with storytelling angle. Line breaks for readability. Tags everyone in caption body. Collaborate invites to top handles. Hashtags at end.

**YouTube Shorts** -- Description format. Hook line, 1 sentence about the show, "Stream free at myvurt.com", hashtags. Title IS the caption. Clean `| A VURT Original` format.

**Facebook** -- Conversational, medium length. More narrative setup. CTA to watch at myvurt.com. Clickable link in caption body.

**LinkedIn** -- Professional/industry angle. Frame as entertainment industry content. Mention cast credentials. Reference vertical cinema as a format.

### Step 4 -- Apply Caption Voice Rules
1. Never give away the twist
2. End every caption with a destination (VURT, myvurt.com, link in bio)
3. Hashtags functional not performative
4. No cursing unless scene dialogue IS the hook and authentic
5. Tag minimum: exec producer + director + top 2 actors (IG only)

### Step 5 -- Write Platform Versions
Output exactly:
- TikTok caption + pinned comment text
- IG caption (with collaborator invite callout)
- FB caption (with clickable link)
- YT Shorts title + description
- LinkedIn caption (if applicable)

## Clip Arc Context
The 5-clip arc determines caption tone:
- **Clip 1 (Hook)** -- Introduction, pull them in, set the premise
- **Clip 2 (Escalation)** -- Stakes rising, tension building
- **Clip 3 (Twist)** -- The unexpected turn, surprise element
- **Clip 4 (Confrontation)** -- Peak conflict, face-to-face moment
- **Clip 5 (Edge of Resolution)** -- Almost resolved, drives to full episode

## Caption Voice
VURT is: confident, clean, culturally fluent, cinematic
VURT is NOT: loud, hype, announcer-y, forced

**Good:** "She got caught and still made it his fault."
**Bad:** "You guys HAVE to see this insane twist!!!"

## Data Files
- `data/shows.yaml` -- Show profiles with synopsis, tone, characters, caption hooks
- `data/titles.yaml` -- Title roster with cast/crew/handles per title
- `data/handles.yaml` -- Master platform handle list
- `data/hashtags.yaml` -- Approved hashtag library (always + rotating + platform-specific)

## How the Script Works

1. Loads show profiles from `data/shows.yaml` (synopsis, tone, hooks, cast)
2. Loads hashtag config from `data/hashtags.yaml` (always + rotating + platform tags)
3. Queries Content Calendar Notion DB for all entries
4. Filters to entries with empty Caption fields
5. Matches each entry to a show profile by title keywords
6. For each entry, generates a caption using:
   - A hook from the show's `caption_hooks` list (rotated deterministically)
   - Clip arc context (Clip 1 = introduction, Clip 5 = edge of resolution)
   - Platform-specific formatting template
   - Hashtags: always tags + 2-3 rotating + platform-specific
7. Writes `[DRAFT] <caption>` to the Caption field
8. Fills Hashtags field if also empty

Caption variety comes from rotating through hooks and template structures using deterministic seeding (same entry always gets the same caption, but different entries get different combinations).

## Frame.io Footage Review Workflow

Before writing captions for a show, ground the work in the actual footage — not Dioni's descriptions and not transcript-only repackaging.

### 0. Rule: Frame.io social folders ≠ TikTok posted clips
Not every file in `Social Media Clips/` was actually posted. Some are unused takes, alt cuts, or pending. Match by dialogue → TikTok caption before assuming anything is live.

### 1. Pull + transcribe
```bash
# VURT_FRAMEIO_* secrets only work in Zo bash
python3 Skills/vurt-captions/scripts/download_cbd_social.py   # template — clone per show
python3 Skills/vurt-captions/scripts/transcribe_cbd_social.py # AssemblyAI upload + transcribe
```
- Downloader uses `frameio_client.get_access_token()` + `/accounts/{ACCT_ID}/files/{id}?include=media_links.original` for signed S3 URLs.
- Transcriber uploads local files to AssemblyAI (key `ASSEMBLYAI_API_KEY`), writes `.json` + `.txt` per clip to `footage/<show>/transcripts/`.

### 2. Match to TikTok posts
Load `Skills/vurt-post-log/data/tiktok_user_url_scrape.json`. For each transcript, search n-grams of the dialogue against every post caption. Bucket each clip as:
- **POSTED** (transcript fragment appears in a caption) → record views/likes/saves/shares
- **UNUSED** (no caption match) → candidate for next post
- **SILENT** (empty transcript) → extract stills via ffmpeg, ID visually
- **UNCLEAR** → ask Dioni

Write results to `footage/<show>/CLIP_MAP.md`.

### 3. Analyze what's working
With POSTED clips scored by view/save/like rate, identify structural patterns. Write `footage/<show>/BREAKOUT_ANALYSIS.md` covering:
- The formula shared by top organic clips (opening punch, wound, receipts, accusation, open ending)
- Save rate vs like rate split (save = "this is me"; like = "go off sis")
- Which unused clips fit the formula, which don't

### 4. Recommend next posts
Rank UNUSED clips against the formula. For each recommended post write actual cut notes + per-platform captions. Output `footage/<show>/NEXT_POSTS.md`.

### 5. Caption writing pulls from real scenes
Now when writing captions (per the framework above), cite the exact dialogue, scene beat, and character — never repackage the transcript back as caption.

## Related
- See `Documents/VURT-Social-Playbook.md` for full posting rules
- See `Skills/vurt-post-log/scripts/sync.py` for the post log sync that reads actual captions back from platforms
- State snapshot: `.context/state-snapshot.md`
- Example application: `footage/come-back-dad/` (CLIP_MAP.md, BREAKOUT_ANALYSIS.md, NEXT_POSTS.md) — CBD pass done 2026-04-22

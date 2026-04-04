---
name: vurt-captions
description: Expert social media caption writing for VURT micro-drama clips. Generates platform-native captions (TikTok, IG, FB, YouTube, LinkedIn) using the VURT brand voice and the 5-clip arc framework. Includes both manual guidance and automated draft generation via Notion API.
metadata:
  author: dioni.zo.computer
---

# VURT Captions Skill

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

**TikTok** -- Shortest, boldest. 1-2 sentences max. Key dialogue line + one context sentence. Trending/provocative hook. Fewer hashtags (5-7). No @mentions in caption. Ends with "myvurt.com" in caption AND pinned comment.

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

## Related
- See `Documents/VURT-Social-Playbook.md` for full posting rules
- See `Skills/vurt-post-log/scripts/sync.py` for the post log sync that reads actual captions back from platforms
- State snapshot: `.context/state-snapshot.md`

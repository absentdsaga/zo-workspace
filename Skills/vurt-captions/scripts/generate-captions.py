#!/usr/bin/env python3
"""
Generate draft captions for VURT Content Calendar entries in Notion.

Reads show profiles and hashtag config from YAML, queries the Content Calendar
for entries with empty Caption fields, generates platform-appropriate template-based
captions, and writes them back prefixed with [DRAFT].

Usage:
    python3 generate-captions.py --all              # Generate for all empty entries
    python3 generate-captions.py --show karma        # Only for a specific show
    python3 generate-captions.py --dry-run           # Preview without writing
    python3 generate-captions.py --all --dry-run     # Preview all
"""

import argparse
import hashlib
import json
import os
import random
import sys
import urllib.request
import urllib.parse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML not installed. Installing...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SHOWS_YAML = DATA_DIR / "shows.yaml"
HASHTAGS_YAML = DATA_DIR / "hashtags.yaml"

# --- Notion ---
CAL_DB_ID = "a7587d5d-8f14-490d-a494-664bd80d6256"
NOTION_BASE = "https://api.notion.com/v1"

# --- Clip Arc Labels ---
CLIP_ARC = {
    1: "hook",
    2: "escalation",
    3: "twist",
    4: "confrontation",
    5: "edge_of_resolution",
}

CLIP_ARC_LABELS = {
    1: "Hook / Introduction",
    2: "Escalation",
    3: "Twist",
    4: "Confrontation",
    5: "Edge of Resolution",
}


def get_env(key):
    val = os.environ.get(key)
    if not val:
        print(f"Error: {key} not set.", file=sys.stderr)
        sys.exit(1)
    return val


# --- Notion API helpers (matches sync.py pattern) ---
def notion_request(method, path, body=None):
    token = get_env("VURT_NOTION_API_KEY")
    url = f"{NOTION_BASE}/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def get_calendar_entries():
    """Fetch all entries from the Content Calendar DB with pagination."""
    results = []
    payload = {"page_size": 100}
    while True:
        data = notion_request("POST", f"databases/{CAL_DB_ID}/query", payload)
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


def update_page(page_id, properties):
    return notion_request("PATCH", f"pages/{page_id}", {"properties": properties})


# --- YAML loaders ---
def load_shows():
    with open(SHOWS_YAML, "r") as f:
        data = yaml.safe_load(f)
    return data.get("shows", {})


def load_hashtags():
    with open(HASHTAGS_YAML, "r") as f:
        data = yaml.safe_load(f)
    return data


# --- Show matching ---
def match_show(title, shows):
    """Match a calendar entry title to a show profile key."""
    tl = title.lower()
    # Direct keyword matching
    mappings = [
        ("karma", "karma-in-heels"),
        ("parking lot", "parking-lot-series"),
        ("parking", "parking-lot-series"),
        ("mardi gras", "mardi-gras"),
        ("marry me", "marry-me-for-christmas"),
        ("my first love", "my-first-love"),
        ("come back dad", "come-back-dad"),
        ("comeback", "come-back-dad"),
        ("35 and ticking", "35-and-ticking"),
        ("35 & ticking", "35-and-ticking"),
        ("something like", "something-like-a-business"),
        ("killer stepdad", "killer-stepdad"),
        ("director spotlight", "director-spotlight"),
        ("filmmaker", "director-spotlight"),
        ("vurt brand", "vurt-brand"),
        ("this is vurt", "vurt-brand"),
        ("vurt 100", "vurt-brand"),
    ]
    for keyword, key in mappings:
        if keyword in tl:
            if key in shows:
                return key
    return None


def extract_clip_number(title):
    """Extract clip number from title like 'Karma in Heels Clip 3'."""
    import re
    m = re.search(r"[Cc]lip\s*#?\s*(\d+)", title)
    if m:
        return int(m.group(1))
    # Also check for Ep/Episode pattern
    m = re.search(r"[Ee]p(?:isode)?\s*#?\s*(\d+)", title)
    if m:
        num = int(m.group(1))
        # Map episode ranges to clip numbers (5 clips per cycle)
        return ((num - 1) % 5) + 1
    return None


def extract_platform(entry_props):
    """Get platform from a calendar entry. Could be multi_select or select."""
    # Content Calendar uses multi_select for Platform
    platforms = []
    multi = entry_props.get("Platform", {}).get("multi_select", [])
    if multi:
        platforms = [s["name"] for s in multi]
    else:
        sel = entry_props.get("Platform", {}).get("select")
        if sel:
            platforms = [sel["name"]]
    return platforms


# --- Deterministic randomness for variety ---
def pick_from_list(items, seed_str, count=1):
    """Pick items from a list using a deterministic seed for reproducibility."""
    if not items:
        return []
    h = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    rng = random.Random(h)
    count = min(count, len(items))
    return rng.sample(items, count)


# --- Caption generation ---
def build_hashtag_string(show_key, platform, hashtag_config, seed_str):
    """Build a hashtag string from config: always + rotating subset + platform tags."""
    show_tags = hashtag_config.get("shows", {}).get(show_key, hashtag_config.get("shows", {}).get("default", {}))
    global_tags = hashtag_config.get("global", {})

    always = list(show_tags.get("always", []))
    rotating = show_tags.get("rotating", [])
    testing = show_tags.get("testing", [])

    # Pick 2-3 rotating tags
    picked_rotating = pick_from_list(rotating, seed_str + "_rotating", min(3, len(rotating)))
    # Pick 0-1 testing tags
    picked_testing = pick_from_list(testing, seed_str + "_testing", min(1, len(testing)))

    # Platform-specific tags
    plat_key = platform.lower().replace(" ", "")
    if plat_key == "ytshorts":
        plat_key = "youtube"
    plat_tags = global_tags.get("platform_specific", {}).get(plat_key, [])

    all_tags = always + picked_rotating + picked_testing + plat_tags

    # Deduplicate preserving order
    seen = set()
    deduped = []
    for t in all_tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            deduped.append(t)

    # TikTok: limit to 5-7 hashtags
    if platform == "TikTok":
        deduped = deduped[:7]

    return " ".join(deduped)


def get_collaborator_mentions(show_data):
    """Build @mention string from show cast/crew data."""
    mentions = []
    # Exec producer
    ep = show_data.get("exec_producer", {})
    if isinstance(ep, dict) and ep.get("ig"):
        mentions.append(ep["ig"])
    # Directors
    for d in show_data.get("directors", []):
        if isinstance(d, dict) and d.get("ig"):
            mentions.append(d["ig"])
    director = show_data.get("director", {})
    if isinstance(director, dict) and director.get("ig"):
        mentions.append(director["ig"])
    # Characters/actors
    for c in show_data.get("characters", []):
        if isinstance(c, dict) and c.get("ig"):
            mentions.append(c["ig"])
    # Cast
    for c in show_data.get("cast", []):
        if isinstance(c, dict) and c.get("ig"):
            mentions.append(c["ig"])
    return [m for m in mentions if m and m != "unknown"]


def generate_caption(show_key, show_data, platform, clip_num, title, hashtag_config):
    """Generate a platform-appropriate template-based caption."""
    display_name = show_data.get("display_name", title)
    hooks = show_data.get("caption_hooks", [])
    tone = show_data.get("tone", "")
    synopsis = show_data.get("synopsis", "")

    # Seed for deterministic variety per entry
    seed = f"{show_key}_{platform}_{clip_num}_{title}"

    # Pick a hook
    if hooks:
        hook = pick_from_list(hooks, seed + "_hook", 1)[0]
    else:
        hook = f"Watch {display_name} -- only on VURT."

    # Clip context line
    clip_label = CLIP_ARC_LABELS.get(clip_num, "")
    clip_context = ""
    if clip_num and clip_label:
        clip_contexts = {
            1: "This is where it all starts.",
            2: "Things are about to escalate.",
            3: "You didn't see this coming.",
            4: "The confrontation you've been waiting for.",
            5: "Right on the edge. No resolution yet.",
        }
        clip_context = clip_contexts.get(clip_num, "")

    # Build hashtags
    hashtags = build_hashtag_string(show_key, platform, hashtag_config, seed)

    # Get mentions for IG
    mentions = get_collaborator_mentions(show_data)
    mention_str = " ".join(mentions) if mentions else ""

    # --- Platform-specific templates ---

    if platform == "Instagram":
        # Longer caption (2-4 sentences), storytelling hook, line breaks, hashtags at end
        templates = [
            f"{hook}\n\n{clip_context} {display_name} -- a VURT Original. Stream free at myvurt.com\n\n{mention_str}\n\n{hashtags}",
            f"{hook}\n\nThis is {display_name}. {clip_context}\n\nStream free on VURT. Link in bio.\n\n{mention_str}\n\n{hashtags}",
            f"{hook}\n\n{clip_context} New episode of {display_name} streaming now on VURT.\n\n{mention_str}\n\n{hashtags}",
        ]
        caption = pick_from_list(templates, seed + "_template", 1)[0]

    elif platform == "TikTok":
        # Short and punchy (1-2 sentences max), fewer hashtags, no @mentions
        templates = [
            f"{hook} Stream {display_name} free on VURT. {hashtags}",
            f"{hook} {clip_context} {hashtags}",
            f"{hook} {display_name} on VURT. {hashtags}",
        ]
        caption = pick_from_list(templates, seed + "_template", 1)[0]

    elif platform == "YT Shorts":
        # Description format: hook line, 1 sentence about show, CTA, hashtags
        templates = [
            f"{hook}\n\n{display_name} -- a VURT Original. Stream free at myvurt.com\n\n{hashtags}",
            f"{hook}\n\n{clip_context} Watch {display_name} on VURT.\nStream free at myvurt.com\n\n{hashtags}",
        ]
        caption = pick_from_list(templates, seed + "_template", 1)[0]

    elif platform == "Facebook":
        # Medium length, conversational, CTA to myvurt.com
        templates = [
            f"{hook}\n\n{clip_context} {display_name} is streaming free on VURT right now. Watch at myvurt.com",
            f"{hook}\n\nThis is {display_name} -- and it hits different. Stream the full series free at myvurt.com",
            f"{hook}\n\n{display_name} is a VURT Original. {clip_context} Watch free at myvurt.com",
        ]
        caption = pick_from_list(templates, seed + "_template", 1)[0]

    elif platform == "LinkedIn":
        # Professional/industry angle
        genre = show_data.get("genre", "drama")
        cast = show_data.get("cast", show_data.get("characters", []))
        cast_names = [c.get("actor", c.get("name", "")) for c in cast[:3] if isinstance(c, dict)]
        cast_line = f"Featuring {', '.join(cast_names)}." if cast_names else ""

        templates = [
            f"{hook}\n\n{display_name} is a vertical-first {genre.lower()} series streaming free on VURT -- the platform built for mobile cinema. {cast_line}\n\nWatch at myvurt.com\n\n{hashtags}",
            f"Vertical cinema is here. {hook}\n\n{display_name} represents a new model for independent entertainment distribution. {cast_line} Stream free at myvurt.com\n\n{hashtags}",
        ]
        caption = pick_from_list(templates, seed + "_template", 1)[0]

    else:
        # Fallback
        caption = f"{hook}\n\nWatch {display_name} free on VURT. myvurt.com\n\n{hashtags}"

    # Clean up double spaces and extra newlines
    caption = caption.replace("  ", " ").strip()
    while "\n\n\n" in caption:
        caption = caption.replace("\n\n\n", "\n\n")

    return caption, hashtags


# --- Main logic ---
def extract_calendar_entry(page):
    """Extract relevant fields from a Notion calendar page."""
    props = page["properties"]

    title_parts = props.get("Title", {}).get("title", [])
    title = "".join(t["plain_text"] for t in title_parts) if title_parts else ""

    caption_parts = props.get("Caption", {}).get("rich_text", [])
    caption = "".join(t["plain_text"] for t in caption_parts) if caption_parts else ""

    hashtags_parts = props.get("Hashtags", {}).get("rich_text", [])
    hashtags = "".join(t["plain_text"] for t in hashtags_parts) if hashtags_parts else ""

    platforms = extract_platform(props)

    clip_num = props.get("Clip #", {}).get("number")
    if clip_num is None:
        clip_num = extract_clip_number(title)

    status = (props.get("Status", {}).get("select") or {}).get("name", "")
    date = (props.get("Post Date", {}).get("date") or {}).get("start", "")

    return {
        "id": page["id"],
        "title": title,
        "caption": caption,
        "hashtags": hashtags,
        "platforms": platforms,
        "clip_num": clip_num,
        "status": status,
        "date": date,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate draft captions for VURT Content Calendar entries in Notion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                 Generate captions for all empty entries
  %(prog)s --show karma          Only generate for Karma in Heels
  %(prog)s --show parking-lot    Only generate for Parking Lot Series
  %(prog)s --all --dry-run       Preview what would be generated
  %(prog)s --show karma --dry-run Preview Karma captions only

The script reads show profiles from data/shows.yaml and hashtag
config from data/hashtags.yaml. Captions are template-based using
hooks, clip arc context, and platform-specific formatting rules.

Requires VURT_NOTION_API_KEY environment variable.
        """,
    )
    parser.add_argument("--all", action="store_true", help="Generate captions for all entries with empty Caption fields")
    parser.add_argument("--show", type=str, help="Only generate for a specific show (keyword match, e.g. 'karma', 'parking-lot')")
    parser.add_argument("--dry-run", action="store_true", help="Preview generated captions without writing to Notion")
    args = parser.parse_args()

    if not args.all and not args.show:
        parser.print_help()
        sys.exit(1)

    # Load data
    print("Loading show profiles...")
    shows = load_shows()
    print(f"  Loaded {len(shows)} shows")

    print("Loading hashtag config...")
    hashtag_config = load_hashtags()
    print(f"  Loaded hashtags for {len(hashtag_config.get('shows', {}))} shows")

    # Fetch calendar entries
    print("\nFetching Content Calendar from Notion...")
    pages = get_calendar_entries()
    entries = [extract_calendar_entry(p) for p in pages]
    print(f"  Found {len(entries)} total entries")

    # Filter to entries needing captions
    needs_caption = [e for e in entries if not e["caption"]]
    print(f"  {len(needs_caption)} entries have empty Caption fields")

    # Filter by show if specified
    if args.show:
        show_filter = args.show.lower()
        filtered = []
        for e in needs_caption:
            matched_key = match_show(e["title"], shows)
            if matched_key and show_filter in matched_key:
                filtered.append(e)
            elif show_filter in e["title"].lower():
                filtered.append(e)
        needs_caption = filtered
        print(f"  {len(needs_caption)} entries match show filter '{args.show}'")

    if not needs_caption:
        print("\nNo entries need captions. Done.")
        return

    # Generate captions
    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{prefix}Generating captions for {len(needs_caption)} entries...\n")

    generated = 0
    skipped = 0

    for entry in needs_caption:
        show_key = match_show(entry["title"], shows)
        if not show_key:
            print(f"  SKIP: No show profile match for '{entry['title']}'")
            skipped += 1
            continue

        show_data = shows[show_key]
        platforms = entry["platforms"]
        if not platforms:
            platforms = ["Instagram"]  # Default

        clip_num = entry["clip_num"]
        if not clip_num:
            clip_num = 1  # Default to hook

        # Generate a caption for the first/primary platform
        # (Calendar entries typically target one platform combo)
        primary_platform = platforms[0]
        caption, hashtags_str = generate_caption(
            show_key, show_data, primary_platform, clip_num,
            entry["title"], hashtag_config,
        )

        # Prefix with [DRAFT]
        draft_caption = f"[DRAFT] {caption}"

        # Display
        print(f"  {entry['title']}")
        print(f"    Platform: {', '.join(platforms)} | Clip: {clip_num} ({CLIP_ARC_LABELS.get(clip_num, 'N/A')})")
        print(f"    Caption: {draft_caption[:120]}{'...' if len(draft_caption) > 120 else ''}")
        if not entry["hashtags"]:
            print(f"    Hashtags: {hashtags_str[:80]}{'...' if len(hashtags_str) > 80 else ''}")
        print()

        # Write to Notion
        if not args.dry_run:
            patch = {
                "Caption": {
                    "rich_text": [{"text": {"content": draft_caption[:2000]}}]
                },
            }
            # Also fill Hashtags if empty
            if not entry["hashtags"]:
                patch["Hashtags"] = {
                    "rich_text": [{"text": {"content": hashtags_str[:2000]}}]
                }

            try:
                update_page(entry["id"], patch)
                generated += 1
            except Exception as ex:
                print(f"    ERROR writing to Notion: {ex}")
        else:
            generated += 1

    # Summary
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  {generated} captions {'would be ' if args.dry_run else ''}generated")
    if skipped:
        print(f"  {skipped} entries skipped (no matching show profile)")
    print("Done.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Walk EVERY folder under each show (episodes + social + everything) and pull
the Status tag for every video file. Filter to Status=Posted.

Replaces inventory_all_shows.py for this purpose because that script only
walked folders whose names contained 'social/ugc/edits/clips/otr' — it missed
posted clips that Dioni pulled directly from episode folders.
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
from frameio_client import (
    api_get_paginated,
    ACCT_ID,
    get_show_folders,
    _parse_clip,
)

OUT_FULL = "/home/workspace/Skills/vurt-captions/footage/inventory_full.json"
OUT_POSTED = "/home/workspace/Skills/vurt-captions/footage/inventory_posted.json"

# Limit to active VURT shows (the ones we're actually posting / mapping)
ACTIVE_SHOWS = {
    "Come Back Dad",
    "Schemers",
    "Something Like A Business",
    "Favorite Son",
    "Karma in Heels",
    "The Parking Lot Series",
    "The Love Network Jam",
    "35 & Ticking",
    "Bride To Be",
}

VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".webm", ".mkv")


def walk_all(folder_id, breadcrumb, depth=0, max_depth=6):
    """Recurse every folder, returning every video file with Status tag."""
    if depth > max_depth:
        return []
    try:
        kids = api_get_paginated(
            f"/accounts/{ACCT_ID}/folders/{folder_id}/children",
            params={"include": "metadata"},
        )
    except Exception as e:
        print(f"  ! walk err {breadcrumb}: {e}", flush=True)
        return []
    out = []
    for c in kids:
        t = c.get("type")
        nm = c.get("name", "")
        if t == "folder":
            out.extend(walk_all(c["id"], f"{breadcrumb}/{nm}", depth + 1, max_depth))
        elif t in ("file", "version_stack"):
            parsed = _parse_clip(c)
            mt = (parsed.get("media_type") or "").lower()
            nm_low = nm.lower()
            is_video = mt.startswith("video/") or nm_low.endswith(VIDEO_EXTS)
            if is_video:
                parsed["breadcrumb"] = breadcrumb
                out.append(parsed)
    return out


def main():
    shows = get_show_folders()
    targets = {n: m for n, m in shows.items() if n in ACTIVE_SHOWS}
    missing = ACTIVE_SHOWS - set(targets)
    if missing:
        print(f"  ! Active shows not found in Frame.io: {sorted(missing)}", flush=True)

    inventory = {}
    for name, meta in sorted(targets.items()):
        print(f"\n=== {name} ===", flush=True)
        clips = walk_all(meta["id"], name, depth=0, max_depth=6)
        statuses = Counter((c.get("review_status") or "").strip() or "—" for c in clips)
        posted = [c for c in clips if (c.get("review_status") or "").lower() == "posted"]
        print(f"  total videos: {len(clips)} | status breakdown: {dict(statuses)}", flush=True)
        print(f"  POSTED: {len(posted)}", flush=True)
        inventory[name] = {
            "show_id": meta["id"],
            "category": meta.get("category", ""),
            "total_videos": len(clips),
            "status_breakdown": dict(statuses),
            "posted_count": len(posted),
            "clips": clips,
        }

    # Full file (every video with its tag)
    with open(OUT_FULL, "w") as f:
        json.dump(inventory, f, indent=2)

    # Posted-only file (compact, ready for CLIP_MAP rebuilds)
    posted_only = {}
    for name, info in inventory.items():
        posted = [c for c in info["clips"] if (c.get("review_status") or "").lower() == "posted"]
        posted_only[name] = {
            "show_id": info["show_id"],
            "posted_count": len(posted),
            "clips": [
                {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "view_url": c.get("view_url"),
                    "breadcrumb": c.get("breadcrumb"),
                    "review_status": c.get("review_status"),
                    "created_at": c.get("created_at"),
                    "updated_at": c.get("updated_at"),
                }
                for c in posted
            ],
        }
    with open(OUT_POSTED, "w") as f:
        json.dump(posted_only, f, indent=2)

    total_videos = sum(v["total_videos"] for v in inventory.values())
    total_posted = sum(v["posted_count"] for v in inventory.values())
    print(f"\nWrote {OUT_FULL} — {total_videos} videos across {len(inventory)} shows", flush=True)
    print(f"Wrote {OUT_POSTED} — {total_posted} POSTED clips", flush=True)


if __name__ == "__main__":
    main()

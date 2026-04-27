#!/usr/bin/env python3
"""Enumerate every social clip for every VURT show under Licensed Titles.
Writes inventory.json with show → list of (id, name, size, review_status, path)."""
import json, os, sys
sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
from frameio_client import (
    api_get_paginated, ACCT_ID, get_show_folders,
    _is_social_folder, _parse_clip,
)

OUT = "/home/workspace/Skills/vurt-captions/footage/inventory.json"


def walk(folder_id, breadcrumb, depth=0, max_depth=4):
    """Collect every video file under a folder recursively."""
    if depth > max_depth:
        return []
    try:
        kids = api_get_paginated(f"/accounts/{ACCT_ID}/folders/{folder_id}/children")
    except Exception as e:
        print(f"  ! walk err {breadcrumb}: {e}")
        return []
    out = []
    for c in kids:
        t = c.get("type")
        nm = c.get("name", "")
        if t == "folder":
            out.extend(walk(c["id"], f"{breadcrumb}/{nm}", depth+1, max_depth))
        elif t in ("file", "version_stack"):
            parsed = _parse_clip(c)
            mt = (parsed.get("media_type") or "").lower()
            nm_low = nm.lower()
            is_video = mt.startswith("video/") or nm_low.endswith((".mp4", ".mov", ".m4v", ".webm", ".mkv"))
            if is_video:
                parsed["breadcrumb"] = breadcrumb
                out.append(parsed)
    return out


def find_social_roots(show_id, show_name):
    """Find every folder under a show whose name contains 'social' (or the show's known OTR/UGC/edits). Also include Social Media Clips + vertical edits."""
    keep_keywords = ["social", "ugc", "vertical edits", "edits", "clips", "otr"]
    try:
        kids = api_get_paginated(f"/accounts/{ACCT_ID}/folders/{show_id}/children")
    except Exception as e:
        print(f"  ! list err {show_name}: {e}")
        return []
    roots = []
    for c in kids:
        if c.get("type") != "folder": continue
        nm_low = c.get("name", "").lower()
        if any(kw in nm_low for kw in keep_keywords):
            roots.append({"id": c["id"], "name": c["name"]})
    return roots


def main():
    shows = get_show_folders()
    print(f"Found {len(shows)} shows")
    inventory = {}
    for name, meta in shows.items():
        print(f"\n=== {name} ===")
        roots = find_social_roots(meta["id"], name)
        print(f"  social-ish folders: {[r['name'] for r in roots]}")
        clips = []
        for root in roots:
            files = walk(root["id"], root["name"], depth=0, max_depth=3)
            print(f"    {root['name']}: {len(files)} files")
            clips.extend(files)
        inventory[name] = {
            "show_id": meta["id"],
            "category": meta.get("category", ""),
            "clips": clips,
        }
    with open(OUT, "w") as f:
        json.dump(inventory, f, indent=2)
    total = sum(len(v["clips"]) for v in inventory.values())
    print(f"\nWrote {OUT} — {total} clips across {len(inventory)} shows")


if __name__ == "__main__":
    main()

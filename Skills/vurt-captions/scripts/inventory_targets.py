#!/usr/bin/env python3
"""Targeted inventory: walk each known show folder, retrying on empty results."""
import json, os, sys, time
sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
from frameio_client import api_get_paginated, ACCT_ID, _parse_clip

OUT = "/home/workspace/Skills/vurt-captions/footage/inventory.json"

SHOWS = {
    "Come Back Dad":               "40b1fb70-8ff3-4ed0-9fae-1d9efe4cd7d1",
    "Favorite Son":                "e30cbb9a-e1be-40a7-89f2-ff3342a7bc15",
    "Karma in Heels":              "4ec09fdf-fb8d-4d64-9b2d-193cfa286f55",
    "The Parking Lot Series":      "0274aab2-6ce9-4353-bfef-cf632012dfc4",
    "The Love Network Jam":        "f8854329-ba71-4260-a89f-52e6564c52a9",
    "35 & Ticking":                "05cbc7d3-3da2-43cf-a082-6d6c488dd88b",
    "Something Like A Business":   "48d3a0c5-6f88-4bfd-bf1f-81c3d62f5452",
    "Schemers":                    "6721ae74-f210-4396-ad95-a152d19612fd",
    "Bride To Be":                 "d0f30e78-2a53-491a-b6f9-6fd78470842b",
}
KEYWORDS = ["social", "ugc", "vertical edit", "edits", "clip", "otr", "trailer"]


def list_children(folder_id, retries=3):
    for i in range(retries):
        try:
            return api_get_paginated(f"/accounts/{ACCT_ID}/folders/{folder_id}/children")
        except Exception as e:
            print(f"  retry {i+1} err: {e}")
            time.sleep(2)
    return []


def walk(folder_id, breadcrumb, depth=0, max_depth=4):
    if depth > max_depth: return []
    kids = list_children(folder_id)
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
            if mt.startswith("video/") or nm_low.endswith((".mp4",".mov",".m4v",".webm",".mkv")):
                parsed["breadcrumb"] = breadcrumb
                out.append(parsed)
    return out


def find_social_roots(show_id, depth=0, max_depth=2):
    """Descend up to max_depth into non-matching subfolders (e.g. 'Season 1', 'Vertical Episodes')."""
    if depth > max_depth: return []
    kids = list_children(show_id)
    roots = []
    for c in kids:
        if c.get("type") != "folder": continue
        nm_low = c.get("name", "").lower()
        if any(kw in nm_low for kw in KEYWORDS):
            roots.append({"id": c["id"], "name": c["name"]})
        elif depth < max_depth:
            # descend into non-matching folder (Season 1, Vertical Episodes, etc)
            roots.extend(find_social_roots(c["id"], depth+1, max_depth))
    return roots


def main():
    inv = {}
    for name, show_id in SHOWS.items():
        print(f"\n=== {name} ===")
        roots = find_social_roots(show_id)
        if not roots:
            # Try one more time
            time.sleep(1)
            roots = find_social_roots(show_id)
        print(f"  roots: {[r['name'] for r in roots]}")
        clips = []
        for r in roots:
            files = walk(r["id"], r["name"])
            if not files:  # retry walk once
                time.sleep(1)
                files = walk(r["id"], r["name"])
            print(f"    {r['name']}: {len(files)}")
            clips.extend(files)
        inv[name] = {"show_id": show_id, "clips": clips}
    with open(OUT, "w") as f:
        json.dump(inv, f, indent=2)
    total = sum(len(v["clips"]) for v in inv.values())
    print(f"\nWrote {OUT} — {total} clips across {len(inv)} shows")
    for k, v in inv.items():
        print(f"  {len(v['clips']):3d}  {k}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Re-query every inventoried clip WITH metadata so we get the Posted/Approved tag.
Overwrites inventory.json with proper status per clip."""
import json, os, sys, subprocess, urllib.parse

sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
from frameio_client import get_access_token, ACCT_ID, API_BASE, _extract_review_status

INV = "/home/workspace/Skills/vurt-captions/footage/inventory.json"


def fetch_with_meta(file_id):
    token = get_access_token()
    url = f"{API_BASE}/accounts/{ACCT_ID}/files/{file_id}?include=metadata"
    r = subprocess.run(
        ["curl","-s","-H",f"Authorization: Bearer {token}","-H","x-api-version: 2", url],
        capture_output=True, text=True, timeout=30)
    try:
        return (json.loads(r.stdout) or {}).get("data") or {}
    except Exception:
        return {}


def main():
    inv = json.load(open(INV))
    tot = 0
    for show, meta in inv.items():
        for c in meta["clips"]:
            fid = c.get("file_id") or c.get("id")
            if not fid: continue
            node = fetch_with_meta(fid)
            rs = _extract_review_status(node)
            c["review_status"] = rs
            tot += 1
            if rs:
                print(f"[{rs:15s}] {show}/{c['name']}")
    with open(INV, "w") as f:
        json.dump(inv, f, indent=2)
    print(f"\nUpdated {tot} clips with Posted tag metadata")


if __name__ == "__main__":
    main()

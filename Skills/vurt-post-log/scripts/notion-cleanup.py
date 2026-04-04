#!/usr/bin/env python3
"""
One-time cleanup script:
1. Merge 'Ready for Social' values into 'Status' on the Content Calendar
2. Populate missing 'Show' fields on the Post Log based on title detection
"""

import json
import os
import sys
import urllib.request

NOTION_BASE = "https://api.notion.com/v1"
CAL_DB_ID = "a7587d5d-8f14-490d-a494-664bd80d6256"
POST_LOG_DB_ID = "c592ce58-b453-436f-b8e0-4510b2dcb412"

SHOW_KEYWORDS = [
    ("karma", "Karma in Heels"),
    ("parking", "Parking Lot Series"),
    ("come back", "Come Back Dad"),
    ("comeback", "Come Back Dad"),
    ("vurt 100", "VURT 100 Series"),
    ("100 series", "VURT 100 Series"),
    ("director", "Director Spotlight"),
    ("spotlight", "Director Spotlight"),
    ("patricia", "Patricia Sandoval"),
    ("sandoval", "Patricia Sandoval"),
    ("this is vurt", "This Is VURT"),
]


def get_token():
    token = os.environ.get("VURT_NOTION_API_KEY")
    if not token:
        print("Error: VURT_NOTION_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    return token


def notion_request(method, path, body=None):
    token = get_token()
    url = f"{NOTION_BASE}/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    })
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"  HTTP {e.code}: {err_body}", file=sys.stderr)
        raise


def query_all(db_id, filter_body=None):
    results = []
    payload = {"page_size": 100}
    if filter_body:
        payload["filter"] = filter_body
    while True:
        data = notion_request("POST", f"databases/{db_id}/query", payload)
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


def update_page(page_id, properties):
    return notion_request("PATCH", f"pages/{page_id}", {"properties": properties})


def detect_show(title):
    tl = title.lower()
    for keyword, show_name in SHOW_KEYWORDS:
        if keyword in tl:
            return show_name
    return None


# ─── Step 1: Merge Ready for Social → Status on Content Calendar ─────────────

def step1_merge_ready_for_social():
    print("=" * 60)
    print("STEP 1: Merge 'Ready for Social' into 'Status' (Content Calendar)")
    print("=" * 60)

    pages = query_all(CAL_DB_ID)
    print(f"  Fetched {len(pages)} calendar entries")

    updated = 0
    skipped = 0

    for page in pages:
        props = page["properties"]
        title_parts = props.get("Title", {}).get("title", [])
        title = title_parts[0]["plain_text"] if title_parts else "(untitled)"

        status_sel = props.get("Status", {}).get("select")
        status = status_sel["name"] if status_sel else ""

        rfs_sel = props.get("Ready for Social", {}).get("select")
        rfs = rfs_sel["name"] if rfs_sel else ""

        # If Ready for Social has a value but Status is empty, copy it over
        if rfs and not status:
            print(f"  MERGE: '{title}' — Ready for Social='{rfs}' → Status='{rfs}'")
            try:
                update_page(page["id"], {
                    "Status": {"select": {"name": rfs}},
                })
                updated += 1
            except Exception as ex:
                print(f"    Failed: {ex}")
        elif rfs and status:
            skipped += 1

    print(f"\n  Results: {updated} merged, {skipped} already had Status (kept existing)")
    return updated


# ─── Step 2: Fix missing Show on Post Log ────────────────────────────────────

def step2_fix_missing_shows():
    print("\n" + "=" * 60)
    print("STEP 2: Populate missing 'Show' field (Post Log)")
    print("=" * 60)

    pages = query_all(POST_LOG_DB_ID)
    print(f"  Fetched {len(pages)} post log entries")

    missing = 0
    fixed = 0
    undetected = []

    for page in pages:
        props = page["properties"]
        title_parts = props.get("Post Title", {}).get("title", [])
        title = title_parts[0]["plain_text"] if title_parts else "(untitled)"

        show_sel = props.get("Show", {}).get("select")
        show = show_sel["name"] if show_sel else ""

        if show:
            continue

        missing += 1
        detected = detect_show(title)

        if detected:
            print(f"  FIX: '{title}' → Show='{detected}'")
            try:
                update_page(page["id"], {
                    "Show": {"select": {"name": detected}},
                })
                fixed += 1
            except Exception as ex:
                print(f"    Failed: {ex}")
        else:
            undetected.append(title)

    print(f"\n  Results: {missing} missing, {fixed} fixed, {len(undetected)} undetected")
    if undetected:
        print("  Undetected titles:")
        for t in undetected:
            print(f"    - {t}")
    return fixed


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("VURT Notion Cleanup Script")
    print(f"Calendar DB: {CAL_DB_ID}")
    print(f"Post Log DB: {POST_LOG_DB_ID}\n")

    s1 = step1_merge_ready_for_social()
    s2 = step2_fix_missing_shows()

    print("\n" + "=" * 60)
    print(f"DONE — Step 1: {s1} merged | Step 2: {s2} shows fixed")
    print("=" * 60)

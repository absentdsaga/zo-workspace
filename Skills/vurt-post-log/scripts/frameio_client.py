#!/usr/bin/env python3
"""Frame.io V4 API client with auto-refreshing OAuth tokens."""

import json
import os
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone

TOKEN_FILE = "/home/workspace/.secrets/frameio-oauth-tokens.json"
IMS_TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"
API_BASE = "https://api.frame.io/v4"

ACCT_ID = "6c77dc3c-f088-486d-a8e3-678fc0fcbd70"
VURT_PROJECT_ID = "6a0a9a57-379a-4d48-a7ba-f63982fa3acc"
VURT_ROOT_FOLDER = "fea68d35-5ac3-4d96-9843-9257d0e06371"
LICENSED_TITLES_FOLDER = "293374f5-7c47-4248-8dd4-6125f4b12204"


def _load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def _save_tokens(data):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _token_expired(tokens):
    obtained = tokens.get("obtained_at", "")
    expires_in = tokens.get("expires_in", 0)
    if not obtained or not expires_in:
        return True
    try:
        obtained_dt = datetime.fromisoformat(obtained)
        now = datetime.now(timezone.utc)
        elapsed = (now - obtained_dt).total_seconds()
        return elapsed > (expires_in - 300)  # refresh 5 min before expiry
    except Exception:
        return True


def _refresh_token(tokens):
    client_id = os.environ.get("VURT_FRAMEIO_CLIENT_ID", "")
    client_secret = os.environ.get("FRAMEIO_CLIENT_SECRET", "")
    refresh = tokens.get("refresh_token", "")
    if not all([client_id, client_secret, refresh]):
        raise RuntimeError("Missing VURT_FRAMEIO_CLIENT_ID, FRAMEIO_CLIENT_SECRET, or refresh_token")

    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh,
    }).encode()

    req = urllib.request.Request(IMS_TOKEN_URL, data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    resp = urllib.request.urlopen(req)
    new_data = json.loads(resp.read())

    if "access_token" not in new_data:
        raise RuntimeError(f"Token refresh failed: {new_data}")

    updated = {
        "access_token": new_data["access_token"],
        "refresh_token": new_data.get("refresh_token", refresh),
        "expires_in": new_data.get("expires_in", 3600),
        "token_type": new_data.get("token_type", "bearer"),
        "obtained_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_tokens(updated)
    print(f"  Frame.io token refreshed (expires in {updated['expires_in']}s)")
    return updated


def get_access_token():
    tokens = _load_tokens()
    if _token_expired(tokens):
        tokens = _refresh_token(tokens)
    return tokens["access_token"]


def api_get(path, params=None):
    token = get_access_token()
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}",
         "-H", "x-api-version: 2", url],
        capture_output=True, text=True, timeout=30,
    )
    return json.loads(result.stdout)


def api_get_paginated(path, params=None, max_items=500):
    items = []
    params = dict(params or {})
    params.setdefault("page_size", 50)
    while len(items) < max_items:
        data = api_get(path, params)
        items.extend(data.get("data", []))
        next_link = data.get("links", {}).get("next")
        if not next_link:
            break
        path = next_link.split("/v4")[-1] if "/v4" in next_link else next_link
        params = {}  # params are in the next link
    return items


def get_show_folders():
    """Get all show folders under Licensed Titles."""
    categories = api_get_paginated(f"/accounts/{ACCT_ID}/folders/{LICENSED_TITLES_FOLDER}/children")
    shows = {}
    for cat in categories:
        if cat["type"] != "folder":
            continue
        cat_children = api_get_paginated(f"/accounts/{ACCT_ID}/folders/{cat['id']}/children")
        for show in cat_children:
            if show["type"] == "folder":
                shows[show["name"]] = {
                    "id": show["id"],
                    "category": cat["name"],
                    "view_url": show.get("view_url", ""),
                }
    return shows


SOCIAL_FOLDER_KEYWORDS = ["social"]


def _is_social_folder(name):
    """Check if a folder name indicates social clip content (not vertical episodes)."""
    lower = name.lower().strip()
    return any(kw in lower for kw in SOCIAL_FOLDER_KEYWORDS)


def _extract_review_status(clip):
    """Extract review status (Posted/Approved/Needs Review) from metadata."""
    metadata = clip.get("metadata", [])
    if not isinstance(metadata, list):
        return ""
    for field in metadata:
        if field.get("field_definition_name") == "Status" and field.get("field_type") == "select":
            values = field.get("value", [])
            if isinstance(values, list) and values:
                return values[0].get("display_name", "")
    return ""


def _parse_clip(clip):
    """Parse a clip/file/version_stack into a standard dict."""
    entry = {
        "id": clip["id"],
        "name": clip["name"],
        "type": clip["type"],
        "view_url": clip.get("view_url", ""),
        "created_at": clip.get("created_at", ""),
        "updated_at": clip.get("updated_at", ""),
        "review_status": _extract_review_status(clip),
    }
    if clip["type"] == "version_stack":
        head = clip.get("head_version", {})
        entry["file_id"] = head.get("id", "")
        entry["file_size"] = head.get("file_size", 0)
        entry["media_type"] = head.get("media_type", "")
        entry["status"] = head.get("status", "")
        entry["file_view_url"] = head.get("view_url", entry["view_url"])
    elif clip["type"] == "file":
        entry["file_id"] = clip["id"]
        entry["file_size"] = clip.get("file_size", 0)
        entry["media_type"] = clip.get("media_type", "")
        entry["status"] = clip.get("status", "")
        entry["file_view_url"] = clip.get("view_url", "")
    return entry


def _find_social_folders(folder_id, depth=0, max_depth=4):
    """Recursively walk folders to find any with 'social' in the name.

    Stops descending into a branch once a Social folder is found at that level
    (the social folder itself is collected; we don't go below it here).
    """
    if depth > max_depth:
        return []
    try:
        children = api_get_paginated(f"/accounts/{ACCT_ID}/folders/{folder_id}/children")
    except Exception:
        return []
    found = []
    for c in children:
        if c["type"] != "folder":
            continue
        if _is_social_folder(c["name"]):
            found.append(c)
        else:
            found.extend(_find_social_folders(c["id"], depth + 1, max_depth))
    return found


def _collect_clips_recursive(folder_id, subfolder_label, depth=0, max_depth=3):
    """Walk a Social folder recursively and collect all clips at any depth."""
    if depth > max_depth:
        return []
    try:
        children = api_get_paginated(
            f"/accounts/{ACCT_ID}/folders/{folder_id}/children",
            params={"include": "metadata"},
        )
    except Exception:
        return []
    result = []
    for c in children:
        if c["type"] in ("file", "version_stack"):
            entry = _parse_clip(c)
            entry["subfolder"] = subfolder_label
            result.append(entry)
        elif c["type"] == "folder":
            result.extend(_collect_clips_recursive(
                c["id"], f"{subfolder_label}/{c['name']}", depth + 1, max_depth,
            ))
    return result


def get_social_clips(show_folder_id):
    """Find any 'Social' subfolders (any depth) and return all clips inside them.

    Recursively walks up to 4 levels deep looking for folders with 'social' in
    the name (e.g. Social, Social Media Clips, Social_Exports). Once a Social
    folder is found, its clips are collected recursively (3 more levels) so
    nested per-episode or per-week subfolders are not missed.

    Does NOT collect from Vertical Episodes/Videos folders, which contain
    chopped show episodes rather than social media clips.
    """
    social_folders = _find_social_folders(show_folder_id)
    if not social_folders:
        return []

    result = []
    for sf in social_folders:
        result.extend(_collect_clips_recursive(sf["id"], sf["name"]))
    return result


def get_all_social_assets():
    """Crawl all shows and return a flat list of social clips with show context."""
    print("  Crawling Frame.io for social assets...")
    shows = get_show_folders()
    print(f"  Found {len(shows)} shows in Frame.io")

    all_clips = []
    for show_name, show_info in shows.items():
        try:
            clips = get_social_clips(show_info["id"])
        except Exception as e:
            print(f"    {show_name}: ERROR {e}")
            continue
        if clips:
            print(f"    {show_name}: {len(clips)} social clips")
        for clip in clips:
            clip["show_name"] = show_name
            clip["show_category"] = show_info["category"]
            all_clips.append(clip)

    print(f"  Total: {len(all_clips)} social clips across all shows")
    return all_clips


def match_clip_to_title(clip_name, show_name):
    """Extract clip number from filename like KARMA_IN_HEELS_SocialEdit_003-v3.mp4"""
    import re
    # Priority 1: Social Edit number (most reliable for calendar clip #)
    m = re.search(r'(?:social\s*edit|social\s*media|social)[\s_-]*(\d+)', clip_name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Priority 2: Clip number
    m = re.search(r'clip[\s_-]*(\d+)', clip_name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Priority 3: SM number (e.g. SM1, SM2)
    m = re.search(r'SM[\s_-]*(\d+)', clip_name)
    if m:
        return int(m.group(1))
    # Priority 4: Episode number (fallback)
    m = re.search(r'[Ee]p[\s_-]*(\d+)', clip_name)
    if m:
        return int(m.group(1))
    # Priority 5: 3-digit number in filename
    m = re.search(r'_(\d{3})', clip_name)
    if m:
        return int(m.group(1))
    return None


READY_STATUSES = {"approved", "scheduled to post"}


def get_approved_clips(show_name=None):
    """Get clips ready for posting (Approved or Scheduled to Post)."""
    assets = get_all_social_assets()
    ready = [a for a in assets if a.get("review_status", "").lower() in READY_STATUSES]
    if show_name:
        ready = [a for a in ready if show_name.lower() in a["show_name"].lower()]
    return ready


def get_clips_by_status(status_filter=None, show_name=None):
    """Get clips filtered by review status. None = all clips."""
    assets = get_all_social_assets()
    if status_filter:
        assets = [a for a in assets if a.get("review_status", "").lower() == status_filter.lower()]
    if show_name:
        assets = [a for a in assets if show_name.lower() in a["show_name"].lower()]
    return assets


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Frame.io V4 client")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--list-shows", action="store_true", help="List all shows")
    parser.add_argument("--list-clips", type=str, help="List social clips for a show folder ID")
    parser.add_argument("--all-assets", action="store_true", help="Crawl all social assets")
    parser.add_argument("--approved", action="store_true", help="Show only Approved clips (ready to post)")
    parser.add_argument("--status", type=str, help="Filter by review status (Approved/Posted/Needs Review)")
    parser.add_argument("--show", type=str, help="Filter by show name")
    args = parser.parse_args()

    if args.test:
        token = get_access_token()
        me = api_get("/me")
        print(f"Connected as: {me['data']['name']} ({me['data']['email']})")
        accts = api_get(f"/accounts")
        for a in accts["data"]:
            print(f"Account: {a['display_name']} | Storage: {a['storage_usage']/(1024**3):.1f}GB / {a['storage_limit']/(1024**3):.0f}GB")

    elif args.list_shows:
        shows = get_show_folders()
        for name, info in sorted(shows.items()):
            print(f"  [{info['category']}] {name} | ID: {info['id']}")

    elif args.list_clips:
        clips = get_social_clips(args.list_clips)
        for c in clips:
            num = match_clip_to_title(c["name"], "")
            tag = f" [{c['review_status']}]" if c.get("review_status") else ""
            print(f"  Clip {num or '?'}: {c['name']}{tag} | {c['view_url']}")

    elif args.approved:
        clips = get_approved_clips(args.show)
        if not clips:
            print("  No clips with 'Approved' status found.")
        for a in clips:
            num = match_clip_to_title(a["name"], a["show_name"])
            print(f"  [{a['show_name']}] Clip {num or '?'}: {a['name']}")
            print(f"    URL: {a['view_url']}")

    elif args.status:
        clips = get_clips_by_status(args.status, args.show)
        print(f"  {len(clips)} clips with status '{args.status}':")
        for a in clips:
            num = match_clip_to_title(a["name"], a["show_name"])
            print(f"  [{a['show_name']}] Clip {num or '?'}: {a['name']}")
            print(f"    URL: {a['view_url']}")

    elif args.all_assets:
        assets = get_all_social_assets()
        from collections import Counter
        status_counts = Counter(a.get("review_status", "") or "No Status" for a in assets)
        print(f"\n  Status breakdown:")
        for s, c in status_counts.most_common():
            print(f"    {s}: {c}")
        print()
        for a in assets:
            num = match_clip_to_title(a["name"], a["show_name"])
            tag = f" [{a['review_status']}]" if a.get("review_status") else ""
            print(f"  [{a['show_name']}] Clip {num or '?'}: {a['name']}{tag}")
            print(f"    URL: {a['view_url']}")

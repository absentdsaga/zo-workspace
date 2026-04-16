#!/usr/bin/env python3
"""TikTok Display API client with auto-refreshing OAuth tokens.

Uses tokens stored at /home/workspace/.secrets/tiktok-tokens.json
(saved by the /api/tiktok-callback zo.space route after the user authorizes).

Scopes used: user.info.basic, user.info.profile, user.info.stats, video.list
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone

TOKEN_FILE = "/home/workspace/.secrets/tiktok-tokens.json"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
API_BASE = "https://open.tiktokapis.com/v2"


def _load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def _save_tokens(data):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _token_expired(tokens):
    saved = tokens.get("saved_at", "")
    expires_in = tokens.get("expires_in", 0)
    if not saved or not expires_in:
        return True
    try:
        saved_dt = datetime.fromisoformat(saved.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        elapsed = (now - saved_dt).total_seconds()
        return elapsed > (expires_in - 300)  # refresh 5 min before expiry
    except Exception:
        return True


def _refresh_token(tokens):
    client_key = os.environ.get("VURT_TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("VURT_TIKTOK_CLIENT_SECRET", "")
    refresh = tokens.get("refresh_token", "")
    if not all([client_key, client_secret, refresh]):
        raise RuntimeError("Missing VURT_TIKTOK_CLIENT_KEY, VURT_TIKTOK_CLIENT_SECRET, or refresh_token")

    data = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh,
    }).encode()

    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp = urllib.request.urlopen(req)
    new_tokens = json.loads(resp.read())
    if not new_tokens.get("access_token"):
        raise RuntimeError(f"TikTok refresh failed: {new_tokens}")
    new_tokens["saved_at"] = datetime.now(timezone.utc).isoformat()
    _save_tokens(new_tokens)
    return new_tokens


def get_access_token():
    tokens = _load_tokens()
    if _token_expired(tokens):
        tokens = _refresh_token(tokens)
    return tokens["access_token"]


def _api_request(path, method="GET", body=None, fields=None):
    token = get_access_token()
    url = f"{API_BASE}{path}"
    if fields:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({"fields": ",".join(fields)})
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def get_user_info():
    fields = ["open_id", "union_id", "avatar_url", "display_name", "username",
              "follower_count", "following_count", "likes_count", "video_count"]
    return _api_request("/user/info/", fields=fields)


def list_videos(max_count=20, cursor=None):
    """List the authenticated user's videos with public metrics."""
    fields = ["id", "create_time", "title", "video_description", "duration",
              "cover_image_url", "share_url", "view_count", "like_count",
              "comment_count", "share_count"]
    body = {"max_count": min(max_count, 20)}
    if cursor:
        body["cursor"] = cursor
    return _api_request("/video/list/", method="POST", body=body, fields=fields)


def get_all_videos(limit=200):
    """Paginate through the full video list up to `limit` videos."""
    videos = []
    cursor = None
    while len(videos) < limit:
        remaining = limit - len(videos)
        resp = list_videos(max_count=min(20, remaining), cursor=cursor)
        data = resp.get("data", {})
        batch = data.get("videos", []) or []
        videos.extend(batch)
        if not data.get("has_more") or not batch:
            break
        cursor = data.get("cursor")
        if cursor is None:
            break
    return videos


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "user"
    if cmd == "user":
        print(json.dumps(get_user_info(), indent=2))
    elif cmd == "videos":
        print(json.dumps(get_all_videos(limit=50), indent=2))
    elif cmd == "refresh":
        tokens = _refresh_token(_load_tokens())
        print(f"Refreshed. expires_in={tokens.get('expires_in')}s")
    else:
        print(f"Unknown command: {cmd}. Use: user | videos | refresh")
        sys.exit(1)

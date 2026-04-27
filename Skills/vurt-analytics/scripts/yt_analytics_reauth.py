#!/usr/bin/env python3
"""
YouTube Analytics OAuth re-auth helper.

Step 1 (generate URL):
    python3 yt_analytics_reauth.py url

Step 2 (exchange code for refresh_token):
    python3 yt_analytics_reauth.py exchange "<full-localhost-url-with-code>"
"""
import json
import os
import sys
import urllib.parse
import urllib.request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
REDIRECT = "http://localhost"
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def load_client():
    c = json.loads(os.environ["VURT_GOOGLE_OAUTH_CLIENT"])["installed"]
    return c["client_id"], c["client_secret"]


def make_url():
    cid, _ = load_client()
    qs = urllib.parse.urlencode({
        "client_id": cid,
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    })
    print(f"{AUTH_URL}?{qs}")


def exchange(url):
    parsed = urllib.parse.urlparse(url)
    code = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]
    if not code:
        sys.exit("No ?code= in URL")
    cid, sec = load_client()
    body = urllib.parse.urlencode({
        "code": code,
        "client_id": cid,
        "client_secret": sec,
        "redirect_uri": REDIRECT,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST")
    resp = json.loads(urllib.request.urlopen(req).read())
    print(json.dumps(resp, indent=2))
    if "refresh_token" in resp:
        print("\n=== SAVE TO ZO SECRETS ===")
        print(f"VURT_YOUTUBE_REFRESH_TOKEN = {resp['refresh_token']}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "url":
        make_url()
    elif sys.argv[1] == "exchange":
        exchange(sys.argv[2])
    else:
        sys.exit(__doc__)

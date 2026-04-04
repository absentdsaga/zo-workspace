#!/usr/bin/env python3
"""Generate YouTube Analytics OAuth URL and exchange code for long-lasting refresh token.

Uses http://localhost redirect (Google deprecated urn:ietf:wg:oauth:2.0:oob).
After authorizing, Google redirects to http://localhost/?code=CODE — copy the CODE from URL bar.
"""

import json
import os
import sys
import urllib.parse
import urllib.request

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

REDIRECT_URI = "http://localhost"


def get_creds():
    raw = os.environ.get("VURT_GOOGLE_OAUTH_CLIENT", "")
    if not raw:
        print("VURT_GOOGLE_OAUTH_CLIENT not set", file=sys.stderr)
        sys.exit(1)
    data = json.loads(raw)
    installed = data.get("installed", data)
    return installed["client_id"], installed["client_secret"]


def generate_url():
    client_id, _ = get_creds()
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    })
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    print("\n1. Open this URL in your browser (logged in as dioni@myvurt.com):\n")
    print(url)
    print("\n2. Authorize access. Google will redirect to http://localhost/?code=XXXX...")
    print("   The page won't load (that's normal). Copy the 'code' value from the URL bar.")
    print("   It's the part after ?code= and before &scope=")
    print("\n3. Run: python3 yt-oauth-setup.py --exchange CODE_HERE\n")


def exchange_code(code):
    client_id, client_secret = get_creds()
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        resp = urllib.request.urlopen(req)
        tokens = json.loads(resp.read())
        refresh = tokens.get("refresh_token")
        access = tokens.get("access_token")
        expires = tokens.get("expires_in")
        if refresh:
            print(f"\nRefresh token (save as VURT_YOUTUBE_REFRESH_TOKEN):\n{refresh}")
            print(f"\nAccess token (expires in {expires}s):\n{access[:50]}...")
            print("\nRefresh tokens are LONG-LASTING — they don't expire unless revoked.")
        else:
            print("No refresh token returned. Full response:")
            print(json.dumps(tokens, indent=2))
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--exchange":
        exchange_code(sys.argv[2])
    else:
        generate_url()

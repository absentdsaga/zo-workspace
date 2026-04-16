#!/usr/bin/env python3
"""
Refresh the VURT Meta (Facebook/Instagram) long-lived access token.

Calls the Meta Graph API token exchange endpoint to get a new long-lived token.
Long-lived tokens last ~60 days, so this should be run every 50 days to stay safe.

Required env vars:
  VURT_META_ACCESS_TOKEN  - Current long-lived token
  VURT_META_APP_SECRET    - Meta app secret

The script prints the new token and expiry info. The caller (scheduled agent)
is responsible for updating the Zo secret with the new token value.
"""
import json
import os
import sys

import requests

BASE_URL = "https://graph.facebook.com/v25.0"
APP_ID = "892877370386060"


def main():
    token = os.environ.get("VURT_META_ACCESS_TOKEN")
    if not token:
        print("ERROR: VURT_META_ACCESS_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    app_secret = os.environ.get("VURT_META_APP_SECRET")
    if not app_secret:
        print("ERROR: VURT_META_APP_SECRET not set", file=sys.stderr)
        sys.exit(1)

    resp = requests.get(f"{BASE_URL}/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": app_secret,
        "fb_exchange_token": token,
    })
    data = resp.json()

    if "error" in data:
        error_msg = data["error"].get("message", "Unknown error")
        print(f"ERROR: Token refresh failed: {error_msg}", file=sys.stderr)
        print(json.dumps(data, indent=2))
        sys.exit(1)

    new_token = data.get("access_token", "")
    expires_in = data.get("expires_in", 0)
    expires_days = expires_in // 86400 if isinstance(expires_in, int) else "unknown"

    # Output as JSON for easy parsing by the agent
    result = {
        "status": "success",
        "new_token": new_token,
        "token_type": data.get("token_type", "bearer"),
        "expires_in_seconds": expires_in,
        "expires_in_days": expires_days,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

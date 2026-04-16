#!/usr/bin/env python3
"""
Auto-refresh the VURT Meta (Facebook/Instagram) long-lived access token.

Calls the Meta Graph API token exchange endpoint to get a new long-lived token
and outputs structured JSON for the scheduled agent to parse and apply.

The scheduled agent that runs this script should:
1. Parse the JSON output
2. If status is "success", update the Zo secret VURT_META_ACCESS_TOKEN
   with the new_token value using update_user_settings
3. If status is "error", alert Dioni via email

Required env vars:
  VURT_META_ACCESS_TOKEN  - Current long-lived token
  VURT_META_APP_SECRET    - Meta app secret

Uses only stdlib (no pip packages).
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

META_API_BASE = "https://graph.facebook.com/v25.0"
META_APP_ID = "892877370386060"


def verify_current_token(token):
    """Verify the current token still works and get its expiry info."""
    try:
        url = f"{META_API_BASE}/me?access_token={token}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return {"valid": True, "user": data.get("name", data.get("id", "unknown"))}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def exchange_token(token, app_secret):
    """Exchange the current token for a new long-lived token."""
    params = urllib.parse.urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": META_APP_ID,
        "client_secret": app_secret,
        "fb_exchange_token": token,
    })
    url = f"{META_API_BASE}/oauth/access_token?{params}"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())


def main():
    token = os.environ.get("VURT_META_ACCESS_TOKEN", "")
    app_secret = os.environ.get("VURT_META_APP_SECRET", "")

    if not token:
        result = {
            "status": "error",
            "error": "VURT_META_ACCESS_TOKEN environment variable not set",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    if not app_secret:
        result = {
            "status": "error",
            "error": "VURT_META_APP_SECRET environment variable not set",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Step 1: Verify current token
    print("Verifying current token...", file=sys.stderr)
    verification = verify_current_token(token)

    if not verification["valid"]:
        result = {
            "status": "error",
            "error": f"Current token is invalid: {verification['error']}",
            "detail": "The token may have already expired. A new token must be obtained manually via the Meta OAuth flow.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    print(f"Current token valid for user: {verification['user']}", file=sys.stderr)

    # Step 2: Exchange for new token
    print("Exchanging for new long-lived token...", file=sys.stderr)
    try:
        data = exchange_token(token, app_secret)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        result = {
            "status": "error",
            "error": f"Token exchange HTTP error: {error_body}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)
    except Exception as e:
        result = {
            "status": "error",
            "error": f"Token exchange failed: {e}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    if "error" in data:
        result = {
            "status": "error",
            "error": data["error"].get("message", "Unknown error"),
            "error_type": data["error"].get("type", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    new_token = data.get("access_token", "")
    expires_in = data.get("expires_in", 0)
    expires_days = expires_in // 86400 if isinstance(expires_in, int) else 0

    if not new_token:
        result = {
            "status": "error",
            "error": "No access_token in response",
            "raw_response": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Step 3: Verify new token works
    print("Verifying new token...", file=sys.stderr)
    new_verification = verify_current_token(new_token)

    result = {
        "status": "success",
        "new_token": new_token,
        "token_type": data.get("token_type", "bearer"),
        "expires_in_seconds": expires_in,
        "expires_in_days": expires_days,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "verified": new_verification["valid"],
        "user": verification["user"],
        "action": "UPDATE_SECRET",
        "secret_name": "VURT_META_ACCESS_TOKEN",
        "instructions": "The scheduled agent should update the Zo secret VURT_META_ACCESS_TOKEN with the new_token value using update_user_settings.",
    }

    print(json.dumps(result, indent=2))
    print(f"\nToken refreshed successfully. Expires in {expires_days} days.", file=sys.stderr)


if __name__ == "__main__":
    main()

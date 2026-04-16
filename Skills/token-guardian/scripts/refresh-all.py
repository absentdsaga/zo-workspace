#!/usr/bin/env python3
"""
Token Guardian: Health check and status report for all VURT API tokens.

Usage:
  python3 refresh-all.py --check     # Report status of all tokens (read-only)
  python3 refresh-all.py --refresh   # Check + refresh Meta token if needed

Outputs JSON with token statuses, expiry info, and any warnings.
Uses only stdlib (urllib.request).
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

META_API_BASE = "https://graph.facebook.com/v25.0"
META_APP_ID = "892877370386060"
FRAMEIO_TOKEN_FILE = "/home/workspace/.secrets/frameio-oauth-tokens.json"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def check_meta_token():
    """Check Meta token health by calling /me endpoint."""
    token = os.environ.get("VURT_META_ACCESS_TOKEN", "")
    if not token:
        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "error",
            "message": "Environment variable not set",
            "expires_in_days": None,
        }

    try:
        url = f"{META_API_BASE}/me?access_token={token}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        # Token works -- now check expiry via debug_token
        result = {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "healthy",
            "message": f"Valid for user: {data.get('name', data.get('id', 'unknown'))}",
            "expires_in_days": None,
        }

        # Try to get expiry info from debug_token
        app_secret = os.environ.get("VURT_META_APP_SECRET", "")
        if app_secret:
            try:
                app_token = f"{META_APP_ID}|{app_secret}"
                debug_url = (
                    f"{META_API_BASE}/debug_token?"
                    f"input_token={token}&access_token={app_token}"
                )
                debug_req = urllib.request.Request(debug_url)
                debug_resp = urllib.request.urlopen(debug_req, timeout=15)
                debug_data = json.loads(debug_resp.read())
                token_data = debug_data.get("data", {})
                expires_at = token_data.get("expires_at", 0)
                if expires_at and expires_at > 0:
                    now = datetime.now(timezone.utc).timestamp()
                    days_left = (expires_at - now) / 86400
                    result["expires_in_days"] = round(days_left, 1)
                    result["expires_at"] = datetime.fromtimestamp(
                        expires_at, tz=timezone.utc
                    ).isoformat()
                    if days_left < 7:
                        result["status"] = "warning"
                        result["message"] += f" | URGENT: expires in {days_left:.1f} days"
                    elif days_left < 14:
                        result["status"] = "warning"
                        result["message"] += f" | Expires in {days_left:.1f} days -- refresh soon"
            except Exception as e:
                result["message"] += f" | Could not check expiry: {e}"

        return result

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "expired",
            "message": f"Token invalid or expired: {error_body}",
            "expires_in_days": 0,
        }
    except Exception as e:
        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "error",
            "message": f"Check failed: {e}",
            "expires_in_days": None,
        }


def check_frameio_token():
    """Check Frame.io token health by reading the local token file."""
    if not os.path.exists(FRAMEIO_TOKEN_FILE):
        return {
            "name": "Frame.io access_token",
            "status": "error",
            "message": f"Token file not found: {FRAMEIO_TOKEN_FILE}",
            "expires_in_days": None,
            "self_managing": True,
        }

    try:
        with open(FRAMEIO_TOKEN_FILE) as f:
            tokens = json.load(f)

        obtained = tokens.get("obtained_at", "")
        expires_in = tokens.get("expires_in", 0)

        result = {
            "name": "Frame.io access_token",
            "status": "healthy",
            "message": "Self-managing via frameio_client.py (auto-refreshes on use)",
            "self_managing": True,
        }

        if obtained and expires_in:
            try:
                obtained_dt = datetime.fromisoformat(obtained)
                now = datetime.now(timezone.utc)
                elapsed = (now - obtained_dt).total_seconds()
                remaining = expires_in - elapsed
                if remaining > 0:
                    result["message"] += f" | Current token has {remaining / 60:.0f} min remaining"
                else:
                    result["message"] += " | Current token expired (will auto-refresh on next use)"
                    result["status"] = "stale"
            except Exception:
                pass

        result["expires_in_days"] = None  # Not applicable -- auto-refreshes
        return result

    except Exception as e:
        return {
            "name": "Frame.io access_token",
            "status": "error",
            "message": f"Could not read token file: {e}",
            "expires_in_days": None,
            "self_managing": True,
        }


def check_youtube_token():
    """Check YouTube API key health by making a simple API call."""
    api_key = os.environ.get("VURT_YOUTUBE_API_KEY", "")
    if not api_key:
        return {
            "name": "VURT_YOUTUBE_API_KEY",
            "status": "error",
            "message": "Environment variable not set",
            "expires_in_days": None,
        }

    try:
        # Simple channels.list call to verify the key works
        url = (
            f"{YOUTUBE_API_BASE}/channels?"
            f"part=id&id=UCB7B5ifo5Pgfc-j_uJGQG1g&key={api_key}"
        )
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        return {
            "name": "VURT_YOUTUBE_API_KEY",
            "status": "healthy",
            "message": "API key valid (permanent, no expiry)",
            "expires_in_days": None,
        }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {
            "name": "VURT_YOUTUBE_API_KEY",
            "status": "error",
            "message": f"API key invalid: {error_body}",
            "expires_in_days": None,
        }
    except Exception as e:
        return {
            "name": "VURT_YOUTUBE_API_KEY",
            "status": "error",
            "message": f"Check failed: {e}",
            "expires_in_days": None,
        }


def check_permanent_tokens():
    """Check that permanent tokens are at least set in the environment."""
    permanent = [
        "VURT_YOUTUBE_REFRESH_TOKEN",
        "VURT_GOOGLE_OAUTH_CLIENT",
        "VURT_NOTION_API_KEY",
        "NPAW_API_SECRET",
        "VURT_FRAMEIO_CLIENT_ID",
        "FRAMEIO_CLIENT_SECRET",
    ]
    results = []
    for name in permanent:
        val = os.environ.get(name, "")
        results.append({
            "name": name,
            "status": "set" if val else "missing",
            "message": "Permanent token (no expiry)" if val else "Environment variable not set",
            "expires_in_days": None,
        })
    return results


def refresh_meta_token():
    """Refresh the Meta long-lived token via Graph API exchange."""
    token = os.environ.get("VURT_META_ACCESS_TOKEN", "")
    app_secret = os.environ.get("VURT_META_APP_SECRET", "")

    if not token:
        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "error",
            "message": "VURT_META_ACCESS_TOKEN not set",
            "new_token": None,
        }
    if not app_secret:
        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "error",
            "message": "VURT_META_APP_SECRET not set",
            "new_token": None,
        }

    try:
        params = urllib.parse.urlencode({
            "grant_type": "fb_exchange_token",
            "client_id": META_APP_ID,
            "client_secret": app_secret,
            "fb_exchange_token": token,
        })
        url = f"{META_API_BASE}/oauth/access_token?{params}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        if "error" in data:
            return {
                "name": "VURT_META_ACCESS_TOKEN",
                "status": "error",
                "message": data["error"].get("message", "Unknown error"),
                "new_token": None,
            }

        new_token = data.get("access_token", "")
        expires_in = data.get("expires_in", 0)
        expires_days = expires_in // 86400 if isinstance(expires_in, int) else "unknown"

        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "refreshed",
            "message": f"New token obtained, expires in {expires_days} days",
            "new_token": new_token,
            "expires_in_seconds": expires_in,
            "expires_in_days": expires_days,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
            "action_required": "Update Zo secret VURT_META_ACCESS_TOKEN with the new_token value",
        }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "error",
            "message": f"Refresh failed: {error_body}",
            "new_token": None,
        }
    except Exception as e:
        return {
            "name": "VURT_META_ACCESS_TOKEN",
            "status": "error",
            "message": f"Refresh failed: {e}",
            "new_token": None,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Token Guardian: VURT API token health check and refresh"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check", action="store_true",
        help="Report status of all tokens (read-only)"
    )
    group.add_argument(
        "--refresh", action="store_true",
        help="Check all tokens + refresh Meta token"
    )
    args = parser.parse_args()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "refresh" if args.refresh else "check",
        "tokens": [],
        "summary": {},
    }

    # Check all expiring tokens
    print("Checking Meta token...", file=sys.stderr)
    meta_status = check_meta_token()
    report["tokens"].append(meta_status)

    print("Checking Frame.io token...", file=sys.stderr)
    frameio_status = check_frameio_token()
    report["tokens"].append(frameio_status)

    print("Checking YouTube API key...", file=sys.stderr)
    yt_status = check_youtube_token()
    report["tokens"].append(yt_status)

    # Check permanent tokens are set
    print("Checking permanent tokens...", file=sys.stderr)
    permanent_statuses = check_permanent_tokens()
    report["tokens"].extend(permanent_statuses)

    # If --refresh, also refresh Meta token
    meta_refresh_result = None
    if args.refresh:
        needs_refresh = meta_status["status"] in ("warning", "expired", "error")
        if meta_status["status"] == "healthy" and meta_status.get("expires_in_days"):
            if meta_status["expires_in_days"] < 14:
                needs_refresh = True

        if needs_refresh or args.refresh:
            print("Refreshing Meta token...", file=sys.stderr)
            meta_refresh_result = refresh_meta_token()
            report["meta_refresh"] = meta_refresh_result

    # Build summary
    statuses = [t["status"] for t in report["tokens"]]
    report["summary"] = {
        "total_tokens": len(report["tokens"]),
        "healthy": statuses.count("healthy") + statuses.count("set"),
        "warnings": statuses.count("warning") + statuses.count("stale"),
        "errors": statuses.count("error") + statuses.count("expired") + statuses.count("missing"),
        "overall": "ok" if all(
            s in ("healthy", "set", "stale") for s in statuses
        ) else "attention_needed",
    }

    if meta_refresh_result and meta_refresh_result["status"] == "refreshed":
        report["summary"]["action_required"] = (
            "Update Zo secret VURT_META_ACCESS_TOKEN with the new token"
        )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

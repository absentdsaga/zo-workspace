#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import requests

BASE_URL = "https://graph.facebook.com/v25.0"
IG_ACCOUNT_ID = "17841479978232203"
FB_PAGE_ID = "943789668811148"
APP_ID = "892877370386060"


def get_token():
    token = os.environ.get("VURT_META_ACCESS_TOKEN")
    if not token:
        print("Error: VURT_META_ACCESS_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


def get_app_secret():
    secret = os.environ.get("VURT_META_APP_SECRET")
    if not secret:
        print("Error: VURT_META_APP_SECRET not set", file=sys.stderr)
        sys.exit(1)
    return secret


def api_get(endpoint, params=None):
    token = get_token()
    params = params or {}
    params["access_token"] = token
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, params=params)
    data = resp.json()
    if "error" in data:
        err = data["error"]
        code = err.get("code", "")
        msg = err.get("message", "Unknown error")
        if code == 190:
            print(f"Error: Access token expired or invalid. Run 'refresh-token' or update VURT_META_ACCESS_TOKEN.\n{msg}", file=sys.stderr)
        else:
            print(f"API Error ({code}): {msg}", file=sys.stderr)
        sys.exit(1)
    return data


def print_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*[str(c) for c in row]))


def cmd_profile(args):
    fields = "id,name,username,biography,followers_count,follows_count,media_count,profile_picture_url,website"
    data = api_get(IG_ACCOUNT_ID, {"fields": fields})
    if args.json:
        print(json.dumps(data, indent=2))
        return
    print(f"Username:    @{data.get('username', 'N/A')}")
    print(f"Name:        {data.get('name', 'N/A')}")
    print(f"Bio:         {data.get('biography', 'N/A')}")
    print(f"Followers:   {data.get('followers_count', 'N/A'):,}")
    print(f"Following:   {data.get('follows_count', 'N/A'):,}")
    print(f"Posts:        {data.get('media_count', 'N/A'):,}")
    print(f"Website:     {data.get('website', 'N/A')}")
    print(f"Account ID:  {data.get('id', 'N/A')}")


def cmd_daily(args):
    days = args.days
    since = datetime.utcnow() - timedelta(days=days)
    until = datetime.utcnow()
    since_ts = int(since.timestamp())
    until_ts = int(until.timestamp())

    period_day_metrics = ["reach", "follower_count"]
    total_value_metrics = [
        "profile_views", "accounts_engaged", "total_interactions",
        "likes", "comments", "shares", "saves", "follows_and_unfollows"
    ]

    results = {}

    period_day_data = api_get(f"{IG_ACCOUNT_ID}/insights", {
        "metric": ",".join(period_day_metrics),
        "period": "day",
        "since": since_ts,
        "until": until_ts,
    })
    for metric_entry in period_day_data.get("data", []):
        name = metric_entry["name"]
        for val in metric_entry.get("values", []):
            date = val["end_time"][:10]
            results.setdefault(date, {})[name] = val["value"]

    dates = sorted(results.keys())
    if not dates:
        day = since
        while day <= until:
            dates.append(day.strftime("%Y-%m-%d"))
            day += timedelta(days=1)
        dates = sorted(set(dates))

    for metric in total_value_metrics:
        for date_str in dates:
            day_start = datetime.strptime(date_str, "%Y-%m-%d")
            day_end = day_start + timedelta(days=1)
            try:
                day_data = api_get(f"{IG_ACCOUNT_ID}/insights", {
                    "metric": metric,
                    "metric_type": "total_value",
                    "period": "day",
                    "since": int(day_start.timestamp()),
                    "until": int(day_end.timestamp()),
                })
                for entry in day_data.get("data", []):
                    val = entry.get("total_value", {}).get("value", 0)
                    results.setdefault(date_str, {})[entry["name"]] = val
            except SystemExit:
                results.setdefault(date_str, {})[metric] = "N/A"

    if args.json:
        print(json.dumps(results, indent=2))
        return

    all_metrics = period_day_metrics + total_value_metrics
    headers = ["Date"] + all_metrics
    rows = []
    for date in sorted(results.keys()):
        row = [date]
        for m in all_metrics:
            v = results[date].get(m, "N/A")
            if isinstance(v, (int, float)):
                row.append(f"{v:,}")
            else:
                row.append(str(v))
        rows.append(row)
    print_table(headers, rows)


def cmd_weekly(args):
    since = datetime.utcnow() - timedelta(days=7)
    until = datetime.utcnow()
    since_ts = int(since.timestamp())
    until_ts = int(until.timestamp())

    period_day_metrics = ["reach", "follower_count"]
    total_value_metrics = [
        "profile_views", "accounts_engaged", "total_interactions",
        "likes", "comments", "shares", "saves", "follows_and_unfollows"
    ]

    summary = {}

    period_data = api_get(f"{IG_ACCOUNT_ID}/insights", {
        "metric": ",".join(period_day_metrics),
        "period": "day",
        "since": since_ts,
        "until": until_ts,
    })
    for metric_entry in period_data.get("data", []):
        name = metric_entry["name"]
        values = [v["value"] for v in metric_entry.get("values", []) if isinstance(v.get("value"), (int, float))]
        summary[name] = sum(values) if name != "follower_count" else (values[-1] if values else 0)

    for metric in total_value_metrics:
        try:
            data = api_get(f"{IG_ACCOUNT_ID}/insights", {
                "metric": metric,
                "metric_type": "total_value",
                "period": "day",
                "since": since_ts,
                "until": until_ts,
            })
            for entry in data.get("data", []):
                summary[entry["name"]] = entry.get("total_value", {}).get("value", 0)
        except SystemExit:
            summary[metric] = "N/A"

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    print(f"Weekly Summary ({since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')})")
    print("-" * 40)
    for metric in period_day_metrics + total_value_metrics:
        v = summary.get(metric, "N/A")
        label = metric.replace("_", " ").title()
        if isinstance(v, (int, float)):
            print(f"  {label:<30} {v:>10,}")
        else:
            print(f"  {label:<30} {str(v):>10}")


def cmd_posts(args):
    limit = args.limit
    data = api_get(f"{IG_ACCOUNT_ID}/media", {
        "fields": "id,caption,timestamp,like_count,comments_count,media_type,permalink",
        "limit": limit,
    })
    posts = data.get("data", [])
    if not posts:
        print("No posts found.")
        return

    enriched = []
    for post in posts:
        post_insights = {"reach": "N/A", "saved": "N/A", "shares": "N/A", "views": "N/A"}
        try:
            insights_data = api_get(f"{post['id']}/insights", {
                "metric": "reach,saved,shares,views",
            })
            for entry in insights_data.get("data", []):
                post_insights[entry["name"]] = entry.get("values", [{}])[0].get("value", 0)
        except SystemExit:
            pass
        enriched.append({**post, **post_insights})

    if args.json:
        print(json.dumps(enriched, indent=2))
        return

    headers = ["Date", "Type", "Likes", "Comments", "Reach", "Views", "Saves", "Shares", "Caption"]
    rows = []
    for p in enriched:
        ts = p.get("timestamp", "")[:10]
        caption = (p.get("caption") or "")[:50]
        if len(p.get("caption") or "") > 50:
            caption += "..."
        rows.append([
            ts,
            p.get("media_type", "N/A"),
            p.get("like_count", 0),
            p.get("comments_count", 0),
            p.get("reach", "N/A"),
            p.get("views", "N/A"),
            p.get("saved", "N/A"),
            p.get("shares", "N/A"),
            caption,
        ])
    print_table(headers, rows)
    print(f"\nShowing {len(rows)} posts. Use --limit N to adjust.")


def cmd_demographics(args):
    demo_metrics = ["reached_audience_demographics", "follower_demographics"]
    all_data = {}

    for metric in demo_metrics:
        try:
            data = api_get(f"{IG_ACCOUNT_ID}/insights", {
                "metric": metric,
                "metric_type": "total_value",
                "period": "lifetime",
            })
            for entry in data.get("data", []):
                all_data[entry["name"]] = entry.get("total_value", {}).get("breakdowns", [])
        except SystemExit:
            all_data[metric] = "unavailable"

    if args.json:
        print(json.dumps(all_data, indent=2))
        return

    for metric_name, breakdowns in all_data.items():
        label = metric_name.replace("_", " ").title()
        print(f"\n{'=' * 60}")
        print(f"  {label}")
        print(f"{'=' * 60}")
        if breakdowns == "unavailable":
            print("  Data unavailable")
            continue
        for breakdown in breakdowns:
            dim = breakdown.get("dimension_keys", ["unknown"])
            print(f"\n  Dimension: {', '.join(dim)}")
            results = breakdown.get("results", [])
            sorted_results = sorted(results, key=lambda r: r.get("value", 0), reverse=True)
            headers = ["Category", "Count"]
            rows = []
            for r in sorted_results[:20]:
                keys = r.get("dimension_values", ["?"])
                rows.append([" / ".join(keys), f"{r.get('value', 0):,}"])
            print_table(headers, rows)


def cmd_refresh_token(args):
    current_token = get_token()
    app_secret = get_app_secret()
    resp = requests.get(f"{BASE_URL}/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": app_secret,
        "fb_exchange_token": current_token,
    })
    data = resp.json()
    if "error" in data:
        print(f"Error: {data['error'].get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    new_token = data.get("access_token", "N/A")
    token_type = data.get("token_type", "N/A")
    expires_in = data.get("expires_in", "N/A")
    if isinstance(expires_in, int):
        expires_days = expires_in // 86400
        print(f"Token Type:  {token_type}")
        print(f"Expires In:  {expires_days} days ({expires_in:,} seconds)")
    else:
        print(f"Token Type:  {token_type}")
        print(f"Expires In:  {expires_in}")
    print(f"\nNew Token:\n{new_token}")
    print(f"\nUpdate VURT_META_ACCESS_TOKEN in Zo secrets with this new token.")


def main():
    parser = argparse.ArgumentParser(description="VURT Instagram Insights via Meta Graph API")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("profile", help="Get current profile info")

    daily_parser = subparsers.add_parser("daily", help="Get daily metrics")
    daily_parser.add_argument("--days", type=int, default=7, help="Number of days (default: 7)")

    subparsers.add_parser("weekly", help="Get weekly summary")

    posts_parser = subparsers.add_parser("posts", help="Get recent posts with insights")
    posts_parser.add_argument("--limit", type=int, default=10, help="Number of posts (default: 10)")

    subparsers.add_parser("demographics", help="Get audience demographics")

    subparsers.add_parser("refresh-token", help="Exchange for long-lived token")

    args = parser.parse_args()

    commands = {
        "profile": cmd_profile,
        "daily": cmd_daily,
        "weekly": cmd_weekly,
        "posts": cmd_posts,
        "demographics": cmd_demographics,
        "refresh-token": cmd_refresh_token,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""YouTube Analytics API — retention, traffic sources, demographics, real-time views."""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

YT_ANALYTICS_BASE = "https://youtubeanalytics.googleapis.com/v2/reports"
YT_DATA_BASE = "https://www.googleapis.com/youtube/v3"
CHANNEL_ID = "UCB7B5ifo5Pgfc-j_uJGQG1g"


def get_creds():
    raw = os.environ.get("VURT_GOOGLE_OAUTH_CLIENT", "")
    if not raw:
        print("VURT_GOOGLE_OAUTH_CLIENT not set", file=sys.stderr)
        sys.exit(1)
    data = json.loads(raw)
    installed = data.get("installed", data)
    return installed["client_id"], installed["client_secret"]


def get_access_token():
    refresh = os.environ.get("VURT_YOUTUBE_REFRESH_TOKEN", "")
    if not refresh:
        print("VURT_YOUTUBE_REFRESH_TOKEN not set. Run yt-oauth-setup.py first.", file=sys.stderr)
        sys.exit(1)
    client_id, client_secret = get_creds()
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["access_token"]


def analytics_query(access_token, params):
    params["ids"] = "channel==MINE"
    qs = urllib.parse.urlencode(params)
    url = f"{YT_ANALYTICS_BASE}?{qs}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {access_token}")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"API error {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return None


def cmd_retention(access_token, video_id):
    if not video_id:
        print("Provide --video-id VIDEO_ID"); return
    params = {
        "startDate": "2020-01-01",
        "endDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "metrics": "audienceWatchRatio,relativeRetentionPerformance",
        "dimensions": "elapsedVideoTimeRatio",
        "filters": f"video=={video_id}",
    }
    data = analytics_query(access_token, params)
    if not data:
        return
    rows = data.get("rows", [])
    print(f"\nAudience Retention — {video_id}")
    print(f"{'Time %':>8} {'Watch Ratio':>12} {'Relative':>10}")
    print("=" * 35)
    for row in rows:
        pct = round(row[0] * 100)
        watch = round(row[1] * 100, 1)
        rel = round(row[2], 2) if len(row) > 2 else 0
        bar = "█" * int(watch / 2)
        print(f"  {pct:>5}%  {watch:>10}%  {rel:>8}  {bar}")


def cmd_traffic(access_token, days=30):
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    params = {
        "startDate": start, "endDate": end,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "insightTrafficSourceType",
        "sort": "-views",
    }
    data = analytics_query(access_token, params)
    if not data:
        return
    print(f"\nTraffic Sources — Last {days} Days")
    print(f"  {'Source':<35} {'Views':>8} {'Watch Min':>10}")
    print("  " + "=" * 58)
    for row in data.get("rows", []):
        print(f"  {row[0][:34]:<35} {row[1]:>8} {row[2]:>10}")


def cmd_demographics(access_token, days=90):
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    params = {
        "startDate": start, "endDate": end,
        "metrics": "viewerPercentage",
        "dimensions": "ageGroup,gender",
        "sort": "-viewerPercentage",
    }
    data = analytics_query(access_token, params)
    if not data:
        return
    print(f"\nDemographics — Last {days} Days")
    print(f"  {'Age Group':<15} {'Gender':<10} {'%':>8}")
    print("  " + "=" * 38)
    for row in data.get("rows", []):
        print(f"  {row[0]:<15} {row[1]:<10} {row[2]:>7.1f}%")


def cmd_top_videos(access_token, days=30):
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    params = {
        "startDate": start, "endDate": end,
        "metrics": "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained",
        "dimensions": "video",
        "sort": "-views",
        "maxResults": "25",
    }
    data = analytics_query(access_token, params)
    if not data:
        return

    api_key = os.environ.get("VURT_YOUTUBE_API_KEY", "")
    video_ids = [row[0] for row in data.get("rows", [])]
    titles = {}
    if api_key and video_ids:
        qs = urllib.parse.urlencode({"part": "snippet", "id": ",".join(video_ids), "key": api_key})
        try:
            resp = urllib.request.urlopen(f"{YT_DATA_BASE}/videos?{qs}")
            for v in json.loads(resp.read()).get("items", []):
                titles[v["id"]] = v["snippet"]["title"]
        except Exception:
            pass

    print(f"\nTop Videos — Last {days} Days")
    print(f"  {'Title':<40} {'Views':>7} {'Watch Min':>10} {'Avg Dur':>8} {'Avg %':>6} {'Subs':>5}")
    print("  " + "=" * 80)
    for row in data.get("rows", []):
        vid = row[0]
        title = titles.get(vid, vid)[:39]
        print(f"  {title:<40} {row[1]:>7} {row[2]:>10} {row[3]:>7}s {row[4]:>5.1f}% {row[5]:>5}")


def cmd_geography(access_token, days=30):
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    params = {
        "startDate": start, "endDate": end,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "country",
        "sort": "-views",
        "maxResults": "20",
    }
    data = analytics_query(access_token, params)
    if not data:
        return
    print(f"\nGeography — Last {days} Days")
    print(f"  {'Country':>10} {'Views':>8} {'Watch Min':>10}")
    print("  " + "=" * 33)
    for row in data.get("rows", []):
        print(f"  {row[0]:>10} {row[1]:>8} {row[2]:>10}")


def main():
    p = argparse.ArgumentParser(description="VURT YouTube Analytics")
    p.add_argument("--retention", action="store_true", help="Audience retention curve")
    p.add_argument("--traffic", action="store_true", help="Traffic sources")
    p.add_argument("--demographics", action="store_true", help="Age/gender breakdown")
    p.add_argument("--top-videos", action="store_true", help="Top videos by views")
    p.add_argument("--geography", action="store_true", help="Views by country")
    p.add_argument("--all", action="store_true", help="Run all reports (except retention)")
    p.add_argument("--video-id", type=str, default="", help="Video ID for retention")
    p.add_argument("--days", type=int, default=30)
    args = p.parse_args()

    if not any([args.retention, args.traffic, args.demographics, args.top_videos, args.geography, args.all]):
        p.print_help(); sys.exit(1)

    token = get_access_token()
    if args.retention or (args.all and args.video_id):
        cmd_retention(token, args.video_id)
    if args.traffic or args.all:
        cmd_traffic(token, args.days)
    if args.demographics or args.all:
        cmd_demographics(token, args.days)
    if args.top_videos or args.all:
        cmd_top_videos(token, args.days)
    if args.geography or args.all:
        cmd_geography(token, args.days)


if __name__ == "__main__":
    main()

import os, json, urllib.request, urllib.parse
from datetime import datetime, timedelta, date

CHANNEL_ID = "UCB7B5ifo5Pgfc-j_uJGQG1g"
YT_API = "https://www.googleapis.com/youtube/v3"
YT_ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2"
TOKEN_URL = "https://oauth2.googleapis.com/token"

def get_youtube_access_token():
    oauth = json.loads(os.environ["VURT_GOOGLE_OAUTH_CLIENT"])
    refresh = os.environ.get("VURT_YOUTUBE_REFRESH_TOKEN") or os.environ.get("VURT_ANALYTICS_REFRESH_TOKEN")
    if not refresh:
        return None
    params = urllib.parse.urlencode({
        "client_id": oauth["installed"]["client_id"],
        "client_secret": oauth["installed"]["client_secret"],
        "refresh_token": refresh,
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=params, method="POST")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["access_token"]

def _yt_get(path, params, token):
    qs = urllib.parse.urlencode(params)
    url = f"{YT_API}/{path}?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def _yt_analytics_get(params, token):
    qs = urllib.parse.urlencode(params)
    url = f"{YT_ANALYTICS_API}/reports?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def get_channel_analytics(days=7):
    """Channel-level analytics for the trailing window. Public Analytics API
    does not expose browse/suggested impressions or CTR (those are Studio-UI
    only); this returns what's actually queryable."""
    token = get_youtube_access_token()
    if not token:
        return None
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    metrics = ",".join([
        "views", "estimatedMinutesWatched", "averageViewDuration",
        "averageViewPercentage", "subscribersGained", "subscribersLost",
        "likes", "shares", "comments",
        "cardImpressions", "cardClickRate", "cardClicks",
    ])
    try:
        resp = _yt_analytics_get({
            "ids": "channel==MINE",
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "metrics": metrics,
        }, token)
    except Exception:
        return None
    rows = resp.get("rows") or []
    if not rows:
        return None
    headers = [c["name"] for c in resp.get("columnHeaders", [])]
    row = dict(zip(headers, rows[0]))
    return {
        "window_days": days,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "views": int(row.get("views") or 0),
        "minutesWatched": int(row.get("estimatedMinutesWatched") or 0),
        "avgViewDurationSec": int(row.get("averageViewDuration") or 0),
        "avgViewPercentage": float(row.get("averageViewPercentage") or 0),
        "subscribersGained": int(row.get("subscribersGained") or 0),
        "subscribersLost": int(row.get("subscribersLost") or 0),
        "likes": int(row.get("likes") or 0),
        "shares": int(row.get("shares") or 0),
        "comments": int(row.get("comments") or 0),
        "cardImpressions": int(row.get("cardImpressions") or 0),
        "cardClicks": int(row.get("cardClicks") or 0),
        "cardClickRate": float(row.get("cardClickRate") or 0),
    }

def get_traffic_sources(days=7):
    """Top traffic sources (Browse, Suggested, Search, External, etc.) for
    the trailing window. Returns list of {source, views, minutesWatched}."""
    token = get_youtube_access_token()
    if not token:
        return []
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    try:
        resp = _yt_analytics_get({
            "ids": "channel==MINE",
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "metrics": "views,estimatedMinutesWatched",
            "dimensions": "insightTrafficSourceType",
            "sort": "-views",
        }, token)
    except Exception:
        return []
    rows = resp.get("rows") or []
    out = []
    for r in rows:
        out.append({
            "source": r[0],
            "views": int(r[1] or 0),
            "minutesWatched": int(r[2] or 0),
        })
    return out

def get_channel_stats():
    token = get_youtube_access_token()
    if not token:
        return None
    data = _yt_get("channels", {"part": "snippet,statistics", "id": CHANNEL_ID}, token)
    if not data.get("items"):
        return None
    stats = data["items"][0]["statistics"]
    snippet = data["items"][0]["snippet"]
    return {
        "title": snippet.get("title", ""),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "totalViews": int(stats.get("viewCount", 0)),
        "videoCount": int(stats.get("videoCount", 0)),
    }

def get_recent_videos(days=7):
    token = get_youtube_access_token()
    if not token:
        return []
    after = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    search = _yt_get("search", {
        "part": "snippet",
        "channelId": CHANNEL_ID,
        "type": "video",
        "order": "date",
        "publishedAfter": after,
        "maxResults": 50
    }, token)
    items = search.get("items", [])
    if not items:
        return []
    video_ids = ",".join(i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId"))
    if not video_ids:
        return []
    stats = _yt_get("videos", {"part": "snippet,statistics,contentDetails", "id": video_ids}, token)
    videos = []
    for v in stats.get("items", []):
        s = v["statistics"]
        videos.append({
            "title": v["snippet"]["title"],
            "videoId": v["id"],
            "publishedAt": v["snippet"]["publishedAt"][:10],
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
        })
    videos.sort(key=lambda x: x["views"], reverse=True)
    return videos

def _fmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def format_youtube_report():
    try:
        channel = get_channel_stats()
    except Exception:
        return None, None
    if not channel:
        return None, None

    lines = []
    lines.append("## YouTube")
    lines.append("")
    lines.append(f"**{channel['title']}** — {_fmt(channel['subscribers'])} subscribers · {_fmt(channel['totalViews'])} total views · {channel['videoCount']} videos")
    lines.append("")

    analytics = None
    try:
        analytics = get_channel_analytics(days=7)
    except Exception:
        analytics = None

    if analytics:
        net_subs = analytics["subscribersGained"] - analytics["subscribersLost"]
        lines.append("### 7d Channel Analytics")
        lines.append("")
        lines.append(f"**{_fmt(analytics['views'])} views** · "
                     f"{_fmt(analytics['minutesWatched'])} min watched · "
                     f"{analytics['avgViewDurationSec']}s avg · "
                     f"{analytics['avgViewPercentage']:.1f}% avg view")
        lines.append("")
        lines.append(f"**Subs:** +{analytics['subscribersGained']} / "
                     f"-{analytics['subscribersLost']} (net {net_subs:+d})  ·  "
                     f"**Engagement:** {_fmt(analytics['likes'])} likes · "
                     f"{_fmt(analytics['shares'])} shares · "
                     f"{_fmt(analytics['comments'])} comments")
        lines.append("")

    sources = []
    try:
        sources = get_traffic_sources(days=7)
    except Exception:
        sources = []
    if sources:
        lines.append("### Traffic Sources (7d)")
        lines.append("")
        lines.append("| Source | Views | Min Watched |")
        lines.append("|--------|-------|-------------|")
        for s in sources[:8]:
            lines.append(f"| {s['source']} | {_fmt(s['views'])} | {_fmt(s['minutesWatched'])} |")
        lines.append("")

    try:
        videos = get_recent_videos(days=7)
    except Exception:
        videos = []

    if videos:
        lines.append("### Recent Videos (7d)")
        lines.append("")
        lines.append("| Video | Published | Views | Likes | Comments |")
        lines.append("|-------|-----------|-------|-------|----------|")
        for v in videos:
            title = v["title"][:45] + "..." if len(v["title"]) > 45 else v["title"]
            lines.append(f"| {title} | {v['publishedAt']} | {_fmt(v['views'])} | {_fmt(v['likes'])} | {_fmt(v['comments'])} |")
        lines.append("")

        total_views = sum(v["views"] for v in videos)
        total_likes = sum(v["likes"] for v in videos)
        total_comments = sum(v["comments"] for v in videos)
        lines.append(f"**7d totals:** {_fmt(total_views)} views · {_fmt(total_likes)} likes · {_fmt(total_comments)} comments")
        lines.append("")
    else:
        lines.append("*No videos published in the last 7 days.*")
        lines.append("")

    collected = {
        "channel": channel,
        "analytics_7d": analytics,
        "traffic_sources_7d": sources,
        "recent_videos": videos,
    }
    return "\n".join(lines), collected

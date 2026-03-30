import os, json, urllib.request, urllib.parse
from datetime import datetime, timedelta

CHANNEL_ID = "UCB7B5ifo5Pgfc-j_uJGQG1g"
YT_API = "https://www.googleapis.com/youtube/v3"
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
        "recent_videos": videos,
    }
    return "\n".join(lines), collected

#!/usr/bin/env python3
"""VURT Social Media Analytics — scrapes public profile data for daily report.

Uses agent-browser CLI to scrape public profiles. Instagram requires Meta Graph API
(not scrapable without auth). Data is cached for day-over-day comparison.
"""

import json, os, re, subprocess, time
from datetime import datetime

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".social-cache.json")

ACCOUNTS = {
    "instagram": {"handle": "myvurt", "url": "https://www.instagram.com/myvurt/"},
    "tiktok": {"handle": "myvurt", "url": "https://www.tiktok.com/@myvurt"},
    "youtube": {"handle": "myVURT1", "url": "https://www.youtube.com/@myVURT1"},
    "x": {"handle": "myvurt", "url": "https://x.com/myvurt"},
}


def _agent_browser_snapshot(url, wait=3, timeout=20):
    """Navigate to URL and return accessibility tree snapshot."""
    try:
        subprocess.run(
            ["agent-browser", "open", url],
            capture_output=True, text=True, timeout=timeout
        )
        time.sleep(wait)
        result = subprocess.run(
            ["agent-browser", "snapshot"],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout
    except Exception as e:
        return f"ERROR: {e}"


def _parse_count(text):
    """Parse counts like '1.2K', '324', '1.5M', '112'."""
    if not text:
        return 0
    text = text.strip().replace(",", "").upper()
    m = re.match(r"([\d.]+)\s*([KMB])?", text)
    if not m:
        return 0
    num = float(m.group(1))
    suffix = m.group(2)
    if suffix == "K":
        num *= 1_000
    elif suffix == "M":
        num *= 1_000_000
    elif suffix == "B":
        num *= 1_000_000_000
    return int(num)


def scrape_youtube():
    """Scrape YouTube channel — subscribers, video count, per-video views."""
    data = {"platform": "youtube", "handle": "@myVURT1",
            "subscribers": None, "videos": None, "top_videos": [], "error": None}
    try:
        snap = _agent_browser_snapshot(ACCOUNTS["youtube"]["url"], wait=3)

        # Subscribers: "11 subscribers"
        m = re.search(r"(\d[\d,.]*[KMB]?)\s+subscribers", snap)
        if m:
            data["subscribers"] = _parse_count(m.group(1))

        # Videos: "6 videos"
        m = re.search(r"(\d[\d,.]*)\s+videos?", snap)
        if m:
            data["videos"] = _parse_count(m.group(1))

        # Per-video views: lines like "769 views"
        view_matches = re.findall(r"([\d,.]+[KMB]?)\s+views?", snap)
        total_views = 0
        for v in view_matches:
            total_views += _parse_count(v)
        if total_views > 0:
            data["total_views"] = total_views

        # Extract video titles and views from snapshot lines
        # Pattern: link "Title" line, then within next 3 lines "text: N views"
        lines = snap.split("\n")
        for i, line in enumerate(lines):
            m_title = re.search(r"""link ['"]?["']?(.+?)['"]?["']?\s*[\[']""", line)
            if not m_title:
                m_title = re.search(r'link "(.+?)"', line)
            if m_title:
                title = m_title.group(1).strip('"\'')
                if any(skip in title.lower() for skip in ["home", "sign in", "shorts", "subscriptions", "you", "youtube"]):
                    continue
                # Check next 3 lines for views
                for j in range(1, 4):
                    if i + j >= len(lines):
                        break
                    m_views = re.search(r"([\d,.]+[KMB]?)\s+views?", lines[i + j])
                    if m_views:
                        data["top_videos"].append({"title": title[:60], "views": _parse_count(m_views.group(1))})
                        break

        if data["subscribers"] is None:
            data["error"] = "Could not parse subscribers"
    except Exception as e:
        data["error"] = str(e)
    return data


def scrape_tiktok():
    """Scrape TikTok public profile — followers, likes."""
    data = {"platform": "tiktok", "handle": "@myvurt",
            "followers": None, "likes": None, "following": None, "error": None}
    try:
        snap = _agent_browser_snapshot(ACCOUNTS["tiktok"]["url"], wait=4)

        # TikTok snapshot has a heading like: "0 Following 5 Followers 112 Likes"
        m = re.search(r"(\d[\d,.]*[KMB]?)\s*Following\s+(\d[\d,.]*[KMB]?)\s*Followers\s+(\d[\d,.]*[KMB]?)\s*Likes", snap)
        if m:
            data["following"] = _parse_count(m.group(1))
            data["followers"] = _parse_count(m.group(2))
            data["likes"] = _parse_count(m.group(3))
        else:
            # Fallback: individual matches
            m = re.search(r'"(\d[\d,.]*[KMB]?)"\s*.*?Followers', snap)
            if m:
                data["followers"] = _parse_count(m.group(1))
            m = re.search(r'"(\d[\d,.]*[KMB]?)"\s*.*?Likes', snap)
            if m:
                data["likes"] = _parse_count(m.group(1))

        if data["followers"] is None:
            data["error"] = "Could not parse followers"
    except Exception as e:
        data["error"] = str(e)
    return data


def scrape_x():
    """Scrape X/Twitter public profile — followers, posts."""
    data = {"platform": "x", "handle": "@myvurt",
            "followers": None, "following": None, "posts": None, "error": None}
    try:
        snap = _agent_browser_snapshot(ACCOUNTS["x"]["url"], wait=4)

        # X snapshot: "3 posts", "0 Following", "6 Followers"
        m = re.search(r"(\d[\d,.]*[KMB]?)\s+posts?", snap)
        if m:
            data["posts"] = _parse_count(m.group(1))

        m = re.search(r'link "(\d[\d,.]*[KMB]?)\s+Following"', snap)
        if m:
            data["following"] = _parse_count(m.group(1))

        m = re.search(r'link "(\d[\d,.]*[KMB]?)\s+Followers"', snap)
        if m:
            data["followers"] = _parse_count(m.group(1))

        if data["followers"] is None:
            data["error"] = "Could not parse followers"
    except Exception as e:
        data["error"] = str(e)
    return data


def scrape_instagram():
    """Instagram requires auth — returns cached/manual data or error."""
    data = {"platform": "instagram", "handle": "@myvurt",
            "followers": None, "posts": None, "error": None}

    # Try Meta Graph API if token is available
    ig_token = os.environ.get("VURT_INSTAGRAM_TOKEN")
    ig_user_id = os.environ.get("VURT_INSTAGRAM_USER_ID")

    if ig_token and ig_user_id:
        try:
            import urllib.request
            url = f"https://graph.instagram.com/{ig_user_id}?fields=followers_count,media_count,username&access_token={ig_token}"
            resp = urllib.request.urlopen(url, timeout=10)
            info = json.loads(resp.read())
            data["followers"] = info.get("followers_count")
            data["posts"] = info.get("media_count")
            return data
        except Exception as e:
            data["error"] = f"Graph API error: {e}"
            return data

    # No API access — use last known data from audit
    data["followers"] = None
    data["error"] = "Requires Meta Graph API (VURT_INSTAGRAM_TOKEN). Last known: ~324 followers, 21 posts (Mar 17)"
    return data


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def collect_social_data():
    """Run all scrapers, compute deltas from cached previous run."""
    previous = load_cache()

    scrapers = [
        ("youtube", scrape_youtube),
        ("tiktok", scrape_tiktok),
        ("x", scrape_x),
        ("instagram", scrape_instagram),
    ]

    current = {"timestamp": datetime.now().isoformat(), "platforms": {}}

    for platform, scraper in scrapers:
        try:
            result = scraper()
            current["platforms"][platform] = result
        except Exception as e:
            current["platforms"][platform] = {"platform": platform, "error": str(e)}

    # Compute deltas
    prev_platforms = previous.get("platforms", {})
    for platform, data in current["platforms"].items():
        prev = prev_platforms.get(platform, {})
        data["_prev"] = prev
        for key in ["followers", "subscribers", "likes", "posts", "videos", "total_views"]:
            cur_val = data.get(key)
            prev_val = prev.get(key)
            if cur_val is not None and prev_val is not None:
                data[f"{key}_delta"] = cur_val - prev_val

    save_cache(current)
    return current


def _delta_str(data, metric):
    key = f"{metric}_delta"
    if key not in data:
        return "—"
    d = data[key]
    if d > 0:
        return f"▲ +{d}"
    elif d < 0:
        return f"▼ {d}"
    return "→ 0"


def _fmt_val(val):
    if val is None:
        return "—"
    return f"{val:,}"


def format_social_report(social_data):
    """Format social media data into markdown report section."""
    lines = []
    lines.append("## Social Media Overview")
    lines.append("")

    platforms = social_data.get("platforms", {})

    # Summary table
    lines.append("| Platform | Handle | Followers/Subs | Change | Activity |")
    lines.append("|----------|--------|---------------|--------|----------|")

    # YouTube
    yt = platforms.get("youtube", {})
    yt_activity = f"{_fmt_val(yt.get('videos'))} videos, {_fmt_val(yt.get('total_views'))} total views"
    lines.append(f"| YouTube | @myVURT1 | {_fmt_val(yt.get('subscribers'))} | {_delta_str(yt, 'subscribers')} | {yt_activity} |")

    # TikTok
    tt = platforms.get("tiktok", {})
    tt_activity = f"{_fmt_val(tt.get('likes'))} likes"
    lines.append(f"| TikTok | @myvurt | {_fmt_val(tt.get('followers'))} | {_delta_str(tt, 'followers')} | {tt_activity} |")

    # Instagram
    ig = platforms.get("instagram", {})
    ig_activity = f"{_fmt_val(ig.get('posts'))} posts" if ig.get("posts") else "API needed"
    ig_followers = _fmt_val(ig.get("followers")) if ig.get("followers") else "~324*"
    lines.append(f"| Instagram | @myvurt | {ig_followers} | {_delta_str(ig, 'followers')} | {ig_activity} |")

    # X
    x = platforms.get("x", {})
    x_activity = f"{_fmt_val(x.get('posts'))} posts"
    lines.append(f"| X | @myvurt | {_fmt_val(x.get('followers'))} | {_delta_str(x, 'followers')} | {x_activity} |")

    lines.append("")

    # YouTube video breakdown (if available)
    yt_videos = yt.get("top_videos", [])
    if yt_videos:
        lines.append("**YouTube Video Performance:**")
        lines.append("")
        lines.append("| Video | Views |")
        lines.append("|-------|-------|")
        for v in yt_videos:
            lines.append(f"| {v['title']} | {v['views']:,} |")
        lines.append("")

    # Cross-platform totals
    total_followers = 0
    for p, d in platforms.items():
        f = d.get("followers") or d.get("subscribers") or 0
        total_followers += f
    if total_followers > 0:
        lines.append(f"**Total cross-platform reach:** {total_followers:,} followers")
        lines.append("")

    # Errors/notes
    errors = [(p, d.get("error")) for p, d in platforms.items() if d.get("error")]
    if errors:
        lines.append("**Notes:**")
        for platform, err in errors:
            lines.append(f"- {platform}: {err}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Collecting VURT social media data...\n")
    data = collect_social_data()
    print(format_social_report(data))
    print(f"Cache saved to: {CACHE_FILE}")

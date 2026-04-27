#!/usr/bin/env python3
"""VURT Social Media Analytics — scrapes public profile data for daily report.

Uses agent-browser CLI to scrape public profiles. Instagram requires Meta Graph API
(not scrapable without auth). Data is cached for day-over-day comparison.
"""

import json, os, re, subprocess, sys, time
from datetime import datetime

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".social-cache.json")
CACHE_PREV_FILE = os.path.join(os.path.dirname(__file__), ".social-cache-prev.json")

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
    """Fetch YouTube channel stats via Data API (subscribers, video count, total views)."""
    data = {"platform": "youtube", "handle": "@myVURT1",
            "subscribers": None, "videos": None, "total_views": None, "top_videos": [], "error": None}
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from youtube_client import get_channel_stats
        stats = get_channel_stats()
        data["subscribers"] = stats.get("subscribers")
        data["videos"] = stats.get("videoCount")
        data["total_views"] = stats.get("totalViews")
    except Exception as e:
        data["error"] = str(e)
    return data


def scrape_tiktok():
    """Fetch TikTok @myvurt stats + recent + top performers.

    Uses tiktok_profile.get_profile_summary() which parses the static profile
    HTML blob (no browser) and reads the per-video scrape cache populated by
    tiktok_url_harvest + tiktok_scraper.
    """
    data = {"platform": "tiktok", "handle": "@myvurt",
            "followers": None, "likes": None, "following": None,
            "posts": None, "top_posts": [], "recent_7d": {}, "error": None}
    try:
        sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
        from tiktok_profile import get_profile_summary
        summary = get_profile_summary(handle="myvurt", top_limit=5)
        stats = summary["stats"]
        if stats.get("error"):
            data["error"] = stats["error"]
        data["followers"] = stats.get("followers")
        data["following"] = stats.get("following")
        data["likes"] = stats.get("likes")
        data["posts"] = stats.get("video_count")
        data["recent_7d"] = summary.get("recent", {})
        data["top_posts"] = [
            {
                "caption": t["caption"],
                "url": t["url"],
                "views": t["views"],
                "likes": t["likes"],
                "saves": t["saves"],
                "save_rate": t["save_rate"],
            }
            for t in summary.get("top_performers", {}).get("top", [])
        ]
        if data["followers"] is None and not data["error"]:
            data["error"] = "Could not parse followers from profile blob"
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
    """Instagram via Meta Graph API — profile + 7-day insights."""
    data = {"platform": "instagram", "handle": "@myvurt",
            "followers": None, "posts": None, "following": None,
            "reach_7d": None, "profile_views_7d": None,
            "accounts_engaged_7d": None, "total_interactions_7d": None,
            "likes_7d": None, "comments_7d": None, "shares_7d": None, "saves_7d": None,
            "active_stories": [], "active_stories_count": 0,
            "active_stories_reach_total": 0, "active_stories_replies_total": 0,
            "active_stories_link_clicks_total": 0,
            "top_posts": [], "error": None}

    ig_token = os.environ.get("VURT_META_ACCESS_TOKEN")
    IG_USER_ID = "17841479978232203"

    if not ig_token:
        data["error"] = "VURT_META_ACCESS_TOKEN not set"
        return data

    try:
        import urllib.request
        from datetime import timedelta

        def _graph_get(path, params=None):
            params = params or {}
            params["access_token"] = ig_token
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"https://graph.facebook.com/v25.0/{path}?{qs}"
            resp = urllib.request.urlopen(url, timeout=15)
            return json.loads(resp.read())

        # Profile
        profile = _graph_get(IG_USER_ID, {
            "fields": "followers_count,follows_count,media_count,username"
        })
        data["followers"] = profile.get("followers_count")
        data["following"] = profile.get("follows_count")
        data["posts"] = profile.get("media_count")

        # 7-day insights (time-series metrics)
        now = datetime.utcnow()
        since = int((now - timedelta(days=7)).timestamp())
        until = int(now.timestamp())
        try:
            ts_insights = _graph_get(f"{IG_USER_ID}/insights", {
                "metric": "reach,follower_count",
                "period": "day",
                "since": since, "until": until,
            })
            for m in ts_insights.get("data", []):
                if m["name"] == "reach":
                    data["reach_7d"] = sum(v["value"] for v in m.get("values", []))
        except:
            pass

        # 7-day insights (total_value metrics)
        try:
            tv_insights = _graph_get(f"{IG_USER_ID}/insights", {
                "metric": "profile_views,accounts_engaged,total_interactions,likes,comments,shares,saves",
                "metric_type": "total_value",
                "period": "day",
                "since": since, "until": until,
            })
            for m in tv_insights.get("data", []):
                val = m.get("total_value", {}).get("value", 0)
                data[f"{m['name']}_7d"] = val
        except:
            pass

        # Active Stories (last 24h) — tracks the "stories ladder" per Reel
        # Metrics: reach, replies, navigation (taps_forward/taps_back/exits/swipe_away),
        #   profile_visits, link_clicks (when a link sticker is present).
        # We use these to flag Reels that did NOT get a stories ladder (i.e. Reel
        # published in last 24h but <3 active stories around it).
        try:
            stories_resp = _graph_get(f"{IG_USER_ID}/stories", {
                "fields": "id,media_type,media_url,permalink,timestamp",
                "limit": "50",
            })
            stories_list = []
            for s in stories_resp.get("data", []):
                story_item = {
                    "id": s["id"],
                    "type": s.get("media_type", ""),
                    "permalink": s.get("permalink", ""),
                    "timestamp": s.get("timestamp", ""),
                    "date": s.get("timestamp", "")[:10],
                    "reach": None,
                    "replies": None,
                    "taps_forward": None,
                    "taps_back": None,
                    "exits": None,
                    "profile_visits": None,
                    "link_clicks": None,
                }
                try:
                    si = _graph_get(f"{s['id']}/insights", {
                        "metric": "reach,replies,profile_visits",
                    })
                    for entry in si.get("data", []):
                        name = entry["name"]
                        val = entry.get("values", [{}])[0].get("value")
                        if val is None:
                            val = entry.get("total_value", {}).get("value", 0)
                        story_item[name] = val
                except Exception:
                    pass
                # Navigation needs its own call w/ breakdown param
                try:
                    nav = _graph_get(f"{s['id']}/insights", {
                        "metric": "navigation",
                        "breakdown": "story_navigation_action_type",
                        "metric_type": "total_value",
                    })
                    for entry in nav.get("data", []):
                        for bd in entry.get("total_value", {}).get("breakdowns", []):
                            for r in bd.get("results", []):
                                dim = (r.get("dimension_values") or [""])[0]
                                v = r.get("value", 0)
                                if dim == "tap_forward":
                                    story_item["taps_forward"] = v
                                elif dim == "tap_back":
                                    story_item["taps_back"] = v
                                elif dim == "tap_exit":
                                    story_item["exits"] = v
                                elif dim == "swipe_forward":
                                    story_item["swipes"] = v
                except Exception:
                    pass
                # Link clicks — only exists if story had a link sticker; metric fails silently otherwise
                try:
                    lc = _graph_get(f"{s['id']}/insights", {"metric": "website_clicks"})
                    for entry in lc.get("data", []):
                        val = entry.get("values", [{}])[0].get("value", 0)
                        if val:
                            story_item["link_clicks"] = val
                except Exception:
                    pass
                stories_list.append(story_item)
            data["active_stories"] = stories_list
            data["active_stories_count"] = len(stories_list)
            data["active_stories_reach_total"] = sum(
                (s.get("reach") or 0) for s in stories_list
            )
            data["active_stories_replies_total"] = sum(
                (s.get("replies") or 0) for s in stories_list
            )
            data["active_stories_link_clicks_total"] = sum(
                (s.get("link_clicks") or 0) for s in stories_list
            )
        except Exception as e:
            data["active_stories_error"] = str(e)

        # Recent posts (top 15)
        try:
            media = _graph_get(f"{IG_USER_ID}/media", {
                "fields": "id,caption,timestamp,like_count,comments_count,media_type,permalink",
                "limit": "15",
            })
            all_comments = []
            for post in media.get("data", []):
                post_data = {
                    "caption": (post.get("caption") or "")[:60],
                    "likes": post.get("like_count", 0),
                    "comments": post.get("comments_count", 0),
                    "type": post.get("media_type", ""),
                    "date": post.get("timestamp", "")[:10],
                    "reach": None, "views": None, "saves": None, "shares": None,
                    "comments_with_replies": 0,
                }
                try:
                    # Use views (not plays — deprecated in v22+); works for VIDEO and IMAGE
                    pi = _graph_get(f"{post['id']}/insights", {"metric": "reach,saved,shares,views"})
                    for entry in pi.get("data", []):
                        key = entry["name"] if entry["name"] != "saved" else "saves"
                        post_data[key] = entry.get("values", [{}])[0].get("value", 0)
                except:
                    pass
                # Pull comments + replies for accurate total count
                if post_data["comments"] > 0:
                    try:
                        c_resp = _graph_get(f"{post['id']}/comments", {
                            "fields": "text,username,timestamp,replies{text,username,timestamp}",
                            "limit": "50",
                        })
                        comment_list = []
                        reply_count = 0
                        for c in c_resp.get("data", []):
                            comment_list.append({
                                "user": c.get("username",""),
                                "text": c.get("text","")[:120],
                                "date": c.get("timestamp","")[:10],
                                "post_caption": (post.get("caption") or "")[:40],
                            })
                            replies = c.get("replies", {}).get("data", [])
                            reply_count += len(replies)
                            for r in replies:
                                comment_list.append({
                                    "user": r.get("username",""),
                                    "text": f"↳ {r.get('text','')[:110]}",
                                    "date": r.get("timestamp","")[:10],
                                    "post_caption": (post.get("caption") or "")[:40],
                                })
                        post_data["comment_list"] = comment_list[:15]
                        post_data["comments_with_replies"] = len(c_resp.get("data", [])) + reply_count
                        all_comments.extend(comment_list)
                    except:
                        post_data["comment_list"] = []
                data["top_posts"].append(post_data)
            data["all_recent_comments"] = sorted(all_comments, key=lambda x: x.get("date",""), reverse=True)[:25]
            data["total_comments_with_replies"] = sum(p.get("comments_with_replies", 0) for p in data["top_posts"])
        except:
            pass

    except Exception as e:
        data["error"] = f"Graph API error: {e}"

    return data


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(data):
    today = datetime.now().strftime("%Y-%m-%d")
    # If existing cache is from a previous day, promote it to prev before overwriting
    if os.path.exists(CACHE_FILE):
        try:
            existing = json.load(open(CACHE_FILE))
            existing_date = existing.get("timestamp", "")[:10]
            if existing_date and existing_date != today:
                with open(CACHE_PREV_FILE, "w") as f:
                    json.dump(existing, f, indent=2)
        except Exception:
            pass
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_facebook_page():
    """Facebook Page metrics via Meta Graph API (New Pages Experience)."""
    data = {"platform": "facebook", "handle": "myvurt",
            "followers": None, "talking_about": None, "recent_posts": [],
            "total_post_reactions": 0, "total_post_shares": 0, "error": None}

    user_token = os.environ.get("VURT_META_ACCESS_TOKEN")
    PAGE_ID = "943789668811148"

    if not user_token:
        data["error"] = "VURT_META_ACCESS_TOKEN not set"
        return data

    try:
        import urllib.request, urllib.parse

        def _graph(path, params=None, token=None):
            params = params or {}
            params["access_token"] = token or user_token
            url = f"https://graph.facebook.com/v19.0/{path}?{urllib.parse.urlencode(params)}"
            return json.loads(urllib.request.urlopen(url, timeout=15).read())

        # Try using stored token directly as page token (if it's already a page token)
        # Otherwise fetch page token from page ID
        page_token = user_token
        try:
            page = _graph(PAGE_ID, {"fields": "fan_count,followers_count,talking_about_count"}, token=page_token)
            if not page.get("followers_count") and page.get("followers_count") != 0:
                # Token might be a user token, get page token
                pt = _graph(PAGE_ID, {"fields": "access_token"}).get("access_token")
                if pt:
                    page_token = pt
                    page = _graph(PAGE_ID, {"fields": "fan_count,followers_count,talking_about_count"}, token=page_token)
        except:
            try:
                pt = _graph(PAGE_ID, {"fields": "access_token"}).get("access_token")
                if pt:
                    page_token = pt
                page = _graph(PAGE_ID, {"fields": "fan_count,followers_count,talking_about_count"}, token=page_token)
            except Exception as e:
                data["error"] = f"Could not access page: {e}"
                return data

        data["followers"] = page.get("followers_count")
        data["talking_about"] = page.get("talking_about_count")

        # Page-level insights (7d) — these capture ALL engagement including
        # Facebook's recommendation engine distribution, which individual post
        # endpoints do NOT return
        try:
            from datetime import timedelta
            now = datetime.utcnow()
            since = int((now - timedelta(days=7)).timestamp())
            until = int(now.timestamp())

            pi_resp = _graph(f"{PAGE_ID}/insights", {
                "metric": "page_actions_post_reactions_total,page_post_engagements,page_video_views,page_video_views_organic,page_video_views_paid,page_posts_impressions",
                "period": "day",
                "since": since,
                "until": until,
            }, token=page_token)

            daily_breakdown = {}
            for m in pi_resp.get("data", []):
                name = m["name"]
                for v in m.get("values", []):
                    day = v["end_time"][:10]
                    if day not in daily_breakdown:
                        daily_breakdown[day] = {"date": day}
                    val = v["value"]
                    if name == "page_actions_post_reactions_total":
                        if isinstance(val, dict):
                            daily_breakdown[day]["reactions"] = sum(val.values())
                            daily_breakdown[day]["reactions_by_type"] = val
                        else:
                            daily_breakdown[day]["reactions"] = val
                    elif name == "page_post_engagements":
                        daily_breakdown[day]["engagements"] = val
                    elif name == "page_video_views":
                        daily_breakdown[day]["video_views"] = val
                    elif name == "page_video_views_organic":
                        daily_breakdown[day]["video_views_organic"] = val
                    elif name == "page_video_views_paid":
                        daily_breakdown[day]["video_views_paid"] = val
                    elif name == "page_posts_impressions":
                        daily_breakdown[day]["impressions"] = val

            data["page_daily_breakdown"] = sorted(daily_breakdown.values(), key=lambda x: x["date"], reverse=True)
            data["page_reactions_7d"] = sum(d.get("reactions", 0) for d in daily_breakdown.values())
            data["page_engagements_7d"] = sum(d.get("engagements", 0) for d in daily_breakdown.values())
            data["page_video_views_7d"] = sum(d.get("video_views", 0) for d in daily_breakdown.values())
            data["page_video_views_organic_7d"] = sum(d.get("video_views_organic", 0) for d in daily_breakdown.values())
            data["page_video_views_paid_7d"] = sum(d.get("video_views_paid", 0) for d in daily_breakdown.values())
            data["page_impressions_7d"] = sum(d.get("impressions", 0) for d in daily_breakdown.values())

            # Aggregate reaction types across all days
            all_types = {}
            for d in daily_breakdown.values():
                for rtype, count in d.get("reactions_by_type", {}).items():
                    all_types[rtype] = all_types.get(rtype, 0) + count
            data["page_reactions_by_type_7d"] = all_types
        except Exception:
            pass

        # Use v19 /feed — v25 throws deprecation errors on aggregated fields
        # Only request likes.summary and comments.summary (reactions.summary and shares are deprecated)
        posts_resp = _graph(f"{PAGE_ID}/feed", {
            "fields": "id,message,story,created_time,likes.summary(true),comments.summary(true),attachments",
            "limit": "20",
        }, token=page_token)

        seen_ids = set()
        for p in posts_resp.get("data", []):
            post_id = p.get("id", "")
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            # Use likes count as reactions proxy (reactions.summary deprecated on feed)
            reactions = p.get("likes", {}).get("summary", {}).get("total_count", 0)
            comment_count = p.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares = 0  # shares field deprecated on feed with attachments
            data["total_post_reactions"] += reactions
            data["total_post_shares"] += shares
            data["total_post_comments"] = data.get("total_post_comments", 0) + comment_count

            caption = (p.get("message") or p.get("story") or "")[:60]

            # Extract FB video views from attachment target (cross-posted IG reels)
            video_views = None
            is_reel = False
            for att in (p.get("attachments", {}).get("data", [])):
                att_type = att.get("type", "")
                target = att.get("target", {})
                target_id = target.get("id")
                target_url = target.get("url", "")
                if att_type == "video_inline" and target_id and "/reel/" in target_url:
                    is_reel = True
                    try:
                        vr = _graph(target_id, {"fields": "views"}, token=page_token)
                        video_views = vr.get("views")
                    except Exception:
                        pass
                    break

            # Pull comments + replies for accurate counts
            recent_comments = []
            total_with_replies = 0
            if comment_count > 0:
                try:
                    comments_resp = _graph(f"{post_id}/comments", {
                        "fields": "message,from,created_time,comments{message,from,created_time}",
                        "limit": "50",
                        "filter": "stream",
                    }, token=page_token)
                    for c in comments_resp.get("data", []):
                        total_with_replies += 1
                        recent_comments.append({
                            "from": (c.get("from") or {}).get("name", ""),
                            "text": (c.get("message") or "")[:120],
                            "date": c.get("created_time", "")[:10],
                        })
                        nested = c.get("comments", {}).get("data", [])
                        total_with_replies += len(nested)
                        for nc in nested:
                            recent_comments.append({
                                "from": (nc.get("from") or {}).get("name", ""),
                                "text": f"↳ {(nc.get('message') or '')[:110]}",
                                "date": nc.get("created_time", "")[:10],
                            })
                except Exception:
                    total_with_replies = comment_count

            post_record = {
                "date": p.get("created_time", "")[:10],
                "reactions": reactions,
                "comments": comment_count,
                "comments_with_replies": total_with_replies,
                "shares": shares,
                "message": caption.replace("\n", " ").replace("|", "/"),
                "recent_comments": recent_comments,
            }
            if is_reel:
                post_record["is_reel"] = True
                post_record["video_views"] = video_views
                data["total_reel_views_feed"] = data.get("total_reel_views_feed", 0) + (video_views or 0)
            data["recent_posts"].append(post_record)

        # Sort by most recent first, keep top 15
        data["recent_posts"].sort(key=lambda x: x.get("date", ""), reverse=True)
        data["recent_posts"] = data["recent_posts"][:15]

        # NOTE: Separate video_reels endpoint removed — reels already appear in feed
        # with accurate FB views. The likes/comments on native FB reels are negligible
        # compared to IG engagement (which Meta surfaces in FB notifications).

    except Exception as e:
        data["error"] = f"Graph API error: {e}"

    return data


def collect_social_data():
    """Run all scrapers, compute deltas from yesterday's snapshot."""
    # Always compare against the previous-day snapshot, not today's last run
    previous = {}
    if os.path.exists(CACHE_PREV_FILE):
        try:
            previous = json.load(open(CACHE_PREV_FILE))
        except Exception:
            pass
    if not previous:
        previous = load_cache()

    scrapers = [
        ("youtube", scrape_youtube),
        ("tiktok", scrape_tiktok),
        ("x", scrape_x),
        ("instagram", scrape_instagram),
        ("facebook", get_facebook_page),
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
        for key in ["followers", "subscribers", "likes", "posts", "videos", "total_views",
                    "talking_about", "total_post_reactions"]:
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
    ig = platforms.get("instagram", {})
    fb = platforms.get("facebook", {})
    yt = platforms.get("youtube", {})
    tt = platforms.get("tiktok", {})
    x = platforms.get("x", {})

    # Summary table
    lines.append("| Platform | Handle | Followers/Subs | Change | Activity |")
    lines.append("|----------|--------|---------------|--------|----------|")

    ig_activity = f"{_fmt_val(ig.get('posts'))} posts" if ig.get("posts") else "API needed"
    lines.append(f"| Instagram | @myvurt | {_fmt_val(ig.get('followers'))} | {_delta_str(ig, 'followers')} | {ig_activity} |")

    if not fb.get("error"):
        fb_activity = f"talking about: {_fmt_val(fb.get('talking_about'))}"
        lines.append(f"| Facebook | myvurt | {_fmt_val(fb.get('followers'))} | {_delta_str(fb, 'followers')} | {fb_activity} |")

    yt_activity = f"{_fmt_val(yt.get('videos'))} videos, {_fmt_val(yt.get('total_views'))} total views"
    lines.append(f"| YouTube | @myVURT1 | {_fmt_val(yt.get('subscribers'))} | {_delta_str(yt, 'subscribers')} | {yt_activity} |")

    tt_parts = []
    if tt.get("likes"):
        tt_parts.append(f"{_fmt_val(tt.get('likes'))} likes")
    if tt.get("posts"):
        tt_parts.append(f"{_fmt_val(tt.get('posts'))} videos")
    recent = tt.get("recent_7d", {})
    if recent.get("post_count"):
        tt_parts.append(f"{recent['post_count']} posts/7d · {_fmt_val(recent.get('total_views'))} views/7d")
    tt_activity = ", ".join(tt_parts) if tt_parts else "—"
    lines.append(f"| TikTok | @myvurt | {_fmt_val(tt.get('followers'))} | {_delta_str(tt, 'followers')} | {tt_activity} |")

    x_activity = f"{_fmt_val(x.get('posts'))} posts"
    lines.append(f"| X | @myvurt | {_fmt_val(x.get('followers'))} | {_delta_str(x, 'followers')} | {x_activity} |")

    lines.append("")

    # Cross-platform totals
    total_followers = sum(
        (d.get("followers") or d.get("subscribers") or 0)
        for p, d in platforms.items() if not d.get("error")
    )
    if total_followers > 0:
        lines.append(f"**Total cross-platform reach:** {total_followers:,} followers")
        lines.append("")

    # Combined engagement summary — uses PAGE-LEVEL insights for FB (accurate)
    # and per-post data for IG
    fb_page_reactions = fb.get("page_reactions_7d", 0)
    fb_page_engagements = fb.get("page_engagements_7d", 0)
    fb_page_video_views = fb.get("page_video_views_7d", 0)
    ig_cwr = ig.get("total_comments_with_replies", 0)
    ig_likes_total = sum(p.get("likes", 0) for p in ig.get("top_posts", []))
    ig_shares_total = sum(p.get("shares", 0) for p in ig.get("top_posts", []) if p.get("shares"))

    if fb_page_reactions > 0 or ig_likes_total > 0:
        lines.append("### Combined Engagement (7d)")
        lines.append("")
        lines.append("| Metric | IG | FB (Page Insights) | Total |")
        lines.append("|--------|----|--------------------|------:|")
        lines.append(f"| Reactions/Likes | {_fmt_val(ig_likes_total)} | {_fmt_val(fb_page_reactions)} | **{_fmt_val(ig_likes_total + fb_page_reactions)}** |")
        lines.append(f"| Comments (w/ replies) | {ig_cwr} | — | **{ig_cwr}** |")
        lines.append(f"| Shares | {_fmt_val(ig_shares_total)} | — | **{_fmt_val(ig_shares_total)}** |")
        lines.append(f"| Total Engagements | — | {_fmt_val(fb_page_engagements)} | — |")
        lines.append(f"| Video Views | — | {_fmt_val(fb_page_video_views)} | — |")
        fb_impressions = fb.get("page_impressions_7d", 0)
        if fb_impressions:
            lines.append(f"| Impressions | — | {_fmt_val(fb_impressions)} | — |")
        lines.append("")

    # =========================================================================
    # INSTAGRAM — lead with this since it drives the engagement in FB notifications
    # =========================================================================
    if ig.get("reach_7d") is not None:
        lines.append("### Instagram Engagement (7d)")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        ig_metrics = [
            ("Reach", ig.get("reach_7d")),
            ("Profile Views", ig.get("profile_views_7d")),
            ("Accounts Engaged", ig.get("accounts_engaged_7d")),
            ("Total Interactions", ig.get("total_interactions_7d")),
            ("Likes", ig.get("likes_7d")),
            ("Comments", ig.get("comments_7d")),
            ("Shares", ig.get("shares_7d")),
            ("Saves", ig.get("saves_7d")),
        ]
        for name, val in ig_metrics:
            lines.append(f"| {name} | {_fmt_val(val)} |")
        lines.append("")

    # Active IG Stories (24h rolling window) — tracks the "stories ladder" per Reel
    stories = ig.get("active_stories", [])
    if stories:
        lines.append("### Instagram Stories (active, 24h rolling)")
        lines.append("")
        total_reach = ig.get("active_stories_reach_total", 0)
        total_replies = ig.get("active_stories_replies_total", 0)
        total_link_clicks = ig.get("active_stories_link_clicks_total", 0)
        lines.append(f"**{len(stories)} active stories** · reach: {_fmt_val(total_reach)} · replies: {_fmt_val(total_replies)} · link-sticker clicks: {_fmt_val(total_link_clicks)}")
        lines.append("")
        lines.append("| Posted | Type | Reach | Replies | Tap→ | Tap← | Exits | Profile Visits | Link Clicks |")
        lines.append("|--------|------|-------|---------|------|------|-------|----------------|-------------|")
        for s in stories:
            ts = s.get("timestamp", "")[:16].replace("T", " ")
            lines.append(
                f"| {ts} | {s.get('type','')} | {_fmt_val(s.get('reach'))} | "
                f"{_fmt_val(s.get('replies'))} | {_fmt_val(s.get('taps_forward'))} | "
                f"{_fmt_val(s.get('taps_back'))} | {_fmt_val(s.get('exits'))} | "
                f"{_fmt_val(s.get('profile_visits'))} | {_fmt_val(s.get('link_clicks'))} |"
            )
        lines.append("")
    elif ig.get("active_stories_error"):
        lines.append(f"_Stories API note: {ig['active_stories_error']}_")
        lines.append("")

    ig_posts = ig.get("top_posts", [])
    if ig_posts:
        total_cwr = ig.get("total_comments_with_replies", 0)
        if total_cwr:
            lines.append(f"**Total IG comments (incl. replies):** {total_cwr}")
            lines.append("")
        lines.append("**Instagram Recent Posts:**")
        lines.append("")
        lines.append("| Date | Type | Likes | Comments (w/ replies) | Reach | Views | Saves | Shares | Caption |")
        lines.append("|------|------|-------|-----------------------|-------|-------|-------|--------|---------|")
        for p in ig_posts:
            raw_caption = (p.get("caption") or "").replace("\n", " ").replace("|", "/")
            caption = raw_caption[:45] + ("..." if len(raw_caption) > 45 else "")
            cwr = p.get("comments_with_replies", p.get("comments", 0))
            top_level = p.get("comments", 0)
            comment_display = f"{cwr}" if cwr == top_level else f"{cwr} ({top_level})"
            lines.append(f"| {p.get('date','')} | {p.get('type','')} | {_fmt_val(p.get('likes'))} | {comment_display} | {_fmt_val(p.get('reach'))} | {_fmt_val(p.get('views'))} | {_fmt_val(p.get('saves'))} | {_fmt_val(p.get('shares'))} | {caption} |")
        lines.append("")

    # =========================================================================
    # FACEBOOK — page-level insights (real numbers) + feed posts for context
    # =========================================================================
    lines.append("### Facebook")
    lines.append("")

    # Page-level insights (7d) — the real numbers
    if fb.get("page_reactions_7d"):
        lines.append("**Page Insights (7d) — all engagement including recommendation distribution:**")
        lines.append("")
        lines.append("| Metric | 7d Total |")
        lines.append("|--------|----------|")
        lines.append(f"| Reactions | {_fmt_val(fb.get('page_reactions_7d'))} |")
        rt = fb.get("page_reactions_by_type_7d", {})
        if rt:
            type_str = ", ".join(f"{k}: {v:,}" for k, v in sorted(rt.items(), key=lambda x: -x[1]) if v > 0)
            lines.append(f"| Breakdown | {type_str} |")
        lines.append(f"| Total Engagements | {_fmt_val(fb.get('page_engagements_7d'))} |")
        lines.append(f"| Video Views | {_fmt_val(fb.get('page_video_views_7d'))} |")
        organic = fb.get("page_video_views_organic_7d", 0)
        paid = fb.get("page_video_views_paid_7d", 0)
        total_vv = fb.get("page_video_views_7d", 0)
        if total_vv and (organic or paid):
            paid_pct = round((paid / total_vv) * 100, 1) if total_vv else 0
            lines.append(f"| Organic vs Paid | {_fmt_val(organic)} organic / {_fmt_val(paid)} paid ({paid_pct}% from paid ads) |")
        lines.append(f"| Post Impressions | {_fmt_val(fb.get('page_impressions_7d'))} |")
        lines.append("")

    # Daily breakdown with posts correlated — shows what was posted each day
    # alongside page-level metrics so you can see which content drives spikes
    daily = fb.get("page_daily_breakdown", [])
    fb_posts = fb.get("recent_posts", []) if not fb.get("error") else []
    if daily:
        # Build posts-by-date lookup
        posts_by_date = {}
        for p in fb_posts:
            d = p.get("date", "")
            if d not in posts_by_date:
                posts_by_date[d] = []
            post_type = "Reel" if p.get("is_reel") else "Post"
            msg = p.get("message", "").replace("\n", " ").replace("|", "/")[:45]
            posts_by_date[d].append(f"{post_type}: {msg}")

        lines.append("**Daily Performance + Content Posted:**")
        lines.append("")
        lines.append("| Date | Reactions | Engagements | Video Views | Impressions | Content Posted |")
        lines.append("|------|-----------|-------------|-------------|-------------|----------------|")
        for d in daily:
            date = d.get("date", "")
            posted = posts_by_date.get(date, [])
            content_str = "; ".join(posted) if posted else "—"
            # Truncate if too long
            if len(content_str) > 80:
                content_str = content_str[:77] + "..."
            lines.append(f"| {date} | {_fmt_val(d.get('reactions'))} | {_fmt_val(d.get('engagements'))} | {_fmt_val(d.get('video_views'))} | {_fmt_val(d.get('impressions'))} | {content_str} |")
        lines.append("")


    # =========================================================================
    # YOUTUBE
    # =========================================================================
    yt_videos = yt.get("top_videos", [])
    if yt_videos:
        lines.append("### YouTube")
        lines.append("")
        lines.append("| Video | Views |")
        lines.append("|-------|-------|")
        for v in yt_videos:
            lines.append(f"| {v['title']} | {v['views']:,} |")
        lines.append("")

    # Errors/notes
    errors = [(p, d.get("error")) for p, d in platforms.items() if d.get("error")]
    if errors:
        lines.append("**Data notes:**")
        for platform, err in errors:
            lines.append(f"- {platform}: {err}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Collecting VURT social media data...\n")
    data = collect_social_data()
    print(format_social_report(data))
    print(f"Cache saved to: {CACHE_FILE}")

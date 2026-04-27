#!/usr/bin/env python3
"""VURT Birds-Eye-View — pulls ALL data sources into a single state file."""

import sys, os, json, traceback
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/home/workspace/Skills/vurt-analytics/scripts")

STATE_FILE = "/home/workspace/Skills/vurt-birdseye/data/state.json"
ET = timezone(timedelta(hours=-4))


def safe_call(fn, label, *args, **kwargs):
    try:
        result = fn(*args, **kwargs)
        print(f"  [OK] {label}")
        return result
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")
        traceback.print_exc()
        return None


def pull_ga4():
    from ga4_client import run_report, extract_rows, fmt_num, fmt_pct, fmt_duration, wow_delta, get_property_timezone

    data = {}

    # Daily snapshot
    overview_metrics = [
        "activeUsers", "newUsers", "sessions", "averageSessionDuration",
        "screenPageViews", "engagedSessions", "userEngagementDuration",
        "sessionsPerUser", "engagementRate", "bounceRate"
    ]

    # Freshness check
    freshness_result = run_report(
        date_ranges=[
            {"startDate": "yesterday", "endDate": "yesterday", "name": "yesterday"},
            {"startDate": "8daysAgo", "endDate": "2daysAgo", "name": "baseline"}
        ],
        metrics=["engagedSessions", "activeUsers"]
    )
    freshness_rows = extract_rows(freshness_result)
    yd_check = next((r for r in freshness_rows if r.get("dateRange") == "yesterday"), {})
    baseline = next((r for r in freshness_rows if r.get("dateRange") == "baseline"), {})
    yd_engaged = float(yd_check.get("engagedSessions", "0"))
    baseline_engaged = float(baseline.get("engagedSessions", "0"))
    daily_avg = baseline_engaged / 7 if baseline_engaged > 0 else 1
    freshness_ratio = yd_engaged / daily_avg if daily_avg > 0 else 0
    yesterday_fresh = freshness_ratio >= 0.10

    if yesterday_fresh:
        latest_label, prev_label = "yesterday", "2daysAgo"
        days_offset = (1, 2)
    else:
        latest_label, prev_label = "2daysAgo", "3daysAgo"
        days_offset = (2, 3)

    result = run_report(
        date_ranges=[
            {"startDate": latest_label, "endDate": latest_label, "name": "latest"},
            {"startDate": prev_label, "endDate": prev_label, "name": "previous"}
        ],
        metrics=overview_metrics
    )
    rows = extract_rows(result)
    latest = next((r for r in rows if r.get("dateRange") == "latest"), {})
    previous = next((r for r in rows if r.get("dateRange") == "previous"), {})
    now = datetime.now()
    data["daily"] = {
        "latest_date": (now - timedelta(days=days_offset[0])).strftime("%Y-%m-%d"),
        "previous_date": (now - timedelta(days=days_offset[1])).strftime("%Y-%m-%d"),
        "yesterday_fresh": yesterday_fresh,
        "latest": latest,
        "previous": previous
    }

    # Weekly
    result = run_report(
        date_ranges=[
            {"startDate": "7daysAgo", "endDate": "yesterday", "name": "thisWeek"},
            {"startDate": "14daysAgo", "endDate": "8daysAgo", "name": "lastWeek"}
        ],
        metrics=overview_metrics
    )
    rows = extract_rows(result)
    data["weekly"] = {
        "this_week": next((r for r in rows if r.get("dateRange") == "thisWeek"), {}),
        "last_week": next((r for r in rows if r.get("dateRange") == "lastWeek"), {})
    }

    # Traffic sources — NO TRUNCATION
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration",
                 "screenPageViews", "engagedSessions", "bounceRate"],
        dimensions=["sessionDefaultChannelGroup"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=100
    )
    data["traffic_sources"] = extract_rows(result)

    # Landing pages — NO TRUNCATION
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["sessions", "engagementRate", "averageSessionDuration", "activeUsers", "bounceRate"],
        dimensions=["landingPagePlusQueryString"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=100
    )
    data["landing_pages"] = extract_rows(result)

    # Channel x Landing Page crossover — use landingPage (no query string) to avoid
    # fbclid/utm fragmentation that causes GA4 to threshold/drop rows
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["sessions", "bounceRate", "activeUsers", "engagementRate"],
        dimensions=["sessionDefaultChannelGroup", "landingPage"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=1000
    )
    data["channel_x_landing"] = extract_rows(result)

    # Geo
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration", "bounceRate"],
        dimensions=["country"],
        order_bys=[{"metric": {"metricName": "activeUsers"}, "desc": True}],
        limit=50
    )
    data["geo"] = extract_rows(result)

    # Platform breakdown
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "averageSessionDuration", "engagementRate",
                 "screenPageViews", "newUsers", "bounceRate"],
        dimensions=["platform"],
        order_bys=[{"metric": {"metricName": "activeUsers"}, "desc": True}]
    )
    data["platforms"] = extract_rows(result)

    # Device breakdown
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration", "bounceRate"],
        dimensions=["deviceCategory"],
        order_bys=[{"metric": {"metricName": "activeUsers"}, "desc": True}]
    )
    data["devices"] = extract_rows(result)

    # 14-day trend
    result = run_report(
        date_ranges=[{"startDate": "14daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "screenPageViews", "engagementRate",
                 "averageSessionDuration", "bounceRate"],
        dimensions=["date"],
        order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}]
    )
    data["trend_14d"] = extract_rows(result)

    # Retention
    result = run_report(
        date_ranges=[
            {"startDate": "7daysAgo", "endDate": "yesterday", "name": "thisWeek"},
            {"startDate": "14daysAgo", "endDate": "8daysAgo", "name": "lastWeek"}
        ],
        metrics=["activeUsers", "sessions", "averageSessionDuration", "engagementRate"],
        dimensions=["newVsReturning"]
    )
    data["retention"] = extract_rows(result)

    # Detail page bounce summary (aggregated)
    detail_pages = [r for r in data["landing_pages"] if "/detail/" in r.get("landingPagePlusQueryString", "")]
    homepage = [r for r in data["landing_pages"] if r.get("landingPagePlusQueryString", "") == "/"]
    data["detail_page_summary"] = {
        "total_detail_sessions": sum(int(r.get("sessions", 0)) for r in detail_pages),
        "avg_detail_bounce": sum(float(r.get("bounceRate", 0)) * int(r.get("sessions", 0)) for r in detail_pages) / max(sum(int(r.get("sessions", 0)) for r in detail_pages), 1),
        "homepage_sessions": int(homepage[0].get("sessions", 0)) if homepage else 0,
        "homepage_bounce": float(homepage[0].get("bounceRate", 0)) if homepage else 0,
        "top_detail_pages": sorted(detail_pages, key=lambda x: int(x.get("sessions", 0)), reverse=True)[:10]
    }

    # Paid social breakdown
    paid_social = [r for r in data["channel_x_landing"] if r.get("sessionDefaultChannelGroup") == "Paid Social"]
    data["paid_social_summary"] = {
        "total_sessions": sum(int(r.get("sessions", 0)) for r in paid_social),
        "total_users": sum(int(r.get("activeUsers", 0)) for r in paid_social),
        "landing_pages": sorted(paid_social, key=lambda x: int(x.get("sessions", 0)), reverse=True)[:20]
    }

    return data


def refresh_mux_title_map():
    """Rebuild the {playback_id -> show/episode title} cache from the public
    Enveu storefront API. Lets get_top_content show real names instead of opaque
    Mux IDs without depending on the dev team to wire videoTitle metadata."""
    from mux_title_resolver import build_map, save_map
    m = build_map(verbose=False)
    save_map(m)
    return {"count": len(m)}


def pull_mux():
    """Pull Mux Data API metrics (replaced NPAW on 2026-04-22)."""
    from mux_client import (get_top_content, get_daily_video_overview, get_device_breakdown,
                             get_cdn_breakdown, get_country_breakdown, get_isp_breakdown,
                             get_content_quality, get_daily_buffer_trend)
    data = {"source": "mux"}
    data["top_content"] = safe_call(get_top_content, "Mux top content", days=7, limit=30) or []
    data["daily_overview"] = safe_call(get_daily_video_overview, "Mux daily overview") or {}
    data["devices"] = safe_call(get_device_breakdown, "Mux devices", days=7) or []
    data["cdn"] = safe_call(get_cdn_breakdown, "Mux CDN", days=7) or []
    data["country"] = safe_call(get_country_breakdown, "Mux country", days=7) or []
    data["isp"] = safe_call(get_isp_breakdown, "Mux ISP/ASN", days=7) or []
    data["content_quality"] = safe_call(get_content_quality, "Mux quality", days=7, limit=30) or []
    data["buffer_trend"] = safe_call(get_daily_buffer_trend, "Mux buffer trend", days=7) or {}
    return data


def pull_meta_ig():
    import requests
    token = os.environ.get("VURT_META_ACCESS_TOKEN", "")
    ig_id = "17841479978232203"
    data = {"available": bool(token)}
    if not token:
        return data

    # Account info
    r = requests.get(f"https://graph.facebook.com/v19.0/{ig_id}",
                     params={"fields": "followers_count,media_count,biography", "access_token": token})
    if r.ok:
        data["account"] = r.json()

    # Recent media with engagement
    r = requests.get(f"https://graph.facebook.com/v19.0/{ig_id}/media",
                     params={"fields": "id,caption,timestamp,like_count,comments_count,media_type,permalink",
                             "limit": 20, "access_token": token})
    if r.ok:
        data["recent_posts"] = r.json().get("data", [])

    return data


def pull_meta_fb():
    import requests
    token = os.environ.get("VURT_META_ACCESS_TOKEN", "")
    page_id = "943789668811148"
    data = {"available": bool(token)}
    if not token:
        return data

    # Page info
    r = requests.get(f"https://graph.facebook.com/v19.0/{page_id}",
                     params={"fields": "name,fan_count,followers_count,talking_about_count", "access_token": token})
    if r.ok:
        data["page"] = r.json()

    # Recent posts with engagement
    r = requests.get(f"https://graph.facebook.com/v19.0/{page_id}/posts",
                     params={"fields": "message,permalink_url,created_time,shares,reactions.summary(total_count),comments.summary(total_count)",
                             "limit": 20, "access_token": token})
    if r.ok:
        posts = r.json().get("data", [])
        for p in posts:
            p["reactions_count"] = p.get("reactions", {}).get("summary", {}).get("total_count", 0)
            p["comments_count"] = p.get("comments", {}).get("summary", {}).get("total_count", 0)
            p["shares_count"] = p.get("shares", {}).get("count", 0)
            p.pop("reactions", None)
            p.pop("comments", None)
            p.pop("shares", None)
        data["recent_posts"] = posts

    return data


def pull_youtube():
    from youtube_client import format_youtube_report
    try:
        yt_md, yt_data = format_youtube_report()
        return yt_data or {}
    except:
        return {}


def pull_app_stores():
    from app_store_client import get_app_store_data
    try:
        return get_app_store_data()
    except:
        return {}


def pull_tiktok():
    """Pull TikTok @myvurt profile stats + recent + top performers."""
    sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
    try:
        from tiktok_profile import get_profile_summary
        return get_profile_summary(handle="myvurt", top_limit=10)
    except Exception:
        return {}


def main():
    print("VURT Birds-Eye-View Snapshot")
    print(f"Time: {datetime.now(ET).strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 50)

    state = {
        "last_updated": datetime.now(ET).isoformat(),
        "last_updated_human": datetime.now(ET).strftime("%B %d, %Y at %I:%M %p ET"),
        "gaps": {
            "meta_ads": "NOT AVAILABLE — page token lacks ad account permissions. Need user-level token with ads_read scope.",
            "fb_reel_comments": "Meta Graph API returns 0 for Reel comments despite visible engagement. Known API limitation."
        }
    }

    print("\n[1/7] Pulling GA4...")
    state["ga4"] = safe_call(pull_ga4, "GA4 full pull") or {}

    print("\n[2/7] Pulling Mux...")
    state["mux_title_map"] = safe_call(refresh_mux_title_map, "Mux title map refresh") or {}
    state["mux"] = safe_call(pull_mux, "Mux full pull") or {}

    print("\n[3/7] Pulling Instagram...")
    state["ig"] = safe_call(pull_meta_ig, "Instagram") or {}

    print("\n[4/7] Pulling Facebook...")
    state["fb"] = safe_call(pull_meta_fb, "Facebook") or {}

    print("\n[5/7] Pulling YouTube...")
    state["youtube"] = safe_call(pull_youtube, "YouTube") or {}

    print("\n[6/7] Pulling TikTok...")
    state["tiktok"] = safe_call(pull_tiktok, "TikTok") or {}

    print("\n[7/7] Pulling App Stores...")
    state["app_stores"] = safe_call(pull_app_stores, "App Stores") or {}

    # Write state
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

    print(f"\n{'=' * 50}")
    print(f"State written to: {STATE_FILE}")
    size_kb = os.path.getsize(STATE_FILE) / 1024
    print(f"Size: {size_kb:.1f} KB")

    # Print key numbers summary
    ga4 = state.get("ga4", {})
    daily = ga4.get("daily", {}).get("latest", {})
    sources = ga4.get("traffic_sources", [])
    detail = ga4.get("detail_page_summary", {})

    print(f"\n--- KEY NUMBERS ---")
    print(f"DAU: {daily.get('activeUsers', '?')}")
    print(f"Sessions: {daily.get('sessions', '?')}")
    print(f"Bounce: {float(daily.get('bounceRate', 0))*100:.1f}%")

    for s in sources[:5]:
        ch = s.get("sessionDefaultChannelGroup", "?")
        sess = s.get("sessions", "0")
        br = float(s.get("bounceRate", 0)) * 100
        print(f"  {ch}: {sess} sessions, {br:.0f}% bounce")

    print(f"Detail page sessions: {detail.get('total_detail_sessions', '?')}")
    print(f"Detail page avg bounce: {detail.get('avg_detail_bounce', 0)*100:.1f}%")
    print(f"Homepage sessions: {detail.get('homepage_sessions', '?')}")
    print(f"Homepage bounce: {detail.get('homepage_bounce', 0)*100:.1f}%")

    ig = state.get("ig", {})
    if ig.get("account"):
        print(f"IG followers: {ig['account'].get('followers_count', '?')}")
    fb = state.get("fb", {})
    if fb.get("page"):
        print(f"FB followers: {fb['page'].get('followers_count', '?')}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""VURT Daily Analytics Report — generates a markdown report with WoW comparisons and insights."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ga4_client import *
from insights_engine import generate_insights
from app_store_client import get_app_store_data
from email_renderer import markdown_to_html
from social_client import collect_social_data, format_social_report
from npaw_client import get_top_content, get_daily_video_overview, get_device_breakdown as get_npaw_device_breakdown, get_cdn_breakdown, get_country_breakdown, get_isp_breakdown, get_content_quality, format_npaw_report
from youtube_client import format_youtube_report
from datetime import datetime, timedelta

def get_overview():
    """Pull daily snapshot with automatic freshness detection.

    Tries yesterday first. If engaged sessions are <30% of the 7-day daily
    average, the data is still processing — falls back to 2daysAgo/3daysAgo.
    Returns (latest_row, previous_row, freshness_info_dict).
    """
    overview_metrics = [
        "activeUsers", "newUsers", "sessions", "averageSessionDuration",
        "screenPageViews", "engagedSessions", "userEngagementDuration",
        "sessionsPerUser", "engagementRate"
    ]

    # Pull yesterday + 7-day baseline in one call to check freshness
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
    # Baseline covers 7 days, so daily average = total / 7
    daily_avg_engaged = baseline_engaged / 7 if baseline_engaged > 0 else 1

    freshness_ratio = yd_engaged / daily_avg_engaged if daily_avg_engaged > 0 else 0
    yesterday_is_fresh = freshness_ratio >= 0.30

    if yesterday_is_fresh:
        # Yesterday's data looks complete — use it
        result = run_report(
            date_ranges=[
                {"startDate": "yesterday", "endDate": "yesterday", "name": "latest"},
                {"startDate": "2daysAgo", "endDate": "2daysAgo", "name": "previous"}
            ],
            metrics=overview_metrics
        )
        days_offset = (1, 2)
    else:
        # Yesterday still processing — fall back to finalized data
        result = run_report(
            date_ranges=[
                {"startDate": "2daysAgo", "endDate": "2daysAgo", "name": "latest"},
                {"startDate": "3daysAgo", "endDate": "3daysAgo", "name": "previous"}
            ],
            metrics=overview_metrics
        )
        days_offset = (2, 3)

    rows = extract_rows(result)
    latest = next((r for r in rows if r.get("dateRange") == "latest"), rows[0] if rows else {})
    previous = next((r for r in rows if r.get("dateRange") == "previous"), rows[1] if len(rows) > 1 else {})

    freshness_info = {
        "yesterday_fresh": yesterday_is_fresh,
        "freshness_ratio": freshness_ratio,
        "yd_engaged": yd_engaged,
        "daily_avg_engaged": daily_avg_engaged,
        "days_offset": days_offset,
    }
    return latest, previous, freshness_info

def get_weekly_overview():
    result = run_report(
        date_ranges=[
            {"startDate": "7daysAgo", "endDate": "yesterday", "name": "thisWeek"},
            {"startDate": "14daysAgo", "endDate": "8daysAgo", "name": "lastWeek"}
        ],
        metrics=[
            "activeUsers", "newUsers", "sessions", "averageSessionDuration",
            "screenPageViews", "engagedSessions", "userEngagementDuration",
            "sessionsPerUser", "engagementRate"
        ]
    )
    rows = extract_rows(result)
    this_week = next((r for r in rows if r.get("dateRange") == "thisWeek"), rows[0] if rows else {})
    last_week = next((r for r in rows if r.get("dateRange") == "lastWeek"), rows[1] if len(rows) > 1 else {})
    return this_week, last_week

def get_traffic_sources():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration",
                 "screenPageViews", "engagedSessions"],
        dimensions=["sessionDefaultChannelGroup"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=10
    )
    return extract_rows(result)

def get_top_pages():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["screenPageViews", "userEngagementDuration", "activeUsers"],
        dimensions=["unifiedScreenName"],
        order_bys=[{"metric": {"metricName": "screenPageViews"}, "desc": True}],
        limit=10
    )
    return extract_rows(result)

def get_platform_breakdown():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "averageSessionDuration", "engagementRate",
                 "screenPageViews", "newUsers"],
        dimensions=["platform"],
        order_bys=[{"metric": {"metricName": "activeUsers"}, "desc": True}]
    )
    return extract_rows(result)

def get_geo():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration"],
        dimensions=["country"],
        order_bys=[{"metric": {"metricName": "activeUsers"}, "desc": True}],
        limit=10
    )
    return extract_rows(result)

def get_daily_trend():
    result = run_report(
        date_ranges=[{"startDate": "14daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "screenPageViews", "engagementRate",
                 "averageSessionDuration"],
        dimensions=["date"],
        order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}]
    )
    return extract_rows(result)

def get_retention():
    result = run_report(
        date_ranges=[
            {"startDate": "7daysAgo", "endDate": "yesterday", "name": "thisWeek"},
            {"startDate": "14daysAgo", "endDate": "8daysAgo", "name": "lastWeek"}
        ],
        metrics=["activeUsers", "sessions", "averageSessionDuration", "engagementRate"],
        dimensions=["newVsReturning"]
    )
    return extract_rows(result)

def get_device_breakdown():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration"],
        dimensions=["deviceCategory"],
        order_bys=[{"metric": {"metricName": "activeUsers"}, "desc": True}]
    )
    return extract_rows(result)

def get_landing_pages():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["sessions", "engagementRate", "averageSessionDuration", "activeUsers"],
        dimensions=["landingPagePlusQueryString"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=10
    )
    return extract_rows(result)

def get_hour_of_day():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions"],
        dimensions=["hour"]
    )
    rows = extract_rows(result)
    rows.sort(key=lambda h: int(h.get("hour", 0)))
    return rows


def build_report():
    now = datetime.now()
    report_date = now.strftime("%B %d, %Y")

    lines = []
    lines.append(f"# VURT Daily Analytics Report")
    lines.append(f"**{report_date}**\n")

    # Collect all data for insights
    collected = {}

    metrics_display = [
        ("Daily Active Users", "activeUsers"),
        ("New Users", "newUsers"),
        ("Sessions", "sessions"),
        ("Avg Session Duration", "averageSessionDuration"),
        ("Page/Screen Views", "screenPageViews"),
        ("Engaged Sessions", "engagedSessions"),
        ("Total Engagement Time", "userEngagementDuration"),
        ("Sessions per User", "sessionsPerUser"),
        ("Engagement Rate", "engagementRate"),
    ]

    # --- Daily Snapshot with automatic freshness detection ---
    try:
        yd, db, freshness = get_overview()
        collected["yesterday"] = yd
        collected["day_before"] = db
        collected["freshness"] = freshness
        latest_offset, prev_offset = freshness["days_offset"]
        latest_date = (now - timedelta(days=latest_offset)).strftime("%A %m/%d")
        prev_date = (now - timedelta(days=prev_offset)).strftime("%A %m/%d")
        if freshness["yesterday_fresh"]:
            freshness_label = "latest data"
        else:
            freshness_label = "finalized data"
        lines.append(f"## Daily Snapshot ({freshness_label}: {latest_date} vs {prev_date})")
        lines.append("")
        lines.append(f"| Metric | {latest_date} | {prev_date} | Change |")
        lines.append("|--------|-----------|------------|--------|")
        for label, key in metrics_display:
            yv = yd.get(key, "0")
            dv = db.get(key, "0")
            if "Duration" in label or "Time" in label:
                fmt_y, fmt_d = fmt_duration(yv), fmt_duration(dv)
            elif "Rate" in label:
                fmt_y, fmt_d = fmt_pct(yv), fmt_pct(dv)
            elif "per User" in label.lower():
                fmt_y, fmt_d = f"{float(yv):.1f}", f"{float(dv):.1f}"
            else:
                fmt_y, fmt_d = fmt_num(yv), fmt_num(dv)
            delta = wow_delta(yv, dv)
            lines.append(f"| {label} | **{fmt_y}** | {fmt_d} | {delta} |")
        lines.append("")
    except Exception as e:
        lines.append(f"*Yesterday snapshot unavailable: {e}*\n")

    # --- Weekly Overview ---
    try:
        tw, lw = get_weekly_overview()
        collected["this_week"] = tw
        collected["last_week"] = lw
        lines.append("## 7-Day Overview (WoW)")
        lines.append("")
        lines.append("| Metric | This Week | Last Week | Change |")
        lines.append("|--------|-----------|-----------|--------|")
        for label, key in metrics_display:
            tv = tw.get(key, "0")
            lv = lw.get(key, "0")
            if "Duration" in label or "Time" in label:
                fmt_t, fmt_l = fmt_duration(tv), fmt_duration(lv)
            elif "Rate" in label:
                fmt_t, fmt_l = fmt_pct(tv), fmt_pct(lv)
            elif "per User" in label.lower():
                fmt_t, fmt_l = f"{float(tv):.1f}", f"{float(lv):.1f}"
            else:
                fmt_t, fmt_l = fmt_num(tv), fmt_num(lv)
            delta = wow_delta(tv, lv)
            lines.append(f"| {label} | **{fmt_t}** | {fmt_l} | {delta} |")
        lines.append("")
    except Exception as e:
        lines.append(f"*Weekly overview unavailable: {e}*\n")

    # --- Platform Breakdown ---
    try:
        platforms = get_platform_breakdown()
        collected["platforms"] = platforms
        if platforms:
            lines.append("## Platform Breakdown (7d)")
            lines.append("")
            lines.append("| Platform | Users | Sessions | Avg Duration | Engagement Rate |")
            lines.append("|----------|-------|----------|-------------|-----------------|")
            for p in platforms:
                lines.append(f"| {p.get('platform','?')} | {fmt_num(p.get('activeUsers','0'))} | {fmt_num(p.get('sessions','0'))} | {fmt_duration(p.get('averageSessionDuration','0'))} | {fmt_pct(p.get('engagementRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Platform breakdown unavailable: {e}*\n")

    # --- Traffic Sources ---
    try:
        sources = get_traffic_sources()
        collected["sources"] = sources
        if sources:
            lines.append("## Traffic Sources (7d)")
            lines.append("")
            lines.append("| Channel | Users | Sessions | Avg Duration | Engagement Rate |")
            lines.append("|---------|-------|----------|-------------|-----------------|")
            for s in sources:
                lines.append(f"| {s.get('sessionDefaultChannelGroup','?')} | {fmt_num(s.get('activeUsers','0'))} | {fmt_num(s.get('sessions','0'))} | {fmt_duration(s.get('averageSessionDuration','0'))} | {fmt_pct(s.get('engagementRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Traffic sources unavailable: {e}*\n")

    # --- Retention ---
    try:
        retention = get_retention()
        collected["retention"] = retention
        if retention:
            tw_rows = [r for r in retention if r.get("dateRange") == "thisWeek"]
            lines.append("## New vs Returning Users (7d)")
            lines.append("")
            lines.append("| Segment | Users | Sessions | Avg Duration | Engagement Rate |")
            lines.append("|---------|-------|----------|-------------|-----------------|")
            for r in tw_rows:
                seg = r.get("newVsReturning", "?").capitalize()
                lines.append(f"| {seg} | {fmt_num(r.get('activeUsers','0'))} | {fmt_num(r.get('sessions','0'))} | {fmt_duration(r.get('averageSessionDuration','0'))} | {fmt_pct(r.get('engagementRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Retention data unavailable: {e}*\n")

    # --- Top Content ---
    try:
        pages = get_top_pages()
        collected["pages"] = pages
        if pages:
            lines.append("## Top Content (7d)")
            lines.append("")
            lines.append("| Screen/Page | Views | Users | Engagement Time |")
            lines.append("|-------------|-------|-------|-----------------|")
            for p in pages:
                screen = p.get('unifiedScreenName','?').replace('|', '/').strip()[:50]
                lines.append(f"| {screen} | {fmt_num(p.get('screenPageViews','0'))} | {fmt_num(p.get('activeUsers','0'))} | {fmt_duration(p.get('userEngagementDuration','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Top content unavailable: {e}*\n")

    # --- Landing Pages ---
    try:
        landing = get_landing_pages()
        collected["landing"] = landing
        if landing:
            lines.append("## Top Landing Pages (7d)")
            lines.append("")
            lines.append("| Landing Page | Sessions | Avg Duration | Engagement Rate |")
            lines.append("|-------------|----------|-------------|-----------------|")
            for l in landing:
                path = l.get("landingPagePlusQueryString", "?").replace('|', '/')
                if len(path) > 60:
                    path = path[:57] + "..."
                lines.append(f"| {path} | {fmt_num(l.get('sessions','0'))} | {fmt_duration(l.get('averageSessionDuration','0'))} | {fmt_pct(l.get('engagementRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Landing page data unavailable: {e}*\n")

    # --- Geography ---
    try:
        geo = get_geo()
        collected["geo"] = geo
        if geo:
            lines.append("## Top Countries (7d)")
            lines.append("")
            lines.append("| Country | Users | Sessions | Avg Duration | Engagement Rate |")
            lines.append("|---------|-------|----------|-------------|-----------------|")
            for g in geo:
                lines.append(f"| {g.get('country','?')} | {fmt_num(g.get('activeUsers','0'))} | {fmt_num(g.get('sessions','0'))} | {fmt_duration(g.get('averageSessionDuration','0'))} | {fmt_pct(g.get('engagementRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Geo data unavailable: {e}*\n")

    # --- 14-Day DAU Trend ---
    try:
        trend = get_daily_trend()
        collected["trend"] = trend
        if trend:
            lines.append("## 14-Day DAU Trend")
            lines.append("")
            lines.append("| Date | DAU | Sessions | Views | Eng Rate |")
            lines.append("|------|-----|----------|-------|----------|")
            for t in trend:
                d = t.get("date", "")
                date_fmt = f"{d[4:6]}/{d[6:8]}" if len(d) == 8 else d
                lines.append(f"| {date_fmt} | {fmt_num(t.get('activeUsers','0'))} | {fmt_num(t.get('sessions','0'))} | {fmt_num(t.get('screenPageViews','0'))} | {fmt_pct(t.get('engagementRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Trend data unavailable: {e}*\n")

    # --- Peak Hours ---
    try:
        hours = get_hour_of_day()
        collected["hours"] = hours
        if hours:
            lines.append("## Hourly Activity (7d)")
            lines.append("")
            lines.append("| Hour | Users | Sessions |")
            lines.append("|------|-------|----------|")
            for h in hours:
                hr = int(h.get("hour", 0))
                ampm = "AM" if hr < 12 else "PM"
                hr12 = hr if hr <= 12 else hr - 12
                if hr12 == 0: hr12 = 12
                lines.append(f"| {hr12}{ampm} | {fmt_num(h.get('activeUsers','0'))} | {fmt_num(h.get('sessions','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Hourly data unavailable: {e}*\n")

    # --- Device breakdown ---
    try:
        devices = get_device_breakdown()
        collected["devices"] = devices
    except:
        pass

    # --- Social Media ---
    try:
        social_data = collect_social_data()
        collected["social"] = social_data
        social_md = format_social_report(social_data)
        lines.extend(social_md.splitlines())
        lines.append("")
    except Exception as e:
        lines.append(f"*Social media data unavailable: {e}*\n")

    # --- YouTube ---
    try:
        yt_md, yt_data = format_youtube_report()
        if yt_md:
            collected["youtube"] = yt_data
            lines.extend(yt_md.splitlines())
            lines.append("")
    except Exception as e:
        lines.append(f"*YouTube data unavailable: {e}*\n")

    # --- NPAW Video Performance ---
    try:
        npaw_top = get_top_content(days=7, limit=20)
        npaw_daily = get_daily_video_overview()
        npaw_devices = get_npaw_device_breakdown(days=7)
        npaw_cdn = get_cdn_breakdown(days=7)
        npaw_country = get_country_breakdown(days=7)
        npaw_isp = get_isp_breakdown(days=7)
        npaw_content_quality = get_content_quality(days=7, limit=20)
        collected["npaw_top"] = npaw_top
        collected["npaw_daily"] = npaw_daily
        npaw_md = format_npaw_report(npaw_top, npaw_daily, npaw_devices, npaw_cdn, npaw_country, npaw_isp, npaw_content_quality)
        lines.extend(npaw_md.splitlines())
        lines.append("")
    except Exception as e:
        lines.append(f"*Video performance data unavailable: {e}*\n")

    # --- App Store Ratings ---
    try:
        collected["app_stores"] = get_app_store_data()
    except:
        pass

    # --- GA4 Property Timezone ---
    try:
        collected["timezone"] = get_property_timezone()
    except:
        collected["timezone"] = "UTC"

    # --- INSIGHTS ---
    try:
        insights = generate_insights(collected)
        if insights:
            lines.append("## Insights & Actions")
            lines.append("")
            for i, insight in enumerate(insights, 1):
                lines.append(f"{i}. {insight}")
                lines.append("")
    except Exception as e:
        lines.append(f"*Insights unavailable: {e}*\n")

    lines.append("---")
    lines.append("### Methodology")
    lines.append("- **Data source:** Google Analytics 4 (Property ID 518738893, myvurt.com)")
    lines.append("- **Engagement Rate:** % of sessions lasting >10s, with 2+ page views, or a key event (GA4 standard definition)")
    lines.append("- **Daily Snapshot freshness:** Automatically uses yesterday's data when GA4 processing is complete (engaged sessions >= 30% of 7-day avg). Falls back to 2-days-ago when data is still processing.")
    lines.append("- **Social media data:** Instagram via Meta Graph API (IG Business Account 17841479978232203), YouTube/TikTok/X via public profile scraping")
    lines.append("- **All numbers are pulled directly from GA4 APIs** — no manual adjustments or estimates except where explicitly labeled as projections")
    lines.append("- **Ad revenue projections** use verified AVOD CPM benchmarks ($15-25, Adwave 2025) and are scaling models, not forecasts")
    lines.append("- **Health Score** is a weighted composite: Growth (25), Engagement (25), Retention (25), Traffic Quality (25) — formulas shown inline")
    lines.append("- **'(not set)' entries** indicate GA4 tracking gaps where screen names aren't being passed in analytics events")
    lines.append("")
    lines.append("*Generated by Zo · VURT Analytics Skill*")

    return "\n".join(lines)

if __name__ == "__main__":
    report = build_report()
    print(report)

    report_dir = "/home/workspace/Documents/analytics-reports"
    os.makedirs(report_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{report_dir}/vurt-daily-{date_str}.md"
    with open(filepath, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {filepath}")

    # Generate HTML email version
    html = markdown_to_html(report)
    html_path = f"{report_dir}/vurt-daily-{date_str}.html"
    with open(html_path, "w") as f:
        f.write(html)
    print(f"HTML email saved to: {html_path}")

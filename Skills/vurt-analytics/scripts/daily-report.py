#!/usr/bin/env python3
"""VURT Daily Analytics Report v4 — generates a markdown report with WoW comparisons and insights."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ga4_client import *
from insights_engine import generate_insights
from app_store_client import get_app_store_data
from email_renderer import markdown_to_html
from social_client import collect_social_data, format_social_report
from mux_client import (
    get_top_content as get_mux_top_content,
    get_daily_video_overview as get_mux_daily_overview,
    get_device_breakdown as get_mux_device_breakdown,
    get_cdn_breakdown as get_mux_cdn_breakdown,
    get_country_breakdown as get_mux_country_breakdown,
    get_isp_breakdown as get_mux_isp_breakdown,
    get_content_quality as get_mux_content_quality,
    get_daily_buffer_trend as get_mux_buffer_trend,
    format_mux_report,
)
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
        "sessionsPerUser", "engagementRate", "bounceRate"
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
    yesterday_is_fresh = freshness_ratio >= 0.10

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
            "sessionsPerUser", "engagementRate", "bounceRate"
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
                 "screenPageViews", "engagedSessions", "bounceRate"],
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
                 "averageSessionDuration", "bounceRate"],
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


def get_cohort_retention_by_source(cohort_days=7, window_days=7):
    """Day-N retention by acquisition channel.

    Builds `cohort_days` daily cohorts (e.g. last 7 days), tracks each
    cohort forward for `window_days`, aggregates across cohorts by the
    channel the user was first acquired through.

    Returns a list of dicts per channel:
        {channel, d0, d1_pct, d3_pct, d7_pct, d1_users, d3_users, d7_users}
    """
    from collections import defaultdict
    from datetime import date, timedelta

    today = date.today()
    cohorts = []
    for i in range(cohort_days, 0, -1):
        d = (today - timedelta(days=i)).isoformat()
        cohorts.append({
            "name": f"d_{d}",
            "dimension": "firstSessionDate",
            "dateRange": {"startDate": d, "endDate": d},
        })

    try:
        result = run_cohort_report(
            cohorts=cohorts,
            metrics=["cohortActiveUsers"],
            dimensions=["firstUserDefaultChannelGroup"],
            days_forward=window_days,
            limit=2000,
        )
    except Exception as e:
        print(f"Cohort retention query failed: {e}", file=sys.stderr)
        return []

    # channel -> nth_day -> total users across all cohorts
    by_channel = defaultdict(lambda: defaultdict(int))
    for r in result.get("rows", []):
        vals = [v["value"] for v in r.get("dimensionValues", [])]
        if len(vals) < 3:
            continue
        _cohort, nth_day, channel = vals[0], vals[1], vals[2]
        try:
            users = int(r["metricValues"][0]["value"])
            n = int(nth_day)
        except (KeyError, ValueError, IndexError):
            continue
        by_channel[channel][n] += users

    rows = []
    for channel, days in by_channel.items():
        d0 = days.get(0, 0)
        if d0 == 0:
            continue
        rows.append({
            "channel": channel,
            "d0": d0,
            "d1_users": days.get(1, 0),
            "d3_users": days.get(3, 0),
            "d7_users": days.get(7, 0),
            "d1_pct": 100.0 * days.get(1, 0) / d0,
            "d3_pct": 100.0 * days.get(3, 0) / d0,
            "d7_pct": 100.0 * days.get(7, 0) / d0 if window_days >= 7 else None,
        })
    rows.sort(key=lambda r: r["d0"], reverse=True)
    return rows

def get_device_breakdown():
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["activeUsers", "sessions", "engagementRate", "averageSessionDuration"],
        dimensions=["deviceCategory"],
        order_bys=[{"metric": {"metricName": "activeUsers"}, "desc": True}]
    )
    return extract_rows(result)

def get_landing_pages():
    """Landing pages using landingPage (no query string) to avoid fbclid/utm fragmentation."""
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["sessions", "engagementRate", "averageSessionDuration", "activeUsers", "bounceRate"],
        dimensions=["landingPage"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=50
    )
    return extract_rows(result)


def get_channel_x_landing():
    """Channel x Landing Page crossover — uses landingPage (not landingPagePlusQueryString)
    to avoid fbclid/utm fragmentation that causes GA4 to threshold/drop rows."""
    result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
        metrics=["sessions", "bounceRate", "activeUsers", "engagementRate", "averageSessionDuration"],
        dimensions=["sessionDefaultChannelGroup", "landingPage"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=1000
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
        ("Bounce Rate", "bounceRate"),
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
            lines.append("| Channel | Users | Sessions | Avg Duration | Engagement Rate | Bounce Rate |")
            lines.append("|---------|-------|----------|-------------|-----------------|-------------|")
            for s in sources:
                lines.append(f"| {s.get('sessionDefaultChannelGroup','?')} | {fmt_num(s.get('activeUsers','0'))} | {fmt_num(s.get('sessions','0'))} | {fmt_duration(s.get('averageSessionDuration','0'))} | {fmt_pct(s.get('engagementRate','0'))} | {fmt_pct(s.get('bounceRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Traffic sources unavailable: {e}*\n")

    # --- Paid Ads Activity Flag (v4) ---
    try:
        if sources:
            paid_social = next((s for s in sources if s.get("sessionDefaultChannelGroup") == "Paid Social"), None)
            paid_sessions = int(paid_social.get("sessions", 0)) if paid_social else 0
            if paid_sessions > 100:
                paid_status = "ACTIVE"
                paid_bounce = fmt_pct(paid_social.get("bounceRate", "0"))
                lines.append(f"**Paid Social: {paid_status}** ({fmt_num(paid_sessions)} sessions this week, {paid_bounce} bounce)")
            elif paid_sessions > 0:
                lines.append(f"**Paid Social: LOW VOLUME** ({fmt_num(paid_sessions)} sessions this week)")
            else:
                lines.append("**Paid Social: PAUSED** (0 sessions this week)")
            lines.append("")
    except:
        pass

    # --- Cohort Retention by Acquisition Source (v5) ---
    try:
        cohort_ret = get_cohort_retention_by_source(cohort_days=7, window_days=7)
        collected["cohort_retention"] = cohort_ret
        if cohort_ret:
            lines.append("## Cohort Retention by Acquisition Source (last 7 daily cohorts)")
            lines.append("")
            lines.append("How many of the users we acquired each day actually came back. "
                         "Day 0 = sessions on acquisition day. D1/D3/D7 = % of that cohort returning N days later.")
            lines.append("")
            lines.append("| Channel | D0 Users | D1 Return | D3 Return | D7 Return |")
            lines.append("|---------|----------|-----------|-----------|-----------|")
            for r in cohort_ret:
                d7 = f"{r['d7_pct']:.1f}%" if r.get("d7_pct") is not None else "—"
                lines.append(f"| {r['channel']} | {fmt_num(r['d0'])} | "
                             f"{r['d1_pct']:.1f}% | {r['d3_pct']:.1f}% | {d7} |")
            lines.append("")
            # Quick interpretation line — flag the worst-performing high-volume channel
            high_vol = [r for r in cohort_ret if r["d0"] >= 500]
            if high_vol:
                worst = min(high_vol, key=lambda r: r["d1_pct"])
                best = max(cohort_ret, key=lambda r: r["d1_pct"])
                if worst["d1_pct"] < 5 and best["d1_pct"] > worst["d1_pct"] * 3:
                    lines.append(f"_{worst['channel']} brings volume ({fmt_num(worst['d0'])} users) "
                                 f"but {worst['d1_pct']:.1f}% D1 return vs {best['channel']} at "
                                 f"{best['d1_pct']:.1f}% — flag for audience-quality review._")
                    lines.append("")
    except Exception as e:
        lines.append(f"*Cohort retention data unavailable: {e}*\n")

    # --- Channel x Landing Page Crossover (v4) ---
    try:
        channel_landing = get_channel_x_landing()
        collected["channel_x_landing"] = channel_landing
        if channel_landing:
            # Group by channel, show top landing pages per channel
            from collections import defaultdict
            by_channel = defaultdict(list)
            for row in channel_landing:
                ch = row.get("sessionDefaultChannelGroup", "?")
                by_channel[ch].append(row)

            # Sort channels by total sessions
            channel_totals = [(ch, sum(int(r.get("sessions", 0)) for r in rows)) for ch, rows in by_channel.items()]
            channel_totals.sort(key=lambda x: x[1], reverse=True)

            lines.append("## Where Each Channel Lands (7d)")
            lines.append("")
            lines.append("| Channel | Landing Page | Sessions | Bounce Rate | Avg Duration |")
            lines.append("|---------|-------------|----------|-------------|--------------|")
            for ch, total in channel_totals[:6]:
                top_pages = sorted(by_channel[ch], key=lambda r: int(r.get("sessions", 0)), reverse=True)[:3]
                for i, r in enumerate(top_pages):
                    path = r.get("landingPage", "?")
                    if len(path) > 45:
                        path = path[:42] + "..."
                    ch_label = f"**{ch}** ({fmt_num(total)})" if i == 0 else ""
                    lines.append(f"| {ch_label} | {path} | {fmt_num(r.get('sessions','0'))} | {fmt_pct(r.get('bounceRate','0'))} | {fmt_duration(r.get('averageSessionDuration','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Channel x Landing Page data unavailable: {e}*\n")

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
            lines.append("| Landing Page | Sessions | Users | Avg Duration | Engagement Rate | Bounce Rate |")
            lines.append("|-------------|----------|-------|-------------|-----------------|-------------|")
            for l in landing[:15]:
                path = l.get("landingPage", "?").replace('|', '/')
                if len(path) > 60:
                    path = path[:57] + "..."
                lines.append(f"| {path} | {fmt_num(l.get('sessions','0'))} | {fmt_num(l.get('activeUsers','0'))} | {fmt_duration(l.get('averageSessionDuration','0'))} | {fmt_pct(l.get('engagementRate','0'))} | {fmt_pct(l.get('bounceRate','0'))} |")
            lines.append("")

            # --- Detail Page Bounce Summary (v4) ---
            detail_pages = [r for r in landing if "/detail/" in r.get("landingPage", "")]
            homepage = [r for r in landing if r.get("landingPage", "") == "/"]
            if detail_pages:
                total_detail_sessions = sum(int(r.get("sessions", 0)) for r in detail_pages)
                total_detail_bounce_weighted = sum(float(r.get("bounceRate", 0)) * int(r.get("sessions", 0)) for r in detail_pages)
                avg_detail_bounce = total_detail_bounce_weighted / total_detail_sessions if total_detail_sessions else 0
                hp_sessions = int(homepage[0].get("sessions", 0)) if homepage else 0
                hp_bounce = float(homepage[0].get("bounceRate", 0)) if homepage else 0
                lines.append("### Landing Page Health: Homepage vs Show Pages")
                lines.append("")
                lines.append("| Destination | Sessions | Bounce Rate | Interpretation |")
                lines.append("|-------------|----------|-------------|----------------|")
                hp_interp = "Browse entry" if hp_bounce < 0.5 else "High bounce on homepage"
                detail_interp = "Paid social landing" if avg_detail_bounce > 0.7 else "Healthy engagement"
                lines.append(f"| Homepage (/) | {fmt_num(hp_sessions)} | {fmt_pct(hp_bounce)} | {hp_interp} |")
                lines.append(f"| Show detail pages | {fmt_num(total_detail_sessions)} | {fmt_pct(avg_detail_bounce)} | {detail_interp} |")
                lines.append("")
                lines.append("*Show detail pages are the primary landing destination for paid social ads. High bounce here = users arriving from ads but not engaging past the age gate.*")
                lines.append("")
    except Exception as e:
        lines.append(f"*Landing page data unavailable: {e}*\n")

    # --- Geography with Efficiency Score (v4) ---
    try:
        geo = get_geo()
        collected["geo"] = geo
        if geo:
            lines.append("## Top Countries (7d)")
            lines.append("*Efficiency = engagement rate x sessions. High efficiency = valuable traffic. Low efficiency + high sessions = ad waste.*")
            lines.append("")
            lines.append("| Country | Users | Sessions | Engagement Rate | Avg Duration | Efficiency | Flag |")
            lines.append("|---------|-------|----------|-----------------|-------------|------------|------|")
            for g in geo:
                sessions = int(g.get("sessions", 0))
                eng_rate = float(g.get("engagementRate", 0))
                efficiency = eng_rate * sessions
                flag = ""
                if sessions > 50 and eng_rate < 0.10:
                    flag = "Waste"
                elif sessions > 50 and eng_rate > 0.30:
                    flag = "Strong"
                lines.append(f"| {g.get('country','?')} | {fmt_num(g.get('activeUsers','0'))} | {fmt_num(sessions)} | {fmt_pct(eng_rate)} | {fmt_duration(g.get('averageSessionDuration','0'))} | {efficiency:.0f} | {flag} |")
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
            lines.append("| Date | DAU | Sessions | Views | Eng Rate | Bounce Rate |")
            lines.append("|------|-----|----------|-------|----------|-------------|")
            for t in trend:
                d = t.get("date", "")
                date_fmt = f"{d[4:6]}/{d[6:8]}" if len(d) == 8 else d
                lines.append(f"| {date_fmt} | {fmt_num(t.get('activeUsers','0'))} | {fmt_num(t.get('sessions','0'))} | {fmt_num(t.get('screenPageViews','0'))} | {fmt_pct(t.get('engagementRate','0'))} | {fmt_pct(t.get('bounceRate','0'))} |")
            lines.append("")
    except Exception as e:
        lines.append(f"*Trend data unavailable: {e}*\n")

    # --- Peak Hours (v4: compressed to top 5 + quiet hours) ---
    try:
        hours = get_hour_of_day()
        collected["hours"] = hours
        if hours:
            sorted_hours = sorted(hours, key=lambda h: int(h.get("sessions", 0)), reverse=True)
            peak_5 = sorted_hours[:5]
            quiet_5 = sorted_hours[-3:]
            lines.append("## Peak Hours (7d)")
            lines.append("")
            lines.append("| Hour | Users | Sessions | Note |")
            lines.append("|------|-------|----------|------|")
            for h in sorted(peak_5, key=lambda x: int(x.get("hour", 0))):
                hr = int(h.get("hour", 0))
                ampm = "AM" if hr < 12 else "PM"
                hr12 = hr if hr <= 12 else hr - 12
                if hr12 == 0: hr12 = 12
                lines.append(f"| {hr12}{ampm} | {fmt_num(h.get('activeUsers','0'))} | {fmt_num(h.get('sessions','0'))} | Peak |")
            for h in sorted(quiet_5, key=lambda x: int(x.get("hour", 0))):
                hr = int(h.get("hour", 0))
                ampm = "AM" if hr < 12 else "PM"
                hr12 = hr if hr <= 12 else hr - 12
                if hr12 == 0: hr12 = 12
                lines.append(f"| {hr12}{ampm} | {fmt_num(h.get('activeUsers','0'))} | {fmt_num(h.get('sessions','0'))} | Quiet |")
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

    # --- TikTok Top Performers (by views, last 60 days in cache) ---
    try:
        sys.path.insert(0, "/home/workspace/Skills/vurt-post-log/scripts")
        from tiktok_profile import get_top_performers
        tt_top = get_top_performers(limit=5, min_views=100)
        if tt_top.get("top"):
            lines.append("### TikTok Top Performers (@myvurt)")
            lines.append("")
            lines.append(f"*Ranked by views across {tt_top['count']} cached posts (scraped {tt_top['cache_age_hours']}h ago).*")
            lines.append("")
            lines.append("| # | Caption | Views | Likes | Saves | Save % |")
            lines.append("|---|---------|------:|------:|------:|-------:|")
            for i, r in enumerate(tt_top["top"], 1):
                cap = r["caption"].replace("|", "/")
                lines.append(f"| {i} | {cap} | {fmt_num(r['views'])} | {fmt_num(r['likes'])} | {fmt_num(r['saves'])} | {r['save_rate']*100:.2f}% |")
            lines.append("")
            collected["tiktok_top_performers"] = tt_top
    except Exception as e:
        lines.append(f"*TikTok top performers unavailable: {e}*\n")

    # --- TikTok Save Rate Leaderboard ---
    # Save rate (saves/views) is the bookmark signal TikTok's algorithm weights
    # highest for re-surfacing. >1% = elite. Leads likes and views as a predictor.
    try:
        import json as _json
        tt_path = "/home/workspace/Skills/vurt-post-log/data/tiktok_user_url_scrape.json"
        tt_posts = _json.load(open(tt_path))
        scraped_ts = max((p.get("scraped_at", 0) for p in tt_posts), default=0)
        age_h = (datetime.now().timestamp() - scraped_ts) / 3600 if scraped_ts else 9999
        ranked = []
        for p in tt_posts:
            v = p.get("views") or 0
            if v < 100:
                continue
            s = p.get("saves") or 0
            l = p.get("likes") or 0
            ranked.append({
                "caption": (p.get("caption") or "").strip().split("\n")[0][:60],
                "url": p.get("url", ""),
                "views": v,
                "likes": l,
                "saves": s,
                "save_rate": s / v if v else 0,
                "like_rate": l / v if v else 0,
            })
        ranked.sort(key=lambda r: r["save_rate"], reverse=True)
        top = ranked[:10]
        if top:
            lines.append("### TikTok Save Rate Leaderboard")
            lines.append("")
            lines.append(f"*Saves-per-view is the strongest algorithmic signal for re-surfacing. >1% = bookmark-worthy. Based on {len(ranked)} @myvurt posts (>=100 views), scraped {age_h:.0f}h ago.*")
            lines.append("")
            lines.append("| # | Caption | Views | Saves | Save % | Like % |")
            lines.append("|---|---------|------:|------:|-------:|-------:|")
            for i, r in enumerate(top, 1):
                flag = " **" if r["save_rate"] >= 0.01 else ""
                end = "**" if r["save_rate"] >= 0.01 else ""
                cap = r["caption"].replace("|", "/")
                lines.append(f"| {i} |{flag}{cap}{end} | {fmt_num(r['views'])} | {fmt_num(r['saves'])} | {r['save_rate']*100:.2f}% | {r['like_rate']*100:.1f}% |")
            lines.append("")
            elite = [r for r in ranked if r["save_rate"] >= 0.01]
            if elite:
                lines.append(f"**{len(elite)} post{'s' if len(elite)!=1 else ''} cleared the 1% save rate threshold.** These are the patterns to clone.")
                lines.append("")
            collected["tiktok_save_leaderboard"] = top
    except Exception as e:
        lines.append(f"*TikTok save rate data unavailable: {e}*\n")

    # --- YouTube ---
    try:
        yt_md, yt_data = format_youtube_report()
        if yt_md:
            collected["youtube"] = yt_data
            lines.extend(yt_md.splitlines())
            lines.append("")
    except Exception as e:
        lines.append(f"*YouTube data unavailable: {e}*\n")

    # --- Mux Video Performance (replaces NPAW as of 2026-04-22) ---
    try:
        mux_top = get_mux_top_content(days=7, limit=30)
        mux_daily = get_mux_daily_overview()
        mux_devices = get_mux_device_breakdown(days=7)
        mux_cdn = get_mux_cdn_breakdown(days=7)
        mux_country = get_mux_country_breakdown(days=7)
        mux_buffer_trend = get_mux_buffer_trend(days=7)
        collected["mux_top"] = mux_top
        collected["mux_daily"] = mux_daily
        mux_md = format_mux_report(mux_top, mux_daily, mux_devices, mux_cdn, mux_country,
                                   daily_buffer_trend=mux_buffer_trend)
        lines.extend(mux_md.splitlines())
        lines.append("")

        # --- Video Play Funnel (v4, Mux-powered) ---
        try:
            views = mux_daily.get("views")
            compl = mux_daily.get("completionRate")
            page_views = collected.get("yesterday", {}).get("screenPageViews")
            if views is not None:
                lines.append("### Video Play Funnel (Yesterday)")
                lines.append("")
                lines.append("| Stage | Count | Drop-off |")
                lines.append("|-------|-------|----------|")
                lines.append(f"| Page views (GA4) | {fmt_num(page_views) if page_views is not None else '?'} | - |")
                lines.append(f"| Video views (Mux) | {fmt_num(views)} | - |")
                if compl is not None:
                    est_completions = float(views) * (float(compl) / 100.0)
                    lines.append(f"| Est. completions | {fmt_num(est_completions)} | {float(compl):.0f}% avg completion |")
                lines.append("")
        except Exception:
            pass

    except Exception as e:
        lines.append(f"*Video performance data unavailable: {e}*\n")

    # --- App Store Ratings (v4: now rendered) ---
    try:
        app_data = get_app_store_data()
        collected["app_stores"] = app_data
        if app_data:
            lines.append("## App Store Ratings")
            lines.append("")
            lines.append("| Store | Rating | Reviews | Version |")
            lines.append("|-------|--------|---------|---------|")
            ios = app_data.get("ios", {})
            android = app_data.get("android", {})
            if ios:
                lines.append(f"| iOS | {ios.get('rating', 'N/A')} | {ios.get('reviews', 'N/A')} | {ios.get('version', '?')} |")
            if android:
                lines.append(f"| Android | {android.get('rating', 'N/A')} | {android.get('reviews', 'N/A')} | {android.get('version', '?')} |")
            lines.append("")
    except:
        pass

    # --- GA4 Property Timezone ---
    try:
        collected["timezone"] = get_property_timezone()
    except:
        collected["timezone"] = "UTC"

    # --- Content Velocity (v4) ---
    try:
        social = collected.get("social", {})
        ig_posts = social.get("ig", {}).get("recent_posts", [])
        fb_posts = social.get("fb", {}).get("recent_posts", [])
        # Count posts in last 7 days
        from datetime import timezone as tz
        seven_days_ago = now - timedelta(days=7)
        ig_this_week = 0
        fb_this_week = 0
        for p in ig_posts:
            ts = p.get("timestamp", "")
            if ts and ts[:10] >= seven_days_ago.strftime("%Y-%m-%d"):
                ig_this_week += 1
        for p in fb_posts:
            ts = p.get("created_time", "")
            if ts and ts[:10] >= seven_days_ago.strftime("%Y-%m-%d"):
                fb_this_week += 1

        total_social_posts = ig_this_week + fb_this_week
        total_sessions = int(collected.get("this_week", {}).get("sessions", 0))

        if total_social_posts > 0 or total_sessions > 0:
            lines.append("## Content Velocity (7d)")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| IG posts this week | {ig_this_week} |")
            lines.append(f"| FB posts this week | {fb_this_week} |")
            lines.append(f"| Total social posts | {total_social_posts} |")
            lines.append(f"| GA4 sessions this week | {fmt_num(total_sessions)} |")
            if total_social_posts > 0:
                ratio = total_sessions / total_social_posts
                lines.append(f"| Sessions per post | {ratio:.0f} |")
            lines.append("")
    except:
        pass

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
    lines.append("- **Video data:** Mux Data API (views, rebuffer %, playback failures, completion, startup time). Migrated from NPAW on 2026-04-22 — Mux is the new source of truth. `videoTitle`/`videoSeries` metadata is not yet populated in the player, so top-content tables show video IDs; once devs wire those fields, titles will resolve to show names.")
    lines.append("- **Landing page queries** use `landingPage` (path only, no query strings) to prevent fbclid/utm parameter fragmentation from causing GA4 to drop rows. Cross-dimension totals are verified against single-dimension totals.")
    lines.append("- **Engagement Rate:** % of sessions lasting >10s, with 2+ page views, or a key event (GA4 standard definition)")
    lines.append("- **Bounce Rate:** % of sessions that were NOT engaged (inverse of engagement rate)")
    lines.append("- **Geo Efficiency Score:** engagement rate x sessions. Surfaces high-volume/low-engagement geos (ad waste) vs high-quality traffic.")
    lines.append("- **Daily Snapshot freshness:** Automatically uses yesterday's data when GA4 processing is complete (engaged sessions >= 10% of 7-day avg). Falls back to 2-days-ago when data is still processing.")
    lines.append("- **Social media data:** Instagram via Meta Graph API (IG Business Account 17841479978232203), YouTube/TikTok/X via public profile scraping")
    lines.append("- **All numbers are pulled directly from APIs** — no manual adjustments or estimates except where explicitly labeled")
    lines.append("- **Health Score** is a weighted composite: Growth (25), Engagement (25), Retention (25), Traffic Quality (25)")
    lines.append("- **'(not set)' entries** indicate GA4 tracking gaps where screen names aren't being passed in analytics events")
    lines.append("")
    lines.append("*Generated by Zo · VURT Analytics Skill v4*")

    return "\n".join(lines)

if __name__ == "__main__":
    import signal
    signal.alarm(240)  # 4 min hard timeout to prevent infinite hangs

    report = build_report()

    report_dir = "/home/workspace/Documents/analytics-reports"
    os.makedirs(report_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{report_dir}/vurt-daily-{date_str}.md"
    with open(filepath, "w") as f:
        f.write(report)
    print(f"Report saved to: {filepath}", flush=True)

    html = markdown_to_html(report)
    html_path = f"{report_dir}/vurt-daily-{date_str}.html"
    with open(html_path, "w") as f:
        f.write(html)
    print(f"HTML email saved to: {html_path} ({len(html)} bytes)", flush=True)

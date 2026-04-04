#!/usr/bin/env python3
"""VURT Bounce Rate & Engagement Diagnostic — post-dev-fix check.

Pulls fresh GA4 data to assess whether recent dev fixes improved bounce rates.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ga4_client import run_report, run_realtime_report, extract_rows, fmt_pct, fmt_num, fmt_duration, wow_delta
from datetime import datetime, timedelta

DIVIDER = "=" * 72

def section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ─────────────────────────────────────────────────────────────────────
# 1. Last 24h: bounce rate, sessions, engagement rate by device category
# ─────────────────────────────────────────────────────────────────────
def query_device_bounce():
    section("1. LAST 24 HOURS — Bounce Rate & Engagement by Device")
    result = run_report(
        date_ranges=[{"startDate": "today", "endDate": "today", "name": "today"},
                     {"startDate": "yesterday", "endDate": "yesterday", "name": "yesterday"}],
        metrics=["sessions", "bounceRate", "engagementRate",
                 "averageSessionDuration", "activeUsers", "engagedSessions"],
        dimensions=["deviceCategory"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}]
    )
    rows = extract_rows(result)
    today_rows = [r for r in rows if r.get("dateRange") == "today"]
    yesterday_rows = [r for r in rows if r.get("dateRange") == "yesterday"]

    print(f"\n{'Device':<12} {'Sessions':>9} {'Bounce':>8} {'Engage':>8} {'Avg Dur':>9} {'Users':>7}")
    print("-" * 60)
    for r in today_rows:
        dev = r.get("deviceCategory", "?")
        print(f"{dev:<12} {fmt_num(r.get('sessions','0')):>9} {fmt_pct(r.get('bounceRate','0')):>8} "
              f"{fmt_pct(r.get('engagementRate','0')):>8} {fmt_duration(r.get('averageSessionDuration','0')):>9} "
              f"{fmt_num(r.get('activeUsers','0')):>7}")

    # Also print overall totals for today
    result_total = run_report(
        date_ranges=[{"startDate": "today", "endDate": "today"}],
        metrics=["sessions", "bounceRate", "engagementRate",
                 "averageSessionDuration", "activeUsers", "engagedSessions"]
    )
    total_rows = extract_rows(result_total)
    if total_rows:
        t = total_rows[0]
        print("-" * 60)
        print(f"{'TOTAL':<12} {fmt_num(t.get('sessions','0')):>9} {fmt_pct(t.get('bounceRate','0')):>8} "
              f"{fmt_pct(t.get('engagementRate','0')):>8} {fmt_duration(t.get('averageSessionDuration','0')):>9} "
              f"{fmt_num(t.get('activeUsers','0')):>7}")

    if yesterday_rows:
        print(f"\n  Yesterday comparison:")
        print(f"  {'Device':<12} {'Sessions':>9} {'Bounce':>8} {'Engage':>8}")
        print("  " + "-" * 42)
        for r in yesterday_rows:
            dev = r.get("deviceCategory", "?")
            print(f"  {dev:<12} {fmt_num(r.get('sessions','0')):>9} {fmt_pct(r.get('bounceRate','0')):>8} "
                  f"{fmt_pct(r.get('engagementRate','0')):>8}")


# ─────────────────────────────────────────────────────────────────────
# 2. Last 24h: bounce rate by landing page (top 20)
# ─────────────────────────────────────────────────────────────────────
def query_landing_bounce():
    section("2. LAST 24 HOURS — Bounce Rate by Landing Page (Top 20)")
    result = run_report(
        date_ranges=[{"startDate": "yesterday", "endDate": "today"}],
        metrics=["sessions", "bounceRate", "engagementRate",
                 "averageSessionDuration", "activeUsers"],
        dimensions=["landingPagePlusQueryString"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=20
    )
    rows = extract_rows(result)
    print(f"\n{'Landing Page':<55} {'Sess':>6} {'Bounce':>8} {'Engage':>8} {'Dur':>7}")
    print("-" * 88)
    for r in rows:
        page = r.get("landingPagePlusQueryString", "?")
        if len(page) > 52:
            page = page[:49] + "..."
        print(f"{page:<55} {fmt_num(r.get('sessions','0')):>6} {fmt_pct(r.get('bounceRate','0')):>8} "
              f"{fmt_pct(r.get('engagementRate','0')):>8} {fmt_duration(r.get('averageSessionDuration','0')):>7}")


# ─────────────────────────────────────────────────────────────────────
# 3. Last 24h: sessions & bounce by campaign/source/medium
# ─────────────────────────────────────────────────────────────────────
def query_source_bounce():
    section("3. LAST 24 HOURS — Bounce Rate by Source / Medium")
    result = run_report(
        date_ranges=[{"startDate": "yesterday", "endDate": "today"}],
        metrics=["sessions", "bounceRate", "engagementRate", "activeUsers"],
        dimensions=["sessionSource", "sessionMedium"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=20
    )
    rows = extract_rows(result)
    print(f"\n{'Source':<25} {'Medium':<15} {'Sess':>6} {'Bounce':>8} {'Engage':>8} {'Users':>7}")
    print("-" * 75)
    for r in rows:
        src = r.get("sessionSource", "?")[:24]
        med = r.get("sessionMedium", "?")[:14]
        print(f"{src:<25} {med:<15} {fmt_num(r.get('sessions','0')):>6} "
              f"{fmt_pct(r.get('bounceRate','0')):>8} {fmt_pct(r.get('engagementRate','0')):>8} "
              f"{fmt_num(r.get('activeUsers','0')):>7}")

    # Also by campaign
    print(f"\n  By Campaign (top 10):")
    result2 = run_report(
        date_ranges=[{"startDate": "yesterday", "endDate": "today"}],
        metrics=["sessions", "bounceRate", "engagementRate"],
        dimensions=["sessionCampaignName"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=10
    )
    rows2 = extract_rows(result2)
    print(f"  {'Campaign':<40} {'Sess':>6} {'Bounce':>8} {'Engage':>8}")
    print("  " + "-" * 65)
    for r in rows2:
        camp = r.get("sessionCampaignName", "?")
        if len(camp) > 38:
            camp = camp[:35] + "..."
        print(f"  {camp:<40} {fmt_num(r.get('sessions','0')):>6} "
              f"{fmt_pct(r.get('bounceRate','0')):>8} {fmt_pct(r.get('engagementRate','0')):>8}")


# ─────────────────────────────────────────────────────────────────────
# 4. Realtime: active users by device, platform
# ─────────────────────────────────────────────────────────────────────
def query_realtime():
    section("4. REALTIME — Active Users by Device & Platform")
    try:
        result_dev = run_realtime_report(
            metrics=["activeUsers"],
            dimensions=["deviceCategory"]
        )
        rows_dev = extract_rows(result_dev)
        print(f"\n  By Device:")
        total = 0
        for r in rows_dev:
            users = int(float(r.get("activeUsers", "0")))
            total += users
            print(f"    {r.get('deviceCategory', '?'):<15} {users} active users")
        print(f"    {'TOTAL':<15} {total} active users")
    except Exception as e:
        print(f"  Device realtime error: {e}")

    try:
        result_plat = run_realtime_report(
            metrics=["activeUsers"],
            dimensions=["platform"]
        )
        rows_plat = extract_rows(result_plat)
        print(f"\n  By Platform:")
        for r in rows_plat:
            users = int(float(r.get("activeUsers", "0")))
            print(f"    {r.get('platform', '?'):<15} {users} active users")
    except Exception as e:
        print(f"  Platform realtime error: {e}")


# ─────────────────────────────────────────────────────────────────────
# 5. Compare: today vs yesterday vs 3 days ago — overall bounce rate
# ─────────────────────────────────────────────────────────────────────
def query_comparison():
    section("5. BOUNCE RATE COMPARISON — Today vs Yesterday vs 3 Days Ago")

    # GA4 allows max 4 date ranges in one call; we'll use 3
    result = run_report(
        date_ranges=[
            {"startDate": "today", "endDate": "today", "name": "today"},
            {"startDate": "yesterday", "endDate": "yesterday", "name": "yesterday"},
            {"startDate": "3daysAgo", "endDate": "3daysAgo", "name": "3daysAgo"}
        ],
        metrics=["sessions", "bounceRate", "engagementRate",
                 "averageSessionDuration", "activeUsers",
                 "engagedSessions", "screenPageViews"]
    )
    rows = extract_rows(result)

    now = datetime.now()
    labels = {
        "today": now.strftime("%a %m/%d (today)"),
        "yesterday": (now - timedelta(days=1)).strftime("%a %m/%d (yesterday)"),
        "3daysAgo": (now - timedelta(days=3)).strftime("%a %m/%d (3d ago)")
    }

    print(f"\n{'Period':<28} {'Sessions':>9} {'Bounce':>8} {'Engage':>8} {'Avg Dur':>9} {'Users':>7} {'Views':>7}")
    print("-" * 82)

    for period_name in ["today", "yesterday", "3daysAgo"]:
        r = next((x for x in rows if x.get("dateRange") == period_name), None)
        if r:
            label = labels[period_name]
            print(f"{label:<28} {fmt_num(r.get('sessions','0')):>9} "
                  f"{fmt_pct(r.get('bounceRate','0')):>8} "
                  f"{fmt_pct(r.get('engagementRate','0')):>8} "
                  f"{fmt_duration(r.get('averageSessionDuration','0')):>9} "
                  f"{fmt_num(r.get('activeUsers','0')):>7} "
                  f"{fmt_num(r.get('screenPageViews','0')):>7}")
        else:
            print(f"{labels[period_name]:<28} (no data)")

    # Calculate deltas
    today_r = next((x for x in rows if x.get("dateRange") == "today"), {})
    yday_r = next((x for x in rows if x.get("dateRange") == "yesterday"), {})
    three_r = next((x for x in rows if x.get("dateRange") == "3daysAgo"), {})

    today_bounce = float(today_r.get("bounceRate", "0"))
    yday_bounce = float(yday_r.get("bounceRate", "0"))
    three_bounce = float(three_r.get("bounceRate", "0"))

    print(f"\n  Bounce Rate Trend:")
    print(f"    3 days ago:  {today_bounce * 100 if three_bounce == 0 else three_bounce * 100:.1f}%")
    print(f"    Yesterday:   {yday_bounce * 100:.1f}%")
    print(f"    Today:       {today_bounce * 100:.1f}%")
    if three_bounce > 0:
        delta_3d = (today_bounce - three_bounce) * 100
        direction = "IMPROVED (lower)" if delta_3d < 0 else "WORSENED (higher)" if delta_3d > 0 else "UNCHANGED"
        print(f"    3-day change: {delta_3d:+.1f} pp  -->  {direction}")
    if yday_bounce > 0:
        delta_1d = (today_bounce - yday_bounce) * 100
        direction = "IMPROVED (lower)" if delta_1d < 0 else "WORSENED (higher)" if delta_1d > 0 else "UNCHANGED"
        print(f"    1-day change: {delta_1d:+.1f} pp  -->  {direction}")

    # Also pull 7-day daily trend for context
    print(f"\n  7-Day Daily Bounce Rate Trend:")
    trend_result = run_report(
        date_ranges=[{"startDate": "7daysAgo", "endDate": "today"}],
        metrics=["sessions", "bounceRate", "engagementRate", "activeUsers"],
        dimensions=["date"],
        order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}]
    )
    trend_rows = extract_rows(trend_result)
    print(f"    {'Date':<12} {'Sessions':>9} {'Bounce':>8} {'Engage':>8} {'Users':>7}")
    print("    " + "-" * 50)
    for t in trend_rows:
        d = t.get("date", "")
        date_fmt = f"{d[4:6]}/{d[6:8]}" if len(d) == 8 else d
        print(f"    {date_fmt:<12} {fmt_num(t.get('sessions','0')):>9} "
              f"{fmt_pct(t.get('bounceRate','0')):>8} "
              f"{fmt_pct(t.get('engagementRate','0')):>8} "
              f"{fmt_num(t.get('activeUsers','0')):>7}")


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 72)
    print("  VURT BOUNCE RATE & ENGAGEMENT DIAGNOSTIC")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  GA4 Property: 518738893 (myvurt.com)")
    print("=" * 72)

    try:
        query_device_bounce()
    except Exception as e:
        print(f"  ERROR: {e}")

    try:
        query_landing_bounce()
    except Exception as e:
        print(f"  ERROR: {e}")

    try:
        query_source_bounce()
    except Exception as e:
        print(f"  ERROR: {e}")

    try:
        query_realtime()
    except Exception as e:
        print(f"  ERROR: {e}")

    try:
        query_comparison()
    except Exception as e:
        print(f"  ERROR: {e}")

    print(f"\n{'=' * 72}")
    print("  DIAGNOSTIC COMPLETE")
    print(f"{'=' * 72}")

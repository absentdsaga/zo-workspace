#!/usr/bin/env python3
"""GA4 Bounce Rate Regression Investigation — All 7 Queries"""
import sys, os, json
sys.path.insert(0, "/home/workspace/Skills/vurt-analytics/scripts")
from ga4_client import get_access_token, PROPERTY_ID, DATA_API
import urllib.request

def run_report_filtered(date_ranges, metrics, dimensions=None, dimension_filter=None, order_bys=None, limit=None):
    """run_report with dimensionFilter support."""
    token = get_access_token()
    body = {"dateRanges": date_ranges, "metrics": [{"name": m} for m in metrics]}
    if dimensions:
        body["dimensions"] = [{"name": d} for d in dimensions]
    if dimension_filter:
        body["dimensionFilter"] = dimension_filter
    if order_bys:
        body["orderBys"] = order_bys
    if limit:
        body["limit"] = str(limit)
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{DATA_API}/properties/{PROPERTY_ID}:runReport",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def extract_rows(result):
    rows = []
    dim_headers = [h["name"] for h in result.get("dimensionHeaders", [])]
    met_headers = [h["name"] for h in result.get("metricHeaders", [])]
    for row in result.get("rows", []):
        dims = {h: v["value"] for h, v in zip(dim_headers, row.get("dimensionValues", []))}
        mets = {h: v["value"] for h, v in zip(met_headers, row.get("metricValues", []))}
        rows.append({**dims, **mets})
    return rows

PAID_SOCIAL_FILTER = {
    "filter": {
        "fieldName": "sessionDefaultChannelGroup",
        "stringFilter": {"matchType": "EXACT", "value": "Paid Social"}
    }
}

out = []
def log(s=""):
    print(s)
    out.append(s)

# ============================================================
# QUERY 1: Hourly bounce rate for Paid Social, Apr 1-4
# ============================================================
log("=" * 70)
log("QUERY 1: HOURLY Paid Social bounce rate, Apr 1 through Apr 4")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[{"startDate": "2026-04-01", "endDate": "2026-04-04"}],
        metrics=["sessions", "bounceRate", "engagedSessions", "engagementRate", "activeUsers"],
        dimensions=["date", "hour"],
        dimension_filter=PAID_SOCIAL_FILTER,
        order_bys=[
            {"dimension": {"dimensionName": "date"}, "desc": False},
            {"dimension": {"dimensionName": "hour"}, "desc": False}
        ],
        limit=200
    )
    rows = extract_rows(result)
    log(f"{'Date':<12} {'Hour':<6} {'Sessions':<10} {'BounceRate':<12} {'EngRate':<10} {'EngSess':<10} {'Users':<8}")
    log("-" * 70)
    for r in rows:
        d = r.get("date", "")
        date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d
        br = float(r.get("bounceRate", "0")) * 100
        er = float(r.get("engagementRate", "0")) * 100
        log(f"{date_fmt:<12} {r.get('hour','?'):<6} {r.get('sessions','0'):<10} {br:<12.1f}% {er:<10.1f}% {r.get('engagedSessions','0'):<10} {r.get('activeUsers','0'):<8}")
except Exception as e:
    log(f"ERROR: {e}")

log()

# ============================================================
# QUERY 2: All channels side by side, Apr 2 vs Apr 3
# ============================================================
log("=" * 70)
log("QUERY 2: ALL channels — Apr 2 vs Apr 3")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[
            {"startDate": "2026-04-02", "endDate": "2026-04-02", "name": "apr2"},
            {"startDate": "2026-04-03", "endDate": "2026-04-03", "name": "apr3"}
        ],
        metrics=["sessions", "bounceRate", "engagementRate", "engagedSessions", "activeUsers", "averageSessionDuration"],
        dimensions=["sessionDefaultChannelGroup"],
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=20
    )
    rows = extract_rows(result)
    log(f"{'Channel':<25} {'DateRange':<10} {'Sessions':<10} {'BounceRate':<12} {'EngRate':<10} {'EngSess':<10} {'Users':<8} {'AvgDur':<8}")
    log("-" * 95)
    for r in rows:
        br = float(r.get("bounceRate", "0")) * 100
        er = float(r.get("engagementRate", "0")) * 100
        dur = float(r.get("averageSessionDuration", "0"))
        log(f"{r.get('sessionDefaultChannelGroup','?'):<25} {r.get('dateRange','?'):<10} {r.get('sessions','0'):<10} {br:<12.1f}% {er:<10.1f}% {r.get('engagedSessions','0'):<10} {r.get('activeUsers','0'):<8} {dur:<8.1f}s")
except Exception as e:
    log(f"ERROR: {e}")

log()

# ============================================================
# QUERY 3: Paid Social — landing page breakdown, Apr 2 vs Apr 3
# ============================================================
log("=" * 70)
log("QUERY 3: Paid Social — landing page breakdown, Apr 2 vs Apr 3")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[
            {"startDate": "2026-04-02", "endDate": "2026-04-02", "name": "apr2"},
            {"startDate": "2026-04-03", "endDate": "2026-04-03", "name": "apr3"}
        ],
        metrics=["sessions", "bounceRate", "engagementRate", "engagedSessions", "activeUsers"],
        dimensions=["landingPagePlusQueryString"],
        dimension_filter=PAID_SOCIAL_FILTER,
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=30
    )
    rows = extract_rows(result)
    log(f"{'Landing Page':<60} {'DateRange':<10} {'Sessions':<10} {'BounceRate':<12} {'EngRate':<10} {'EngSess':<10}")
    log("-" * 115)
    for r in rows:
        br = float(r.get("bounceRate", "0")) * 100
        er = float(r.get("engagementRate", "0")) * 100
        lp = r.get("landingPagePlusQueryString", "?")
        if len(lp) > 58: lp = lp[:55] + "..."
        log(f"{lp:<60} {r.get('dateRange','?'):<10} {r.get('sessions','0'):<10} {br:<12.1f}% {er:<10.1f}% {r.get('engagedSessions','0'):<10}")
except Exception as e:
    log(f"ERROR: {e}")

log()

# ============================================================
# QUERY 4: Paid Social — device category breakdown, Apr 2 vs Apr 3
# ============================================================
log("=" * 70)
log("QUERY 4: Paid Social — device category, Apr 2 vs Apr 3")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[
            {"startDate": "2026-04-02", "endDate": "2026-04-02", "name": "apr2"},
            {"startDate": "2026-04-03", "endDate": "2026-04-03", "name": "apr3"}
        ],
        metrics=["sessions", "bounceRate", "engagementRate", "engagedSessions", "activeUsers", "averageSessionDuration"],
        dimensions=["deviceCategory"],
        dimension_filter=PAID_SOCIAL_FILTER,
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=10
    )
    rows = extract_rows(result)
    log(f"{'Device':<15} {'DateRange':<10} {'Sessions':<10} {'BounceRate':<12} {'EngRate':<10} {'EngSess':<10} {'Users':<8} {'AvgDur':<8}")
    log("-" * 85)
    for r in rows:
        br = float(r.get("bounceRate", "0")) * 100
        er = float(r.get("engagementRate", "0")) * 100
        dur = float(r.get("averageSessionDuration", "0"))
        log(f"{r.get('deviceCategory','?'):<15} {r.get('dateRange','?'):<10} {r.get('sessions','0'):<10} {br:<12.1f}% {er:<10.1f}% {r.get('engagedSessions','0'):<10} {r.get('activeUsers','0'):<8} {dur:<8.1f}s")
except Exception as e:
    log(f"ERROR: {e}")

log()

# ============================================================
# QUERY 5: Event counts hourly for Paid Social, Apr 2-3
# ============================================================
log("=" * 70)
log("QUERY 5: Event counts (page_view, session_start, first_visit) hourly — Paid Social, Apr 2-3")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[{"startDate": "2026-04-02", "endDate": "2026-04-03"}],
        metrics=["eventCount"],
        dimensions=["date", "hour", "eventName"],
        dimension_filter={
            "andGroup": {
                "expressions": [
                    {"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"matchType": "EXACT", "value": "Paid Social"}}},
                    {"filter": {"fieldName": "eventName", "inListFilter": {"values": ["page_view", "session_start", "first_visit"]}}}
                ]
            }
        },
        order_bys=[
            {"dimension": {"dimensionName": "date"}, "desc": False},
            {"dimension": {"dimensionName": "hour"}, "desc": False}
        ],
        limit=500
    )
    rows = extract_rows(result)
    log(f"{'Date':<12} {'Hour':<6} {'Event':<20} {'Count':<10}")
    log("-" * 50)
    for r in rows:
        d = r.get("date", "")
        date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d
        log(f"{date_fmt:<12} {r.get('hour','?'):<6} {r.get('eventName','?'):<20} {r.get('eventCount','0'):<10}")
except Exception as e:
    log(f"ERROR: {e}")

log()

# ============================================================
# QUERY 6: screen_view vs page_view for Paid Social, Apr 2 vs Apr 3
# ============================================================
log("=" * 70)
log("QUERY 6: screen_view vs page_view — Paid Social, Apr 2 vs Apr 3")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[
            {"startDate": "2026-04-02", "endDate": "2026-04-02", "name": "apr2"},
            {"startDate": "2026-04-03", "endDate": "2026-04-03", "name": "apr3"}
        ],
        metrics=["eventCount"],
        dimensions=["eventName"],
        dimension_filter={
            "andGroup": {
                "expressions": [
                    {"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"matchType": "EXACT", "value": "Paid Social"}}},
                    {"filter": {"fieldName": "eventName", "inListFilter": {"values": ["page_view", "screen_view", "screen_viewed", "session_start", "first_visit", "user_engagement", "scroll"]}}}
                ]
            }
        },
        limit=50
    )
    rows = extract_rows(result)
    log(f"{'Event':<25} {'DateRange':<10} {'Count':<10}")
    log("-" * 50)
    for r in rows:
        log(f"{r.get('eventName','?'):<25} {r.get('dateRange','?'):<10} {r.get('eventCount','0'):<10}")
except Exception as e:
    log(f"ERROR: {e}")

log()

# ============================================================
# QUERY 7: Campaign names/sources for Paid Social, Apr 2 vs Apr 3
# ============================================================
log("=" * 70)
log("QUERY 7: Campaign names + sources — Paid Social, Apr 2 vs Apr 3")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[
            {"startDate": "2026-04-02", "endDate": "2026-04-02", "name": "apr2"},
            {"startDate": "2026-04-03", "endDate": "2026-04-03", "name": "apr3"}
        ],
        metrics=["sessions", "bounceRate", "engagementRate", "engagedSessions", "activeUsers"],
        dimensions=["sessionCampaignName", "sessionSource", "sessionMedium"],
        dimension_filter=PAID_SOCIAL_FILTER,
        order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
        limit=30
    )
    rows = extract_rows(result)
    log(f"{'Campaign':<40} {'Source':<20} {'Medium':<15} {'DateRange':<10} {'Sessions':<10} {'BounceRate':<12} {'EngRate':<10} {'EngSess':<10}")
    log("-" * 130)
    for r in rows:
        br = float(r.get("bounceRate", "0")) * 100
        er = float(r.get("engagementRate", "0")) * 100
        camp = r.get("sessionCampaignName", "?")
        if len(camp) > 38: camp = camp[:35] + "..."
        log(f"{camp:<40} {r.get('sessionSource','?'):<20} {r.get('sessionMedium','?'):<15} {r.get('dateRange','?'):<10} {r.get('sessions','0'):<10} {br:<12.1f}% {er:<10.1f}% {r.get('engagedSessions','0'):<10}")
except Exception as e:
    log(f"ERROR: {e}")

log()

# ============================================================
# BONUS: Daily totals for Paid Social Apr 1-4 (summary view)
# ============================================================
log("=" * 70)
log("BONUS: Daily totals for Paid Social, Apr 1-4")
log("=" * 70)
try:
    result = run_report_filtered(
        date_ranges=[{"startDate": "2026-04-01", "endDate": "2026-04-04"}],
        metrics=["sessions", "bounceRate", "engagementRate", "engagedSessions", "activeUsers", "screenPageViews", "averageSessionDuration"],
        dimensions=["date"],
        dimension_filter=PAID_SOCIAL_FILTER,
        order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}]
    )
    rows = extract_rows(result)
    log(f"{'Date':<12} {'Sessions':<10} {'BounceRate':<12} {'EngRate':<10} {'EngSess':<10} {'Users':<8} {'Views':<8} {'AvgDur':<8}")
    log("-" * 80)
    for r in rows:
        d = r.get("date", "")
        date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d
        br = float(r.get("bounceRate", "0")) * 100
        er = float(r.get("engagementRate", "0")) * 100
        dur = float(r.get("averageSessionDuration", "0"))
        log(f"{date_fmt:<12} {r.get('sessions','0'):<10} {br:<12.1f}% {er:<10.1f}% {r.get('engagedSessions','0'):<10} {r.get('activeUsers','0'):<8} {r.get('screenPageViews','0'):<8} {dur:<8.1f}s")
except Exception as e:
    log(f"ERROR: {e}")

# Save raw output
outpath = "/tmp/ga4-regression-raw.txt"
with open(outpath, "w") as f:
    f.write("\n".join(out))
print(f"\n\nSaved raw output to {outpath}")

#!/usr/bin/env python3
"""GA4 Hourly Diagnostic — bounce rates, events, landing pages, page_view vs screen_viewed."""

import os, json, urllib.request, urllib.parse, sys
from datetime import datetime, timedelta, timezone

PROPERTY_ID = "518738893"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_API = "https://analyticsdata.googleapis.com/v1beta"

def get_access_token():
    oauth = json.loads(os.environ["VURT_GOOGLE_OAUTH_CLIENT"])
    params = urllib.parse.urlencode({
        "client_id": oauth["installed"]["client_id"],
        "client_secret": oauth["installed"]["client_secret"],
        "refresh_token": os.environ["VURT_ANALYTICS_REFRESH_TOKEN"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=params, method="POST")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["access_token"]

def run_report(body):
    token = get_access_token()
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{DATA_API}/properties/{PROPERTY_ID}:runReport",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def pp(obj):
    print(json.dumps(obj, indent=2))

def print_table(result, label=""):
    """Pretty-print a GA4 result as a table."""
    if label:
        print(f"\n{'='*80}")
        print(f"  {label}")
        print(f"{'='*80}")

    dims = [h.get("name","?") for h in result.get("dimensionHeaders", [])]
    mets = [h.get("name","?") for h in result.get("metricHeaders", [])]
    headers = dims + mets

    rows_data = []
    for row in result.get("rows", []):
        dim_vals = [v.get("value","") for v in row.get("dimensionValues", [])]
        met_vals = [v.get("value","") for v in row.get("metricValues", [])]
        rows_data.append(dim_vals + met_vals)

    if not rows_data:
        print("  (no data)")
        return

    # Column widths
    widths = [len(h) for h in headers]
    for r in rows_data:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(str(v)))

    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("-" * sum(widths) + "-" * (2 * len(widths)))
    for r in rows_data:
        print(fmt.format(*r))

    print(f"\n  Row count: {result.get('rowCount', len(rows_data))}")
    print(f"  Metadata: {result.get('metadata', {})}")

# -- Time range: last 12 hours --
now_utc = datetime.now(timezone.utc)
cutoff = now_utc - timedelta(hours=12)
cutoff_datehour = cutoff.strftime("%Y%m%d%H")
print(f"Current UTC time: {now_utc.isoformat()}")
print(f"12h cutoff (dateHour >= {cutoff_datehour})")
print(f"Note: GA4 intraday data may lag 4-8 hours. We pull today+yesterday to maximize coverage.\n")

# -- REPORT 1: Hourly bounce rate by channel --
print("Fetching Report 1: Hourly bounce rate by channel...")
r1 = run_report({
    "dateRanges": [{"startDate": "yesterday", "endDate": "today"}],
    "dimensions": [
        {"name": "dateHour"},
        {"name": "sessionDefaultChannelGroup"}
    ],
    "metrics": [
        {"name": "sessions"},
        {"name": "bounceRate"},
        {"name": "engagedSessions"},
        {"name": "engagementRate"},
        {"name": "averageSessionDuration"}
    ],
    "orderBys": [{"dimension": {"dimensionName": "dateHour", "orderType": "ALPHANUMERIC"}, "desc": True}],
    "limit": 500
})
print_table(r1, "REPORT 1: Hourly Bounce Rate by Channel (last 48h window)")

# Filter to last 12h and reprint
filtered_rows_1 = []
for row in r1.get("rows", []):
    dh = row["dimensionValues"][0]["value"]
    if dh >= cutoff_datehour:
        filtered_rows_1.append(row)

print(f"\n--- Filtered to last 12h ({len(filtered_rows_1)} rows, dateHour >= {cutoff_datehour}) ---")
for row in filtered_rows_1:
    vals = [v["value"] for v in row["dimensionValues"]] + [v["value"] for v in row["metricValues"]]
    print(f"  {vals}")

# -- REPORT 2: Hourly event counts by channel --
print("\n\nFetching Report 2: Hourly event counts by channel...")
r2 = run_report({
    "dateRanges": [{"startDate": "yesterday", "endDate": "today"}],
    "dimensions": [
        {"name": "dateHour"},
        {"name": "sessionDefaultChannelGroup"},
        {"name": "eventName"}
    ],
    "metrics": [
        {"name": "eventCount"}
    ],
    "dimensionFilter": {
        "filter": {
            "fieldName": "eventName",
            "inListFilter": {
                "values": ["page_view", "screen_viewed", "session_start", "sign_up"]
            }
        }
    },
    "orderBys": [{"dimension": {"dimensionName": "dateHour", "orderType": "ALPHANUMERIC"}, "desc": True}],
    "limit": 1000
})
print_table(r2, "REPORT 2: Hourly Event Counts (page_view, screen_viewed, session_start, sign_up) by Channel")

filtered_rows_2 = []
for row in r2.get("rows", []):
    dh = row["dimensionValues"][0]["value"]
    if dh >= cutoff_datehour:
        filtered_rows_2.append(row)

print(f"\n--- Filtered to last 12h ({len(filtered_rows_2)} rows) ---")
for row in filtered_rows_2:
    vals = [v["value"] for v in row["dimensionValues"]] + [v["value"] for v in row["metricValues"]]
    print(f"  {vals}")

# -- REPORT 3: Landing page report for Paid Social --
print("\n\nFetching Report 3: Landing pages for Paid Social sessions...")
r3 = run_report({
    "dateRanges": [{"startDate": "yesterday", "endDate": "today"}],
    "dimensions": [
        {"name": "dateHour"},
        {"name": "landingPage"}
    ],
    "metrics": [
        {"name": "sessions"},
        {"name": "bounceRate"},
        {"name": "engagedSessions"},
        {"name": "averageSessionDuration"},
        {"name": "screenPageViews"}
    ],
    "dimensionFilter": {
        "filter": {
            "fieldName": "sessionDefaultChannelGroup",
            "stringFilter": {
                "value": "Paid Social",
                "matchType": "EXACT"
            }
        }
    },
    "orderBys": [{"dimension": {"dimensionName": "dateHour", "orderType": "ALPHANUMERIC"}, "desc": True}],
    "limit": 500
})
print_table(r3, "REPORT 3: Paid Social Landing Pages (hourly)")

filtered_rows_3 = []
for row in r3.get("rows", []):
    dh = row["dimensionValues"][0]["value"]
    if dh >= cutoff_datehour:
        filtered_rows_3.append(row)

print(f"\n--- Filtered to last 12h ({len(filtered_rows_3)} rows) ---")
for row in filtered_rows_3:
    vals = [v["value"] for v in row["dimensionValues"]] + [v["value"] for v in row["metricValues"]]
    print(f"  {vals}")

# -- REPORT 4: page_view vs screen_viewed ratio per hour --
print("\n\nFetching Report 4: page_view vs screen_viewed ratio per hour...")
r4 = run_report({
    "dateRanges": [{"startDate": "yesterday", "endDate": "today"}],
    "dimensions": [
        {"name": "dateHour"},
        {"name": "eventName"}
    ],
    "metrics": [
        {"name": "eventCount"}
    ],
    "dimensionFilter": {
        "filter": {
            "fieldName": "eventName",
            "inListFilter": {
                "values": ["page_view", "screen_viewed"]
            }
        }
    },
    "orderBys": [{"dimension": {"dimensionName": "dateHour", "orderType": "ALPHANUMERIC"}, "desc": True}],
    "limit": 500
})
print_table(r4, "REPORT 4: page_view vs screen_viewed per hour (Angular render check)")

# Build ratio table
pv_by_hour = {}
sv_by_hour = {}
for row in r4.get("rows", []):
    dh = row["dimensionValues"][0]["value"]
    ev = row["dimensionValues"][1]["value"]
    cnt = int(row["metricValues"][0]["value"])
    if ev == "page_view":
        pv_by_hour[dh] = cnt
    elif ev == "screen_viewed":
        sv_by_hour[dh] = cnt

all_hours = sorted(set(list(pv_by_hour.keys()) + list(sv_by_hour.keys())), reverse=True)
print(f"\n--- page_view / screen_viewed RATIO TABLE (last 12h filtered) ---")
print(f"  {'dateHour':<14} {'page_view':>10} {'screen_viewed':>14} {'ratio (pv/sv)':>14} {'gap':>8}")
print(f"  {'-'*60}")
for h in all_hours:
    if h < cutoff_datehour:
        continue
    pv = pv_by_hour.get(h, 0)
    sv = sv_by_hour.get(h, 0)
    ratio = f"{pv/sv:.2f}" if sv > 0 else "INF" if pv > 0 else "N/A"
    gap = pv - sv
    print(f"  {h:<14} {pv:>10} {sv:>14} {ratio:>14} {gap:>8}")

# -- REPORT 5 (bonus): Aggregate channel summary for last 12h context --
print("\n\nFetching Report 5 (bonus): Channel summary for today + yesterday...")
r5 = run_report({
    "dateRanges": [
        {"startDate": "today", "endDate": "today", "name": "today"},
        {"startDate": "yesterday", "endDate": "yesterday", "name": "yesterday"}
    ],
    "dimensions": [
        {"name": "sessionDefaultChannelGroup"}
    ],
    "metrics": [
        {"name": "sessions"},
        {"name": "bounceRate"},
        {"name": "engagedSessions"},
        {"name": "engagementRate"},
        {"name": "activeUsers"},
        {"name": "newUsers"},
        {"name": "screenPageViews"},
        {"name": "averageSessionDuration"}
    ]
})
print_table(r5, "REPORT 5 (bonus): Channel Summary -- Today vs Yesterday")

# Print raw JSON for all reports
print("\n\n" + "="*80)
print("  RAW JSON DUMPS")
print("="*80)
for i, (label, data) in enumerate([
    ("Report 1: Hourly Bounce by Channel", r1),
    ("Report 2: Hourly Events by Channel", r2),
    ("Report 3: Paid Social Landing Pages", r3),
    ("Report 4: page_view vs screen_viewed", r4),
    ("Report 5: Channel Summary", r5),
], 1):
    print(f"\n--- {label} ---")
    pp(data)

print("\n\nDiagnostic complete.")

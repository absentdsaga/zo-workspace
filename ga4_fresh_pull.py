#!/usr/bin/env python3
"""Fresh GA4 data pull for VURT — bounce rate, engagement, session data."""

import os, json, sys, urllib.request, urllib.parse
from datetime import datetime, timedelta

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

def run_report(token, date_ranges, metrics, dimensions=None, order_bys=None, limit=None):
    body = {"dateRanges": date_ranges, "metrics": [{"name": m} for m in metrics]}
    if dimensions:
        body["dimensions"] = [{"name": d} for d in dimensions]
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

def fmt_pct(val):
    v = float(val)
    return f"{v*100:.2f}%" if v <= 1 else f"{v:.2f}%"

def fmt_dur(val):
    s = float(val)
    m, sec = divmod(int(s), 60)
    return f"{m}m {sec}s"

def fmt_num(val):
    return str(int(float(val)))

def print_separator(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

# ===== MAIN =====
token = get_access_token()
print("GA4 access token obtained successfully.")
print(f"Property ID: {PROPERTY_ID}")
print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------- 1. BOUNCE RATE BY DAY — LAST 7 DAYS ----------
print_separator("1. BOUNCE RATE BY DAY — LAST 7 DAYS")
result = run_report(token,
    date_ranges=[{"startDate": "7daysAgo", "endDate": "yesterday"}],
    metrics=["bounceRate", "engagementRate", "sessions", "engagedSessions", "activeUsers"],
    dimensions=["date"],
    order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}]
)
rows = extract_rows(result)
print(f"{'Date':<12} {'Bounce Rate':>12} {'Eng Rate':>10} {'Sessions':>10} {'Engaged':>10} {'Users':>8}")
print("-" * 66)
for r in rows:
    d = r["date"]
    date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
    print(f"{date_fmt:<12} {fmt_pct(r['bounceRate']):>12} {fmt_pct(r['engagementRate']):>10} {fmt_num(r['sessions']):>10} {fmt_num(r['engagedSessions']):>10} {fmt_num(r['activeUsers']):>8}")

# ---------- 2. BOUNCE RATE BY SOURCE/MEDIUM — LAST 3 DAYS ----------
print_separator("2. BOUNCE RATE BY SOURCE/MEDIUM — LAST 3 DAYS")
result = run_report(token,
    date_ranges=[{"startDate": "3daysAgo", "endDate": "yesterday"}],
    metrics=["bounceRate", "engagementRate", "sessions", "engagedSessions", "activeUsers",
             "averageSessionDuration", "screenPageViews"],
    dimensions=["sessionSourceMedium"],
    order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
    limit=30
)
rows = extract_rows(result)
print(f"{'Source/Medium':<40} {'Bounce':>8} {'Eng Rate':>10} {'Sessions':>9} {'Engaged':>9} {'Users':>7} {'Avg Dur':>8} {'Views':>7}")
print("-" * 104)
for r in rows:
    sm = r["sessionSourceMedium"][:39]
    print(f"{sm:<40} {fmt_pct(r['bounceRate']):>8} {fmt_pct(r['engagementRate']):>10} {fmt_num(r['sessions']):>9} {fmt_num(r['engagedSessions']):>9} {fmt_num(r['activeUsers']):>7} {fmt_dur(r['averageSessionDuration']):>8} {fmt_num(r['screenPageViews']):>7}")

# ---------- 2b. BOUNCE RATE BY SOURCE/MEDIUM BY DAY — LAST 3 DAYS (key sources) ----------
print_separator("2b. BOUNCE RATE BY SOURCE/MEDIUM BY DAY — LAST 3 DAYS (daily breakdown)")
result = run_report(token,
    date_ranges=[{"startDate": "3daysAgo", "endDate": "yesterday"}],
    metrics=["bounceRate", "engagementRate", "sessions", "engagedSessions", "averageSessionDuration"],
    dimensions=["date", "sessionSourceMedium"],
    order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}],
    limit=100
)
rows = extract_rows(result)
print(f"{'Date':<12} {'Source/Medium':<35} {'Bounce':>8} {'Eng Rate':>10} {'Sessions':>9} {'Engaged':>9} {'Avg Dur':>8}")
print("-" * 95)
for r in sorted(rows, key=lambda x: (x["date"], x["sessionSourceMedium"])):
    sm = r["sessionSourceMedium"]
    d = r["date"]
    date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
    marker = " ***" if any(k in sm.lower() for k in ["facebook", "instagram", "google", "direct"]) else ""
    print(f"{date_fmt:<12} {sm[:34]:<35} {fmt_pct(r['bounceRate']):>8} {fmt_pct(r['engagementRate']):>10} {fmt_num(r['sessions']):>9} {fmt_num(r['engagedSessions']):>9} {fmt_dur(r['averageSessionDuration']):>8}{marker}")

# ---------- 3. ENGAGEMENT RATE & AVG SESSION DURATION — LAST 3 DAYS ----------
print_separator("3. ENGAGEMENT RATE & AVG SESSION DURATION — LAST 3 DAYS (by day)")
result = run_report(token,
    date_ranges=[{"startDate": "3daysAgo", "endDate": "yesterday"}],
    metrics=["engagementRate", "averageSessionDuration", "sessions", "engagedSessions",
             "userEngagementDuration", "sessionsPerUser", "activeUsers", "bounceRate",
             "screenPageViews"],
    dimensions=["date"],
    order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}]
)
rows = extract_rows(result)
print(f"{'Date':<12} {'Eng Rate':>10} {'Bounce':>8} {'Avg Dur':>8} {'Sessions':>9} {'Engaged':>9} {'Users':>7} {'Sess/User':>10} {'Views':>7} {'Total Eng':>10}")
print("-" * 100)
for r in rows:
    d = r["date"]
    date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
    print(f"{date_fmt:<12} {fmt_pct(r['engagementRate']):>10} {fmt_pct(r['bounceRate']):>8} {fmt_dur(r['averageSessionDuration']):>8} {fmt_num(r['sessions']):>9} {fmt_num(r['engagedSessions']):>9} {fmt_num(r['activeUsers']):>7} {float(r['sessionsPerUser']):.2f}{' ':>4} {fmt_num(r['screenPageViews']):>7} {fmt_dur(r['userEngagementDuration']):>10}")

# ---------- 4. LANDING PAGE PERFORMANCE — LAST 3 DAYS ----------
print_separator("4. LANDING PAGE PERFORMANCE — LAST 3 DAYS")
result = run_report(token,
    date_ranges=[{"startDate": "3daysAgo", "endDate": "yesterday"}],
    metrics=["sessions", "bounceRate", "engagementRate", "averageSessionDuration",
             "activeUsers", "screenPageViews", "engagedSessions"],
    dimensions=["landingPagePlusQueryString"],
    order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
    limit=20
)
rows = extract_rows(result)
print(f"{'Landing Page':<55} {'Sessions':>9} {'Bounce':>8} {'Eng Rate':>10} {'Avg Dur':>8} {'Users':>7} {'Views':>7} {'Engaged':>9}")
print("-" * 120)
for r in rows:
    lp = r["landingPagePlusQueryString"][:54]
    print(f"{lp:<55} {fmt_num(r['sessions']):>9} {fmt_pct(r['bounceRate']):>8} {fmt_pct(r['engagementRate']):>10} {fmt_dur(r['averageSessionDuration']):>8} {fmt_num(r['activeUsers']):>7} {fmt_num(r['screenPageViews']):>7} {fmt_num(r['engagedSessions']):>9}")

# ---------- 4b. LANDING PAGE BY DAY — TOP 5 PAGES ----------
print_separator("4b. LANDING PAGE BY DAY — LAST 3 DAYS (top pages daily)")
result = run_report(token,
    date_ranges=[{"startDate": "3daysAgo", "endDate": "yesterday"}],
    metrics=["sessions", "bounceRate", "engagementRate", "averageSessionDuration"],
    dimensions=["date", "landingPagePlusQueryString"],
    order_bys=[{"dimension": {"dimensionName": "date"}, "desc": False}],
    limit=60
)
rows = extract_rows(result)
print(f"{'Date':<12} {'Landing Page':<45} {'Sessions':>9} {'Bounce':>8} {'Eng Rate':>10} {'Avg Dur':>8}")
print("-" * 96)
for r in sorted(rows, key=lambda x: (x["date"], -int(float(x["sessions"])))):
    d = r["date"]
    date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
    lp = r["landingPagePlusQueryString"][:44]
    print(f"{date_fmt:<12} {lp:<45} {fmt_num(r['sessions']):>9} {fmt_pct(r['bounceRate']):>8} {fmt_pct(r['engagementRate']):>10} {fmt_dur(r['averageSessionDuration']):>8}")

# ---------- 5. TRAFFIC CHANNELS — LAST 3 DAYS ----------
print_separator("5. TRAFFIC CHANNELS — LAST 3 DAYS")
result = run_report(token,
    date_ranges=[{"startDate": "3daysAgo", "endDate": "yesterday"}],
    metrics=["sessions", "bounceRate", "engagementRate", "averageSessionDuration",
             "activeUsers", "newUsers"],
    dimensions=["sessionDefaultChannelGroup"],
    order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
    limit=15
)
rows = extract_rows(result)
print(f"{'Channel':<30} {'Sessions':>9} {'Bounce':>8} {'Eng Rate':>10} {'Avg Dur':>8} {'Users':>7} {'New':>7}")
print("-" * 84)
for r in rows:
    ch = r["sessionDefaultChannelGroup"][:29]
    print(f"{ch:<30} {fmt_num(r['sessions']):>9} {fmt_pct(r['bounceRate']):>8} {fmt_pct(r['engagementRate']):>10} {fmt_dur(r['averageSessionDuration']):>8} {fmt_num(r['activeUsers']):>7} {fmt_num(r['newUsers']):>7}")

print(f"\n{'='*70}")
print("  DONE — All queries completed successfully")
print(f"{'='*70}")

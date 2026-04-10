#!/usr/bin/env python3
"""GA4 paid traffic bounce deep analysis."""
import os, json, urllib.request, urllib.parse
from datetime import datetime, timezone

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

def run_report(date_ranges, metrics, dimensions=None, dim_filter=None, order_bys=None, limit=None):
    token = get_access_token()
    body = {"dateRanges": date_ranges, "metrics": [{"name": m} for m in metrics]}
    if dimensions:
        body["dimensions"] = [{"name": d} for d in dimensions]
    if dim_filter:
        body["dimensionFilter"] = dim_filter
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

def safe(val):
    try: return float(val)
    except: return 0.0

def extract(report):
    rows = []
    dim_headers = [h["name"] for h in report.get("dimensionHeaders", [])]
    met_headers = [h["name"] for h in report.get("metricHeaders", [])]
    for row in report.get("rows", []):
        d = {}
        for i, dv in enumerate(row.get("dimensionValues", [])):
            d[dim_headers[i]] = dv["value"]
        for i, mv in enumerate(row.get("metricValues", [])):
            d[met_headers[i]] = mv["value"]
        rows.append(d)
    return rows

LAST_7 = [{"startDate": "7daysAgo", "endDate": "yesterday"}]
PAID_FILTER = {
    "orGroup": {
        "expressions": [
            {"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"value": "Paid Social", "matchType": "EXACT"}}},
            {"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"value": "Paid Search", "matchType": "EXACT"}}},
            {"filter": {"fieldName": "sessionMedium", "stringFilter": {"value": "cpc", "matchType": "EXACT"}}},
            {"filter": {"fieldName": "sessionMedium", "stringFilter": {"value": "paid", "matchType": "CONTAINS"}}},
        ]
    }
}
ALL_DATA = {}

# 1. PAID vs ORGANIC vs DIRECT comparison
print("="*80)
print("1. CHANNEL COMPARISON (Last 7 Days)")
print("="*80)
r1 = run_report(LAST_7, 
    ["sessions","bounceRate","engagedSessions","engagementRate","averageSessionDuration","eventsPerSession","totalUsers","newUsers"],
    ["sessionDefaultChannelGroup"],
    order_bys=[{"metric":{"metricName":"sessions"},"desc":True}], limit=15)
rows1 = extract(r1)
ALL_DATA["channel_comparison"] = rows1
print(f"{'Channel':<25} {'Sess':>6} {'Bounce':>8} {'EngRate':>8} {'AvgDur':>8} {'Evt/S':>6} {'Users':>6} {'New':>6}")
print("-"*80)
for r in rows1:
    ch = r.get("sessionDefaultChannelGroup","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    er = safe(r.get("engagementRate"))*100
    dur = safe(r.get("averageSessionDuration"))
    eps = safe(r.get("eventsPerSession"))
    u = int(safe(r.get("totalUsers")))
    nu = int(safe(r.get("newUsers")))
    flag = " <<<" if br > 80 and s > 5 else ""
    print(f"{ch:<25} {s:>6} {br:>7.1f}% {er:>7.1f}% {dur:>7.1f}s {eps:>6.1f} {u:>6} {nu:>6}{flag}")

# 2. PAID bounce by device
print("\n" + "="*80)
print("2. PAID TRAFFIC BY DEVICE (Last 7 Days)")
print("="*80)
r2 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate","averageSessionDuration","eventsPerSession"],
    ["deviceCategory"], dim_filter=PAID_FILTER,
    order_bys=[{"metric":{"metricName":"sessions"},"desc":True}])
rows2 = extract(r2)
ALL_DATA["paid_by_device"] = rows2
for r in rows2:
    dev = r.get("deviceCategory","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    eps = safe(r.get("eventsPerSession"))
    print(f"  {dev:<15} {s:>6} sessions | {br:.1f}% bounce | {eps:.1f} events/session")

# 3. PAID bounce by landing page
print("\n" + "="*80)
print("3. PAID TRAFFIC BY LANDING PAGE (Last 7 Days)")
print("="*80)
r3 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate","averageSessionDuration","eventsPerSession"],
    ["landingPage"], dim_filter=PAID_FILTER,
    order_bys=[{"metric":{"metricName":"sessions"},"desc":True}], limit=20)
rows3 = extract(r3)
ALL_DATA["paid_by_landing_page"] = rows3
print(f"{'Landing Page':<55} {'Sess':>5} {'Bounce':>8} {'EngRate':>8} {'Evt/S':>6}")
print("-"*85)
for r in rows3:
    pg = r.get("landingPage","?")[:54]
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    er = safe(r.get("engagementRate"))*100
    eps = safe(r.get("eventsPerSession"))
    flag = " <<<" if br > 85 and s > 3 else ""
    print(f"{pg:<55} {s:>5} {br:>7.1f}% {er:>7.1f}% {eps:>6.1f}{flag}")

# 4. PAID bounce by browser (looking for in-app browsers)
print("\n" + "="*80)
print("4. PAID TRAFFIC BY BROWSER (Last 7 Days)")
print("="*80)
r4 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate","averageSessionDuration","eventsPerSession"],
    ["browser"], dim_filter=PAID_FILTER,
    order_bys=[{"metric":{"metricName":"sessions"},"desc":True}], limit=15)
rows4 = extract(r4)
ALL_DATA["paid_by_browser"] = rows4
for r in rows4:
    brow = r.get("browser","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    eps = safe(r.get("eventsPerSession"))
    inapp = " [IN-APP]" if any(x in brow.lower() for x in ["instagram","facebook","webview","fbav","fban"]) else ""
    flag = " <<<" if br > 85 and s > 3 else ""
    print(f"  {brow:<30} {s:>5} sessions | {br:.1f}% bounce | {eps:.1f} evt/s{inapp}{flag}")

# 5. PAID by day (trend)
print("\n" + "="*80)
print("5. PAID BOUNCE RATE BY DAY (Last 7 Days)")
print("="*80)
r5 = run_report(LAST_7,
    ["sessions","bounceRate","engagedSessions","engagementRate","averageSessionDuration"],
    ["date"], dim_filter=PAID_FILTER,
    order_bys=[{"dimension":{"dimensionName":"date"},"desc":False}])
rows5 = extract(r5)
ALL_DATA["paid_by_day"] = rows5
for r in rows5:
    dt = r.get("date","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    er = safe(r.get("engagementRate"))*100
    dur = safe(r.get("averageSessionDuration"))
    print(f"  {dt} | {s:>5} sessions | {br:.1f}% bounce | {er:.1f}% engaged | {dur:.1f}s avg")

# 6. PAID by new vs returning
print("\n" + "="*80)
print("6. PAID NEW vs RETURNING (Last 7 Days)")
print("="*80)
r6 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate","averageSessionDuration","eventsPerSession"],
    ["newVsReturning"], dim_filter=PAID_FILTER)
rows6 = extract(r6)
ALL_DATA["paid_new_vs_returning"] = rows6
for r in rows6:
    typ = r.get("newVsReturning","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    eps = safe(r.get("eventsPerSession"))
    print(f"  {typ:<15} {s:>5} sessions | {br:.1f}% bounce | {eps:.1f} evt/s")

# 7. PAID events breakdown
print("\n" + "="*80)
print("7. EVENTS FIRED IN PAID SESSIONS (Last 7 Days)")
print("="*80)
r7 = run_report(LAST_7,
    ["eventCount","eventCountPerUser"],
    ["eventName"], dim_filter=PAID_FILTER,
    order_bys=[{"metric":{"metricName":"eventCount"},"desc":True}], limit=25)
rows7 = extract(r7)
ALL_DATA["paid_events"] = rows7
for r in rows7:
    ev = r.get("eventName","?")
    cnt = int(safe(r.get("eventCount")))
    per = safe(r.get("eventCountPerUser"))
    print(f"  {ev:<35} {cnt:>8} total | {per:.2f} per user")

# 8. PAID source/medium/campaign
print("\n" + "="*80)
print("8. PAID SOURCE/MEDIUM/CAMPAIGN (Last 7 Days)")
print("="*80)
r8 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate","averageSessionDuration","eventsPerSession"],
    ["sessionSource","sessionMedium","sessionCampaignName"], dim_filter=PAID_FILTER,
    order_bys=[{"metric":{"metricName":"sessions"},"desc":True}], limit=20)
rows8 = extract(r8)
ALL_DATA["paid_source_medium_campaign"] = rows8
print(f"{'Source':<18} {'Medium':<12} {'Campaign':<25} {'Sess':>5} {'Bounce':>7} {'Evt/S':>6}")
print("-"*80)
for r in rows8:
    src = r.get("sessionSource","?")[:17]
    med = r.get("sessionMedium","?")[:11]
    camp = r.get("sessionCampaignName","?")[:24]
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    eps = safe(r.get("eventsPerSession"))
    flag = " <<<" if br > 85 and s > 3 else ""
    print(f"{src:<18} {med:<12} {camp:<25} {s:>5} {br:>6.1f}% {eps:>6.1f}{flag}")

# 9. PAID by hour of day
print("\n" + "="*80)
print("9. PAID BOUNCE BY HOUR OF DAY (Last 7 Days)")
print("="*80)
r9 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate"],
    ["hour"], dim_filter=PAID_FILTER,
    order_bys=[{"dimension":{"dimensionName":"hour"},"desc":False}])
rows9 = extract(r9)
ALL_DATA["paid_by_hour"] = rows9
for r in rows9:
    hr = r.get("hour","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    bar = "█" * min(int(s/2), 30)
    print(f"  {hr}:00 | {s:>4} sess | {br:>5.1f}% bounce {bar}")

# 10. PAID mobile browser + OS
print("\n" + "="*80)
print("10. PAID MOBILE BROWSER + OS (Last 7 Days)")
print("="*80)
mob_paid = {"andGroup":{"expressions":[PAID_FILTER,{"filter":{"fieldName":"deviceCategory","stringFilter":{"value":"mobile","matchType":"EXACT"}}}]}}
r10 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate","averageSessionDuration"],
    ["browser","operatingSystem"], dim_filter=mob_paid,
    order_bys=[{"metric":{"metricName":"sessions"},"desc":True}], limit=15)
rows10 = extract(r10)
ALL_DATA["paid_mobile_browser_os"] = rows10
for r in rows10:
    brow = r.get("browser","?")
    opsys = r.get("operatingSystem","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    inapp = " [IN-APP]" if any(x in brow.lower() for x in ["instagram","facebook","webview"]) else ""
    flag = " <<<" if br > 85 and s > 3 else ""
    print(f"  {brow:<25} {opsys:<12} {s:>5} sess | {br:.1f}% bounce{inapp}{flag}")

# 11. Country
print("\n" + "="*80)
print("11. PAID BY COUNTRY (Last 7 Days)")
print("="*80)
r11 = run_report(LAST_7,
    ["sessions","bounceRate","engagementRate","averageSessionDuration"],
    ["country"], dim_filter=PAID_FILTER,
    order_bys=[{"metric":{"metricName":"sessions"},"desc":True}], limit=15)
rows11 = extract(r11)
ALL_DATA["paid_by_country"] = rows11
for r in rows11:
    c = r.get("country","?")
    s = int(safe(r.get("sessions")))
    br = safe(r.get("bounceRate"))*100
    print(f"  {c:<25} {s:>5} sessions | {br:.1f}% bounce")

# Save
with open("/home/.z/workspaces/con_v55GP1lr46UmN5fa/paid-bounce-data.json","w") as f:
    json.dump(ALL_DATA, f, indent=2, default=str)
print(f"\nData saved to paid-bounce-data.json")

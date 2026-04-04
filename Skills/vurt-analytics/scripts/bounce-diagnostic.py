#!/usr/bin/env python3
"""VURT Bounce Rate Spike Diagnostic — April 2, 2026
Investigates whether 97.1% bounce rate is real or a measurement/tracking failure."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ga4_client import get_access_token, run_report, extract_rows, fmt_pct, fmt_num
import json, urllib.request

PROPERTY_ID = "518738893"
DATA_API = "https://analyticsdata.googleapis.com/v1beta"

TODAY = "2026-04-02"
YESTERDAY = "2026-04-01"

def run_report_with_filter(date_ranges, metrics, dimensions=None, dim_filter=None, order_bys=None, limit=None):
    """Extended run_report that supports dimensionFilter."""
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


def section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def pct(val):
    v = float(val)
    return f"{v*100:.1f}%" if v <= 1 else f"{v:.1f}%"


# ─────────────────────────────────────────────────────────────────────────────
# 1) HOURLY BOUNCE RATE: Today vs Yesterday
# ─────────────────────────────────────────────────────────────────────────────
section("1. HOURLY BOUNCE RATE — Today (Apr 2) vs Yesterday (Apr 1)")

hourly = run_report(
    date_ranges=[
        {"startDate": TODAY, "endDate": TODAY, "name": "today"},
        {"startDate": YESTERDAY, "endDate": YESTERDAY, "name": "yesterday"},
    ],
    metrics=["sessions", "bounceRate", "engagedSessions", "engagementRate",
             "averageSessionDuration", "userEngagementDuration"],
    dimensions=["hour"],
    order_bys=[{"dimension": {"dimensionName": "hour", "orderType": "NUMERIC"}, "desc": False}],
)
hourly_rows = extract_rows(hourly)

today_hours = sorted([r for r in hourly_rows if r.get("dateRange") == "today"],
                     key=lambda r: int(r["hour"]))
yest_hours = sorted([r for r in hourly_rows if r.get("dateRange") == "yesterday"],
                    key=lambda r: int(r["hour"]))

# Build lookup for yesterday
yest_lookup = {r["hour"]: r for r in yest_hours}

print(f"{'Hour':>4}  {'Today Sess':>10}  {'Today Bounce':>12}  {'Today Engaged':>13}  {'Yest Sess':>10}  {'Yest Bounce':>12}  {'Yest Engaged':>13}")
print("-" * 90)
for r in today_hours:
    h = r["hour"]
    yl = yest_lookup.get(h, {})
    t_sess = int(float(r.get("sessions", "0")))
    t_br = float(r.get("bounceRate", "0"))
    t_eng = int(float(r.get("engagedSessions", "0")))
    y_sess = int(float(yl.get("sessions", "0")))
    y_br = float(yl.get("bounceRate", "0"))
    y_eng = int(float(yl.get("engagedSessions", "0")))

    flag = " <<<" if t_br > 0.90 and t_sess > 5 else ""
    print(f"{h:>4}  {t_sess:>10}  {t_br*100:>11.1f}%  {t_eng:>13}  {y_sess:>10}  {y_br*100:>11.1f}%  {y_eng:>13}{flag}")

# Also print yesterday hours that today might be missing (future hours)
for r in yest_hours:
    if r["hour"] not in {tr["hour"] for tr in today_hours}:
        h = r["hour"]
        y_sess = int(float(r.get("sessions", "0")))
        y_br = float(r.get("bounceRate", "0"))
        y_eng = int(float(r.get("engagedSessions", "0")))
        print(f"{h:>4}  {'--':>10}  {'--':>12}  {'--':>13}  {y_sess:>10}  {y_br*100:>11.1f}%  {y_eng:>13}")


# ─────────────────────────────────────────────────────────────────────────────
# 2) TODAY'S SESSIONS BY SOURCE/MEDIUM/CAMPAIGN WITH BOUNCE RATE
# ─────────────────────────────────────────────────────────────────────────────
section("2. TODAY'S SESSIONS BY SOURCE/MEDIUM — Bounce Rate per Channel")

source_result = run_report(
    date_ranges=[{"startDate": TODAY, "endDate": TODAY}],
    metrics=["sessions", "bounceRate", "engagedSessions", "engagementRate",
             "averageSessionDuration"],
    dimensions=["sessionSource", "sessionMedium", "sessionCampaignName"],
    order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
    limit=25,
)
source_rows = extract_rows(source_result)

print(f"{'Source':>20}  {'Medium':>12}  {'Campaign':>25}  {'Sessions':>8}  {'Bounce':>8}  {'Engaged':>8}  {'EngRate':>8}  {'AvgDur':>8}")
print("-" * 120)
for r in source_rows:
    src = r.get("sessionSource", "(none)")[:20]
    med = r.get("sessionMedium", "(none)")[:12]
    camp = r.get("sessionCampaignName", "(none)")[:25]
    sess = int(float(r.get("sessions", "0")))
    br = float(r.get("bounceRate", "0"))
    eng = int(float(r.get("engagedSessions", "0")))
    er = float(r.get("engagementRate", "0"))
    dur = float(r.get("averageSessionDuration", "0"))
    flag = " <<<" if br > 0.90 and sess > 3 else ""
    print(f"{src:>20}  {med:>12}  {camp:>25}  {sess:>8}  {br*100:>7.1f}%  {eng:>8}  {er*100:>7.1f}%  {dur:>7.1f}s{flag}")


# ─────────────────────────────────────────────────────────────────────────────
# 3) TODAY'S SESSIONS BY LANDING PAGE WITH BOUNCE RATE
# ─────────────────────────────────────────────────────────────────────────────
section("3. TODAY'S SESSIONS BY LANDING PAGE — Bounce Rate per Page")

page_result = run_report(
    date_ranges=[{"startDate": TODAY, "endDate": TODAY}],
    metrics=["sessions", "bounceRate", "engagedSessions", "engagementRate",
             "averageSessionDuration", "screenPageViews"],
    dimensions=["landingPage"],
    order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
    limit=25,
)
page_rows = extract_rows(page_result)

print(f"{'Landing Page':>50}  {'Sessions':>8}  {'Bounce':>8}  {'Engaged':>8}  {'PgViews':>8}  {'AvgDur':>8}")
print("-" * 100)
for r in page_rows:
    page = r.get("landingPage", "(none)")
    if len(page) > 50:
        page = "..." + page[-47:]
    sess = int(float(r.get("sessions", "0")))
    br = float(r.get("bounceRate", "0"))
    eng = int(float(r.get("engagedSessions", "0")))
    pvs = int(float(r.get("screenPageViews", "0")))
    dur = float(r.get("averageSessionDuration", "0"))
    flag = " <<<" if br > 0.90 and sess > 3 else ""
    print(f"{page:>50}  {sess:>8}  {br*100:>7.1f}%  {eng:>8}  {pvs:>8}  {dur:>7.1f}s{flag}")


# ─────────────────────────────────────────────────────────────────────────────
# 4) TODAY'S SESSIONS BY DEVICE/BROWSER/OS
# ─────────────────────────────────────────────────────────────────────────────
section("4. TODAY'S SESSIONS BY DEVICE CATEGORY / BROWSER / OS")

device_result = run_report(
    date_ranges=[{"startDate": TODAY, "endDate": TODAY}],
    metrics=["sessions", "bounceRate", "engagedSessions", "averageSessionDuration"],
    dimensions=["deviceCategory", "browser", "operatingSystem"],
    order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
    limit=25,
)
device_rows = extract_rows(device_result)

print(f"{'Device':>10}  {'Browser':>15}  {'OS':>15}  {'Sessions':>8}  {'Bounce':>8}  {'Engaged':>8}  {'AvgDur':>8}")
print("-" * 95)
for r in device_rows:
    dev = r.get("deviceCategory", "?")
    brow = r.get("browser", "?")[:15]
    opsys = r.get("operatingSystem", "?")[:15]
    sess = int(float(r.get("sessions", "0")))
    br = float(r.get("bounceRate", "0"))
    eng = int(float(r.get("engagedSessions", "0")))
    dur = float(r.get("averageSessionDuration", "0"))
    flag = " <<<" if br > 0.90 and sess > 3 else ""
    print(f"{dev:>10}  {brow:>15}  {opsys:>15}  {sess:>8}  {br*100:>7.1f}%  {eng:>8}  {dur:>7.1f}s{flag}")


# ─────────────────────────────────────────────────────────────────────────────
# 5) EVENT COUNTS TODAY — Are engagement events firing?
# ─────────────────────────────────────────────────────────────────────────────
section("5. EVENT COUNTS TODAY — Are engagement events firing?")

events_result = run_report(
    date_ranges=[{"startDate": TODAY, "endDate": TODAY}],
    metrics=["eventCount"],
    dimensions=["eventName"],
    order_bys=[{"metric": {"metricName": "eventCount"}, "desc": True}],
    limit=30,
)
events_rows = extract_rows(events_result)

key_events = ["session_start", "first_visit", "page_view", "scroll", "click",
              "user_engagement", "form_start", "form_submit", "file_download",
              "view_search_results"]

print(f"{'Event Name':>30}  {'Count':>10}  {'Notes':>40}")
print("-" * 85)
for r in events_rows:
    name = r.get("eventName", "?")
    count = int(float(r.get("eventCount", "0")))
    note = ""
    if name == "user_engagement" and count == 0:
        note = "CRITICAL: No user_engagement = all bounces!"
    elif name == "session_start":
        note = "Sessions started"
    elif name == "user_engagement":
        note = "GA4 uses this to determine non-bounce"
    print(f"{name:>30}  {count:>10}  {note}")

# Check the critical ratio
ss_count = next((int(float(r.get("eventCount", "0"))) for r in events_rows if r.get("eventName") == "session_start"), 0)
ue_count = next((int(float(r.get("eventCount", "0"))) for r in events_rows if r.get("eventName") == "user_engagement"), 0)
pv_count = next((int(float(r.get("eventCount", "0"))) for r in events_rows if r.get("eventName") == "page_view"), 0)
scroll_count = next((int(float(r.get("eventCount", "0"))) for r in events_rows if r.get("eventName") == "scroll"), 0)
click_count = next((int(float(r.get("eventCount", "0"))) for r in events_rows if r.get("eventName") == "click"), 0)

print(f"\n--- KEY RATIO ---")
print(f"session_start:      {ss_count}")
print(f"user_engagement:    {ue_count}")
print(f"page_view:          {pv_count}")
print(f"scroll:             {scroll_count}")
print(f"click:              {click_count}")
if ss_count > 0:
    ratio = ue_count / ss_count
    print(f"\nuser_engagement / session_start = {ratio:.2%}")
    if ratio < 0.10:
        print(">>> ALERT: user_engagement is firing at <10% of sessions.")
        print(">>> This strongly suggests engagement tracking is BROKEN, not that users are bouncing.")
    elif ratio < 0.30:
        print(">>> WARNING: Engagement ratio is unusually low. Possible partial tracking failure.")
    else:
        print(">>> Engagement ratio looks reasonable — bounce may be genuine.")


# ─────────────────────────────────────────────────────────────────────────────
# 6) EVENT COUNT COMPARISON: Today vs Yesterday
# ─────────────────────────────────────────────────────────────────────────────
section("6. EVENT COUNT COMPARISON — Today vs Yesterday (did tracking break?)")

events_compare = run_report(
    date_ranges=[
        {"startDate": TODAY, "endDate": TODAY, "name": "today"},
        {"startDate": YESTERDAY, "endDate": YESTERDAY, "name": "yesterday"},
    ],
    metrics=["eventCount"],
    dimensions=["eventName"],
    order_bys=[{"metric": {"metricName": "eventCount"}, "desc": True}],
    limit=50,
)
events_cmp_rows = extract_rows(events_compare)

today_events = {r["eventName"]: int(float(r.get("eventCount", "0")))
                for r in events_cmp_rows if r.get("dateRange") == "today"}
yest_events = {r["eventName"]: int(float(r.get("eventCount", "0")))
               for r in events_cmp_rows if r.get("dateRange") == "yesterday"}

all_event_names = sorted(set(list(today_events.keys()) + list(yest_events.keys())),
                         key=lambda n: max(today_events.get(n, 0), yest_events.get(n, 0)),
                         reverse=True)

print(f"{'Event Name':>30}  {'Today':>10}  {'Yesterday':>10}  {'Change':>12}  {'Notes':>30}")
print("-" * 100)
for name in all_event_names[:30]:
    t = today_events.get(name, 0)
    y = yest_events.get(name, 0)
    if y > 0:
        change = ((t - y) / y) * 100
        change_str = f"{change:+.1f}%"
    elif t > 0:
        change_str = "NEW"
    else:
        change_str = "—"

    note = ""
    if name == "user_engagement":
        if y > 0 and t / y < 0.3:
            note = "TRACKING FAILURE?"
        elif t == 0 and y > 0:
            note = "COMPLETELY GONE!"
    elif name in ("scroll", "click") and y > 0 and t == 0:
        note = "STOPPED FIRING"

    print(f"{name:>30}  {t:>10}  {y:>10}  {change_str:>12}  {note}")


# ─────────────────────────────────────────────────────────────────────────────
# 7) SESSIONS WITH 0 ENGAGEMENT TIME — true bounces vs tracking failure
# ─────────────────────────────────────────────────────────────────────────────
section("7. ENGAGEMENT TIME DISTRIBUTION — True Bounces vs Tracking Failure")

# Get engagement time per session for today vs yesterday
eng_time_result = run_report(
    date_ranges=[
        {"startDate": TODAY, "endDate": TODAY, "name": "today"},
        {"startDate": YESTERDAY, "endDate": YESTERDAY, "name": "yesterday"},
    ],
    metrics=["sessions", "engagedSessions", "userEngagementDuration",
             "averageSessionDuration", "bounceRate", "engagementRate"],
)
eng_rows = extract_rows(eng_time_result)

print(f"{'Period':>12}  {'Sessions':>8}  {'Engaged':>8}  {'EngRate':>8}  {'Bounce':>8}  {'EngDur(s)':>10}  {'AvgSessDur':>10}")
print("-" * 80)
for r in eng_rows:
    period = r.get("dateRange", "?")
    sess = int(float(r.get("sessions", "0")))
    eng = int(float(r.get("engagedSessions", "0")))
    er = float(r.get("engagementRate", "0"))
    br = float(r.get("bounceRate", "0"))
    eng_dur = float(r.get("userEngagementDuration", "0"))
    avg_dur = float(r.get("averageSessionDuration", "0"))
    print(f"{period:>12}  {sess:>8}  {eng:>8}  {er*100:>7.1f}%  {br*100:>7.1f}%  {eng_dur:>10.1f}  {avg_dur:>10.1f}")

# Bounced vs non-bounced sessions
for r in eng_rows:
    if r.get("dateRange") == "today":
        t_sess = int(float(r.get("sessions", "0")))
        t_eng = int(float(r.get("engagedSessions", "0")))
        t_bounced = t_sess - t_eng
        t_eng_dur = float(r.get("userEngagementDuration", "0"))
        avg_eng_per_engaged = t_eng_dur / t_eng if t_eng > 0 else 0
        print(f"\nToday: {t_bounced} bounced sessions out of {t_sess} total ({t_bounced/t_sess*100:.1f}% bounced)")
        print(f"Engaged sessions avg engagement: {avg_eng_per_engaged:.1f}s per engaged session")
    if r.get("dateRange") == "yesterday":
        y_sess = int(float(r.get("sessions", "0")))
        y_eng = int(float(r.get("engagedSessions", "0")))
        y_bounced = y_sess - y_eng
        y_eng_dur = float(r.get("userEngagementDuration", "0"))
        avg_eng_per_engaged_y = y_eng_dur / y_eng if y_eng > 0 else 0
        print(f"Yesterday: {y_bounced} bounced sessions out of {y_sess} total ({y_bounced/y_sess*100:.1f}% bounced)")
        print(f"Engaged sessions avg engagement: {avg_eng_per_engaged_y:.1f}s per engaged session")


# ─────────────────────────────────────────────────────────────────────────────
# 8) SESSIONS BY COUNTRY — bot/spam detection
# ─────────────────────────────────────────────────────────────────────────────
section("8. SESSIONS BY COUNTRY — Bot/Spam Traffic Detection")

country_result = run_report(
    date_ranges=[
        {"startDate": TODAY, "endDate": TODAY, "name": "today"},
        {"startDate": YESTERDAY, "endDate": YESTERDAY, "name": "yesterday"},
    ],
    metrics=["sessions", "bounceRate", "engagedSessions", "averageSessionDuration"],
    dimensions=["country"],
    order_bys=[{"metric": {"metricName": "sessions"}, "desc": True}],
    limit=25,
)
country_rows = extract_rows(country_result)

today_countries = sorted([r for r in country_rows if r.get("dateRange") == "today"],
                        key=lambda r: int(float(r.get("sessions", "0"))), reverse=True)
yest_countries = {r["country"]: r for r in country_rows if r.get("dateRange") == "yesterday"}

print(f"{'Country':>25}  {'Today Sess':>10}  {'Today Bounce':>12}  {'Yest Sess':>10}  {'Yest Bounce':>12}  {'Spike?':>8}")
print("-" * 90)
for r in today_countries:
    c = r.get("country", "?")
    t_sess = int(float(r.get("sessions", "0")))
    t_br = float(r.get("bounceRate", "0"))
    yl = yest_countries.get(c, {})
    y_sess = int(float(yl.get("sessions", "0")))
    y_br = float(yl.get("bounceRate", "0"))

    spike = ""
    if y_sess > 0 and t_sess / y_sess > 3:
        spike = "YES +{:.0f}%".format((t_sess/y_sess - 1)*100)
    elif y_sess == 0 and t_sess > 5:
        spike = "NEW!"

    flag = " <<<" if t_br > 0.95 and t_sess > 5 else ""
    print(f"{c:>25}  {t_sess:>10}  {t_br*100:>11.1f}%  {y_sess:>10}  {y_br*100:>11.1f}%  {spike:>8}{flag}")


# ─────────────────────────────────────────────────────────────────────────────
# 9) FINAL DIAGNOSIS
# ─────────────────────────────────────────────────────────────────────────────
section("9. DIAGNOSIS SUMMARY")

# Rebuild key metrics for diagnosis
diag_signals = []

# Signal 1: user_engagement ratio
if ss_count > 0:
    ue_ratio = ue_count / ss_count
    if ue_ratio < 0.10:
        diag_signals.append(("MEASUREMENT ISSUE", f"user_engagement fires at only {ue_ratio:.1%} of sessions (should be ~35-50%+). Engagement tracking is likely broken."))
    elif ue_ratio < 0.25:
        diag_signals.append(("LIKELY MEASUREMENT", f"user_engagement ratio ({ue_ratio:.1%}) is suspiciously low."))

# Signal 2: scroll/click events dropped
y_scroll = yest_events.get("scroll", 0)
t_scroll = today_events.get("scroll", 0)
y_click = yest_events.get("click", 0)
t_click = today_events.get("click", 0)

if y_scroll > 0 and t_scroll == 0:
    diag_signals.append(("TRACKING BROKEN", "scroll events went from {} yesterday to 0 today.".format(y_scroll)))
elif y_scroll > 0 and t_scroll / y_scroll < 0.2:
    diag_signals.append(("TRACKING DEGRADED", f"scroll events dropped {(1-t_scroll/y_scroll)*100:.0f}% vs yesterday."))

if y_click > 0 and t_click == 0:
    diag_signals.append(("TRACKING BROKEN", "click events went from {} yesterday to 0 today.".format(y_click)))
elif y_click > 0 and t_click / y_click < 0.2:
    diag_signals.append(("TRACKING DEGRADED", f"click events dropped {(1-t_click/y_click)*100:.0f}% vs yesterday."))

# Signal 3: user_engagement dropped dramatically
y_ue = yest_events.get("user_engagement", 0)
t_ue = today_events.get("user_engagement", 0)
if y_ue > 0 and t_ue / y_ue < 0.2:
    diag_signals.append(("TRACKING FAILURE", f"user_engagement events dropped {(1-t_ue/y_ue)*100:.0f}% vs yesterday ({t_ue} vs {y_ue})."))

# Signal 4: Unusual country spikes with 100% bounce
for r in today_countries:
    c = r.get("country", "?")
    t_sess = int(float(r.get("sessions", "0")))
    t_br = float(r.get("bounceRate", "0"))
    yl = yest_countries.get(c, {})
    y_sess = int(float(yl.get("sessions", "0")))
    if t_br > 0.95 and t_sess > 10 and (y_sess == 0 or t_sess / max(y_sess, 1) > 5):
        diag_signals.append(("BOT/SPAM TRAFFIC", f"{c}: {t_sess} sessions today (was {y_sess} yesterday) with {t_br*100:.0f}% bounce."))

# Signal 5: single source dominating with high bounce
for r in source_rows[:5]:
    src = r.get("sessionSource", "(none)")
    med = r.get("sessionMedium", "(none)")
    sess = int(float(r.get("sessions", "0")))
    br = float(r.get("bounceRate", "0"))
    total_today_sess = sum(int(float(x.get("sessions", "0"))) for x in source_rows)
    if br > 0.95 and sess > 0.5 * total_today_sess and sess > 10:
        diag_signals.append(("BAD TRAFFIC SOURCE", f"{src}/{med} accounts for {sess}/{total_today_sess} sessions with {br*100:.0f}% bounce."))

if not diag_signals:
    print("No strong diagnostic signals detected. The bounce rate may be genuinely elevated")
    print("due to a mix of factors. Review the hourly and source breakdowns above for patterns.")
else:
    for severity, msg in diag_signals:
        print(f"[{severity}] {msg}")

print()
print("KEY QUESTION ANSWER:")
print("-" * 60)
measurement_signals = sum(1 for s, _ in diag_signals if "MEASUREMENT" in s or "TRACKING" in s)
traffic_signals = sum(1 for s, _ in diag_signals if "BOT" in s or "SPAM" in s or "BAD TRAFFIC" in s)

if measurement_signals > 0:
    print(">>> LIKELY A MEASUREMENT/TRACKING ISSUE")
    print("    GA4 counts a session as 'bounced' if user_engagement event never fires.")
    print("    If the gtag/GTM config broke or enhanced measurement got disabled,")
    print("    GA4 would report ~100% bounce even if users are actually engaging.")
    print()
    print("    RECOMMENDED ACTIONS:")
    print("    1. Check GTM/gtag config — was anything published or changed today?")
    print("    2. Check if Enhanced Measurement is still enabled in GA4 settings")
    print("    3. Use GA4 DebugView or Tag Assistant to verify events fire on page load")
    print("    4. Check site for JS errors that might block analytics scripts")
elif traffic_signals > 0:
    print(">>> LIKELY A TRAFFIC QUALITY ISSUE")
    print("    Unusual traffic patterns suggest bot/spam or a bad campaign driving")
    print("    low-quality visitors who immediately leave.")
    print()
    print("    RECOMMENDED ACTIONS:")
    print("    1. Check for new ad campaigns launched today")
    print("    2. Review referral sources for spam domains")
    print("    3. Consider adding bot filtering in GA4 admin")
else:
    print(">>> INCONCLUSIVE — Review the detailed breakdowns above")
    print("    The bounce spike doesn't show clear tracking failure OR spam patterns.")
    print("    Could be a genuine UX issue (site down, slow loading, etc.).")
    print()
    print("    RECOMMENDED ACTIONS:")
    print("    1. Check if the site/app is actually loading properly")
    print("    2. Check server response times and uptime monitors")
    print("    3. Review any recent deployments or content changes")

print()
print("=" * 80)
print("  END OF DIAGNOSTIC REPORT")
print("=" * 80)

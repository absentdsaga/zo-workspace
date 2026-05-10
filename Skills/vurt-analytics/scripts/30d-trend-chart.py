"""30-day trend chart: daily users vs engagement rate vs rebuffer %."""
import sys, json
from datetime import date, timedelta
sys.path.insert(0, "/home/workspace/Skills/vurt-analytics/scripts")

import ga4_client
import mux_client

DAYS = 30
end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=DAYS - 1)

# --- GA4 daily users + engagement rate ---
ga4 = ga4_client.run_report(
    date_ranges=[{"startDate": start_date.isoformat(), "endDate": end_date.isoformat()}],
    metrics=["activeUsers", "engagementRate", "sessions"],
    dimensions=["date"],
    order_bys=[{"dimension": {"dimensionName": "date"}}],
)
ga4_rows = {}
for r in ga4.get("rows", []):
    d = r["dimensionValues"][0]["value"]  # YYYYMMDD
    iso = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    ga4_rows[iso] = {
        "users": int(r["metricValues"][0]["value"]),
        "eng_rate": float(r["metricValues"][1]["value"]) * 100,
        "sessions": int(r["metricValues"][2]["value"]),
    }

# --- Mux daily views + rebuffer % ---
buf = mux_client.get_daily_buffer_trend(days=DAYS)
views_ts = mux_client._extract_timeseries_pairs(buf["views"])
rebuf_ts = mux_client._extract_timeseries_pairs(buf["rebuffer"])

mux_rows = {}
for ts_ms, val in views_ts:
    iso = date.fromtimestamp(ts_ms / 1000).isoformat()
    mux_rows.setdefault(iso, {})["views"] = float(val or 0)
for ts_ms, val in rebuf_ts:
    iso = date.fromtimestamp(ts_ms / 1000).isoformat()
    mux_rows.setdefault(iso, {})["rebuffer"] = float(val or 0) * 100

# --- Merge ---
all_dates = []
d = start_date
while d <= end_date:
    iso = d.isoformat()
    g = ga4_rows.get(iso, {})
    m = mux_rows.get(iso, {})
    all_dates.append({
        "date": iso,
        "users": g.get("users", 0),
        "eng_rate": g.get("eng_rate", 0),
        "rebuffer": m.get("rebuffer", 0),
        "views": m.get("views", 0),
    })
    d += timedelta(days=1)

with open("/tmp/30d-trend.json", "w") as f:
    json.dump(all_dates, f, indent=2)

print(f"Wrote {len(all_dates)} days to /tmp/30d-trend.json")
print(f"Date range: {start_date} to {end_date}")
print(f"\nFirst 3:")
for r in all_dates[:3]:
    print(r)
print(f"\nLast 3:")
for r in all_dates[-3:]:
    print(r)

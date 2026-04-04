#!/usr/bin/env python3
"""VURT NPAW Buffering & Quality Check v2 -- Full-population analytics.

Two strategies to overcome the ~40 session rawdata cap:
  1. Batch rawdata: Split time range into 30-min windows, query each, stitch + dedupe.
  2. Aggregated /data with groupBy: Get full-population metrics broken down by
     CDN, device, ISP, title, country using the proven groupBy param.

API notes (from npaw_client.py):
  - groupBy param: cdn, device, isp, title, country
  - Metric names are camelCase: plays, views, bufferRatio, errors, uniqueUsers, etc.
  - Date format: YYYY-MM-DD or lastNdays or "yesterday"
  - Grouped response: data[].name = dimension value, data[].metrics[] = metric values

Usage:
  python buffer-check-v2.py --hours 4
  python buffer-check-v2.py --hours 24
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from collections import defaultdict
from datetime import datetime, timedelta, timezone

SYSTEM_CODE = os.environ.get("NPAW_SYSTEM_CODE", "vurt")
API_SECRET = os.environ.get("NPAW_API_SECRET", "")
BASE_URL = "https://api.youbora.com"


# -- Auth -----------------------------------------------------------------
def sign_request(path, params):
    future_time = int(round(time.time() * 1000) + 36000)
    params_with_date = list(params) + [("dateToken", future_time)]
    qs = urllib.parse.urlencode(params_with_date, doseq=True)
    raw = f"{path}?{qs}{API_SECRET}"
    token = hashlib.md5(raw.encode()).hexdigest()
    params_with_date.append(("token", token))
    return params_with_date


def api_get(endpoint, params, label=""):
    path = f"/{SYSTEM_CODE}/{endpoint}"
    signed = sign_request(path, params)
    qs = urllib.parse.urlencode(signed, doseq=True)
    url = f"{BASE_URL}{path}?{qs}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=60)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  [{label or endpoint}] HTTP {e.code}: {body[:400]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [{label or endpoint}] Error: {e}", file=sys.stderr)
        return None


# -- Time helpers ---------------------------------------------------------
def time_windows(hours, window_minutes=30):
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)
    fmt = "%Y-%m-%d %H:%M:%S"
    windows = []
    cursor = start
    while cursor < now:
        win_end = min(cursor + timedelta(minutes=window_minutes), now)
        windows.append((cursor.strftime(fmt), win_end.strftime(fmt)))
        cursor = win_end
    return windows


def last_n_hours(hours):
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)
    fmt = "%Y-%m-%d %H:%M:%S"
    return start.strftime(fmt), now.strftime(fmt)


def date_range_days(days):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


# -- Stats helpers --------------------------------------------------------
def safe_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def avg(lst):
    return sum(lst) / len(lst) if lst else None


def p50(lst):
    if not lst:
        return None
    s = sorted(lst)
    return s[len(s) // 2]


def p95(lst):
    if not lst or len(lst) < 2:
        return max(lst) if lst else None
    s = sorted(lst)
    return s[int(len(s) * 0.95)]


def fmt_pct(val):
    return f"{val:.2f}%" if val is not None else "N/A"


def fmt_sec(ms):
    return f"{ms/1000:.2f}s" if ms is not None else "N/A"


def fmt_sec_raw(s):
    return f"{s:.1f}s" if s is not None else "N/A"


def fmt_val(v):
    if v is None:
        return "N/A"
    try:
        f = float(v)
        if f == int(f) and abs(f) < 1e15:
            return f"{int(f):,}"
        return f"{f:,.2f}"
    except (ValueError, TypeError):
        return str(v)


# -- Printing helpers -----------------------------------------------------
def print_header(title):
    print(f"\n{'='*76}")
    print(f"  {title}")
    print(f"{'='*76}")


def print_table(headers, rows, col_widths=None):
    if not rows:
        print("  (no data)")
        return
    if not col_widths:
        col_widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=5)) + 2
                      for i, h in enumerate(headers)]
    header_line = "  " + "".join(str(h).ljust(w) if i == 0 else str(h).rjust(w)
                                  for i, (h, w) in enumerate(zip(headers, col_widths)))
    print(header_line)
    print("  " + "-" * sum(col_widths))
    for row in rows:
        line = "  " + "".join(str(v).ljust(w) if i == 0 else str(v).rjust(w)
                               for i, (v, w) in enumerate(zip(row, col_widths)))
        print(line)


# -- Aggregated metric extraction -----------------------------------------
def extract_metric_value(data, metric_code):
    """Extract a single aggregate value from a /data response (no groupBy)."""
    if not data or not data.get("data"):
        return None
    for series in data["data"]:
        for m in series.get("metrics", []):
            if m.get("code") == metric_code:
                for v in m.get("values", []):
                    for pt in v.get("data", []):
                        if isinstance(pt, dict):
                            return pt.get("value")
                        elif isinstance(pt, list) and len(pt) >= 2:
                            # [timestamp, value] or [None, value]
                            return pt[1]
    return None


def extract_grouped_metrics(data, group_by_key=None):
    """Parse NPAW grouped response (groupBy=...).

    NPAW grouped responses have a single data[0] block where each metric's
    values[] array contains objects keyed by the dimension name:
      data[0].metrics[].values[] = [{cdn: "CloudFlare", value: 2610}, ...]

    The dimension key in each value object matches the groupBy param name
    (e.g., "cdn", "device", "isp", "title", "country").

    Returns list of dicts: [{name: "CloudFlare", views: 2610, bufferRatio: 1.2, ...}]
    """
    rows_by_name = {}
    if not data or not data.get("data"):
        return []

    for block in data.get("data", []):
        for metric in block.get("metrics", []):
            code = metric.get("code", "")
            for val_obj in metric.get("values", []):
                # Grouped format: each val_obj is {dim_key: "name", value: X}
                if isinstance(val_obj, dict) and "value" in val_obj:
                    # Find the dimension key (it's whatever key isn't "value")
                    dim_name = None
                    for k, v in val_obj.items():
                        if k != "value":
                            if group_by_key and k == group_by_key:
                                dim_name = v
                                break
                            elif not group_by_key and isinstance(v, str):
                                dim_name = v
                                break
                    if dim_name is None:
                        dim_name = "(unknown)"

                    if dim_name not in rows_by_name:
                        rows_by_name[dim_name] = {"name": dim_name}
                    rows_by_name[dim_name][code] = val_obj["value"]

                # Also handle nested data[] format (for daily granularity)
                elif isinstance(val_obj, dict) and "data" in val_obj:
                    for pt in val_obj.get("data", []):
                        if isinstance(pt, dict) and "value" in pt:
                            dim_name = None
                            for k, v in pt.items():
                                if k != "value" and isinstance(v, str):
                                    dim_name = v
                                    break
                            if dim_name is None:
                                dim_name = "(unknown)"
                            if dim_name not in rows_by_name:
                                rows_by_name[dim_name] = {"name": dim_name}
                            # Accumulate for totals, last-write for averages
                            rows_by_name[dim_name][code] = pt["value"]

    return list(rows_by_name.values())


# -- Rawdata session extraction -------------------------------------------
def _extract_sessions(data):
    sessions = []
    if not data or not data.get("data"):
        return sessions
    if isinstance(data["data"], list):
        for entry in data["data"]:
            if isinstance(entry, dict) and "values" in entry:
                sessions.extend(entry["values"])
    elif isinstance(data["data"], dict):
        sessions = data["data"].get("values", [])
    return sessions


def get_session_id(s):
    return s.get("session_id") or s.get("id") or s.get("view_code") or json.dumps(s, sort_keys=True)


# =====================================================================
# APPROACH 1: Batched rawdata queries
# =====================================================================
def batch_rawdata(hours, window_minutes=30):
    """Query /rawdata in small time windows and stitch together.

    Strategy:
    1. Split hours into N-minute windows, query each for up to 40 sessions.
    2. If hours window yields nothing (quiet period), fall back to date-range
       batching over the last 1-2 days in 4-hour chunks.
    """
    windows = time_windows(hours, window_minutes)
    all_sessions = []
    seen_ids = set()
    errors = 0

    print(f"\n  Batching rawdata: {len(windows)} windows of {window_minutes}min each...")

    for i, (win_start, win_end) in enumerate(windows):
        label = f"batch-{i+1}/{len(windows)}"
        data = api_get("rawdata", [
            ("fromDate", win_start), ("toDate", win_end),
            ("timezone", "America/New_York"),
        ], label=label)

        sessions = _extract_sessions(data)
        new_count = 0
        for s in sessions:
            sid = get_session_id(s)
            if sid not in seen_ids:
                seen_ids.add(sid)
                all_sessions.append(s)
                new_count += 1

        if sessions:
            print(f"    Window {i+1:>3}/{len(windows)}: {win_start[11:16]}-{win_end[11:16]} UTC -> "
                  f"{len(sessions)} raw, {new_count} new (total: {len(all_sessions)})")
        elif data is None:
            errors += 1
            print(f"    Window {i+1:>3}/{len(windows)}: {win_start[11:16]}-{win_end[11:16]} UTC -> ERROR")

    # Fallback: if no sessions in the hourly windows, batch over wider date range
    if not all_sessions:
        print(f"\n  No sessions in {hours}h window. Falling back to 1-day date-range batching (4h chunks)...")
        fallback_windows = time_windows(24, window_minutes=240)  # 4-hour chunks over 1 day
        for i, (win_start, win_end) in enumerate(fallback_windows):
            label = f"fallback-{i+1}/{len(fallback_windows)}"
            data = api_get("rawdata", [
                ("fromDate", win_start), ("toDate", win_end),
                ("timezone", "America/New_York"),
            ], label=label)

            sessions = _extract_sessions(data)
            new_count = 0
            for s in sessions:
                sid = get_session_id(s)
                if sid not in seen_ids:
                    seen_ids.add(sid)
                    all_sessions.append(s)
                    new_count += 1

            if sessions:
                print(f"    Fallback {i+1:>2}/{len(fallback_windows)}: {win_start[11:16]}-{win_end[11:16]} UTC -> "
                      f"{len(sessions)} raw, {new_count} new (total: {len(all_sessions)})")
            elif data is None:
                errors += 1

    print(f"\n  Batch complete: {len(all_sessions)} unique sessions ({errors} errors)")
    return all_sessions


# =====================================================================
# APPROACH 2: Aggregated /data with groupBy
# =====================================================================
def query_aggregated_totals(hours):
    """Get overall aggregated totals from /data endpoint."""
    start, end = last_n_hours(hours)
    # Use camelCase metric names as per npaw_client.py
    metrics = "plays,views,playtime,bufferRatio,errors,uniqueUsers,startup_time,join_time,bitrate,throughput"

    data = api_get("data", [
        ("metrics", metrics),
        ("fromDate", start), ("toDate", end),
        ("timezone", "America/New_York"),
    ], label="agg-totals-hours")

    if data:
        plays = extract_metric_value(data, "plays")
        if plays and plays > 0:
            return data, metrics, f"last {hours}h"

    # Fallback: try date-range format for wider window
    start_d, end_d = date_range_days(max(1, hours // 24))
    data = api_get("data", [
        ("metrics", metrics),
        ("fromDate", start_d), ("toDate", end_d),
        ("timezone", "America/New_York"),
    ], label="agg-totals-days")

    if data:
        plays = extract_metric_value(data, "plays")
        if plays and plays > 0:
            return data, metrics, f"{start_d} to {end_d}"

    return data, metrics, f"last {hours}h (no plays)"


def query_grouped(group_by, hours, metrics=None, limit=20):
    """Query /data with groupBy parameter. Returns parsed rows."""
    if not metrics:
        metrics = "views,bufferRatio,errors"
    start, end = last_n_hours(hours)

    # Try datetime format first
    data = api_get("data", [
        ("metrics", metrics),
        ("fromDate", start), ("toDate", end),
        ("groupBy", group_by),
        ("limit", str(limit)),
        ("timezone", "America/New_York"),
    ], label=f"groupBy-{group_by}-hours")

    rows = extract_grouped_metrics(data, group_by_key=group_by)
    if rows and any(r.get("views") for r in rows):
        return rows, f"last {hours}h"

    # Fallback to date format
    start_d, end_d = date_range_days(max(1, hours // 24))
    data = api_get("data", [
        ("metrics", metrics),
        ("fromDate", start_d), ("toDate", end_d),
        ("groupBy", group_by),
        ("limit", str(limit)),
        ("timezone", "America/New_York"),
    ], label=f"groupBy-{group_by}-days")

    rows = extract_grouped_metrics(data, group_by_key=group_by)
    if rows:
        return rows, f"{start_d} to {end_d}"

    return [], "no data"


def print_grouped_table(rows, dim_label, top_n=10):
    """Print a grouped breakdown table."""
    sorted_rows = sorted(rows, key=lambda r: float(r.get("views") or 0), reverse=True)[:top_n]

    headers = [dim_label, "Views", "Buf Ratio", "Errors", "Err Rate"]
    widths = [32, 10, 12, 10, 10]
    table_rows = []
    for r in sorted_rows:
        views = r.get("views")
        buf = r.get("bufferRatio")
        errs = r.get("errors")
        views_f = float(views or 0)
        errs_f = float(errs or 0)
        err_rate = f"{errs_f/views_f*100:.1f}%" if views_f > 0 else "N/A"
        table_rows.append([
            str(r.get("name", "?"))[:31],
            fmt_val(views),
            f"{float(buf):.2f}%" if buf is not None else "N/A",
            fmt_val(errs),
            err_rate,
        ])
    print_table(headers, table_rows, widths)
    return sorted_rows


# =====================================================================
# Session-level analysis (from batched rawdata)
# =====================================================================
def analyze_sessions(sessions):
    all_buf_ratios = []
    all_buf_times_ms = []
    all_buf_counts = []
    all_startup_ms = []
    all_play_times_s = []
    all_happiness = []
    error_count = 0

    by_cdn = defaultdict(lambda: {"buf_ratios": [], "buf_times_ms": [], "startup_ms": [], "count": 0, "errors": 0})
    by_device = defaultdict(lambda: {"buf_ratios": [], "startup_ms": [], "count": 0})
    by_isp = defaultdict(lambda: {"buf_ratios": [], "startup_ms": [], "count": 0})
    by_title = defaultdict(lambda: {"buf_ratios": [], "buf_times_ms": [], "count": 0})
    by_country = defaultdict(lambda: {"buf_ratios": [], "count": 0})

    for s in sessions:
        br = safe_float(s.get("buffer_ratio"))
        bt = safe_float(s.get("buffer_underrun_total"))
        bu = safe_float(s.get("buffer_underruns"))
        st = safe_float(s.get("startup_time"))
        pt = safe_float(s.get("play_time"))
        hs = safe_float(s.get("happiness_score"))

        if br is not None: all_buf_ratios.append(br)
        if bt is not None: all_buf_times_ms.append(bt)
        if bu is not None: all_buf_counts.append(bu)
        if st is not None: all_startup_ms.append(st)
        if pt is not None: all_play_times_s.append(pt)
        if hs is not None: all_happiness.append(hs)
        if s.get("error_code"): error_count += 1

        cdn = s.get("cdn") or "Unknown"
        by_cdn[cdn]["count"] += 1
        if br is not None: by_cdn[cdn]["buf_ratios"].append(br)
        if bt is not None: by_cdn[cdn]["buf_times_ms"].append(bt)
        if st is not None: by_cdn[cdn]["startup_ms"].append(st)
        if s.get("error_code"): by_cdn[cdn]["errors"] += 1

        dev = s.get("device", {}) or {}
        dev_type = dev.get("device_type") or "Unknown"
        by_device[dev_type]["count"] += 1
        if br is not None: by_device[dev_type]["buf_ratios"].append(br)
        if st is not None: by_device[dev_type]["startup_ms"].append(st)

        loc = s.get("location", {}) or {}
        isp = loc.get("isp") or s.get("isp") or "Unknown"
        by_isp[isp]["count"] += 1
        if br is not None: by_isp[isp]["buf_ratios"].append(br)
        if st is not None: by_isp[isp]["startup_ms"].append(st)

        ep = (s.get("extraparams") or {}).get("extraparam4", "") or "Unknown"
        by_title[ep]["count"] += 1
        if br is not None: by_title[ep]["buf_ratios"].append(br)
        if bt is not None: by_title[ep]["buf_times_ms"].append(bt)

        country = loc.get("country") or "Unknown"
        by_country[country]["count"] += 1
        if br is not None: by_country[country]["buf_ratios"].append(br)

    n = len(sessions)

    print(f"\n    Total sessions:          {n}")
    print(f"    Buffer Ratio (avg):      {fmt_pct(avg(all_buf_ratios))}")
    print(f"    Buffer Ratio (median):   {fmt_pct(p50(all_buf_ratios))}")
    print(f"    Buffer Ratio (p95):      {fmt_pct(p95(all_buf_ratios))}")
    print(f"    Buffer Time (avg):       {fmt_sec(avg(all_buf_times_ms))}")
    if all_buf_counts:
        print(f"    Buffer Underruns (avg):  {avg(all_buf_counts):.1f}")
    print(f"    Startup Time (avg):      {fmt_sec(avg(all_startup_ms))}")
    print(f"    Startup Time (p95):      {fmt_sec(p95(all_startup_ms))}")
    print(f"    Avg Play Time:           {fmt_sec_raw(avg(all_play_times_s))}")
    if all_happiness:
        print(f"    Happiness Score (avg):   {avg(all_happiness):.1f}/10")
    print(f"    Error Sessions:          {error_count}/{n} ({error_count/max(n,1)*100:.1f}%)")

    buffered = [r for r in all_buf_ratios if r > 0]
    print(f"\n    Sessions with ANY buffering: {len(buffered)}/{len(all_buf_ratios)}")
    if buffered:
        print(f"      Avg buffer ratio (buffered only): {fmt_pct(avg(buffered))}")
        buf_times_nonzero = [t for t in all_buf_times_ms if t > 0]
        if buf_times_nonzero:
            print(f"      Avg buffer time (buffered only):  {fmt_sec(avg(buf_times_nonzero))}")

    # CDN breakdown
    print(f"\n  By CDN (rawdata):")
    headers = ["CDN", "Sessions", "Buf%(avg)", "Buf%(p95)", "Startup(avg)", "Errors"]
    widths = [20, 10, 12, 12, 14, 8]
    rows = []
    for cdn, d in sorted(by_cdn.items(), key=lambda x: -x[1]["count"]):
        rows.append([cdn, d["count"], fmt_pct(avg(d["buf_ratios"])), fmt_pct(p95(d["buf_ratios"])),
                      fmt_sec(avg(d["startup_ms"])), d["errors"]])
    print_table(headers, rows, widths)

    # Device breakdown
    print(f"\n  By Device (rawdata):")
    headers = ["Device", "Sessions", "Buf%(avg)", "Buf%(p95)", "Startup(avg)"]
    widths = [22, 10, 12, 12, 14]
    rows = []
    for dev, d in sorted(by_device.items(), key=lambda x: -x[1]["count"]):
        rows.append([dev, d["count"], fmt_pct(avg(d["buf_ratios"])), fmt_pct(p95(d["buf_ratios"])),
                      fmt_sec(avg(d["startup_ms"]))])
    print_table(headers, rows, widths)

    # ISP breakdown (top 10)
    print(f"\n  By ISP (rawdata, top 10):")
    headers = ["ISP", "Sessions", "Buf%(avg)", "Startup(avg)"]
    widths = [32, 10, 12, 14]
    rows = []
    for isp, d in sorted(by_isp.items(), key=lambda x: -x[1]["count"])[:10]:
        rows.append([isp[:31], d["count"], fmt_pct(avg(d["buf_ratios"])), fmt_sec(avg(d["startup_ms"]))])
    print_table(headers, rows, widths)

    # Title breakdown (top 10)
    print(f"\n  By Title (rawdata, top 10):")
    headers = ["Title", "Sessions", "Buf%(avg)", "BufTime(avg)"]
    widths = [30, 10, 12, 14]
    rows = []
    for title, d in sorted(by_title.items(), key=lambda x: -x[1]["count"])[:10]:
        rows.append([title[:29], d["count"], fmt_pct(avg(d["buf_ratios"])), fmt_sec(avg(d["buf_times_ms"]))])
    print_table(headers, rows, widths)

    # Country breakdown (top 10)
    print(f"\n  By Country (rawdata, top 10):")
    headers = ["Country", "Sessions", "Buf%(avg)"]
    widths = [22, 10, 12]
    rows = []
    for country, d in sorted(by_country.items(), key=lambda x: -x[1]["count"])[:10]:
        rows.append([country[:21], d["count"], fmt_pct(avg(d["buf_ratios"]))])
    print_table(headers, rows, widths)

    return {
        "total": n,
        "buf_ratio_avg": avg(all_buf_ratios),
        "plays_with_buffer": len(buffered),
        "startup_avg_ms": avg(all_startup_ms),
    }


# =====================================================================
# Main
# =====================================================================
def main():
    if not API_SECRET:
        print("ERROR: NPAW_API_SECRET not set in environment.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="VURT NPAW Buffer Check v2 -- Full-population analytics")
    parser.add_argument("--hours", type=int, default=4, help="Time window in hours (default: 4)")
    parser.add_argument("--window", type=int, default=30, help="Batch window size in minutes (default: 30)")
    args = parser.parse_args()

    hours = args.hours
    window_min = args.window
    now = datetime.now(timezone.utc)

    print(f"\n{'#'*76}")
    print(f"  VURT NPAW BUFFER CHECK v2 -- Full-Population Analytics")
    print(f"{'#'*76}")
    print(f"  Run at:    {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"  Window:    last {hours} hours")
    print(f"  System:    {SYSTEM_CODE}")
    print(f"  Strategy:  Batched rawdata ({window_min}min windows) + Aggregated /data with groupBy")

    # ==================================================================
    # SECTION 1: Aggregated totals (/data -- full population)
    # ==================================================================
    print_header("1. AGGREGATED TOTALS (/data -- full population)")

    agg_data, metrics_used, agg_window = query_aggregated_totals(hours)

    agg_totals = {}
    if agg_data:
        print(f"\n  Data window: {agg_window}")
        for code in metrics_used.split(","):
            val = extract_metric_value(agg_data, code)
            if val is not None:
                agg_totals[code] = val
                if "Ratio" in code or "ratio" in code:
                    print(f"    {code:<25} {val:.2f}%")
                elif code == "playtime":
                    print(f"    {code:<25} {val:.2f} min")
                elif "time" in code or "Time" in code:
                    print(f"    {code:<25} {fmt_sec(val)}")
                elif code in ("bitrate", "throughput"):
                    print(f"    {code:<25} {val:.2f} Mbps")
                else:
                    print(f"    {code:<25} {val:,.0f}")
        if not agg_totals:
            print("    No aggregated metric values returned.")
    else:
        print("    Failed to get aggregated totals.")

    total_plays_agg = agg_totals.get("plays", agg_totals.get("views", 0))
    print(f"\n    ** Total sessions (aggregated): {total_plays_agg:,.0f} **")

    # ==================================================================
    # SECTION 2: Buffer ratio by CDN (groupBy=cdn)
    # ==================================================================
    print_header("2. BUFFER RATIO BY CDN (groupBy=cdn, full population)")

    cdn_rows, cdn_window = query_grouped("cdn", hours,
                                          metrics="views,bufferRatio,errors")
    if cdn_rows:
        print(f"  Data window: {cdn_window}")
        print_grouped_table(cdn_rows, "CDN")
    else:
        print("  No CDN breakdown data returned.")

    # ==================================================================
    # SECTION 3: Buffer ratio by Device (groupBy=device)
    # ==================================================================
    print_header("3. BUFFER RATIO BY DEVICE (groupBy=device, full population)")

    dev_rows, dev_window = query_grouped("device", hours,
                                          metrics="views,bufferRatio,errors,completionRate")
    if dev_rows:
        print(f"  Data window: {dev_window}")
        print_grouped_table(dev_rows, "Device")
    else:
        print("  No Device breakdown data returned.")

    # ==================================================================
    # SECTION 4: Buffer ratio by ISP (groupBy=isp)
    # ==================================================================
    print_header("4. BUFFER RATIO BY ISP (groupBy=isp, full population)")

    isp_rows, isp_window = query_grouped("isp", hours,
                                          metrics="views,bufferRatio,errors",
                                          limit=15)
    if isp_rows:
        print(f"  Data window: {isp_window}")
        print_grouped_table(isp_rows, "ISP", top_n=10)
    else:
        print("  No ISP breakdown data returned.")

    # ==================================================================
    # SECTION 5: Buffer ratio by Title (groupBy=title)
    # ==================================================================
    print_header("5. BUFFER RATIO BY TITLE (groupBy=title, full population)")

    title_rows, title_window = query_grouped("title", hours,
                                              metrics="views,bufferRatio,errors,completionRate",
                                              limit=20)
    if title_rows:
        print(f"  Data window: {title_window}")
        print_grouped_table(title_rows, "Title", top_n=10)
    else:
        print("  No Title breakdown data returned.")

    # ==================================================================
    # SECTION 5b: Buffer ratio by Country (groupBy=country)
    # ==================================================================
    print_header("5b. BUFFER RATIO BY COUNTRY (groupBy=country, full population)")

    country_rows, country_window = query_grouped("country", hours,
                                                  metrics="views,bufferRatio,errors",
                                                  limit=15)
    if country_rows:
        print(f"  Data window: {country_window}")
        print_grouped_table(country_rows, "Country", top_n=10)
    else:
        print("  No Country breakdown data returned.")

    # ==================================================================
    # SECTION 6: Batched rawdata (all sessions stitched)
    # ==================================================================
    print_header(f"6. BATCHED RAWDATA SESSION DETAIL ({window_min}min windows)")

    all_sessions = batch_rawdata(hours, window_minutes=window_min)

    rawdata_stats = None
    if all_sessions:
        rawdata_stats = analyze_sessions(all_sessions)

        # Worst buffering sessions
        print(f"\n  Worst Buffering Sessions (top 15):")
        worst = sorted(all_sessions, key=lambda s: -(safe_float(s.get("buffer_ratio")) or 0))[:15]
        headers = ["Title", "Buf%", "BufTime", "Underruns", "CDN", "Device", "Country"]
        widths = [30, 10, 10, 10, 14, 14, 12]
        rows = []
        for s in worst:
            br = safe_float(s.get("buffer_ratio")) or 0
            if br <= 0:
                break
            bt = safe_float(s.get("buffer_underrun_total")) or 0
            bu = safe_float(s.get("buffer_underruns")) or 0
            title = (s.get("title") or "?")[:29]
            cdn = s.get("cdn", "?")[:13]
            dev = (s.get("device", {}) or {}).get("device_type", "?")[:13]
            country = ((s.get("location", {}) or {}).get("country", "?"))[:11]
            rows.append([title, f"{br:.1f}%", f"{bt/1000:.1f}s", int(bu), cdn, dev, country])
        print_table(headers, rows, widths)
    else:
        print("  No sessions found in any batch window.")

    # ==================================================================
    # SECTION 7: Summary comparison
    # ==================================================================
    print_header("7. SUMMARY COMPARISON: Aggregated vs Rawdata Sample")

    print(f"\n    {'Metric':<35} {'Aggregated (/data)':>20} {'Rawdata (batched)':>20}")
    print(f"    {'-'*75}")

    raw_total = rawdata_stats["total"] if rawdata_stats else 0
    print(f"    {'Total Plays/Sessions':<35} {total_plays_agg:>20,.0f} {raw_total:>20,}")

    coverage = (raw_total / total_plays_agg * 100) if total_plays_agg > 0 else 0
    print(f"    {'Rawdata Coverage':<35} {'':>20} {coverage:>19.1f}%")

    agg_br = agg_totals.get("bufferRatio")
    raw_br = rawdata_stats.get("buf_ratio_avg") if rawdata_stats else None
    agg_br_str = f"{agg_br:.2f}%" if agg_br is not None else "N/A"
    raw_br_str = f"{raw_br:.2f}%" if raw_br is not None else "N/A"
    print(f"    {'Buffer Ratio (avg)':<35} {agg_br_str:>20} {raw_br_str:>20}")

    agg_st = agg_totals.get("startup_time") or agg_totals.get("join_time")
    raw_st = rawdata_stats.get("startup_avg_ms") if rawdata_stats else None
    agg_st_str = fmt_sec(agg_st) if agg_st is not None else "N/A"
    raw_st_str = fmt_sec(raw_st) if raw_st is not None else "N/A"
    print(f"    {'Startup Time (avg)':<35} {agg_st_str:>20} {raw_st_str:>20}")

    # CDN comparison (aggregated vs rawdata)
    if cdn_rows and rawdata_stats:
        print(f"\n  CDN Comparison (aggregated vs rawdata sample):")
        for agg_row in sorted(cdn_rows, key=lambda r: float(r.get("views") or 0), reverse=True)[:5]:
            cdn_name = agg_row.get("name", "?")
            agg_buf = agg_row.get("bufferRatio")
            agg_views = agg_row.get("views")
            print(f"    {cdn_name:<20} Agg: {fmt_val(agg_views)} views, "
                  f"buf={float(agg_buf):.2f}%" if agg_buf is not None else f"    {cdn_name:<20} Agg: {fmt_val(agg_views)} views, buf=N/A")

    print(f"\n{'#'*76}")
    print(f"  DONE -- v2 full-population check complete")
    print(f"{'#'*76}\n")


if __name__ == "__main__":
    main()

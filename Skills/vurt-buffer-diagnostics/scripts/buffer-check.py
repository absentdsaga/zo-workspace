#!/usr/bin/env python3
"""VURT NPAW Buffering & Quality Check -- last 4 hours (with 1-day fallback).

Pulls data from both /data (aggregated totals) and /rawdata (session-level detail).
NPAW buffer_ratio is on a 0-100 scale (percentage).
buffer_underrun_total is in milliseconds.

The /data endpoint returns plays/views/playtime accurately but does NOT return
buffer metrics for dimension breakdowns. All CDN/device/ISP/platform breakdowns
come from the /rawdata session sample (~40 sessions).
"""

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


# ── Auth ────────────────────────────────────────────────────────────────
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
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  [{label or endpoint}] HTTP {e.code}: {body[:300]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [{label or endpoint}] Error: {e}", file=sys.stderr)
        return None


# ── Time helpers ────────────────────────────────────────────────────────
def last_n_hours(hours=4):
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)
    fmt = "%Y-%m-%d %H:%M:%S"
    return start.strftime(fmt), now.strftime(fmt)


def date_range_days(days=1):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


# ── Aggregated helpers ──────────────────────────────────────────────────
def extract_metric_value(data, metric_code):
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
                            if pt[0] is None:
                                return pt[1]
    return None


# ── Rawdata fetcher ─────────────────────────────────────────────────────
def get_sessions(hours=4, fallback_days=1):
    """Try to get sessions from the last N hours; fall back to 1 day if empty."""
    start, end = last_n_hours(hours)
    data = api_get("rawdata", [
        ("fromDate", start), ("toDate", end), ("timezone", "America/New_York"),
    ], label=f"rawdata-{hours}h")

    sessions = _extract_sessions(data)
    window_label = f"last {hours}h"

    if not sessions and fallback_days:
        print(f"  No sessions in {hours}h window. Falling back to {fallback_days}-day window...")
        start2, end2 = date_range_days(fallback_days)
        data2 = api_get("rawdata", [
            ("fromDate", start2), ("toDate", end2), ("timezone", "America/New_York"),
        ], label=f"rawdata-{fallback_days}d")
        sessions = _extract_sessions(data2)
        window_label = f"last {fallback_days} day(s)"

    return sessions, window_label


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


# ── Stats helpers ───────────────────────────────────────────────────────
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
    """Format milliseconds as seconds."""
    return f"{ms/1000:.2f}s" if ms is not None else "N/A"


def fmt_sec_raw(s):
    """Format raw seconds."""
    return f"{s:.1f}s" if s is not None else "N/A"


# ── Printing helpers ────────────────────────────────────────────────────
def print_header(title):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


def print_table(headers, rows, col_widths=None):
    """Print a formatted table."""
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


# ── Main report ─────────────────────────────────────────────────────────
def main():
    if not API_SECRET:
        print("ERROR: NPAW_API_SECRET not set in environment.", file=sys.stderr)
        sys.exit(1)

    hours = 4
    now = datetime.now(timezone.utc)
    print(f"\n  VURT NPAW BUFFERING & QUALITY CHECK")
    print(f"  Run at: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"  Window: last {hours} hours (1-day fallback if no recent data)")
    print(f"  System: {SYSTEM_CODE}")

    # ════════════════════════════════════════════════════════════════════
    # SECTION 1: Aggregated totals from /data endpoint
    # ════════════════════════════════════════════════════════════════════
    print_header("1. AGGREGATED TOTALS (/data endpoint)")

    agg_metrics = "plays,views,playtime,buffer_ratio,buffer_time,startup_time,join_time,error_ratio,bitrate,throughput"

    # Try 4h first
    start4, end4 = last_n_hours(hours)
    data_4h = api_get("data", [
        ("metrics", agg_metrics), ("fromDate", start4), ("toDate", end4),
        ("timezone", "America/New_York"),
    ], label="data-4h")

    plays_4h = extract_metric_value(data_4h, "plays") or 0
    if plays_4h > 0:
        print(f"\n  Data from last {hours}h:")
        for code in agg_metrics.split(","):
            val = extract_metric_value(data_4h, code)
            if val is not None:
                if "ratio" in code:
                    print(f"    {code:<25} {val:.2f}%")
                elif "time" in code:
                    print(f"    {code:<25} {val:.2f} min" if code == "playtime" else f"    {code:<25} {fmt_sec(val)}")
                elif code in ("bitrate", "throughput"):
                    print(f"    {code:<25} {val:.2f} Mbps")
                else:
                    print(f"    {code:<25} {val:,.0f}")
    else:
        print(f"\n  No plays in last {hours}h. Showing 1-day totals:")
        start1d, end1d = date_range_days(1)
        data_1d = api_get("data", [
            ("metrics", agg_metrics), ("fromDate", start1d), ("toDate", end1d),
            ("timezone", "America/New_York"),
        ], label="data-1d")
        for code in agg_metrics.split(","):
            val = extract_metric_value(data_1d, code)
            if val is not None:
                if "ratio" in code:
                    print(f"    {code:<25} {val:.2f}%")
                elif "time" in code:
                    print(f"    {code:<25} {val:.2f} min" if code == "playtime" else f"    {code:<25} {fmt_sec(val)}")
                elif code in ("bitrate", "throughput"):
                    print(f"    {code:<25} {val:.2f} Mbps")
                else:
                    print(f"    {code:<25} {val:,.0f}")

    # ════════════════════════════════════════════════════════════════════
    # SECTION 2-5: Session-level breakdowns from /rawdata
    # ════════════════════════════════════════════════════════════════════
    sessions, window_label = get_sessions(hours, fallback_days=1)

    if not sessions:
        print("\n  No raw sessions found in any window. Cannot produce breakdowns.")
        return

    n = len(sessions)
    print_header(f"2. OVERALL BUFFER & QUALITY (from {n}-session sample, {window_label})")

    # Parse all sessions
    all_buf_ratios = []       # 0-100 scale (percentage)
    all_buf_times_ms = []     # buffer_underrun_total in ms
    all_buf_counts = []       # buffer_underruns count
    all_startup_ms = []
    all_play_times_s = []
    all_happiness = []
    error_count = 0

    by_cdn = defaultdict(lambda: {"buf_ratios": [], "buf_times_ms": [], "buf_counts": [],
                                   "startup_ms": [], "play_s": [], "count": 0, "errors": 0})
    by_device = defaultdict(lambda: {"buf_ratios": [], "startup_ms": [], "count": 0})
    by_os = defaultdict(lambda: {"buf_ratios": [], "startup_ms": [], "count": 0})
    by_isp = defaultdict(lambda: {"buf_ratios": [], "startup_ms": [], "count": 0})
    by_title = defaultdict(lambda: {"buf_ratios": [], "buf_times_ms": [], "count": 0})

    for s in sessions:
        br = safe_float(s.get("buffer_ratio"))         # 0-100 pct
        bt = safe_float(s.get("buffer_underrun_total")) # ms
        bu = safe_float(s.get("buffer_underruns"))      # count
        st = safe_float(s.get("startup_time"))          # ms
        pt = safe_float(s.get("play_time"))             # seconds
        hs = safe_float(s.get("happiness_score"))

        if br is not None:
            all_buf_ratios.append(br)
        if bt is not None:
            all_buf_times_ms.append(bt)
        if bu is not None:
            all_buf_counts.append(bu)
        if st is not None:
            all_startup_ms.append(st)
        if pt is not None:
            all_play_times_s.append(pt)
        if hs is not None:
            all_happiness.append(hs)
        if s.get("error_code"):
            error_count += 1

        # CDN
        cdn = s.get("cdn") or "Unknown"
        by_cdn[cdn]["count"] += 1
        if br is not None: by_cdn[cdn]["buf_ratios"].append(br)
        if bt is not None: by_cdn[cdn]["buf_times_ms"].append(bt)
        if bu is not None: by_cdn[cdn]["buf_counts"].append(bu)
        if st is not None: by_cdn[cdn]["startup_ms"].append(st)
        if pt is not None: by_cdn[cdn]["play_s"].append(pt)
        if s.get("error_code"): by_cdn[cdn]["errors"] += 1

        # Device
        dev = s.get("device", {}) or {}
        dev_type = dev.get("device_type") or "Unknown"
        by_device[dev_type]["count"] += 1
        if br is not None: by_device[dev_type]["buf_ratios"].append(br)
        if st is not None: by_device[dev_type]["startup_ms"].append(st)

        # OS
        os_name = dev.get("os") or "Unknown"
        by_os[os_name]["count"] += 1
        if br is not None: by_os[os_name]["buf_ratios"].append(br)
        if st is not None: by_os[os_name]["startup_ms"].append(st)

        # ISP
        loc = s.get("location", {}) or {}
        isp = loc.get("isp") or s.get("isp") or "Unknown"
        if isp:
            by_isp[isp]["count"] += 1
            if br is not None: by_isp[isp]["buf_ratios"].append(br)
            if st is not None: by_isp[isp]["startup_ms"].append(st)

        # Show/title (extraparam4 = show name)
        ep = (s.get("extraparams") or {}).get("extraparam4", "") or "Unknown"
        by_title[ep]["count"] += 1
        if br is not None: by_title[ep]["buf_ratios"].append(br)
        if bt is not None: by_title[ep]["buf_times_ms"].append(bt)

    # ── Print overall ──
    print(f"\n    Buffer Ratio (avg):      {fmt_pct(avg(all_buf_ratios))}")
    print(f"    Buffer Ratio (median):   {fmt_pct(p50(all_buf_ratios))}")
    print(f"    Buffer Ratio (p95):      {fmt_pct(p95(all_buf_ratios))}")
    print(f"    Buffer Time (avg):       {fmt_sec(avg(all_buf_times_ms))}")
    print(f"    Buffer Underruns (avg):  {avg(all_buf_counts):.1f}" if all_buf_counts else "    Buffer Underruns:        N/A")
    print(f"    Startup Time (avg):      {fmt_sec(avg(all_startup_ms))}")
    print(f"    Startup Time (p95):      {fmt_sec(p95(all_startup_ms))}")
    print(f"    Avg Play Time:           {fmt_sec_raw(avg(all_play_times_s))}")
    if all_happiness:
        print(f"    Happiness Score (avg):   {avg(all_happiness):.1f}/10")
    print(f"    Error Sessions:          {error_count}/{n} ({error_count/max(n,1)*100:.1f}%)")

    # Sessions with buffering
    buffered = [r for r in all_buf_ratios if r > 0]
    print(f"\n    Sessions with ANY buffering: {len(buffered)}/{len(all_buf_ratios)}")
    if buffered:
        print(f"    Among buffered sessions:")
        print(f"      Avg buffer ratio:  {fmt_pct(avg(buffered))}")
        print(f"      Avg buffer time:   {fmt_sec(avg([t for t in all_buf_times_ms if t > 0]))}")

    # ════════════════════════════════════════════════════════════════════
    print_header(f"3. BUFFER RATIO BY CDN ({window_label})")
    # ════════════════════════════════════════════════════════════════════
    headers = ["CDN", "Sessions", "Buf Ratio", "Buf Ratio(p95)", "Buf Time(avg)", "Buf Events", "Startup", "Errors"]
    widths = [20, 10, 12, 15, 15, 12, 12, 8]
    rows = []
    for cdn, d in sorted(by_cdn.items(), key=lambda x: -x[1]["count"]):
        rows.append([
            cdn,
            d["count"],
            fmt_pct(avg(d["buf_ratios"])),
            fmt_pct(p95(d["buf_ratios"])),
            fmt_sec(avg(d["buf_times_ms"])),
            f"{avg(d['buf_counts']):.1f}" if d["buf_counts"] else "N/A",
            fmt_sec(avg(d["startup_ms"])),
            d["errors"],
        ])
    print_table(headers, rows, widths)

    # Fastly vs CloudFlare comparison
    if "Fastly" in by_cdn and "CloudFlare" in by_cdn:
        f = by_cdn["Fastly"]
        c = by_cdn["CloudFlare"]
        print(f"\n  ** Fastly vs CloudFlare comparison **")
        print(f"     Fastly:     {f['count']} sessions, avg buf ratio {fmt_pct(avg(f['buf_ratios']))}, "
              f"avg buf time {fmt_sec(avg(f['buf_times_ms']))}, "
              f"avg startup {fmt_sec(avg(f['startup_ms']))}")
        print(f"     CloudFlare: {c['count']} sessions, avg buf ratio {fmt_pct(avg(c['buf_ratios']))}, "
              f"avg buf time {fmt_sec(avg(c['buf_times_ms']))}, "
              f"avg startup {fmt_sec(avg(c['startup_ms']))}")
        # Buffered sessions per CDN
        f_buffered = [r for r in f["buf_ratios"] if r > 0]
        c_buffered = [r for r in c["buf_ratios"] if r > 0]
        print(f"     Fastly sessions with buffering: {len(f_buffered)}/{len(f['buf_ratios'])}")
        print(f"     CloudFlare sessions with buffering: {len(c_buffered)}/{len(c['buf_ratios'])}")

    # ════════════════════════════════════════════════════════════════════
    print_header(f"4. BUFFER RATIO BY DEVICE/PLATFORM ({window_label})")
    # ════════════════════════════════════════════════════════════════════
    print(f"\n  By Device Type:")
    headers = ["Device", "Sessions", "Buf Ratio(avg)", "Buf Ratio(p95)", "Startup(avg)"]
    widths = [22, 10, 16, 16, 14]
    rows = []
    for dev, d in sorted(by_device.items(), key=lambda x: -x[1]["count"]):
        rows.append([
            dev, d["count"],
            fmt_pct(avg(d["buf_ratios"])),
            fmt_pct(p95(d["buf_ratios"])),
            fmt_sec(avg(d["startup_ms"])),
        ])
    print_table(headers, rows, widths)

    print(f"\n  By OS/Platform:")
    headers = ["OS", "Sessions", "Buf Ratio(avg)", "Buf Ratio(p95)", "Startup(avg)"]
    rows = []
    for os_name, d in sorted(by_os.items(), key=lambda x: -x[1]["count"]):
        rows.append([
            os_name, d["count"],
            fmt_pct(avg(d["buf_ratios"])),
            fmt_pct(p95(d["buf_ratios"])),
            fmt_sec(avg(d["startup_ms"])),
        ])
    print_table(headers, rows, widths)

    # ════════════════════════════════════════════════════════════════════
    print_header(f"5. BUFFER RATIO BY ISP ({window_label})")
    # ════════════════════════════════════════════════════════════════════
    headers = ["ISP", "Sessions", "Buf Ratio(avg)", "Startup(avg)"]
    widths = [32, 10, 16, 14]
    rows = []
    for isp, d in sorted(by_isp.items(), key=lambda x: -x[1]["count"])[:15]:
        rows.append([
            isp[:31], d["count"],
            fmt_pct(avg(d["buf_ratios"])),
            fmt_sec(avg(d["startup_ms"])),
        ])
    print_table(headers, rows, widths)

    # ════════════════════════════════════════════════════════════════════
    print_header(f"6. BUFFER RATIO BY SHOW/TITLE ({window_label})")
    # ════════════════════════════════════════════════════════════════════
    headers = ["Show", "Sessions", "Buf Ratio(avg)", "Buf Time(avg)"]
    widths = [30, 10, 16, 14]
    rows = []
    for title, d in sorted(by_title.items(), key=lambda x: -x[1]["count"]):
        rows.append([
            title[:29], d["count"],
            fmt_pct(avg(d["buf_ratios"])),
            fmt_sec(avg(d["buf_times_ms"])),
        ])
    print_table(headers, rows, widths)

    # ════════════════════════════════════════════════════════════════════
    print_header(f"7. WORST BUFFERING SESSIONS ({window_label})")
    # ════════════════════════════════════════════════════════════════════
    worst = sorted(sessions, key=lambda s: -(safe_float(s.get("buffer_ratio")) or 0))[:15]
    headers = ["Title", "Buf%", "Buf Time", "Underruns", "CDN", "Device", "Country"]
    widths = [32, 10, 10, 10, 14, 14, 12]
    rows = []
    for s in worst:
        br = safe_float(s.get("buffer_ratio")) or 0
        if br <= 0:
            break
        bt = safe_float(s.get("buffer_underrun_total")) or 0
        bu = safe_float(s.get("buffer_underruns")) or 0
        title = (s.get("title") or "?")[:31]
        cdn = s.get("cdn", "?")[:13]
        dev = (s.get("device", {}) or {}).get("device_type", "?")[:13]
        country = ((s.get("location", {}) or {}).get("country", "?"))[:11]
        rows.append([title, f"{br:.1f}%", f"{bt/1000:.1f}s", int(bu), cdn, dev, country])
    if rows:
        print_table(headers, rows, widths)
    else:
        print("  No sessions with buffering detected.")

    # ════════════════════════════════════════════════════════════════════
    print_header("8. FULL SESSION DETAIL")
    # ════════════════════════════════════════════════════════════════════
    headers = ["Title", "Buf%", "BufTime", "CDN", "Device", "OS", "PlayTime", "Country"]
    widths = [30, 8, 9, 14, 14, 12, 9, 12]
    rows = []
    for s in sessions:
        br = safe_float(s.get("buffer_ratio")) or 0
        bt = safe_float(s.get("buffer_underrun_total")) or 0
        pt = safe_float(s.get("play_time")) or 0
        title = (s.get("title") or "?")[:29]
        cdn = s.get("cdn", "?")[:13]
        dev = (s.get("device", {}) or {}).get("device_type", "?")[:13]
        os_name = (s.get("device", {}) or {}).get("os", "?")[:11]
        country = ((s.get("location", {}) or {}).get("country", "?"))[:11]
        rows.append([title, f"{br:.1f}%", f"{bt/1000:.1f}s", cdn, dev, os_name, f"{pt:.0f}s", country])
    print_table(headers, rows, widths)

    # ════════════════════════════════════════════════════════════════════
    print(f"\n{'='*72}")
    print(f"  DONE -- {n} sessions analyzed ({window_label})")
    print(f"{'='*72}\n")


if __name__ == "__main__":
    main()

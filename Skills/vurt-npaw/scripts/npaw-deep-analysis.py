#!/usr/bin/env python3
"""Deep NPAW analysis for VURT bounce rate investigation.

Pulls 48 hours of session data and analyzes:
1. Buffer ratio by hour
2. Buffer ratio by CDN (Fastly vs CloudFront vs CloudFlare)
3. Buffer ratio by device type
4. Buffer ratio by referrer/traffic source
5. Facebook/Instagram vs direct/organic behavior
6. Startup time trends (pre/post Apr 2 deploy)
7. Error rates by hour
8. Play time distribution (are ad users getting 0s playback?)
9. CDN switch visibility (CloudFront transition Apr 2-3)

Outputs JSON for post-processing.
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


def sign_request(path, params):
    future_time = int(round(time.time() * 1000) + 36000)
    params_with_date = list(params) + [("dateToken", future_time)]
    qs = urllib.parse.urlencode(params_with_date, doseq=True)
    raw = f"{path}?{qs}{API_SECRET}"
    token = hashlib.md5(raw.encode()).hexdigest()
    params_with_date.append(("token", token))
    return params_with_date


def api_get(endpoint, params):
    path = f"/{SYSTEM_CODE}/{endpoint}"
    signed = sign_request(path, params)
    qs = urllib.parse.urlencode(signed, doseq=True)
    url = f"{BASE_URL}{path}?{qs}"
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url), timeout=90)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body[:500]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return None


def get_sessions(hours=48, max_sessions=3000):
    """Pull raw sessions with pagination for last N hours."""
    now = datetime.now(timezone.utc)
    # Use date range that covers the full window
    start = (now - timedelta(hours=hours)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    all_sessions = []
    offset = 0
    per_page = 500
    dev_filtered = 0

    print(f"Pulling sessions from {start} to {end} (last {hours}h)...", file=sys.stderr)
    while len(all_sessions) < max_sessions:
        data = api_get("rawdata", [
            ("fromDate", start), ("toDate", end),
            ("type", "VOD"), ("timezone", "America/New_York"),
            ("limit", str(per_page)),
            ("offset", str(offset)),
        ])
        if not data:
            break
        sessions = data.get("data", [])
        batch = sessions[0].get("values", []) if sessions else []
        if not batch:
            break

        for s in batch:
            domain = (s.get("domain") or "").lower().strip()
            if "localhost" in domain or "10.1." in domain or "127.0.0.1" in domain or "0.0.0.0" in domain:
                dev_filtered += 1
                continue
            all_sessions.append(s)

        print(f"  Page {offset // per_page + 1}: got {len(batch)} (total kept: {len(all_sessions)}, dev filtered: {dev_filtered})", file=sys.stderr)
        if len(batch) < per_page:
            break
        offset += len(batch)

    print(f"Total: {len(all_sessions)} sessions (filtered {dev_filtered} dev)", file=sys.stderr)
    return all_sessions[:max_sessions]


def get_sessions_date_range(from_date, to_date, max_sessions=3000):
    """Pull raw sessions for a specific date range."""
    all_sessions = []
    offset = 0
    per_page = 500
    dev_filtered = 0

    print(f"Pulling sessions from {from_date} to {to_date}...", file=sys.stderr)
    while len(all_sessions) < max_sessions:
        data = api_get("rawdata", [
            ("fromDate", from_date), ("toDate", to_date),
            ("type", "VOD"), ("timezone", "America/New_York"),
            ("limit", str(per_page)),
            ("offset", str(offset)),
        ])
        if not data:
            break
        sessions = data.get("data", [])
        batch = sessions[0].get("values", []) if sessions else []
        if not batch:
            break

        for s in batch:
            domain = (s.get("domain") or "").lower().strip()
            if "localhost" in domain or "10.1." in domain or "127.0.0.1" in domain or "0.0.0.0" in domain:
                dev_filtered += 1
                continue
            all_sessions.append(s)

        print(f"  Page {offset // per_page + 1}: got {len(batch)} (total kept: {len(all_sessions)}, dev filtered: {dev_filtered})", file=sys.stderr)
        if len(batch) < per_page:
            break
        offset += len(batch)

    print(f"Total: {len(all_sessions)} sessions (filtered {dev_filtered} dev)", file=sys.stderr)
    return all_sessions[:max_sessions]


def safe_float(val, default=None):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def detect_cdn(session):
    cdn = session.get("cdn", "") or ""
    if not cdn:
        cdn = session.get("cdn_name", "") or ""
    if not cdn:
        ep = session.get("extraparams", {}) or {}
        cdn = ep.get("extraparam1", "") or ep.get("extraparam2", "") or ""
    if not cdn:
        resource = (session.get("resource", "") or "").lower()
        if "cloudfront" in resource:
            cdn = "CloudFront"
        elif "fastly" in resource:
            cdn = "Fastly"
        elif "cloudflare" in resource:
            cdn = "Cloudflare"
        elif "akamai" in resource:
            cdn = "Akamai"
        else:
            cdn = "Unknown"
    return cdn.strip() or "Unknown"


def get_resource_hostname(session):
    resource = session.get("resource", "") or ""
    if resource:
        try:
            parsed = urllib.parse.urlparse(resource)
            return parsed.hostname or "no-host"
        except:
            return "parse-error"
    return "no-resource"


def get_device_category(session):
    dev = session.get("device", {}) or {}
    dtype = (dev.get("device_type", "") or "").lower()
    if "phone" in dtype or "smartphone" in dtype:
        return "Mobile"
    elif "tablet" in dtype or "ipad" in dtype:
        return "Tablet"
    elif "pc" in dtype or "desktop" in dtype:
        return "Desktop"
    elif "tv" in dtype or "smart" in dtype:
        return "Smart TV"
    elif dtype:
        return dtype.title()
    return "Unknown"


def get_referrer_category(session):
    """Categorize traffic source from referrer and other fields."""
    referrer = (session.get("referrer", "") or "").lower()
    domain = (session.get("domain", "") or "").lower()

    # Check extraparams for referrer info
    ep = session.get("extraparams", {}) or {}
    ep_vals = " ".join(str(v).lower() for v in ep.values() if v)

    combined = f"{referrer} {ep_vals}"

    if "facebook" in combined or "fb." in combined or "fbclid" in combined or "l.facebook" in referrer:
        return "Facebook"
    elif "instagram" in combined or "ig." in combined:
        return "Instagram"
    elif "tiktok" in combined or "tt." in combined:
        return "TikTok"
    elif "google" in combined or "gclid" in combined:
        return "Google"
    elif "youtube" in combined or "yt." in combined:
        return "YouTube"
    elif "twitter" in combined or "t.co" in combined or "x.com" in combined:
        return "X/Twitter"
    elif referrer and referrer not in ["", "none", "null", "(none)", "direct"]:
        if "myvurt" in referrer:
            return "Direct/Internal"
        return f"Other ({referrer[:50]})"
    else:
        return "Direct/None"


def get_session_hour(session):
    """Extract hour from session timestamp."""
    # Try multiple timestamp fields
    for field in ["start_time", "timestamp", "date", "session_start"]:
        ts = session.get(field)
        if ts:
            try:
                if isinstance(ts, (int, float)):
                    # Milliseconds
                    if ts > 1e12:
                        ts = ts / 1000
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                    return dt.strftime("%Y-%m-%d %H:00")
                elif isinstance(ts, str):
                    # Try parsing
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            dt = datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
                            return dt.strftime("%Y-%m-%d %H:00")
                        except:
                            pass
            except:
                pass
    return "Unknown"


def get_session_date(session):
    """Extract date from session timestamp."""
    for field in ["start_time", "timestamp", "date", "session_start"]:
        ts = session.get(field)
        if ts:
            try:
                if isinstance(ts, (int, float)):
                    if ts > 1e12:
                        ts = ts / 1000
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                    return dt.strftime("%Y-%m-%d")
                elif isinstance(ts, str):
                    return ts[:10]
            except:
                pass
    return "Unknown"


def analyze(sessions):
    results = {}
    n = len(sessions)
    results["total_sessions"] = n

    # ===== 1. BUFFER RATIO BY HOUR =====
    hourly = defaultdict(lambda: {"count": 0, "buffer_ratios": [], "errors": 0, "startup_times": [], "play_times": []})
    for s in sessions:
        h = get_session_hour(s)
        hourly[h]["count"] += 1
        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            hourly[h]["buffer_ratios"].append(br)
        if s.get("error_code"):
            hourly[h]["errors"] += 1
        st = safe_float(s.get("startup_time"))
        if st is not None and st >= 0:
            hourly[h]["startup_times"].append(st)
        pt = safe_float(s.get("play_time"))
        if pt is not None:
            hourly[h]["play_times"].append(pt)

    hourly_out = {}
    for h in sorted(hourly.keys()):
        d = hourly[h]
        brs = d["buffer_ratios"]
        sts_list = d["startup_times"]
        entry = {
            "sessions": d["count"],
            "errors": d["errors"],
            "error_rate": round(d["errors"] / max(d["count"], 1) * 100, 1),
        }
        if brs:
            sorted_br = sorted(brs)
            entry["avg_buffer_pct"] = round(sum(brs) / len(brs) * 100, 2)
            entry["median_buffer_pct"] = round(sorted_br[len(sorted_br) // 2] * 100, 2)
            entry["p95_buffer_pct"] = round(sorted_br[min(int(len(sorted_br) * 0.95), len(sorted_br) - 1)] * 100, 2)
            entry["zero_buffer_count"] = sum(1 for b in brs if b == 0)
            entry["high_buffer_count"] = sum(1 for b in brs if b > 0.10)
        if sts_list:
            entry["avg_startup_ms"] = round(sum(sts_list) / len(sts_list), 0)
            entry["median_startup_ms"] = round(sorted(sts_list)[len(sts_list) // 2], 0)
        if d["play_times"]:
            entry["avg_play_sec"] = round(sum(d["play_times"]) / len(d["play_times"]), 1)
            entry["zero_play_count"] = sum(1 for p in d["play_times"] if p == 0)
        hourly_out[h] = entry
    results["by_hour"] = hourly_out

    # ===== 2. BUFFER RATIO BY CDN =====
    cdn_data = defaultdict(lambda: {"count": 0, "buffer_ratios": [], "startup_times": [],
                                     "errors": 0, "play_times": [], "happiness": []})
    for s in sessions:
        cdn = detect_cdn(s)
        d = cdn_data[cdn]
        d["count"] += 1
        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            d["buffer_ratios"].append(br)
        st = safe_float(s.get("startup_time"))
        if st is not None and st >= 0:
            d["startup_times"].append(st)
        pt = safe_float(s.get("play_time"))
        if pt is not None:
            d["play_times"].append(pt)
        if s.get("error_code"):
            d["errors"] += 1
        hs = safe_float(s.get("happiness_score"))
        if hs is not None:
            d["happiness"].append(hs)

    cdn_out = {}
    for cdn_name, d in sorted(cdn_data.items(), key=lambda x: -x[1]["count"]):
        entry = {"sessions": d["count"], "errors": d["errors"]}
        if d["buffer_ratios"]:
            brs = sorted(d["buffer_ratios"])
            entry["avg_buffer_pct"] = round(sum(brs) / len(brs) * 100, 2)
            entry["median_buffer_pct"] = round(brs[len(brs) // 2] * 100, 2)
            entry["p95_buffer_pct"] = round(brs[min(int(len(brs) * 0.95), len(brs) - 1)] * 100, 2)
            entry["zero_buffer"] = sum(1 for b in brs if b == 0)
            entry["high_buffer_gt10pct"] = sum(1 for b in brs if b > 0.10)
        if d["startup_times"]:
            sts = sorted(d["startup_times"])
            entry["avg_startup_ms"] = round(sum(sts) / len(sts), 0)
            entry["median_startup_ms"] = round(sts[len(sts) // 2], 0)
            entry["p95_startup_ms"] = round(sts[min(int(len(sts) * 0.95), len(sts) - 1)], 0)
        if d["play_times"]:
            entry["avg_play_sec"] = round(sum(d["play_times"]) / len(d["play_times"]), 1)
            entry["zero_play_count"] = sum(1 for p in d["play_times"] if p == 0)
        if d["happiness"]:
            entry["avg_happiness"] = round(sum(d["happiness"]) / len(d["happiness"]), 1)
        cdn_out[cdn_name] = entry
    results["by_cdn"] = cdn_out

    # ===== 3. BUFFER RATIO BY DEVICE =====
    device_data = defaultdict(lambda: {"count": 0, "buffer_ratios": [], "startup_times": [],
                                        "errors": 0, "play_times": [], "os": defaultdict(int)})
    for s in sessions:
        cat = get_device_category(s)
        d = device_data[cat]
        d["count"] += 1
        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            d["buffer_ratios"].append(br)
        st = safe_float(s.get("startup_time"))
        if st is not None and st >= 0:
            d["startup_times"].append(st)
        pt = safe_float(s.get("play_time"))
        if pt is not None:
            d["play_times"].append(pt)
        if s.get("error_code"):
            d["errors"] += 1
        dev = s.get("device", {}) or {}
        os_name = dev.get("os", "Unknown") or "Unknown"
        d["os"][os_name] += 1

    device_out = {}
    for cat, d in sorted(device_data.items(), key=lambda x: -x[1]["count"]):
        entry = {"sessions": d["count"], "errors": d["errors"], "pct_of_total": round(d["count"] / max(n, 1) * 100, 1)}
        if d["buffer_ratios"]:
            brs = sorted(d["buffer_ratios"])
            entry["avg_buffer_pct"] = round(sum(brs) / len(brs) * 100, 2)
            entry["median_buffer_pct"] = round(brs[len(brs) // 2] * 100, 2)
        if d["startup_times"]:
            entry["avg_startup_ms"] = round(sum(d["startup_times"]) / len(d["startup_times"]), 0)
        if d["play_times"]:
            entry["avg_play_sec"] = round(sum(d["play_times"]) / len(d["play_times"]), 1)
            entry["zero_play_count"] = sum(1 for p in d["play_times"] if p == 0)
        entry["top_os"] = dict(sorted(d["os"].items(), key=lambda x: -x[1])[:5])
        device_out[cat] = entry
    results["by_device"] = device_out

    # ===== 4. BUFFER RATIO BY REFERRER =====
    ref_data = defaultdict(lambda: {"count": 0, "buffer_ratios": [], "startup_times": [],
                                     "errors": 0, "play_times": []})
    for s in sessions:
        ref = get_referrer_category(s)
        d = ref_data[ref]
        d["count"] += 1
        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            d["buffer_ratios"].append(br)
        st = safe_float(s.get("startup_time"))
        if st is not None and st >= 0:
            d["startup_times"].append(st)
        pt = safe_float(s.get("play_time"))
        if pt is not None:
            d["play_times"].append(pt)
        if s.get("error_code"):
            d["errors"] += 1

    ref_out = {}
    for ref, d in sorted(ref_data.items(), key=lambda x: -x[1]["count"]):
        entry = {"sessions": d["count"], "errors": d["errors"], "pct_of_total": round(d["count"] / max(n, 1) * 100, 1)}
        if d["buffer_ratios"]:
            brs = sorted(d["buffer_ratios"])
            entry["avg_buffer_pct"] = round(sum(brs) / len(brs) * 100, 2)
            entry["median_buffer_pct"] = round(brs[len(brs) // 2] * 100, 2)
        if d["startup_times"]:
            entry["avg_startup_ms"] = round(sum(d["startup_times"]) / len(d["startup_times"]), 0)
        if d["play_times"]:
            entry["avg_play_sec"] = round(sum(d["play_times"]) / len(d["play_times"]), 1)
            entry["zero_play_count"] = sum(1 for p in d["play_times"] if p == 0)
            entry["under_5s_play_count"] = sum(1 for p in d["play_times"] if 0 < p < 5)
            entry["under_10s_play_count"] = sum(1 for p in d["play_times"] if 0 < p < 10)
        ref_out[ref] = entry
    results["by_referrer"] = ref_out

    # ===== 5. FACEBOOK/INSTAGRAM vs DIRECT COMPARISON =====
    social_sessions = []
    direct_sessions = []
    for s in sessions:
        ref = get_referrer_category(s)
        if ref in ("Facebook", "Instagram"):
            social_sessions.append(s)
        elif ref == "Direct/None" or ref == "Direct/Internal":
            direct_sessions.append(s)

    def summarize_group(group, label):
        if not group:
            return {"count": 0, "label": label}
        brs = [safe_float(s.get("buffer_ratio")) for s in group]
        brs = [b for b in brs if b is not None and 0 <= b <= 1]
        sts = [safe_float(s.get("startup_time")) for s in group]
        sts = [s for s in sts if s is not None and s >= 0]
        pts = [safe_float(s.get("play_time")) for s in group]
        pts = [p for p in pts if p is not None]
        errs = sum(1 for s in group if s.get("error_code"))

        out = {"count": len(group), "label": label, "errors": errs}
        if brs:
            sorted_br = sorted(brs)
            out["avg_buffer_pct"] = round(sum(brs) / len(brs) * 100, 2)
            out["median_buffer_pct"] = round(sorted_br[len(sorted_br) // 2] * 100, 2)
        if sts:
            out["avg_startup_ms"] = round(sum(sts) / len(sts), 0)
        if pts:
            out["avg_play_sec"] = round(sum(pts) / len(pts), 1)
            out["zero_play_count"] = sum(1 for p in pts if p == 0)
            out["under_5s_play_count"] = sum(1 for p in pts if 0 < p < 5)
            out["median_play_sec"] = round(sorted(pts)[len(pts) // 2], 1)
        return out

    results["social_vs_direct"] = {
        "facebook_instagram": summarize_group(social_sessions, "Facebook/Instagram"),
        "direct": summarize_group(direct_sessions, "Direct/None"),
    }

    # ===== 6. STARTUP TIME BY DATE (pre/post Apr 2) =====
    daily_startup = defaultdict(lambda: {"startup_times": [], "count": 0})
    for s in sessions:
        date = get_session_date(s)
        daily_startup[date]["count"] += 1
        st = safe_float(s.get("startup_time"))
        if st is not None and st >= 0:
            daily_startup[date]["startup_times"].append(st)

    startup_by_date = {}
    for date in sorted(daily_startup.keys()):
        d = daily_startup[date]
        entry = {"sessions": d["count"]}
        if d["startup_times"]:
            sts = sorted(d["startup_times"])
            entry["avg_startup_ms"] = round(sum(sts) / len(sts), 0)
            entry["median_startup_ms"] = round(sts[len(sts) // 2], 0)
            entry["p95_startup_ms"] = round(sts[min(int(len(sts) * 0.95), len(sts) - 1)], 0)
            entry["sample_count"] = len(sts)
        startup_by_date[date] = entry
    results["startup_by_date"] = startup_by_date

    # ===== 7. ERROR ANALYSIS =====
    error_sessions = [s for s in sessions if s.get("error_code")]
    error_codes = defaultdict(int)
    for s in error_sessions:
        code = s.get("error_code", "unknown")
        error_codes[str(code)] += 1

    results["errors"] = {
        "total_error_sessions": len(error_sessions),
        "error_rate_pct": round(len(error_sessions) / max(n, 1) * 100, 1),
        "error_code_distribution": dict(sorted(error_codes.items(), key=lambda x: -x[1])[:20]),
    }

    # ===== 8. PLAY TIME DISTRIBUTION =====
    all_play_times = []
    for s in sessions:
        pt = safe_float(s.get("play_time"))
        if pt is not None:
            all_play_times.append(pt)

    if all_play_times:
        buckets = {
            "0s_exactly": sum(1 for p in all_play_times if p == 0),
            "1_to_5s": sum(1 for p in all_play_times if 0 < p <= 5),
            "5_to_10s": sum(1 for p in all_play_times if 5 < p <= 10),
            "10_to_30s": sum(1 for p in all_play_times if 10 < p <= 30),
            "30s_to_1min": sum(1 for p in all_play_times if 30 < p <= 60),
            "1_to_5min": sum(1 for p in all_play_times if 60 < p <= 300),
            "5_to_15min": sum(1 for p in all_play_times if 300 < p <= 900),
            "15min_plus": sum(1 for p in all_play_times if p > 900),
        }
        sorted_pt = sorted(all_play_times)
        results["play_time_distribution"] = {
            "total_with_play_time": len(all_play_times),
            "buckets": buckets,
            "avg_play_sec": round(sum(sorted_pt) / len(sorted_pt), 1),
            "median_play_sec": round(sorted_pt[len(sorted_pt) // 2], 1),
            "p95_play_sec": round(sorted_pt[min(int(len(sorted_pt) * 0.95), len(sorted_pt) - 1)], 1),
        }

    # ===== 9. CDN SWITCH VISIBILITY BY DATE =====
    cdn_by_date = defaultdict(lambda: defaultdict(int))
    for s in sessions:
        date = get_session_date(s)
        cdn = detect_cdn(s)
        cdn_by_date[date][cdn] += 1

    cdn_transition = {}
    for date in sorted(cdn_by_date.keys()):
        cdn_transition[date] = dict(cdn_by_date[date])
    results["cdn_by_date"] = cdn_transition

    # ===== 10. RESOURCE HOSTNAME DISTRIBUTION =====
    host_data = defaultdict(lambda: {"count": 0, "buffer_ratios": []})
    for s in sessions:
        host = get_resource_hostname(s)
        host_data[host]["count"] += 1
        br = safe_float(s.get("buffer_ratio"))
        if br is not None and 0 <= br <= 1:
            host_data[host]["buffer_ratios"].append(br)

    host_out = {}
    for host, d in sorted(host_data.items(), key=lambda x: -x[1]["count"])[:25]:
        entry = {"sessions": d["count"]}
        if d["buffer_ratios"]:
            entry["avg_buffer_pct"] = round(sum(d["buffer_ratios"]) / len(d["buffer_ratios"]) * 100, 2)
        host_out[host] = entry
    results["resource_hostnames"] = host_out

    # ===== 11. SAMPLE RAW FIELDS (for debugging) =====
    if sessions:
        sample = sessions[0]
        results["sample_session_keys"] = list(sample.keys())
        # Get referrer field values for first 20 sessions
        ref_samples = []
        for s in sessions[:30]:
            ref_samples.append({
                "referrer": s.get("referrer", ""),
                "domain": s.get("domain", ""),
                "resource": (s.get("resource", "") or "")[:100],
                "cdn": s.get("cdn", ""),
                "cdn_name": s.get("cdn_name", ""),
                "buffer_ratio": s.get("buffer_ratio"),
                "play_time": s.get("play_time"),
                "startup_time": s.get("startup_time"),
                "error_code": s.get("error_code"),
                "start_time": s.get("start_time"),
                "timestamp": s.get("timestamp"),
                "date": s.get("date"),
                "title": s.get("title"),
                "device_type": (s.get("device", {}) or {}).get("device_type", ""),
                "os": (s.get("device", {}) or {}).get("os", ""),
                "extraparams": s.get("extraparams"),
            })
        results["sample_sessions"] = ref_samples

    return results


def main():
    if not API_SECRET:
        print("Error: NPAW_API_SECRET not set.", file=sys.stderr)
        sys.exit(1)

    # Pull 48 hours of data
    sessions_48h = get_sessions(hours=48, max_sessions=3000)

    if not sessions_48h:
        print("No sessions found in last 48 hours. Trying 7-day range...", file=sys.stderr)
        sessions_48h = get_sessions_date_range("2026-03-28", "2026-04-04", max_sessions=3000)

    if not sessions_48h:
        print("ERROR: No sessions returned from API.", file=sys.stderr)
        sys.exit(1)

    results = analyze(sessions_48h)

    # Also try to pull wider date range for CDN transition visibility (Apr 1-4)
    print("\nPulling wider window (Apr 1-4) for CDN transition analysis...", file=sys.stderr)
    sessions_wide = get_sessions_date_range("2026-04-01", "2026-04-04", max_sessions=3000)
    if sessions_wide:
        wide_results = analyze(sessions_wide)
        results["wide_window_apr1_4"] = {
            "total_sessions": wide_results["total_sessions"],
            "by_cdn": wide_results.get("by_cdn", {}),
            "cdn_by_date": wide_results.get("cdn_by_date", {}),
            "startup_by_date": wide_results.get("startup_by_date", {}),
            "by_referrer": wide_results.get("by_referrer", {}),
            "play_time_distribution": wide_results.get("play_time_distribution", {}),
            "errors": wide_results.get("errors", {}),
        }

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()

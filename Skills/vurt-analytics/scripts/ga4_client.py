import os, json, urllib.request, urllib.parse

PROPERTY_ID = "518738893"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_API = "https://analyticsdata.googleapis.com/v1beta"
ADMIN_API = "https://analyticsadmin.googleapis.com/v1beta"

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

def run_report(date_ranges, metrics, dimensions=None, order_bys=None, limit=None):
    token = get_access_token()
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

def run_cohort_report(cohorts, metrics, dimensions=None, days_forward=7, granularity="DAILY", limit=1000):
    """Run a GA4 cohort report.

    cohorts: list of dicts like {"name": "...", "dimension": "firstSessionDate",
             "dateRange": {"startDate": "...", "endDate": "..."}}
    dimensions: optional list of dimension names; "cohort" and "cohortNthDay" are
                always added so callers don't have to remember.
    """
    token = get_access_token()
    base_dims = ["cohort", "cohortNthDay"]
    extra_dims = [d for d in (dimensions or []) if d not in base_dims]
    body = {
        "cohortSpec": {
            "cohorts": cohorts,
            "cohortsRange": {"granularity": granularity, "startOffset": 0, "endOffset": days_forward},
        },
        "dimensions": [{"name": d} for d in base_dims + extra_dims],
        "metrics": [{"name": m} for m in metrics],
        "limit": str(limit),
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{DATA_API}/properties/{PROPERTY_ID}:runReport",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def run_realtime_report(metrics, dimensions=None):
    token = get_access_token()
    body = {"metrics": [{"name": m} for m in metrics]}
    if dimensions:
        body["dimensions"] = [{"name": d} for d in dimensions]
    
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{DATA_API}/properties/{PROPERTY_ID}:runRealtimeReport",
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

def get_property_timezone():
    """Get the GA4 property timezone via Admin API."""
    try:
        token = get_access_token()
        req = urllib.request.Request(
            f"{ADMIN_API}/properties/{PROPERTY_ID}",
            headers={"Authorization": f"Bearer {token}"},
            method="GET"
        )
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        return data.get("timeZone", "UTC")
    except Exception:
        return "UTC"


def fmt_duration(seconds_str):
    s = float(seconds_str)
    m, sec = divmod(int(s), 60)
    return f"{m}m {sec}s"

def fmt_pct(val):
    return f"{float(val) * 100:.1f}%" if float(val) <= 1 else f"{float(val):.1f}%"

def fmt_num(val):
    n = float(val)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{int(n)}" if n == int(n) else f"{n:.1f}"

def wow_delta(current, previous):
    c, p = float(current), float(previous)
    if p == 0:
        return "+∞" if c > 0 else "—"
    delta = ((c - p) / p) * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}%"

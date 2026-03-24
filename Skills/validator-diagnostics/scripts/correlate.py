#!/usr/bin/env python3
"""
UTC / EDT Timestamp Correlator for Validator Monitoring

Solana validator logs and terminal monitoring output timestamps in UTC.
The Grafana dashboard at thevalidators.io displays in EDT (UTC-4).
This tool converts between the two and helps correlate events across sources.

Usage:
  python3 correlate.py --help
  python3 correlate.py --utc "2026-03-22 03:45:00"       # Convert UTC -> EDT
  python3 correlate.py --edt "2026-03-21 23:45:00"       # Convert EDT -> UTC
  python3 correlate.py --slot 345678901                   # Estimate time from slot
  python3 correlate.py --log-file /path/to/monitor.log    # Parse log, add EDT column
  python3 correlate.py --window "2026-03-22 03:40:00" 10  # Show 10min window around time
  python3 correlate.py --now                              # Show current time in both zones
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Constants ----------------------------------------------------------------

EDT_OFFSET = timedelta(hours=-4)
EDT_TZ = timezone(EDT_OFFSET)
UTC_TZ = timezone.utc

# Solana slot timing: ~400ms per slot, genesis time for mainnet-beta
# This is approximate. For precise correlation, we query the RPC.
SLOT_DURATION_MS = 400
SOLANA_GENESIS_UNIX = 1616442000  # Approximate mainnet-beta genesis

RPC_URL = "https://api.mainnet-beta.solana.com"

VALIDATOR_IDENTITY = "SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ"

# Common timestamp formats in validator logs
TIMESTAMP_PATTERNS = [
    # ISO 8601 with timezone
    (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)', "%Y-%m-%dT%H:%M:%SZ"),
    (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2}))', None),
    # Standard date+time
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC', "%Y-%m-%d %H:%M:%S"),
    (r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC\]', "%Y-%m-%d %H:%M:%S"),
    # Time only (HH:MM:SS) -- assume UTC
    (r'\b(\d{2}:\d{2}:\d{2})\b', "%H:%M:%S"),
    # Unix timestamp
    (r'timestamp[=: ]+(\d{10,13})', None),
]


# -- Conversion Functions -----------------------------------------------------

def utc_to_edt(dt_utc):
    """Convert a UTC datetime to EDT."""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=UTC_TZ)
    return dt_utc.astimezone(EDT_TZ)


def edt_to_utc(dt_edt):
    """Convert an EDT datetime to UTC."""
    if dt_edt.tzinfo is None:
        dt_edt = dt_edt.replace(tzinfo=EDT_TZ)
    return dt_edt.astimezone(UTC_TZ)


def format_both(dt_utc):
    """Format a UTC datetime in both UTC and EDT."""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=UTC_TZ)
    dt_edt = utc_to_edt(dt_utc)
    return {
        "utc": dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "edt": dt_edt.strftime("%Y-%m-%d %H:%M:%S EDT"),
    }


def parse_timestamp(ts_str):
    """
    Try to parse a timestamp string in various formats.
    Returns a UTC datetime or None.
    """
    ts_str = ts_str.strip()

    # Try explicit formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S UTC",
        "%Y-%m-%d %H:%M:%S EDT",
        "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%H:%M:%S",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(ts_str.replace(" UTC", "").replace(" EDT", ""), fmt)
            if fmt == "%H:%M:%S":
                # Time only -- assume today UTC
                today = datetime.now(UTC_TZ).date()
                dt = datetime.combine(today, dt.time(), tzinfo=UTC_TZ)
            elif "EDT" in ts_str:
                dt = dt.replace(tzinfo=EDT_TZ).astimezone(UTC_TZ)
            else:
                dt = dt.replace(tzinfo=UTC_TZ)
            return dt
        except ValueError:
            continue

    # Try unix timestamp
    try:
        ts = float(ts_str)
        if ts > 1e12:
            ts /= 1000  # milliseconds
        return datetime.fromtimestamp(ts, tz=UTC_TZ)
    except (ValueError, OverflowError):
        pass

    return None


# -- Slot / Time Estimation ---------------------------------------------------

def rpc_request(method, params=None):
    """Make an RPC call to Solana mainnet."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or [],
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        RPC_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            if "error" in result:
                return None
            return result.get("result")
    except Exception:
        return None


def estimate_time_from_slot(slot):
    """
    Estimate the UTC time for a given slot number.
    Uses current slot + time as anchor, then extrapolates backwards.
    """
    # Get current slot from RPC for accurate anchoring
    current_slot = rpc_request("getSlot", [{"commitment": "confirmed"}])
    if current_slot is None:
        # Fallback: rough estimate from genesis
        elapsed_ms = slot * SLOT_DURATION_MS
        ts = SOLANA_GENESIS_UNIX + (elapsed_ms / 1000)
        return datetime.fromtimestamp(ts, tz=UTC_TZ)

    now = datetime.now(UTC_TZ)
    slot_diff = current_slot - slot
    time_diff = timedelta(milliseconds=slot_diff * SLOT_DURATION_MS)
    estimated = now - time_diff
    return estimated


def estimate_slot_from_time(dt_utc):
    """Estimate the slot number for a given UTC time."""
    current_slot = rpc_request("getSlot", [{"commitment": "confirmed"}])
    if current_slot is None:
        # Fallback
        elapsed_s = (dt_utc - datetime(2021, 3, 23, tzinfo=UTC_TZ)).total_seconds()
        return int(elapsed_s * 1000 / SLOT_DURATION_MS)

    now = datetime.now(UTC_TZ)
    time_diff = now - dt_utc
    slot_diff = int(time_diff.total_seconds() * 1000 / SLOT_DURATION_MS)
    return current_slot - slot_diff


# -- Log Parsing --------------------------------------------------------------

def parse_log_line(line):
    """Extract timestamp from a log line and return (utc_dt, original_match)."""
    for pattern, fmt in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            ts_str = match.group(1)
            dt = parse_timestamp(ts_str)
            if dt:
                return dt, ts_str
    return None, None


def annotate_log_file(log_path, output_path=None):
    """
    Read a log file with UTC timestamps and add an EDT column.
    Outputs to stdout or a file.
    """
    log_path = Path(log_path)
    if not log_path.exists():
        print(f"Error: file not found: {log_path}", file=sys.stderr)
        sys.exit(1)

    out = open(output_path, 'w') if output_path else sys.stdout
    line_count = 0
    annotated = 0

    try:
        with open(log_path) as f:
            for line in f:
                line = line.rstrip('\n')
                line_count += 1

                dt_utc, original = parse_log_line(line)
                if dt_utc:
                    dt_edt = utc_to_edt(dt_utc)
                    edt_str = dt_edt.strftime("%H:%M:%S EDT")
                    out.write(f"[{edt_str}] {line}\n")
                    annotated += 1
                else:
                    out.write(f"{'':>14s} {line}\n")
    finally:
        if output_path:
            out.close()

    print(f"\nProcessed {line_count} lines, annotated {annotated} with EDT times.",
          file=sys.stderr)


def show_time_window(center_time_str, window_minutes, log_path=None):
    """
    Given a center time, show the UTC/EDT window and optionally filter log lines.
    """
    dt = parse_timestamp(center_time_str)
    if dt is None:
        print(f"Error: could not parse timestamp: {center_time_str}", file=sys.stderr)
        sys.exit(1)

    half = timedelta(minutes=window_minutes / 2)
    start = dt - half
    end = dt + half

    print(f"\nTime Window ({window_minutes} minutes):")
    print(f"  Center: {format_both(dt)['utc']} / {format_both(dt)['edt']}")
    print(f"  Start:  {format_both(start)['utc']} / {format_both(start)['edt']}")
    print(f"  End:    {format_both(end)['utc']} / {format_both(end)['edt']}")

    # Estimate slot range
    start_slot = estimate_slot_from_time(start)
    end_slot = estimate_slot_from_time(end)
    if start_slot and end_slot:
        print(f"\n  Estimated slot range: {start_slot:,} - {end_slot:,}")
        print(f"  Slot span: ~{end_slot - start_slot:,} slots")

    # Grafana URL for this window
    from_ts = int(start.timestamp() * 1000)
    to_ts = int(end.timestamp() * 1000)
    grafana_url = (
        f"https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring"
        f"?orgId=2&var-cluster=mainnet-beta&var-server=saga-mainnet"
        f"&from={from_ts}&to={to_ts}"
    )
    print(f"\n  Grafana URL for this window:")
    print(f"  {grafana_url}")

    # Filter log file if provided
    if log_path:
        log_path = Path(log_path)
        if log_path.exists():
            print(f"\n  Log lines in window ({log_path}):")
            with open(log_path) as f:
                for line in f:
                    dt_utc, _ = parse_log_line(line.rstrip('\n'))
                    if dt_utc and start <= dt_utc <= end:
                        dt_edt = utc_to_edt(dt_utc)
                        print(f"  [{dt_edt.strftime('%H:%M:%S EDT')}] {line.rstrip()}")


# -- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UTC/EDT Timestamp Correlator for Validator Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Context:
  Grafana dashboard displays in EDT (UTC-4).
  Validator logs and terminal monitoring use UTC.
  This tool bridges the two for event correlation.

Examples:
  %(prog)s --now
  %(prog)s --utc "2026-03-22 03:45:00"
  %(prog)s --edt "2026-03-21 23:45:00"
  %(prog)s --slot 345678901
  %(prog)s --window "2026-03-22 03:40:00" 10
  %(prog)s --window "2026-03-22 03:40:00" 10 --log-file monitor.log
  %(prog)s --log-file /path/to/vote-latency.log
  %(prog)s --grafana-range "2026-03-22 02:00:00" "2026-03-22 04:00:00"
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--now",
        action="store_true",
        help="Show current time in UTC and EDT",
    )
    group.add_argument(
        "--utc",
        metavar="TIMESTAMP",
        help="Convert a UTC timestamp to EDT",
    )
    group.add_argument(
        "--edt",
        metavar="TIMESTAMP",
        help="Convert an EDT timestamp to UTC",
    )
    group.add_argument(
        "--slot",
        type=int,
        help="Estimate UTC/EDT time for a Solana slot number",
    )
    group.add_argument(
        "--window",
        nargs=2,
        metavar=("TIMESTAMP", "MINUTES"),
        help="Show a time window around a center timestamp (UTC)",
    )
    group.add_argument(
        "--log-file",
        metavar="PATH",
        help="Parse a log file and annotate with EDT timestamps",
    )
    group.add_argument(
        "--grafana-range",
        nargs=2,
        metavar=("START_UTC", "END_UTC"),
        help="Generate a Grafana URL for a specific UTC time range",
    )

    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Output file for --log-file mode (default: stdout)",
    )

    args = parser.parse_args()

    if args.now:
        now_utc = datetime.now(UTC_TZ)
        now_edt = utc_to_edt(now_utc)
        current_slot = rpc_request("getSlot", [{"commitment": "confirmed"}])
        print(f"Current time:")
        print(f"  UTC:  {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  EDT:  {now_edt.strftime('%Y-%m-%d %H:%M:%S EDT')}")
        print(f"  Unix: {int(now_utc.timestamp())}")
        if current_slot:
            print(f"  Slot: {current_slot:,}")
        print(f"\n  Grafana shows: {now_edt.strftime('%H:%M')} on its time axis")

    elif args.utc:
        dt = parse_timestamp(args.utc)
        if dt is None:
            print(f"Error: could not parse: {args.utc}", file=sys.stderr)
            sys.exit(1)
        both = format_both(dt)
        print(f"  UTC: {both['utc']}")
        print(f"  EDT: {both['edt']} (Grafana display)")
        est_slot = estimate_slot_from_time(dt)
        if est_slot:
            print(f"  Estimated slot: ~{est_slot:,}")

    elif args.edt:
        dt_str = args.edt
        dt = parse_timestamp(dt_str)
        if dt is None:
            # Try forcing EDT interpretation
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%H:%M:%S"]:
                try:
                    dt = datetime.strptime(dt_str, fmt)
                    if fmt == "%H:%M:%S":
                        today = datetime.now(EDT_TZ).date()
                        dt = datetime.combine(today, dt.time(), tzinfo=EDT_TZ)
                    else:
                        dt = dt.replace(tzinfo=EDT_TZ)
                    break
                except ValueError:
                    continue

        if dt is None:
            print(f"Error: could not parse: {args.edt}", file=sys.stderr)
            sys.exit(1)

        # Ensure it's treated as EDT
        if dt.tzinfo != EDT_TZ:
            dt = dt.replace(tzinfo=EDT_TZ)

        dt_utc = edt_to_utc(dt)
        print(f"  EDT: {dt.strftime('%Y-%m-%d %H:%M:%S EDT')} (Grafana display)")
        print(f"  UTC: {dt_utc.strftime('%Y-%m-%d %H:%M:%S UTC')} (validator logs)")
        est_slot = estimate_slot_from_time(dt_utc)
        if est_slot:
            print(f"  Estimated slot: ~{est_slot:,}")

    elif args.slot is not None:
        est_time = estimate_time_from_slot(args.slot)
        both = format_both(est_time)
        print(f"  Slot:  {args.slot:,}")
        print(f"  UTC:   {both['utc']} (estimated)")
        print(f"  EDT:   {both['edt']} (Grafana display, estimated)")
        print(f"\n  Note: Slot times are estimates based on ~400ms/slot.")
        print(f"  Accuracy decreases for slots further from the current slot.")

    elif args.window:
        ts_str, minutes_str = args.window
        try:
            minutes = float(minutes_str)
        except ValueError:
            print(f"Error: invalid minutes: {minutes_str}", file=sys.stderr)
            sys.exit(1)
        show_time_window(ts_str, minutes)

    elif args.log_file:
        annotate_log_file(args.log_file, args.output)

    elif args.grafana_range:
        start_str, end_str = args.grafana_range
        start_dt = parse_timestamp(start_str)
        end_dt = parse_timestamp(end_str)
        if start_dt is None or end_dt is None:
            print("Error: could not parse time range", file=sys.stderr)
            sys.exit(1)

        from_ts = int(start_dt.timestamp() * 1000)
        to_ts = int(end_dt.timestamp() * 1000)
        grafana_url = (
            f"https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring"
            f"?orgId=2&var-cluster=mainnet-beta&var-server=saga-mainnet"
            f"&from={from_ts}&to={to_ts}"
        )
        print(f"  Start: {format_both(start_dt)['utc']} / {format_both(start_dt)['edt']}")
        print(f"  End:   {format_both(end_dt)['utc']} / {format_both(end_dt)['edt']}")
        print(f"\n  Grafana URL:")
        print(f"  {grafana_url}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

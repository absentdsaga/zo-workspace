---
name: validator-diagnostics
description: Real-time Solana validator performance diagnostics. Checks per-epoch vote credits vs cluster, skip rate, vote latency, BAM status, DoubleZero health, Grafana dashboard monitoring, and UTC/EDT timestamp correlation. Use when checking validator health, diagnosing TVC/performance issues, or capturing/analyzing Grafana dashboard snapshots.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# Validator Diagnostics

Tools for monitoring and diagnosing Solana validator performance, with a focus on Timely Vote Credits (TVC), per-epoch ranking, Grafana dashboard capture, and cross-source event correlation.

## Scripts

### grafana-monitor.py

Captures screenshots of the Saga DAO Grafana monitoring dashboard using Playwright. Supports configurable time ranges, individual panel capture, metric extraction, and historical trend analysis.

```bash
# Capture last 1 hour (default)
python3 scripts/grafana-monitor.py --range 1h

# Capture last 6 hours with individual panel screenshots
python3 scripts/grafana-monitor.py --range 6h --panels

# Full snapshot: screenshots + metric extraction + JSON
python3 scripts/grafana-monitor.py --snapshot --range 3h

# View trend analysis from historical snapshots
python3 scripts/grafana-monitor.py --trend

# Just get the Grafana URL for a time range
python3 scripts/grafana-monitor.py --url-only --range 12h

# Custom output directory
python3 scripts/grafana-monitor.py --range 24h --output /path/to/dir
```

Key features:
- Captures full dashboard + scrolled sections for long dashboards
- Individual panel capture via `--panels`
- Metric extraction from visible panel values via `--snapshot`
- Historical snapshots stored in dated directories for trend tracking
- Uses Playwright with Chromium (headless, --no-sandbox)

Dashboard: `https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?orgId=2&var-cluster=mainnet-beta&var-server=saga-mainnet`

### correlate.py

Cross-correlates timestamps between UTC (validator logs) and EDT (Grafana display). Converts between timezones, estimates slot numbers from timestamps, annotates log files with EDT, and generates Grafana URLs for specific time windows.

```bash
# Show current time in both zones
python3 scripts/correlate.py --now

# Convert UTC to EDT (what Grafana shows)
python3 scripts/correlate.py --utc "2026-03-22 03:45:00"

# Convert EDT (from Grafana) to UTC (for log correlation)
python3 scripts/correlate.py --edt "2026-03-21 23:45:00"

# Estimate time for a slot number
python3 scripts/correlate.py --slot 345678901

# Show a 10-minute window around a time (with slot estimates + Grafana URL)
python3 scripts/correlate.py --window "2026-03-22 03:40:00" 10

# Annotate a log file with EDT timestamps
python3 scripts/correlate.py --log-file /path/to/vote-latency.log

# Generate Grafana URL for a specific time range
python3 scripts/correlate.py --grafana-range "2026-03-22 02:00:00" "2026-03-22 04:00:00"
```

### epoch-performance.py

Pulls real-time epoch data from Solana mainnet RPC and generates a performance report for a given validator.

```bash
python3 scripts/epoch-performance.py [VALIDATOR_IDENTITY_PUBKEY]
```

Default validator: `SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ`

Outputs:
- Current epoch credits vs cluster (top 5, top 50, median, bottom quartile)
- Per-epoch rank (not cumulative)
- Credits/slot rate vs cluster average
- Projected end-of-epoch credits and rank
- Historical epoch comparison when available

### vote-latency-analysis.py

Compares Saga DAO vote latency against top validators by stake. Samples on-chain tower state and historical vote transactions.

### vote-latency-monitor.py

Continuous vote latency monitor. Runs on the validator node, tracking vote distance over hours and surfacing spike patterns.

```bash
python3 scripts/vote-latency-monitor.py [--duration HOURS] [--rpc URL] [--output FILE]
```

### health-check.sh

Generates a JSON-friendly diagnostic command bundle to run ON the validator node.

```bash
bash scripts/health-check.sh
```

Copy the output and run it on the validator. It checks:
- Vote account status and credits
- Vote latency
- Skip rate
- DoubleZero interface stats
- BAM connection status
- NIC stats
- System resources (CPU, memory, disk, network)

## References

### grafana-dashboard.md

Dashboard URL, panel descriptions, timezone handling, and correlation workflow documentation. Key panels tracked: Last Vote Distance, Root Slot Distance, Credits/min, UDP Errors, Load Average, Skipped Votes %.

### tvc-explainer.md

Deep reference on how Timely Vote Credits (SIMD-0033) work, why cumulative rank is misleading, and how to correctly interpret validator performance data.

## Snapshot Storage

Grafana snapshots are stored at:
```
Skills/validator-diagnostics/snapshots/<YYYY-MM-DD>/
```

Each snapshot includes:
- `grafana-<range>-<timestamp>.png` -- full dashboard screenshot(s)
- `panel-<name>-<range>-<timestamp>.png` -- individual panel screenshots
- `snapshot-<range>-<timestamp>.json` -- extracted metrics, timestamps, and metadata

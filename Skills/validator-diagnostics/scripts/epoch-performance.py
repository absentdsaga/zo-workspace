#!/usr/bin/env python3
"""
Solana Validator Epoch Performance Report
Queries mainnet RPC for vote account data and produces a per-epoch performance analysis.
"""

import json
import sys
import urllib.request
import urllib.error
import time
from collections import defaultdict

RPC_URL = "https://api.mainnet-beta.solana.com"
DEFAULT_VALIDATOR = "SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2


def rpc_request(method, params=None, retries=MAX_RETRIES):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or [],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        RPC_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if "error" in result:
                    err = result["error"]
                    code = err.get("code", 0)
                    if code == 429 and attempt < retries - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    print(f"RPC error: {err}", file=sys.stderr)
                    sys.exit(1)
                return result["result"]
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            print(f"Request failed after {retries} attempts: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

    print("Max retries exceeded", file=sys.stderr)
    sys.exit(1)


def get_epoch_info():
    return rpc_request("getEpochInfo")


def get_vote_accounts():
    return rpc_request("getVoteAccounts")


def find_validator(vote_accounts, identity):
    for v in vote_accounts.get("current", []):
        if v["nodePubkey"] == identity:
            return v, True
    for v in vote_accounts.get("delinquent", []):
        if v["nodePubkey"] == identity:
            return v, False
    return None, None


def extract_epoch_credits(epoch_credits, target_epoch):
    """
    epochCredits entries are [epoch, cumulative_credits, prev_cumulative_credits].
    Credits for the epoch = cumulative - prev_cumulative.
    """
    for entry in epoch_credits:
        if entry[0] == target_epoch:
            return entry[1] - entry[2]
    return None


def build_epoch_map(vote_accounts, epoch):
    """Build a map of identity -> credits for the given epoch."""
    result = {}
    for v in vote_accounts.get("current", []) + vote_accounts.get("delinquent", []):
        credits = extract_epoch_credits(v["epochCredits"], epoch)
        if credits is not None and credits > 0:
            result[v["nodePubkey"]] = credits
    return result


def percentile(sorted_vals, p):
    if not sorted_vals:
        return 0
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_vals) else f
    d = k - f
    return sorted_vals[f] + d * (sorted_vals[c] - sorted_vals[f])


def rank_of(val, sorted_vals_desc):
    for i, v in enumerate(sorted_vals_desc):
        if val >= v:
            return i + 1
    return len(sorted_vals_desc)


def format_number(n):
    return f"{n:,.0f}"


def generate_report(identity):
    print(f"Fetching epoch info...", file=sys.stderr)
    epoch_info = get_epoch_info()
    current_epoch = epoch_info["epoch"]
    slot_index = epoch_info["slotIndex"]
    slots_in_epoch = epoch_info["slotsInEpoch"]
    epoch_progress = slot_index / slots_in_epoch
    slots_remaining = slots_in_epoch - slot_index

    print(f"Fetching vote accounts...", file=sys.stderr)
    vote_accounts = get_vote_accounts()

    validator, is_current = find_validator(vote_accounts, identity)
    if validator is None:
        print(f"\n# Validator Not Found\n")
        print(f"Identity `{identity}` not found in current or delinquent vote accounts.")
        print("Verify the pubkey is the validator identity (not vote account).")
        return

    vote_pubkey = validator["votePubkey"]
    activated_stake = validator["activatedStake"] / 1e9

    # Current epoch credits
    my_credits = extract_epoch_credits(validator["epochCredits"], current_epoch)
    if my_credits is None:
        my_credits = 0

    # All validators' credits this epoch
    epoch_map = build_epoch_map(vote_accounts, current_epoch)
    all_credits = sorted(epoch_map.values())
    all_credits_desc = sorted(epoch_map.values(), reverse=True)
    total_validators = len(all_credits)

    my_rank = rank_of(my_credits, all_credits_desc) if my_credits > 0 else total_validators

    top5_avg = sum(all_credits_desc[:5]) / min(5, len(all_credits_desc)) if all_credits_desc else 0
    top50_avg = sum(all_credits_desc[:50]) / min(50, len(all_credits_desc)) if all_credits_desc else 0
    median_credits = percentile(all_credits, 50)
    bottom_q = percentile(all_credits, 25)
    cluster_avg = sum(all_credits) / len(all_credits) if all_credits else 0

    # Credits per slot rate
    my_rate = my_credits / slot_index if slot_index > 0 else 0
    cluster_rate = cluster_avg / slot_index if slot_index > 0 else 0
    top5_rate = top5_avg / slot_index if slot_index > 0 else 0

    # Projections
    projected_my = my_credits / epoch_progress if epoch_progress > 0 else 0
    projected_top5 = top5_avg / epoch_progress if epoch_progress > 0 else 0
    projected_median = median_credits / epoch_progress if epoch_progress > 0 else 0

    # Projected rank (rough)
    projected_all = sorted(
        [(creds / epoch_progress if epoch_progress > 0 else 0) for creds in all_credits],
        reverse=True,
    )
    projected_rank = rank_of(projected_my, projected_all)

    # Historical epochs (from epochCredits array)
    historical = []
    for entry in validator["epochCredits"]:
        ep = entry[0]
        creds = entry[1] - entry[2]
        if ep != current_epoch and creds > 0:
            historical.append((ep, creds))
    historical.sort()

    # Historical cluster data for comparison
    hist_cluster = {}
    for ep, _ in historical[-3:]:
        ep_map = build_epoch_map(vote_accounts, ep)
        if ep_map:
            vals = sorted(ep_map.values())
            hist_cluster[ep] = {
                "median": percentile(vals, 50),
                "count": len(vals),
                "top50_avg": sum(sorted(vals, reverse=True)[:50]) / min(50, len(vals)),
            }

    # Output report
    status_label = "CURRENT" if is_current else "DELINQUENT"
    status_indicator = "OK" if is_current else "!! DELINQUENT !!"

    print(f"\n# Validator Epoch Performance Report")
    print(f"\n**Generated:** {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}")
    print(f"\n## Validator")
    print(f"| Field | Value |")
    print(f"|-------|-------|")
    print(f"| Identity | `{identity}` |")
    print(f"| Vote Account | `{vote_pubkey}` |")
    print(f"| Status | {status_indicator} |")
    print(f"| Activated Stake | {activated_stake:,.2f} SOL |")

    print(f"\n## Epoch {current_epoch} -- {epoch_progress*100:.1f}% Complete")
    print(f"\nSlot {format_number(slot_index)} / {format_number(slots_in_epoch)} ({format_number(slots_remaining)} remaining)")

    print(f"\n### Credits Comparison")
    print(f"| Benchmark | Credits | Credits/Slot |")
    print(f"|-----------|---------|-------------|")
    print(f"| **Your validator** | **{format_number(my_credits)}** | **{my_rate:.2f}** |")
    print(f"| Top 5 avg | {format_number(top5_avg)} | {top5_rate:.2f} |")
    print(f"| Top 50 avg | {format_number(top50_avg)} | {top50_avg/slot_index if slot_index > 0 else 0:.2f} |")
    print(f"| Cluster median | {format_number(median_credits)} | {median_credits/slot_index if slot_index > 0 else 0:.2f} |")
    print(f"| Cluster average | {format_number(cluster_avg)} | {cluster_rate:.2f} |")
    print(f"| Bottom 25% | {format_number(bottom_q)} | {bottom_q/slot_index if slot_index > 0 else 0:.2f} |")

    print(f"\n### Ranking")
    print(f"| Metric | Value |")
    print(f"|--------|-------|")
    print(f"| Per-epoch rank | **{my_rank}** / {total_validators} |")
    print(f"| Percentile | {(1 - my_rank/total_validators)*100:.1f}th |")

    delta_top5 = my_credits - top5_avg
    delta_median = my_credits - median_credits
    print(f"| vs Top 5 avg | {format_number(delta_top5)} ({delta_top5/top5_avg*100 if top5_avg else 0:+.1f}%) |")
    print(f"| vs Median | {format_number(delta_median)} ({delta_median/median_credits*100 if median_credits else 0:+.1f}%) |")

    print(f"\n### Projection (End of Epoch)")
    print(f"| Metric | Projected |")
    print(f"|--------|-----------|")
    print(f"| Your credits | {format_number(projected_my)} |")
    print(f"| Top 5 avg | {format_number(projected_top5)} |")
    print(f"| Median | {format_number(projected_median)} |")
    print(f"| Projected rank | ~{projected_rank} / {total_validators} |")

    # Rate analysis
    print(f"\n### Rate Analysis")
    if my_rate > 0:
        theoretical_max = 16.0
        efficiency = (my_rate / theoretical_max) * 100
        print(f"- Credits/slot: **{my_rate:.2f}** (theoretical max: 16.00)")
        print(f"- Vote efficiency: **{efficiency:.1f}%**")
        if my_rate >= 15.5:
            print(f"- Assessment: Excellent. Votes consistently landing within grace period.")
        elif my_rate >= 14.5:
            print(f"- Assessment: Good. Minor latency beyond grace period on some votes.")
        elif my_rate >= 13.0:
            print(f"- Assessment: Below average. Consistent ~1-2 slot extra latency. Investigate vote propagation.")
        else:
            print(f"- Assessment: Poor. Significant vote latency. Check connectivity, BAM, compute resources.")
    else:
        print(f"- No credits earned yet this epoch.")

    # Historical
    if historical:
        print(f"\n### Historical Trend (Recent Epochs)")
        print(f"| Epoch | Your Credits | Cluster Median | vs Median |")
        print(f"|-------|-------------|----------------|-----------|")
        for ep, creds in historical[-5:]:
            if ep in hist_cluster:
                med = hist_cluster[ep]["median"]
                delta = creds - med
                print(f"| {ep} | {format_number(creds)} | {format_number(med)} | {format_number(delta)} ({delta/med*100 if med else 0:+.1f}%) |")
            else:
                print(f"| {ep} | {format_number(creds)} | -- | -- |")

    if not is_current:
        print(f"\n---")
        print(f"\n**WARNING: Validator is DELINQUENT.** It is not currently voting.")
        print(f"This means zero credits are being earned. Investigate immediately:")
        print(f"- Check if the validator process is running")
        print(f"- Check if it is caught up (solana catchup)")
        print(f"- Check vote account balance for transaction fees")
        print(f"- Check logs for errors")


def main():
    identity = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VALIDATOR

    if identity in ("-h", "--help"):
        print("Usage: epoch-performance.py [VALIDATOR_IDENTITY_PUBKEY]")
        print(f"Default: {DEFAULT_VALIDATOR}")
        sys.exit(0)

    generate_report(identity)


if __name__ == "__main__":
    main()

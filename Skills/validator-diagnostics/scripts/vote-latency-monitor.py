#!/usr/bin/env python3
"""
Vote Latency Monitor for Solana Validators
Continuously tracks vote timing, distance, and shred reception patterns.
Designed to run for hours and surface patterns invisible in snapshots.

Usage: python3 vote-latency-monitor.py [--duration HOURS] [--rpc URL] [--output FILE]
"""

import json
import time
import sys
import os
import signal
import urllib.request
import urllib.error
from datetime import datetime, timezone
from collections import defaultdict

# Config
RPC_URL = "http://127.0.0.1:8899"
SAMPLE_INTERVAL = 0.4  # ~1 slot
SUMMARY_INTERVAL = 300  # 5 minutes
OUTPUT_FILE = None
DURATION_HOURS = 12

# Parse args
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--duration" and i + 1 < len(args):
        DURATION_HOURS = float(args[i + 1])
        i += 2
    elif args[i] == "--rpc" and i + 1 < len(args):
        RPC_URL = args[i + 1]
        i += 2
    elif args[i] == "--output" and i + 1 < len(args):
        OUTPUT_FILE = args[i + 1]
        i += 2
    else:
        i += 1

if OUTPUT_FILE is None:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    OUTPUT_FILE = f"/home/solv/vote-latency-{timestamp}.log"


class VoteLatencyMonitor:
    def __init__(self):
        self.running = True
        self.start_time = time.time()
        self.samples = []
        self.window_samples = []
        self.window_start = time.time()
        self.summary_count = 0
        self.last_vote_slot = None
        self.last_sample_time = None
        self.vote_distances = defaultdict(int)
        self.window_distances = defaultdict(int)
        self.errors = []
        self.max_distance_seen = 0
        self.spikes = []  # (timestamp, distance, cluster_slot, vote_slot)
        self.outfile = None

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        self.running = False

    def rpc_call(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            RPC_URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=2) as resp:
                result = json.loads(resp.read().decode())
                if "error" in result:
                    return None
                return result.get("result")
        except Exception:
            return None

    def get_slot(self):
        return self.rpc_call("getSlot", [{"commitment": "processed"}])

    def get_vote_accounts(self):
        return self.rpc_call("getVoteAccounts")

    def get_epoch_info(self):
        return self.rpc_call("getEpochInfo")

    def get_vote_distance(self):
        """Get current vote distance: cluster_slot - validator_last_vote_slot"""
        cluster_slot = self.get_slot()
        if cluster_slot is None:
            return None

        vote_accounts = self.get_vote_accounts()
        if vote_accounts is None:
            return None

        # Find our validator
        for va in vote_accounts.get("current", []):
            if va.get("votePubkey") == "sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw":
                last_vote = va.get("lastVote", 0)
                root_slot = va.get("rootSlot", 0)
                distance = cluster_slot - last_vote
                return {
                    "cluster_slot": cluster_slot,
                    "last_vote": last_vote,
                    "root_slot": root_slot,
                    "distance": distance,
                    "timestamp": time.time(),
                }

        return None

    def log(self, msg, also_print=True):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        line = f"[{ts}] {msg}"
        if also_print:
            print(line, flush=True)
        if self.outfile:
            self.outfile.write(line + "\n")
            self.outfile.flush()

    def print_summary(self, distances, samples, label=""):
        if not samples:
            self.log(f"  No samples collected in this window")
            return

        dists = [s["distance"] for s in samples]
        avg_dist = sum(dists) / len(dists)
        max_dist = max(dists)
        min_dist = min(dists)

        # Distribution
        dist_counts = defaultdict(int)
        for d in dists:
            dist_counts[d] += 1

        total = len(dists)

        self.log(f"  Samples: {total}")
        self.log(f"  Vote Distance: avg={avg_dist:.2f}, min={min_dist}, max={max_dist}")
        self.log(f"  Distribution:")
        for d in sorted(dist_counts.keys()):
            count = dist_counts[d]
            pct = count / total * 100
            bar = "#" * int(pct / 2)
            self.log(f"    distance {d:2d}: {count:6d} ({pct:5.1f}%) {bar}")

        # Slot progression check
        if len(samples) >= 2:
            time_span = samples[-1]["timestamp"] - samples[0]["timestamp"]
            slot_span = samples[-1]["cluster_slot"] - samples[0]["cluster_slot"]
            if time_span > 0:
                slots_per_sec = slot_span / time_span
                self.log(f"  Cluster rate: {slots_per_sec:.2f} slots/sec (expected ~2.5)")

                vote_span = samples[-1]["last_vote"] - samples[0]["last_vote"]
                vote_rate = vote_span / time_span
                self.log(f"  Vote rate: {vote_rate:.2f} votes/sec")

        # Spikes in this window
        window_spikes = [s for s in samples if s["distance"] >= 3]
        if window_spikes:
            self.log(f"  ⚠ High-distance votes ({len(window_spikes)}):")
            for s in window_spikes[:10]:
                ts = datetime.fromtimestamp(s["timestamp"], timezone.utc).strftime("%H:%M:%S")
                self.log(f"    {ts}: distance={s['distance']} (cluster={s['cluster_slot']}, vote={s['last_vote']})")

    def run(self):
        end_time = self.start_time + (DURATION_HOURS * 3600)

        try:
            self.outfile = open(OUTPUT_FILE, "w")
        except Exception as e:
            print(f"Warning: can't write to {OUTPUT_FILE}: {e}", flush=True)
            self.outfile = None

        self.log(f"Vote Latency Monitor started")
        self.log(f"  RPC: {RPC_URL}")
        self.log(f"  Duration: {DURATION_HOURS}h")
        self.log(f"  Output: {OUTPUT_FILE}")
        self.log(f"  Sample interval: {SAMPLE_INTERVAL}s")
        self.log(f"  Summary every: {SUMMARY_INTERVAL}s")
        self.log(f"  Validator: sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw")
        self.log("")

        # Initial epoch info
        epoch_info = self.get_epoch_info()
        if epoch_info:
            self.log(f"  Epoch: {epoch_info.get('epoch')}")
            self.log(f"  Slot: {epoch_info.get('absoluteSlot')} ({epoch_info.get('slotIndex')}/{epoch_info.get('slotsInEpoch')})")
        self.log("=" * 70)
        self.log("")

        consecutive_errors = 0

        while self.running and time.time() < end_time:
            sample = self.get_vote_distance()

            if sample is None:
                consecutive_errors += 1
                if consecutive_errors >= 10:
                    self.log("ERROR: 10 consecutive RPC failures, waiting 10s...")
                    time.sleep(10)
                    consecutive_errors = 0
                else:
                    time.sleep(SAMPLE_INTERVAL)
                continue

            consecutive_errors = 0
            self.samples.append(sample)
            self.window_samples.append(sample)

            # Track distances
            d = sample["distance"]
            self.vote_distances[d] += 1
            self.window_distances[d] += 1

            if d > self.max_distance_seen:
                self.max_distance_seen = d

            # Log spikes immediately
            if d >= 3:
                self.spikes.append(sample)
                ts = datetime.fromtimestamp(sample["timestamp"], timezone.utc).strftime("%H:%M:%S")
                self.log(f"⚠ SPIKE: distance={d} at {ts} (cluster={sample['cluster_slot']}, vote={sample['last_vote']})")

            # Periodic summary
            if time.time() - self.window_start >= SUMMARY_INTERVAL:
                self.summary_count += 1
                elapsed = time.time() - self.start_time
                elapsed_min = elapsed / 60

                self.log("")
                self.log(f"{'=' * 70}")
                self.log(f"SUMMARY #{self.summary_count} (elapsed: {elapsed_min:.1f} min)")
                self.log(f"{'=' * 70}")
                self.log(f"--- Last {SUMMARY_INTERVAL}s window ---")
                self.print_summary(self.window_distances, self.window_samples, "window")
                self.log(f"--- Cumulative ---")
                self.print_summary(self.vote_distances, self.samples, "cumulative")
                self.log(f"{'=' * 70}")
                self.log("")

                # Reset window
                self.window_samples = []
                self.window_distances = defaultdict(int)
                self.window_start = time.time()

            self.last_vote_slot = sample["last_vote"]
            self.last_sample_time = sample["timestamp"]

            time.sleep(SAMPLE_INTERVAL)

        # Final summary
        self.log("")
        self.log("=" * 70)
        self.log("FINAL SUMMARY")
        self.log("=" * 70)
        elapsed = time.time() - self.start_time
        self.log(f"Total runtime: {elapsed / 3600:.2f} hours")
        self.log(f"Total samples: {len(self.samples)}")
        self.log(f"Total spikes (distance >= 3): {len(self.spikes)}")
        self.print_summary(self.vote_distances, self.samples, "final")

        if self.spikes:
            self.log("")
            self.log(f"ALL SPIKES (distance >= 3):")
            for s in self.spikes:
                ts = datetime.fromtimestamp(s["timestamp"], timezone.utc).strftime("%H:%M:%S")
                self.log(f"  {ts}: distance={s['distance']} (cluster={s['cluster_slot']}, vote={s['last_vote']})")

        self.log("")
        self.log("=" * 70)
        self.log(f"Monitor stopped. Full log: {OUTPUT_FILE}")

        if self.outfile:
            self.outfile.close()


if __name__ == "__main__":
    monitor = VoteLatencyMonitor()
    monitor.run()

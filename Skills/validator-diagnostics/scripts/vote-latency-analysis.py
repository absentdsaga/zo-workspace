#!/usr/bin/env python3
"""
Solana Vote Latency Analysis
Compares Saga DAO vote latency against top validators by stake.

Two data sources:
1. On-chain vote state (tower snapshot, ~31 recent votes with embedded latency)
2. Historical vote transactions via getSignaturesForAddress + getTransaction
   to compute (landing_slot - voted_slot) over hundreds of votes

Uses only stdlib. Handles RPC rate limits with exponential backoff.
"""

import json
import struct
import time
import base64
import urllib.request
import urllib.error
from collections import Counter, defaultdict

RPC_URL = "https://api.mainnet-beta.solana.com"
SAGA_VOTE_ACCOUNT = "sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw"

# Number of recent vote txs to sample per validator
TX_SAMPLE_SIZE = 150

# ── Base58 decode (inline, no deps) ─────────────────────────────────

BASE58_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58decode(s):
    """Decode a base58-encoded string to bytes."""
    if isinstance(s, str):
        s = s.encode('ascii')
    origlen = len(s)
    s = s.lstrip(BASE58_ALPHABET[0:1])
    newlen = len(s)
    acc = 0
    for c in s:
        acc = acc * 58 + BASE58_ALPHABET.index(c)
    result = []
    while acc > 0:
        acc, mod = divmod(acc, 256)
        result.append(mod)
    # Add leading zeros
    result.extend([0] * (origlen - newlen))
    return bytes(reversed(result))


# ── RPC helpers ──────────────────────────────────────────────────────

def rpc_call(method, params=None, max_retries=6):
    """Make a JSON-RPC call with exponential backoff on rate limits."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or [],
    }
    data = json.dumps(payload).encode()

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                RPC_URL,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                if "error" in result:
                    err = result["error"]
                    if err.get("code") == 429 or "Too many requests" in str(err).lower():
                        wait = 2 ** attempt + 1
                        print(f"  Rate limited, waiting {wait}s...")
                        time.sleep(wait)
                        continue
                    # Server busy / resource exhausted
                    if err.get("code") in (-32005, -32009):
                        wait = 2 ** attempt + 1
                        print(f"  Server busy ({err.get('code')}), waiting {wait}s...")
                        time.sleep(wait)
                        continue
                    raise RuntimeError(f"RPC error: {err}")
                return result.get("result")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 2 ** attempt + 1
                print(f"  HTTP 429, waiting {wait}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            wait = 2 ** attempt + 1
            print(f"  Connection error: {e}, retrying in {wait}s...")
            time.sleep(wait)
            continue
    raise RuntimeError(f"Failed after {max_retries} retries for {method}")


# ── Parse on-chain vote state (tower snapshot) ──────────────────────

def parse_vote_state(account_data_b64):
    """Parse vote account binary data. Returns (votes_list, version)."""
    raw = base64.b64decode(account_data_b64)
    offset = 0

    def read_u32():
        nonlocal offset
        val = struct.unpack_from('<I', raw, offset)[0]
        offset += 4
        return val

    def read_u64():
        nonlocal offset
        val = struct.unpack_from('<Q', raw, offset)[0]
        offset += 8
        return val

    def read_pubkey():
        nonlocal offset
        offset += 32

    def read_u8():
        nonlocal offset
        val = raw[offset]
        offset += 1
        return val

    version = read_u32()        # 4 bytes
    read_pubkey()               # node_pubkey: 32 bytes
    read_pubkey()               # authorized_withdrawer: 32 bytes
    commission = read_u8()      # commission: 1 byte
    # Now at offset 69

    votes = []
    if version >= 1:
        # Current format: LandedVote = { latency: u8, lockout: { slot: u64, confirmation_count: u32 } }
        num_votes = read_u64()
        if num_votes > 150:
            return [], version
        for _ in range(num_votes):
            latency = read_u8()
            slot = read_u64()
            confirmation_count = read_u32()
            votes.append({
                'slot': slot,
                'latency': latency,
                'confirmation_count': confirmation_count,
            })
    else:
        num_votes = read_u64()
        if num_votes > 150:
            return [], version
        for _ in range(num_votes):
            slot = read_u64()
            confirmation_count = read_u32()
            votes.append({
                'slot': slot,
                'latency': None,
                'confirmation_count': confirmation_count,
            })

    return votes, version


def fetch_vote_state(vote_account_pubkey):
    """Fetch and parse vote account on-chain state."""
    result = rpc_call("getAccountInfo", [
        vote_account_pubkey,
        {"encoding": "base64"}
    ])
    if not result or not result.get("value"):
        return None, None
    data = result["value"]["data"]
    account_data_b64 = data[0] if isinstance(data, list) else data
    return parse_vote_state(account_data_b64)


# ── Historical vote transaction analysis ────────────────────────────

def fetch_recent_vote_signatures(vote_account, limit=TX_SAMPLE_SIZE):
    """Get recent transaction signatures for a vote account."""
    sigs = []
    before = None
    while len(sigs) < limit:
        params = [vote_account, {"limit": min(50, limit - len(sigs))}]
        if before:
            params[1]["before"] = before
        result = rpc_call("getSignaturesForAddress", params)
        if not result:
            break
        sigs.extend(result)
        if len(result) < 50:
            break
        before = result[-1]["signature"]
        time.sleep(0.3)
    return sigs[:limit]


def parse_vote_instruction(tx_data):
    """
    Extract the voted-for slot from a vote transaction.
    Vote instructions use program Vote111111111111111111111111111111111111111.
    The vote instruction contains the slot being voted on.

    Returns (voted_slot, landing_slot) or None.
    """
    if not tx_data:
        return None

    meta = tx_data.get("meta")
    transaction = tx_data.get("transaction")
    if not meta or not transaction:
        return None

    landing_slot = tx_data.get("slot")
    if not landing_slot:
        return None

    # The transaction message contains instructions
    message = transaction.get("message", {})
    account_keys = message.get("accountKeys", [])
    instructions = message.get("instructions", [])

    # Find the Vote program instruction
    vote_program = "Vote111111111111111111111111111111111111111"
    for ix in instructions:
        program_idx = ix.get("programIdIndex", -1)
        if program_idx < len(account_keys) and account_keys[program_idx] == vote_program:
            # Decode the instruction data
            ix_data_b58 = ix.get("data", "")
            if not ix_data_b58:
                continue
            try:
                ix_bytes = b58decode(ix_data_b58)
            except Exception:
                continue

            # Vote instruction types:
            # 0 = InitializeAccount, 2 = Vote, 6 = UpdateVoteState,
            # 9 = CompactUpdateVoteState, 12 = TowerSync, 13 = CompactTowerSync
            if len(ix_bytes) < 4:
                continue

            ix_type = struct.unpack_from('<I', ix_bytes, 0)[0]

            # Parse based on instruction type
            if ix_type == 2:
                # Vote: { slots: Vec<u64>, hash: Hash, timestamp: Option<i64> }
                if len(ix_bytes) < 12:
                    continue
                num_slots = struct.unpack_from('<I', ix_bytes, 4)[0]
                if num_slots == 0 or num_slots > 100:
                    continue
                # Last slot in the vector is the most recent vote
                last_offset = 8 + (num_slots - 1) * 8
                if last_offset + 8 > len(ix_bytes):
                    continue
                voted_slot = struct.unpack_from('<Q', ix_bytes, last_offset)[0]
                return (voted_slot, landing_slot)

            elif ix_type in (6, 9):
                # UpdateVoteState / CompactUpdateVoteState
                # { lockouts: Vec<Lockout>, root: Option<u64>, hash: Hash, timestamp: Option<i64> }
                offset = 4
                if ix_type == 9:
                    # CompactUpdateVoteState uses compact-u16 for vec length
                    # Simple approach: read first byte
                    if offset >= len(ix_bytes):
                        continue
                    num_lockouts = ix_bytes[offset]
                    offset += 1
                    if num_lockouts > 127:
                        # multi-byte compact-u16, skip for now
                        continue
                else:
                    if offset + 4 > len(ix_bytes):
                        continue
                    num_lockouts = struct.unpack_from('<I', ix_bytes, offset)[0]
                    offset += 4

                if num_lockouts == 0 or num_lockouts > 100:
                    continue

                # Each Lockout = { slot: u64, confirmation_count: u32 } for type 6
                # For type 9 (compact): { offset: compact-u16, confirmation_count: u8 }
                if ix_type == 6:
                    last_off = offset + (num_lockouts - 1) * 12
                    if last_off + 8 > len(ix_bytes):
                        continue
                    voted_slot = struct.unpack_from('<Q', ix_bytes, last_off)[0]
                    return (voted_slot, landing_slot)
                else:
                    # compact: first lockout has absolute slot, rest have offsets
                    if offset + 8 > len(ix_bytes):
                        continue
                    base_slot = struct.unpack_from('<Q', ix_bytes, offset)[0]
                    offset += 8
                    conf = ix_bytes[offset] if offset < len(ix_bytes) else 0
                    offset += 1
                    current_slot = base_slot
                    for _ in range(num_lockouts - 1):
                        if offset >= len(ix_bytes):
                            break
                        # Read compact offset
                        slot_off = ix_bytes[offset]
                        offset += 1
                        if slot_off > 127:
                            break
                        current_slot += slot_off
                        conf = ix_bytes[offset] if offset < len(ix_bytes) else 0
                        offset += 1
                    return (current_slot, landing_slot)

            elif ix_type in (12, 13):
                # TowerSync / CompactTowerSync (newer format, similar structure)
                offset = 4
                if ix_type == 13:
                    if offset >= len(ix_bytes):
                        continue
                    num_lockouts = ix_bytes[offset]
                    offset += 1
                    if num_lockouts > 127:
                        continue
                else:
                    if offset + 4 > len(ix_bytes):
                        continue
                    num_lockouts = struct.unpack_from('<I', ix_bytes, offset)[0]
                    offset += 4

                if num_lockouts == 0 or num_lockouts > 100:
                    continue

                if ix_type == 12:
                    # TowerSync: lockouts are { slot: u64, confirmation_count: u32 }
                    last_off = offset + (num_lockouts - 1) * 12
                    if last_off + 8 > len(ix_bytes):
                        continue
                    voted_slot = struct.unpack_from('<Q', ix_bytes, last_off)[0]
                    return (voted_slot, landing_slot)
                else:
                    # CompactTowerSync: first has absolute slot, rest have offsets
                    if offset + 8 > len(ix_bytes):
                        continue
                    base_slot = struct.unpack_from('<Q', ix_bytes, offset)[0]
                    offset += 8
                    conf = ix_bytes[offset] if offset < len(ix_bytes) else 0
                    offset += 1
                    current_slot = base_slot
                    for _ in range(num_lockouts - 1):
                        if offset >= len(ix_bytes):
                            break
                        slot_off = ix_bytes[offset]
                        offset += 1
                        if slot_off > 127:
                            break
                        current_slot += slot_off
                        conf = ix_bytes[offset] if offset < len(ix_bytes) else 0
                        offset += 1
                    return (current_slot, landing_slot)

    return None


def analyze_vote_transactions(vote_account, label):
    """Fetch recent vote transactions and compute latency distribution."""
    print(f"\n  Fetching recent vote signatures for {label}...")
    sigs = fetch_recent_vote_signatures(vote_account, limit=TX_SAMPLE_SIZE)
    print(f"  Got {len(sigs)} signatures")

    if not sigs:
        return None

    latencies = []
    parsed = 0
    errors = 0

    for i, sig_info in enumerate(sigs):
        sig = sig_info["signature"]
        if sig_info.get("err"):
            continue  # Skip failed transactions

        try:
            tx = rpc_call("getTransaction", [
                sig,
                {"encoding": "json", "maxSupportedTransactionVersion": 0}
            ])
        except RuntimeError as e:
            errors += 1
            if errors > 10:
                print(f"  Too many errors, stopping after {parsed} txs")
                break
            continue

        if not tx:
            continue

        result = parse_vote_instruction(tx)
        if result:
            voted_slot, landing_slot = result
            latency = landing_slot - voted_slot
            if 0 <= latency < 50:  # Sanity check
                latencies.append({
                    'voted_slot': voted_slot,
                    'landing_slot': landing_slot,
                    'latency': latency,
                })
            parsed += 1

        # Rate limit protection
        if (i + 1) % 10 == 0:
            time.sleep(0.5)

        # Progress
        if (i + 1) % 25 == 0:
            print(f"  Processed {i+1}/{len(sigs)} txs, {len(latencies)} valid latencies...")

    print(f"  Parsed {parsed} vote txs, {len(latencies)} valid latency samples, {errors} errors")
    return latencies


# ── Find top validators ─────────────────────────────────────────────

def get_top_validators(n=3):
    """Get top N validators by activated stake."""
    print("\nFetching vote accounts...")
    result = rpc_call("getVoteAccounts")

    current = result.get("current", [])
    print(f"  Found {len(current)} current vote accounts")

    current.sort(key=lambda v: int(v["activatedStake"]), reverse=True)

    top = []
    for v in current[:20]:
        addr = v["votePubkey"]
        if addr == SAGA_VOTE_ACCOUNT:
            continue
        top.append({
            'votePubkey': addr,
            'nodePubkey': v['nodePubkey'],
            'activatedStake': int(v['activatedStake']),
            'lastVote': v['lastVote'],
            'commission': v['commission'],
            'epochCredits': v['epochCredits'],
        })
        if len(top) >= n:
            break

    saga_info = None
    for v in current:
        if v["votePubkey"] == SAGA_VOTE_ACCOUNT:
            saga_info = {
                'votePubkey': v['votePubkey'],
                'nodePubkey': v['nodePubkey'],
                'activatedStake': int(v['activatedStake']),
                'lastVote': v['lastVote'],
                'commission': v['commission'],
                'epochCredits': v['epochCredits'],
            }
            break

    if saga_info is None:
        for v in result.get("delinquent", []):
            if v["votePubkey"] == SAGA_VOTE_ACCOUNT:
                saga_info = {
                    'votePubkey': v['votePubkey'],
                    'nodePubkey': v['nodePubkey'],
                    'activatedStake': int(v['activatedStake']),
                    'lastVote': v['lastVote'],
                    'commission': v['commission'],
                    'epochCredits': v['epochCredits'],
                    'delinquent': True,
                }
                print(f"\n  WARNING: Saga DAO is in the DELINQUENT list!")
                break

    return saga_info, top


# ── Analysis & reporting ────────────────────────────────────────────

def compute_latency_stats(latencies, label):
    """Compute and display latency distribution from a list of latency dicts."""
    if not latencies:
        print(f"\n  {label}: No latency data")
        return None

    lats = [l['latency'] for l in latencies]
    total = len(lats)
    counter = Counter(lats)

    print(f"\n{'='*65}")
    print(f"  {label}")
    print(f"  Sample size: {total} votes")
    if latencies:
        slots = [l.get('voted_slot') or l.get('slot') for l in latencies]
        slots = [s for s in slots if s]
        if slots:
            print(f"  Slot range: {min(slots):,} - {max(slots):,}")
    print(f"{'='*65}")

    print(f"\n  {'Latency':>10}  {'Count':>6}  {'Pct':>7}  {'Cumul':>7}  {'Bar'}")
    print(f"  {'-'*60}")

    cumulative = 0
    for lat in sorted(counter.keys()):
        count = counter[lat]
        pct = count / total * 100
        cumulative += pct
        bar = '#' * max(1, int(pct / 2)) if pct > 0 else ''
        label_str = f"slot+{lat}"
        print(f"  {label_str:>10}  {count:>6}  {pct:>6.1f}%  {cumulative:>6.1f}%  {bar}")

    slot0 = counter.get(0, 0) / total * 100
    slot1 = counter.get(1, 0) / total * 100
    slot2 = counter.get(2, 0) / total * 100
    slot3plus = sum(c for l, c in counter.items() if l >= 3) / total * 100

    avg = sum(lats) / len(lats)
    median = sorted(lats)[len(lats) // 2]

    print(f"\n  Summary:")
    print(f"    slot+0 (same slot): {slot0:.1f}%")
    print(f"    slot+1 (next slot): {slot1:.1f}%")
    print(f"    slot+2:             {slot2:.1f}%")
    print(f"    slot+3+:            {slot3plus:.1f}%")
    print(f"    Average latency:    {avg:.2f} slots")
    print(f"    Median latency:     {median} slot(s)")

    return {
        'total': total,
        'avg': avg,
        'median': median,
        'slot0_pct': slot0,
        'slot1_pct': slot1,
        'slot2_pct': slot2,
        'slot3plus_pct': slot3plus,
        'distribution': dict(counter),
        'latencies': latencies,
    }


def analyze_late_patterns(result, label):
    """Look for clustering/burst patterns in late votes."""
    if not result or not result.get('latencies'):
        return

    lats = result['latencies']
    late = [(l.get('voted_slot') or l.get('slot'), l['latency'])
            for l in lats if l['latency'] >= 2]

    if not late:
        print(f"\n  {label}: No late votes (latency >= 2)")
        return

    total = result['total']
    print(f"\n  {label} - Late Vote Patterns (latency >= 2):")
    print(f"  Late: {len(late)}/{total} ({len(late)/total*100:.1f}%)")

    # Group by latency bucket
    by_lat = defaultdict(list)
    for slot, lat in late:
        by_lat[lat].append(slot)

    for lat in sorted(by_lat.keys()):
        slots = by_lat[lat]
        print(f"    latency={lat}: {len(slots)} occurrences")

    # Check for bursts (multiple late votes within 10-slot window)
    late_slots = sorted([s for s, _ in late if s])
    if len(late_slots) >= 2:
        bursts = []
        current_burst = [late_slots[0]]
        for i in range(1, len(late_slots)):
            if late_slots[i] - late_slots[i-1] <= 10:
                current_burst.append(late_slots[i])
            else:
                if len(current_burst) >= 3:
                    bursts.append(current_burst)
                current_burst = [late_slots[i]]
        if len(current_burst) >= 3:
            bursts.append(current_burst)

        if bursts:
            print(f"  Burst clusters (3+ late votes within 10 slots):")
            for b in bursts[:5]:
                print(f"    Slots {b[0]:,}-{b[-1]:,} ({len(b)} late votes, span={b[-1]-b[0]})")


def compare_epoch_credits(saga_info, top_validators):
    """Compare epoch credits between validators."""
    print(f"\n{'='*65}")
    print(f"  EPOCH CREDITS COMPARISON (last 3 epochs)")
    print(f"{'='*65}")

    all_v = []
    if saga_info:
        all_v.append(('Saga DAO', saga_info))
    for i, v in enumerate(top_validators):
        all_v.append((f"Top #{i+1}", v))

    # Build table
    # Find common epochs
    epochs = set()
    for _, info in all_v:
        for e in info.get('epochCredits', [])[-3:]:
            epochs.add(e[0])
    epochs = sorted(epochs)

    print(f"\n  {'Validator':<20} {'Stake (SOL)':>14} {'Comm':>5}", end='')
    for e in epochs:
        print(f"  {'E'+str(e):>10}", end='')
    print()
    print(f"  {'-'*20} {'-'*14} {'-'*5}", end='')
    for _ in epochs:
        print(f"  {'-'*10}", end='')
    print()

    for label, info in all_v:
        stake = info['activatedStake'] / 1e9
        comm = info['commission']
        credits_map = {}
        for e, earned, prev in info.get('epochCredits', []):
            credits_map[e] = earned - prev

        print(f"  {label:<20} {stake:>13,.0f} {comm:>4}%", end='')
        for e in epochs:
            c = credits_map.get(e, 0)
            print(f"  {c:>10,}", end='')
        print()

    # Credit gap analysis
    if saga_info and top_validators:
        saga_credits = {e: earned - prev for e, earned, prev in saga_info.get('epochCredits', [])}
        for e in epochs:
            saga_c = saga_credits.get(e, 0)
            top_avg = 0
            count = 0
            for v in top_validators:
                for ep, earned, prev in v.get('epochCredits', []):
                    if ep == e:
                        top_avg += (earned - prev)
                        count += 1
            if count > 0:
                top_avg /= count
                gap = saga_c - top_avg
                gap_pct = (gap / top_avg * 100) if top_avg else 0
                print(f"\n  Epoch {e}: Saga DAO vs Top avg = {gap:+,.0f} credits ({gap_pct:+.2f}%)")


# ── Main ────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  SOLANA VOTE LATENCY ANALYSIS")
    print("  Saga DAO vs Top Validators by Stake")
    print("=" * 65)

    # ── Step 1: Identify validators ──
    saga_info, top_validators = get_top_validators(n=3)

    if saga_info:
        flag = " [DELINQUENT]" if saga_info.get('delinquent') else ""
        print(f"\n  Saga DAO: {SAGA_VOTE_ACCOUNT}{flag}")
        print(f"  Stake: {saga_info['activatedStake']/1e9:,.0f} SOL | Commission: {saga_info['commission']}%")
    else:
        print(f"\n  WARNING: Saga DAO not found in vote accounts list")

    print(f"\n  Comparison validators (top 3 by stake):")
    for i, v in enumerate(top_validators):
        print(f"    #{i+1}: {v['votePubkey'][:32]}... ({v['activatedStake']/1e9:,.0f} SOL, {v['commission']}%)")

    # ── Step 2: Tower snapshot (on-chain vote state) ──
    print(f"\n{'='*65}")
    print(f"  PART 1: ON-CHAIN TOWER SNAPSHOT")
    print(f"  (Current lockout tower, ~31 most recent votes)")
    print(f"{'='*65}")

    tower_data = {}
    accounts_to_check = [(SAGA_VOTE_ACCOUNT, "Saga DAO")]
    for i, v in enumerate(top_validators):
        accounts_to_check.append((v['votePubkey'], f"Top #{i+1}"))

    for acct, label in accounts_to_check:
        votes, version = fetch_vote_state(acct)
        if votes:
            print(f"\n  {label}: {len(votes)} tower votes, version={version}")
            lats = [v['latency'] for v in votes if v.get('latency') is not None]
            if lats:
                counter = Counter(lats)
                print(f"    Latency breakdown: ", end='')
                for lat in sorted(counter.keys()):
                    print(f"slot+{lat}={counter[lat]}", end=' ')
                print()
                print(f"    Avg={sum(lats)/len(lats):.2f}, Median={sorted(lats)[len(lats)//2]}")
            tower_data[acct] = votes
        time.sleep(0.3)

    # ── Step 3: Historical vote transaction analysis ──
    print(f"\n{'='*65}")
    print(f"  PART 2: HISTORICAL VOTE TRANSACTION ANALYSIS")
    print(f"  (Sampling ~{TX_SAMPLE_SIZE} recent vote txs per validator)")
    print(f"{'='*65}")

    results = {}

    # Saga DAO
    saga_latencies = analyze_vote_transactions(SAGA_VOTE_ACCOUNT, "Saga DAO")
    saga_result = compute_latency_stats(saga_latencies, "Saga DAO")
    results['saga'] = saga_result

    # Top validators
    for i, v in enumerate(top_validators):
        label = f"Top #{i+1} ({v['votePubkey'][:16]}...)"
        lats = analyze_vote_transactions(v['votePubkey'], label)
        result = compute_latency_stats(lats, label)
        results[f'top_{i}'] = result

    # ── Step 4: Late vote patterns ──
    print(f"\n{'='*65}")
    print(f"  LATE VOTE PATTERN ANALYSIS")
    print(f"{'='*65}")

    if saga_result:
        analyze_late_patterns(saga_result, "Saga DAO")
    for i in range(len(top_validators)):
        r = results.get(f'top_{i}')
        if r:
            analyze_late_patterns(r, f"Top #{i+1}")

    # ── Step 5: Epoch credits ──
    compare_epoch_credits(saga_info, top_validators)

    # ── Step 6: Comparative summary ──
    print(f"\n{'='*65}")
    print(f"  COMPARATIVE SUMMARY")
    print(f"{'='*65}")

    top_results = [results.get(f'top_{i}') for i in range(len(top_validators))]
    valid_top = [r for r in top_results if r]

    if saga_result and valid_top:
        avg_top = lambda key: sum(r[key] for r in valid_top) / len(valid_top)

        print(f"\n  {'Metric':<32} {'Saga DAO':>10} {'Top Avg':>10} {'Delta':>10}")
        print(f"  {'-'*62}")
        print(f"  {'Avg latency (slots)':<32} {saga_result['avg']:>10.2f} {avg_top('avg'):>10.2f} {saga_result['avg']-avg_top('avg'):>+10.2f}")
        print(f"  {'Median latency':<32} {saga_result['median']:>10} {avg_top('median'):>10.1f} {saga_result['median']-avg_top('median'):>+10.1f}")
        print(f"  {'slot+0 (same slot) %':<32} {saga_result['slot0_pct']:>9.1f}% {avg_top('slot0_pct'):>9.1f}% {saga_result['slot0_pct']-avg_top('slot0_pct'):>+9.1f}%")
        print(f"  {'slot+1 (next slot) %':<32} {saga_result['slot1_pct']:>9.1f}% {avg_top('slot1_pct'):>9.1f}% {saga_result['slot1_pct']-avg_top('slot1_pct'):>+9.1f}%")
        print(f"  {'slot+2 %':<32} {saga_result['slot2_pct']:>9.1f}% {avg_top('slot2_pct'):>9.1f}% {saga_result['slot2_pct']-avg_top('slot2_pct'):>+9.1f}%")
        print(f"  {'slot+3+ (late) %':<32} {saga_result['slot3plus_pct']:>9.1f}% {avg_top('slot3plus_pct'):>9.1f}% {saga_result['slot3plus_pct']-avg_top('slot3plus_pct'):>+9.1f}%")
        print(f"  {'Sample size':<32} {saga_result['total']:>10} {avg_top('total'):>10.0f}")

        diff = saga_result['avg'] - avg_top('avg')
        print(f"\n  Assessment:")
        if abs(diff) < 0.05:
            print(f"    Saga DAO vote latency is IDENTICAL to top validators (delta: {diff:+.3f} slots)")
        elif diff < 0.15:
            print(f"    Saga DAO vote latency is ON PAR with top validators (delta: {diff:+.3f} slots)")
        elif diff < 0.3:
            print(f"    Saga DAO vote latency is SLIGHTLY HIGHER (delta: {diff:+.3f} slots)")
            print(f"    Minor optimization opportunity -- check network peering and Agave tuning.")
        elif diff < 0.5:
            print(f"    Saga DAO vote latency is MODERATELY HIGHER (delta: {diff:+.3f} slots)")
            print(f"    Investigate: network hops to leaders, turbine reception, CPU load during voting.")
        else:
            print(f"    Saga DAO vote latency is SIGNIFICANTLY HIGHER (delta: {diff:+.3f} slots)")
            print(f"    Action needed: check datacenter connectivity, validator hardware, software version.")

        # Credit impact estimate
        if saga_info:
            saga_credits = saga_info.get('epochCredits', [])
            if saga_credits and len(saga_credits) >= 2:
                last_epoch = saga_credits[-2]  # Use last complete epoch
                epoch_credits = last_epoch[1] - last_epoch[2]
                # Rough estimate: each slot of extra latency costs ~0.5% of credits
                # (since you miss the timing point reward component)
                if diff > 0:
                    estimated_credit_loss_pct = diff * 0.5  # rough heuristic
                    estimated_lost = int(epoch_credits * estimated_credit_loss_pct / 100)
                    print(f"\n    Estimated per-epoch credit impact: ~{estimated_lost:,} credits ({estimated_credit_loss_pct:.2f}%)")
                    print(f"    (Based on last complete epoch: {epoch_credits:,} credits earned)")
    else:
        print("\n  Insufficient data for comparative analysis.")

    print(f"\n{'='*65}")
    print(f"  Analysis complete.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()

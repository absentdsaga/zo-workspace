# Timely Vote Credits (TVC) -- SIMD-0033

## What TVC Changed

Before TVC (pre-SIMD-0033), validators earned 1 vote credit per successful vote, regardless of how quickly they voted. A validator voting 10 slots late earned the same credit as one voting within 1 slot.

TVC introduced a latency-weighted credit system. Votes landing within the grace period earn maximum credits. Votes landing later earn progressively fewer credits, down to a minimum of 1.

## The Credit Formula

Credits earned per vote = max(1, MAX_CREDITS - (latency - GRACE_PERIOD))

Where:
- MAX_CREDITS = 16 (maximum credits per vote)
- GRACE_PERIOD = 2 slots (~800ms)
- latency = number of slots between the block being voted on and the vote landing on-chain

So:
- Latency 1-2 slots: 16 credits (full marks)
- Latency 3 slots: 15 credits
- Latency 4 slots: 14 credits
- ...
- Latency 17+ slots: 1 credit (minimum)

## The 2-Slot Grace Period

The grace period exists specifically to equalize geographic differences. A validator in Tokyo and a validator in Virginia both have ~2 slots of inherent network propagation time. The grace period absorbs this, so geographic location alone should not determine credit earnings.

What this means: if your validator is earning fewer credits than peers, it is NOT because of your geographic location (assuming reasonable connectivity). It is because of:
- Vote transaction propagation delays (your vote tx is slow to reach the leader)
- Compute delays (your validator is slow to process and vote on blocks)
- Network connectivity issues (packet loss, jitter, routing problems)

## What Actually Affects Vote Credits

### Vote latency (the big one)
Your validator needs to:
1. Receive the block
2. Replay/verify the block
3. Generate a vote transaction
4. Get that vote transaction to the current leader

Every slot of delay beyond the grace period costs 1 credit. At ~432,000 slots per epoch, even a consistent 1-slot extra latency costs ~432,000 credits per epoch.

### Skip rate (does NOT directly affect TVC)
Skip rate measures how often your validator fails to produce a block when it is the leader. This affects block rewards, not vote credits. A validator with a 50% skip rate but perfect vote latency will earn the same vote credits as a validator with 0% skip rate and the same vote latency.

However, high skip rate CAN indicate underlying issues (compute problems, network issues) that also affect vote latency.

### Missed votes
If your validator misses a vote entirely (delinquent, restarting, etc.), you earn 0 credits for that slot. This is different from a late vote (which earns at least 1 credit).

## Cumulative Rank vs Per-Epoch Rank

### Why cumulative rank is misleading

The `solana validators` command shows cumulative activated stake rank and cumulative credits. This includes ALL historical epochs since the validator was created. A validator that has been running for 100 epochs with mediocre performance will have a higher cumulative credit total than a new validator with excellent performance after 5 epochs.

Cumulative rank tells you almost nothing about current performance.

### Per-epoch rank is what matters

To assess current health, look at credits earned THIS epoch compared to the cluster. The epoch-performance.py script does exactly this.

Key benchmarks:
- Top 5 validators: These are your ceiling. Usually validators with premium networking (DoubleZero, dedicated links) and optimized hardware.
- Top 50: Strong performance tier. Where a well-configured validator should land.
- Median: Average cluster performance. Being here is acceptable but leaves money on the table.
- Bottom quartile: Indicates a problem. Investigate vote latency, connectivity, compute.

### The cost of restarts

When you restart your validator, you earn 0 credits for the duration of the restart (typically 10-30 minutes, sometimes longer for a full snapshot download). This creates a credit gap that drags down your cumulative rank.

A validator that restarts once per epoch will show a lower cumulative rank than an identical validator that never restarts, even if their per-slot performance is identical when both are running.

This is why per-epoch rank with context (noting any restarts) is the correct way to evaluate performance.

## How to Read Grafana TVC Panels

### Vote Latency Distribution
- X-axis: vote latency in slots
- Y-axis: count of votes at that latency
- What to look for: the distribution should be heavily concentrated at 1-2 slots. A fat tail (lots of votes at 5+ slots) indicates a problem.

### Credits Per Slot
- Shows your credits/slot rate over time
- Ideal: close to 16 (meaning nearly all votes land within grace period)
- Normal healthy range: 14-16
- Concerning: below 13 consistently
- A sudden drop usually indicates a network event or validator issue

### Epoch Credits vs Cluster
- Bar chart comparing your epoch credits to cluster percentiles
- This is the most useful panel for quick health checks
- Your bar should be at or above the median line

### Common Patterns

**Steady ~15.5 credits/slot, occasional dips to ~12**: Normal. The dips usually correspond to network congestion or leader schedule gaps.

**Consistent ~13 credits/slot**: Your votes are landing ~1 slot late on average beyond grace. Check: NIC configuration, BAM connection quality, system load.

**Periodic drops to near-zero then recovery**: Validator is restarting or experiencing delinquency. Check logs for crash/restart cycles.

**Gradual decline over hours/days**: Usually indicates increasing system load (memory pressure, disk I/O contention, growing account state). Check system resources.

**Sudden permanent drop**: Configuration change, network routing change, or hardware failure. Compare against cluster -- if the cluster also dropped, it is a network-wide event, not your problem.

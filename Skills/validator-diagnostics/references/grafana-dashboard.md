# Grafana Dashboard Reference

## Dashboard URL

```
https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?orgId=2&var-cluster=mainnet-beta&var-server=saga-mainnet
```

## Validator Details

| Field | Value |
|-------|-------|
| Name | Saga DAO |
| Identity | `SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ` |
| Vote Account | `sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw` |
| Cluster | mainnet-beta |
| Server | saga-mainnet |

## Timezone Handling

- Grafana displays timestamps in **EDT (UTC-4)**
- Validator terminal logs use **UTC**
- Use `correlate.py` to convert between the two

Example: a Grafana spike at "11:45 PM EDT" corresponds to "03:45 AM UTC" in validator logs.

## Key Panels

### Last Vote Distance
- Shows how many slots behind the cluster tip the validator's last vote is
- Normal: 1-2 slots
- Concerning: 3+ slots sustained
- Spikes to 5+ indicate vote propagation issues or validator falling behind

### Root Slot Distance
- Distance between the validator's root slot and the cluster tip
- Root slot is the most recent finalized slot from the validator's perspective
- Normal: 50-100 slots behind
- High values (200+) indicate the validator is struggling to confirm blocks

### Credits per Minute
- Rate of TVC (Timely Vote Credits) earned
- Directly correlates to epoch rewards
- Sudden drops indicate vote latency problems
- Compare against cluster average for relative performance

### UDP Errors
- Network-level packet errors on the validator
- Includes send/receive errors, dropped packets
- Spikes correlate with vote latency increases
- Sustained errors indicate network infrastructure problems

### Load Average
- System load on the validator machine
- Expressed as 1-min, 5-min, 15-min averages
- High load (above CPU count) causes vote processing delays
- Correlates with increased vote distance

### Skipped Votes %
- Percentage of slots where the validator failed to vote
- Affects block rewards when the validator is leader
- High skip rate alongside high vote distance = systemic issue
- High skip rate with normal vote distance = leader-specific problem

### Vote Latency Distribution
- Histogram of vote landing times (how many slots after the voted-on block)
- Should be heavily concentrated at 1-2 slots
- Fat tail (lots of 3+ slot votes) = investigation needed

### Slot Processing Time
- Time taken to replay/verify each block
- Affects how quickly the validator can generate a vote
- Spikes here directly cause vote latency spikes

### Epoch Progress
- Current epoch number and completion percentage
- Credits earned this epoch vs cluster
- Useful for tracking per-epoch performance trends

## Correlating Grafana with Terminal Monitoring

### Workflow

1. Spot an anomaly on Grafana (e.g., vote distance spike at 11:45 PM EDT)
2. Convert to UTC: `python3 correlate.py --edt "23:45:00"` -> 03:45:00 UTC
3. Check terminal monitoring logs around that UTC time
4. Generate a Grafana URL for the specific window: `python3 correlate.py --window "2026-03-22 03:45:00" 10`
5. Capture that specific window: use the generated URL with `grafana-monitor.py`

### Common Correlation Patterns

**UDP errors spike -> Vote distance increases**
Network packet loss causes the validator to receive blocks late, leading to late votes.

**Load average spikes -> Slot processing time increases -> Vote distance increases**
High CPU/memory pressure slows block replay, delaying vote generation.

**Root slot distance increases -> Credits/min drops**
The validator is falling behind on finalization, losing credits.

**Skipped votes spike -> Check if leader or voter issue**
If skip rate spikes but vote distance is normal, the problem is leader-specific (block production). If both spike, the issue is systemic.

## Snapshot Storage

Snapshots are stored at:
```
/home/workspace/Skills/validator-diagnostics/snapshots/<date>/
```

Each snapshot includes:
- Full dashboard screenshot(s)
- Individual panel screenshots (if --panels used)
- JSON metadata with extracted metrics and timestamps

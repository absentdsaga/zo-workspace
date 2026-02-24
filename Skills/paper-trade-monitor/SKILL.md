---
name: paper-trade-monitor
description: Single source of truth for paper trading positions with clean monitoring and data validation
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# Paper Trade Monitor

Establishes a single source of truth for paper trading bot positions and provides clean, validated monitoring.

## Problem

The current paper trading bot has:
- Multiple inconsistent data sources
- Garbled/corrupted display output
- Duplicate percentage calculations (Entry % AND P&L %)
- No clear source of truth for position state

## Solution

This skill provides:
1. **Single SQLite database** as source of truth
2. **Clean validation** of all position data
3. **Normalized display** with proper formatting
4. **Data integrity checks** to catch corruption early

## Usage

Run the monitor to see current positions from the canonical source:
```bash
bun scripts/monitor.ts
```

Validate data integrity:
```bash
bun scripts/validate.ts
```

## Data Model

Single source of truth: `/tmp/paper-trades.db`

Schema:
- `positions` table: Current open/closed positions
- `price_updates` table: Historical price tracking
- `events` table: Trade events (entry, exit, stop loss)

All other files (JSON, logs) are derived from this database.

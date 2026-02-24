---
name: polymarket-edge-analyzer
description: Deep analysis of Polymarket price ranges to discover statistical edges. Analyzes resolved markets to find where actual outcomes diverge from implied probabilities.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: "1.0.0"
  created: "2026-02-14"
---

# Polymarket Edge Analyzer

Discovers statistical edges in prediction markets by analyzing resolved market data.

## What It Does

1. **Loads resolved market history** from Polymarket
2. **Segments by price range** (e.g., 10-20¢, 5-10¢, 1-5¢)
3. **Calculates edge metrics:**
   - Expected win rate (based on price)
   - Actual win rate (what really happened)
   - Edge percentage (actual - expected)
   - Sample size and statistical significance
4. **Identifies profitable ranges** with sustained mispricing
5. **Generates deployment recommendations**

## When to Use

- Before deploying capital to a new price range
- When current range becomes illiquid
- For validating trading hypotheses
- To discover new opportunities

## Usage

```bash
cd /home/workspace/Projects/polymarket-bot
python3 /home/workspace/Skills/polymarket-edge-analyzer/scripts/analyze.py \
  --ranges "5-10,10-20,20-30,30-40" \
  --min-volume 50000 \
  --output analysis_results.json
```

## Output

Generates comprehensive analysis including:
- Win rate comparison tables
- Edge calculations per range
- Statistical significance tests
- Sample distribution analysis
- Deployment recommendations
- Risk assessments

## Requirements

- `resolved_markets.csv` file in analysis directory
- Python 3 with standard library
- Minimum 50+ resolved markets per range for validity

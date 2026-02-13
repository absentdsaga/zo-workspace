# Shocked PDF Extraction Guide

## Quick Start

When you have a new Shocked Discord PDF to extract:

```bash
# 1. Extract tokens from PDF
cd /home/workspace/Projects/survival-agent
python3 shocked-extractions/extract-shocked-pdf.py /path/to/shocked-chat.pdf

# 2. Review extraction
cat shocked-extractions/YYYY-MM-DD/extraction-summary.md

# 3. Add to bot watchlist
python3 shocked-extractions/add-to-watchlist.py YYYY-MM-DD

# 4. Restart bot to load new tokens
kill $(pgrep -f paper-trade-bot.ts)
source ~/.zo_secrets && nohup bun run testing/paper-trade-bot.ts > /tmp/paper-bot.log 2>&1 &

# 5. Verify bot picked up new tokens
tail -f /tmp/paper-bot.log | grep "Watching"
```

## System Overview

### Directory Structure
```
shocked-extractions/
├── README.md                           # System documentation
├── extract-shocked-pdf.py             # PDF → tokens extractor
├── add-to-watchlist.py                # Merge tokens to bot
├── 2026-02-12/                        # Dated extractions
│   ├── extraction-summary.md          # Human-readable summary
│   ├── tokens-with-info.txt           # Tab-separated data
│   ├── addresses-only.txt             # Just addresses
│   └── source-pdf-info.txt            # PDF metadata
└── 2026-02-13/                        # Next extraction...
    └── ...
```

### Extraction Process

1. **PDF Upload**: Upload PDF to `/home/.z/chat-uploads/` via Claude
2. **Run Extractor**: Script finds all pump.fun addresses (44 chars ending in 'pump')
3. **Context Analysis**: Extracts symbol, FDV, gain% from surrounding text
4. **Priority Assignment**:
   - 🔥 High: 200%+ gains
   - ⚡ Medium: 50-200% gains  
   - 📊 Low: <50% gains
5. **Save to Dated Folder**: Creates YYYY-MM-DD directory with all files
6. **Merge to Watchlist**: Adds tokens to `/tmp/shocked-watchlist.json`
7. **Bot Restart**: Bot picks up new tokens on next scan

### Token Priority in Bot

- **High priority** tokens get bonus score when detected on-chain
- **All priorities** are monitored, but high/medium are favored
- Bot tracks source as `shocked-pdf-YYYY-MM-DD` for analytics

### File Formats

**tokens-with-info.txt** (tab-separated):
```
ADDRESS                                         SYMBOL      FDV     GAIN
9ekm6h4pxZcNbdyMw5fWkEnqAStjQCSzZ3TEfZ7tpump   Tweet       803K    555%
```

**addresses-only.txt** (one per line):
```
9ekm6h4pxZcNbdyMw5fWkEnqAStjQCSzZ3TEfZ7tpump
FP3wqEhXkoFvRRJFi5PSvrotrnvm8kJ7NHuKRf78pump
```

**extraction-summary.md** (markdown report):
```markdown
# Shocked Extraction - 2026-02-12
**Total Tokens:** 17
## Priority Breakdown
- 🔥 High: 3 tokens
- ⚡ Medium: 7 tokens
- 📊 Low: 7 tokens
```

## Current Extractions

### 2026-02-12 (Initial Extraction)
- **PDF**: shocked-51512087884f.pdf (94 pages)
- **Tokens**: 17 unique addresses
- **Status**: ✅ Added to watchlist, bot monitoring
- **Performance**: TBD (v2.0 tracking started)

## Troubleshooting

### "No tokens found"
- PDF might be image-based (OCR needed)
- Try: `strings /path/to/pdf | grep pump`

### "Symbol extraction incorrect"
- PDF chat format is imperfect
- Symbols auto-correct from on-chain metadata on first trade

### "Duplicate tokens"
- Script automatically skips duplicates
- Check existing watchlist: `cat /tmp/shocked-watchlist.json`

### "Bot not picking up tokens"
- Restart bot after adding tokens
- Check bot log: `tail -f /tmp/paper-bot.log | grep "Watching"`
- Verify watchlist loaded: Should show count on startup

## Advanced Usage

### Extract without adding to watchlist
```bash
python3 shocked-extractions/extract-shocked-pdf.py /path/to/pdf
# Review before adding
cat shocked-extractions/YYYY-MM-DD/extraction-summary.md
```

### Add only high-priority tokens
Edit `add-to-watchlist.py` line 82 to filter:
```python
if token['priority'] == 'high':  # Only add high priority
    watchlist.append([...])
```

### Re-extract from old PDF
```bash
# Creates new dated folder
python3 shocked-extractions/extract-shocked-pdf.py /path/to/old-pdf
```

## Integration with v2.0 Bot

The extraction system is designed for the v2.0 paper trading bot:
- Bot runs at `/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts`
- Watchlist at `/tmp/shocked-watchlist.json`
- v2.0 filters exclude dexscreener-only signals
- Shocked tokens get priority scoring boost

## Future Enhancements

- [ ] Auto-OCR for image-based PDFs
- [ ] Real-time on-chain verification of extracted addresses
- [ ] Historical performance tracking per extraction batch
- [ ] Auto-merge on PDF upload (no manual steps)
- [ ] Symbol correction from on-chain metadata

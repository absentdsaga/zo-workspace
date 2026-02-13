# Shocked Alpha Extraction System

This directory organizes all token extractions from Shocked Discord PDFs.

## Directory Structure

```
shocked-extractions/
├── README.md                    # This file
├── 2026-02-12/                  # Date-based extraction folders
│   ├── extraction-summary.md    # Summary of extracted tokens
│   ├── tokens-raw.txt          # Raw addresses
│   ├── tokens-with-info.txt    # Addresses with FDV, gains, etc.
│   └── source-pdf-info.txt     # Original PDF metadata
└── templates/
    └── extraction-template.md   # Template for new extractions
```

## How to Use

### When extracting new PDFs:

1. **Create dated folder**: `YYYY-MM-DD/`
2. **Run extraction script**: Will be created for automated extraction
3. **Review summary**: Check `extraction-summary.md` for quality
4. **Add to watchlist**: Bot will auto-load from dated folders

### Current Extractions

- **2026-02-12**: 17 tokens from 94-page Shocked chat export
  - High priority: 3 tokens (200%+ gains)
  - Medium priority: 7 tokens (50-200% gains)
  - Low priority: 7 tokens (<50% gains)

## Watchlist Integration

The bot automatically loads tokens from:
- `/tmp/shocked-watchlist.json` (active runtime watchlist)
- This directory's dated folders (for historical tracking)

To add new tokens:
```bash
python3 /home/workspace/Projects/survival-agent/shocked-extractions/add-tokens.py YYYY-MM-DD
```

## Token Priority System

- **High**: 200%+ historical gains, strong FDV
- **Medium**: 50-200% gains, decent volume
- **Low**: <50% gains or very early stage

Bot scans all priorities but prioritizes high/medium in scoring.

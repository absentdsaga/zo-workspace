---
name: efficient-referencing
description: |
  Preserves credits by referencing content more efficiently. Use this skill when working with large files, 
  multiple documents, or repetitive content access. It provides strategies and tools for: caching file 
  summaries, extracting targeted sections instead of full reads, deduplicating repeated lookups, and 
  batching related queries. Activates automatically when Zo detects patterns that would benefit from 
  optimization.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---
## Overview

This skill helps you get more out of your Claude plan by reducing unnecessary token usage. The $20/month plan has limits — this skill maximizes what you can do within them.

## User Tips (How YOU Can Help)

### Batch Your Requests
Instead of:
- "Change the color to red"
- "Also make it bigger"  
- "And move it left"

Do this:
- "Change color to red, make it 30% bigger, and move it 20px left"

**Why:** Each message = new API call. Combining requests = fewer calls.

### Be Specific
Instead of: "Fix the bug"
Do this: "The button on line 45 doesn't trigger onClick — fix it"

**Why:** Vague requests require Zo to search/explore first, using more tokens.

### Reference Files by Path
Instead of: "Update that file we were working on"
Do this: "Update `/home/workspace/project/index.html`"

**Why:** Direct paths skip search operations.

### Group Related Tasks
Working on a feature? List everything upfront:
"I need to: 1) Add login form, 2) Style it, 3) Add validation, 4) Connect to API"

**Why:** Zo can plan efficiently and avoid re-reading context.

---

## How Zo Uses This Skill

### File Caching

The cache stores **full file content** with structural indexing. No information is lost.

1. **First read**: Normal `read_file`, then cache with `cache.py cache <file>`
2. **Subsequent access**: Use cache commands instead of re-reading:
   - `cache.py search <file> "query"` — find content by keyword
   - `cache.py section <file> "section name"` — get a section
   - `cache.py lines <file> 50 100` — get specific lines
3. **Stale detection**: Cache auto-invalidates when file changes

### Commands

```bash
# Cache a file
python Skills/efficient-referencing/scripts/cache.py cache <filepath>

# Check cache status
python Skills/efficient-referencing/scripts/cache.py lookup <filepath> --structure

# Search within cached file
python Skills/efficient-referencing/scripts/cache.py search <filepath> "query" --context 3

# Get specific lines
python Skills/efficient-referencing/scripts/cache.py lines <filepath> <start> <end>

# Get a section by name
python Skills/efficient-referencing/scripts/cache.py section <filepath> "section name"

# Clear cache
python Skills/efficient-referencing/scripts/cache.py clear [filepath]
```

### When Zo Should Cache

- File is 200+ lines
- Same file accessed multiple times
- Large documents being searched
- Multi-file operations

### Credit Savings

| Scenario | Without | With | Savings |
|----------|---------|------|---------|
| Read 500-line file 3x | 1500 lines | 500 + cache | ~67% |
| Find quote in large doc | Full read | Cache search | ~90%+ |
| Get one section | Full read | Section only | ~80%+ |

---

## Zo's Efficiency Principles

1. **Don't re-read files** — cache after first read
2. **Targeted edits** — use `edit_file_llm` with precise instructions, not full rewrites
3. **Batch tool calls** — multiple independent operations in one response
4. **Concise responses** — answer directly, skip unnecessary elaboration
5. **Remember context** — don't ask user to repeat what's in conversation history
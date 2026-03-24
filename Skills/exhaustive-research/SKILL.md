---
name: exhaustive-research
description: Enforces exhaustive content research before any analysis or writing. Prevents the pattern of stopping at first results. Must scroll through full profiles, check all media tabs, exhaust all pages of results, and verify completeness before proceeding. Activate this skill before ANY research task.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# Exhaustive Research Protocol

This skill exists because of a repeated pattern: research tasks stop at the first page of results, miss most of the available content, and then produce analysis based on incomplete data. This is unacceptable.

## Core Rules

### 1. NEVER stop at first results
- Always paginate through ALL results
- If a search returns 20 results but you know there should be more, keep going
- Use multiple search queries with different keywords to catch what one query misses

### 2. For X/Twitter profiles
- Go through the ENTIRE media tab, not just recent posts
- Scroll back through the full timeline for the relevant date range
- Check replies, quotes, and tagged posts — not just original posts
- Search for the handle AND the project name separately
- Check who they tagged and follow those threads too

### 3. For video research
- Find ALL videos, not just the ones that match a keyword
- Download and actually watch/transcribe each one
- Extract timestamps for key moments
- Note who appears, what's said, what sponsors/brands are visible
- If burned-in subtitles exist, capture them

### 4. For websites
- Click through every page, every tab, every section
- Don't assume you've seen everything from the homepage
- Check navigation menus, footer links, embedded media

### 5. Completeness verification (MANDATORY)
Before declaring research complete, answer these questions:
- How many pieces of content did I find?
- How many should exist based on profile stats / date ranges?
- If there's a gap, what am I missing?
- Did I check all platforms, not just the primary one?
- Did I follow creator tags and cross-references?

### 6. Documentation
- Log every piece of content found with URL, date, description
- Create a structured inventory before any analysis begins
- Mark items as "found", "downloaded", "transcribed", "analyzed"
- Flag gaps explicitly: "Expected X, found Y, missing Z"

### 7. Only declare complete when
- You can account for ALL content in the date range
- You've checked multiple search approaches
- You've followed cross-references and tags
- Your count matches what's publicly visible on the profile
- You've documented everything in a structured file

## Anti-Patterns (NEVER do these)
- Finding 5 videos when there are 20+ and calling it done
- Searching one keyword and stopping
- Skipping a platform because "probably nothing there"
- Assuming you've seen everything without counting
- Starting to write before research is actually complete
- Declaring research done without a completeness check

## Activation
This skill should be activated BEFORE starting any research task. Run the checklist script to create a tracking document, then fill it in as you go.

## Scripts
- `scripts/research-checklist.py` — Generate a structured research checklist for any topic

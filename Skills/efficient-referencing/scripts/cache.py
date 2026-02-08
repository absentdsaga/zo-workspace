#!/usr/bin/env python3
"""
Intelligent file caching for efficient referencing.
Stores full content with structure indexing — no information loss.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path("/home/.z/cache/file-refs")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_path(filepath: str) -> Path:
    """Get cache file path for a given file."""
    abs_path = os.path.abspath(filepath)
    hash_key = hashlib.md5(abs_path.encode()).hexdigest()[:12]
    name = Path(filepath).stem[:30]
    return CACHE_DIR / f"{name}_{hash_key}.json"

def get_file_hash(filepath: str) -> str:
    """Get content hash to detect changes."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def extract_structure(content: str, filepath: str) -> dict:
    """Extract navigable structure from content."""
    lines = content.split('\n')
    ext = Path(filepath).suffix.lower()
    
    structure = {
        "sections": [],
        "definitions": [],
        "key_lines": {}
    }
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Markdown headers
        if ext in ['.md', '.markdown'] and stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            title = stripped.lstrip('#').strip()
            structure["sections"].append({
                "line": i,
                "level": level,
                "title": title
            })
        
        # Python
        elif ext == '.py':
            if stripped.startswith('def '):
                match = re.match(r'def\s+(\w+)', stripped)
                if match:
                    structure["definitions"].append({
                        "line": i,
                        "type": "function",
                        "name": match.group(1)
                    })
            elif stripped.startswith('class '):
                match = re.match(r'class\s+(\w+)', stripped)
                if match:
                    structure["definitions"].append({
                        "line": i,
                        "type": "class",
                        "name": match.group(1)
                    })
        
        # JavaScript/TypeScript
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            if 'function ' in stripped:
                match = re.search(r'function\s+(\w+)', stripped)
                if match:
                    structure["definitions"].append({
                        "line": i,
                        "type": "function",
                        "name": match.group(1)
                    })
            elif re.match(r'(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s+)?\(', stripped):
                match = re.search(r'(const|let|var)\s+(\w+)', stripped)
                if match:
                    structure["definitions"].append({
                        "line": i,
                        "type": "arrow_fn",
                        "name": match.group(2)
                    })
    
    return structure

def cache_file(filepath: str) -> dict:
    """Cache a file with full content and structure."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    lines = content.split('\n')
    structure = extract_structure(content, filepath)
    
    entry = {
        "filepath": os.path.abspath(filepath),
        "filename": os.path.basename(filepath),
        "cached_at": datetime.now().isoformat(),
        "file_hash": get_file_hash(filepath),
        "line_count": len(lines),
        "byte_size": len(content.encode('utf-8')),
        "content": content,
        "lines": lines,
        "structure": structure
    }
    
    cache_path = get_cache_path(filepath)
    with open(cache_path, 'w') as f:
        json.dump(entry, f)
    
    return entry

def lookup_cache(filepath: str) -> dict | None:
    """Look up cached file, returns None if stale or missing."""
    cache_path = get_cache_path(filepath)
    
    if not cache_path.exists():
        return None
    
    with open(cache_path, 'r') as f:
        entry = json.load(f)
    
    # Check if file changed
    if os.path.exists(filepath):
        current_hash = get_file_hash(filepath)
        if current_hash != entry.get("file_hash"):
            return None  # Stale cache
    
    return entry

def get_or_cache(filepath: str) -> dict:
    """Get from cache or cache if needed."""
    entry = lookup_cache(filepath)
    if entry is None:
        entry = cache_file(filepath)
    return entry

def search_content(entry: dict, query: str, context: int = 2) -> list:
    """Search cached content, return matches with context."""
    results = []
    lines = entry["lines"]
    query_lower = query.lower()
    
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            results.append({
                "line": i + 1,
                "match": line,
                "context": lines[start:end],
                "context_start": start + 1
            })
    
    return results

def get_lines(entry: dict, start: int, end: int) -> list:
    """Get specific line range from cache."""
    lines = entry["lines"]
    start_idx = max(0, start - 1)
    end_idx = min(len(lines), end)
    return lines[start_idx:end_idx]

def get_section(entry: dict, section_query: str) -> dict | None:
    """Find a section by name and return its content."""
    sections = entry["structure"]["sections"]
    query_lower = section_query.lower()
    
    # Find matching section
    match_idx = None
    for i, s in enumerate(sections):
        if query_lower in s["title"].lower():
            match_idx = i
            break
    
    if match_idx is None:
        return None
    
    section = sections[match_idx]
    start_line = section["line"]
    
    # Find end (next section at same or higher level, or EOF)
    end_line = len(entry["lines"])
    for s in sections[match_idx + 1:]:
        if s["level"] <= section["level"]:
            end_line = s["line"] - 1
            break
    
    return {
        "title": section["title"],
        "level": section["level"],
        "start_line": start_line,
        "end_line": end_line,
        "content": "\n".join(entry["lines"][start_line - 1:end_line])
    }

def format_structure(entry: dict) -> str:
    """Format structure for display."""
    output = []
    output.append(f"File: {entry['filename']} ({entry['line_count']} lines, {entry['byte_size']} bytes)")
    output.append(f"Cached: {entry['cached_at']}")
    
    if entry["structure"]["sections"]:
        output.append("\nSections:")
        for s in entry["structure"]["sections"]:
            indent = "  " * s["level"]
            output.append(f"  {indent}L{s['line']}: {s['title']}")
    
    if entry["structure"]["definitions"]:
        output.append("\nDefinitions:")
        for d in entry["structure"]["definitions"][:20]:
            output.append(f"  L{d['line']}: {d['type']} {d['name']}")
        if len(entry["structure"]["definitions"]) > 20:
            output.append(f"  ... and {len(entry['structure']['definitions']) - 20} more")
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Intelligent file cache")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Cache command
    cache_p = subparsers.add_parser("cache", help="Cache a file")
    cache_p.add_argument("filepath", help="File to cache")
    
    # Lookup command
    lookup_p = subparsers.add_parser("lookup", help="Check if file is cached")
    lookup_p.add_argument("filepath", help="File to look up")
    lookup_p.add_argument("--structure", "-s", action="store_true", help="Show structure only")
    
    # Search command
    search_p = subparsers.add_parser("search", help="Search cached content")
    search_p.add_argument("filepath", help="File to search")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--context", "-c", type=int, default=2, help="Lines of context")
    
    # Lines command
    lines_p = subparsers.add_parser("lines", help="Get specific lines")
    lines_p.add_argument("filepath", help="File")
    lines_p.add_argument("start", type=int, help="Start line (1-indexed)")
    lines_p.add_argument("end", type=int, help="End line (inclusive)")
    
    # Section command
    section_p = subparsers.add_parser("section", help="Get a section by name")
    section_p.add_argument("filepath", help="File")
    section_p.add_argument("query", help="Section name to find")
    
    # Clear command
    clear_p = subparsers.add_parser("clear", help="Clear cache")
    clear_p.add_argument("filepath", nargs="?", help="Specific file, or all if omitted")
    
    args = parser.parse_args()
    
    if args.command == "cache":
        entry = cache_file(args.filepath)
        print(format_structure(entry))
        
    elif args.command == "lookup":
        entry = lookup_cache(args.filepath)
        if entry:
            if args.structure:
                print(format_structure(entry))
            else:
                print(f"Cached: {entry['filename']} ({entry['line_count']} lines)")
                print(f"Hash: {entry['file_hash'][:8]}...")
        else:
            print("Not cached or stale")
            sys.exit(1)
            
    elif args.command == "search":
        entry = get_or_cache(args.filepath)
        results = search_content(entry, args.query, args.context)
        print(f"Found {len(results)} matches for '{args.query}':\n")
        for r in results:
            print(f"Line {r['line']}: {r['match'].strip()}")
            if args.context > 0:
                print(f"  Context (L{r['context_start']}-{r['context_start'] + len(r['context']) - 1}):")
                for ctx_line in r['context']:
                    print(f"    {ctx_line}")
                print()
                
    elif args.command == "lines":
        entry = get_or_cache(args.filepath)
        lines = get_lines(entry, args.start, args.end)
        for i, line in enumerate(lines, args.start):
            print(f"{i}: {line}")
            
    elif args.command == "section":
        entry = get_or_cache(args.filepath)
        section = get_section(entry, args.query)
        if section:
            print(f"## {section['title']} (lines {section['start_line']}-{section['end_line']})\n")
            print(section['content'])
        else:
            print(f"Section matching '{args.query}' not found")
            sys.exit(1)
            
    elif args.command == "clear":
        if args.filepath:
            cache_path = get_cache_path(args.filepath)
            if cache_path.exists():
                cache_path.unlink()
                print(f"Cleared cache for: {args.filepath}")
            else:
                print(f"No cache found for: {args.filepath}")
        else:
            count = 0
            for f in CACHE_DIR.glob("*.json"):
                f.unlink()
                count += 1
            print(f"Cleared {count} cache entries")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Batch operations for efficient multi-file processing.
Extract patterns, search, and aggregate across files in single passes.
"""

import argparse
import fnmatch
import os
import re
import sys
from pathlib import Path

def find_files(pattern: str, root: str = "/home/workspace") -> list[str]:
    """Find files matching a glob pattern."""
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip common non-content directories
        dirnames[:] = [d for d in dirnames if d not in {
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            'dist', 'build', '.next', 'Trash', '.z'
        }]
        
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                matches.append(os.path.join(dirpath, filename))
    
    return sorted(matches)

def extract_pattern(files: list[str], pattern: str, context: int = 0) -> dict:
    """Extract lines matching a pattern from multiple files."""
    results = {}
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception as e:
            continue
        
        matches = []
        for i, line in enumerate(lines):
            if re.search(pattern, line) if pattern.startswith('^') or '\\' in pattern else pattern in line:
                match_data = {
                    "line": i + 1,
                    "content": line.rstrip()
                }
                
                if context > 0:
                    start = max(0, i - context)
                    end = min(len(lines), i + context + 1)
                    match_data["context"] = [l.rstrip() for l in lines[start:end]]
                    match_data["context_start"] = start + 1
                
                matches.append(match_data)
        
        if matches:
            results[filepath] = matches
    
    return results

def aggregate_headers(files: list[str]) -> dict:
    """Aggregate all headers/sections from markdown files."""
    all_headers = {}
    
    for filepath in files:
        if not filepath.endswith(('.md', '.markdown')):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception:
            continue
        
        headers = []
        for i, line in enumerate(lines):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                headers.append({"line": i + 1, "level": level, "title": title})
        
        if headers:
            all_headers[filepath] = headers
    
    return all_headers

def search_definitions(files: list[str], name_pattern: str = None) -> dict:
    """Search for function/class definitions across files."""
    results = {}
    
    patterns = [
        (r'^(async\s+)?def\s+(\w+)', 'function'),
        (r'^class\s+(\w+)', 'class'),
        (r'^(export\s+)?(async\s+)?function\s+(\w+)', 'function'),
        (r'^(export\s+)?class\s+(\w+)', 'class'),
        (r'^(export\s+)?(const|let)\s+(\w+)\s*=.*=>', 'arrow_fn'),
    ]
    
    for filepath in files:
        ext = Path(filepath).suffix
        if ext not in ['.py', '.js', '.ts', '.tsx', '.jsx']:
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception:
            continue
        
        definitions = []
        for i, line in enumerate(lines):
            for pattern, kind in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    groups = [g for g in match.groups() if g and not g.isspace()]
                    name = groups[-1] if groups else None
                    
                    if name and (name_pattern is None or re.search(name_pattern, name, re.I)):
                        definitions.append({
                            "line": i + 1,
                            "type": kind,
                            "name": name,
                            "signature": line.strip()[:100]
                        })
                    break
        
        if definitions:
            results[filepath] = definitions
    
    return results

def format_results(results: dict, mode: str) -> str:
    """Format batch results for display."""
    if not results:
        return "No results found."
    
    out = []
    total_matches = sum(len(v) for v in results.values())
    out.append(f"Found {total_matches} matches in {len(results)} files:\n")
    
    for filepath, matches in results.items():
        rel_path = os.path.relpath(filepath, "/home/workspace")
        out.append(f"## {rel_path}")
        
        for m in matches[:20]:  # Limit per file
            if mode == "pattern":
                out.append(f"  L{m['line']}: {m['content'][:100]}")
            elif mode == "headers":
                indent = "  " * (m['level'] - 1)
                out.append(f"  {indent}L{m['line']}: {m['title']}")
            elif mode == "definitions":
                out.append(f"  L{m['line']}: {m['type']} `{m['name']}`")
        
        if len(matches) > 20:
            out.append(f"  ... and {len(matches) - 20} more")
        out.append("")
    
    return '\n'.join(out)

def main():
    parser = argparse.ArgumentParser(description="Batch file operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # extract-pattern
    extract_p = subparsers.add_parser("extract-pattern", help="Extract lines matching a pattern")
    extract_p.add_argument("file_pattern", help="Glob pattern for files (e.g. '*.md')")
    extract_p.add_argument("search_pattern", help="Pattern to search for in files")
    extract_p.add_argument("--context", "-c", type=int, default=0, help="Lines of context")
    extract_p.add_argument("--root", default="/home/workspace", help="Root directory")
    
    # headers
    headers_p = subparsers.add_parser("headers", help="Aggregate headers from markdown files")
    headers_p.add_argument("file_pattern", nargs="?", default="*.md", help="Glob pattern")
    headers_p.add_argument("--root", default="/home/workspace", help="Root directory")
    
    # definitions
    defs_p = subparsers.add_parser("definitions", help="Find function/class definitions")
    defs_p.add_argument("file_pattern", nargs="?", default="*.py", help="Glob pattern")
    defs_p.add_argument("--name", "-n", help="Filter by name pattern (regex)")
    defs_p.add_argument("--root", default="/home/workspace", help="Root directory")
    
    # list-files
    list_p = subparsers.add_parser("list-files", help="List files matching pattern")
    list_p.add_argument("file_pattern", help="Glob pattern")
    list_p.add_argument("--root", default="/home/workspace", help="Root directory")
    
    args = parser.parse_args()
    
    if args.command == "extract-pattern":
        files = find_files(args.file_pattern, args.root)
        if not files:
            print(f"No files matching: {args.file_pattern}")
            sys.exit(1)
        results = extract_pattern(files, args.search_pattern, args.context)
        print(format_results(results, "pattern"))
    
    elif args.command == "headers":
        files = find_files(args.file_pattern, args.root)
        results = aggregate_headers(files)
        print(format_results(results, "headers"))
    
    elif args.command == "definitions":
        files = find_files(args.file_pattern, args.root)
        results = search_definitions(files, args.name)
        print(format_results(results, "definitions"))
    
    elif args.command == "list-files":
        files = find_files(args.file_pattern, args.root)
        print(f"Found {len(files)} files:\n")
        for f in files[:100]:
            print(os.path.relpath(f, args.root))
        if len(files) > 100:
            print(f"\n... and {len(files) - 100} more")

if __name__ == "__main__":
    main()

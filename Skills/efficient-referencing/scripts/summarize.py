#!/usr/bin/env python3
"""
Generate lightweight summaries of files for efficient referencing.
Extracts structure, key terms, and section boundaries without full content.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from collections import Counter

def extract_summary(filepath: str) -> dict:
    """Extract a lightweight summary from a file."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    lines = content.split('\n')
    ext = Path(filepath).suffix.lower()
    
    summary = {
        "file": os.path.basename(filepath),
        "path": os.path.abspath(filepath),
        "extension": ext,
        "total_lines": len(lines),
        "size_bytes": len(content.encode('utf-8')),
        "sections": [],
        "definitions": [],
        "imports": [],
        "key_terms": [],
        "line_index": {}  # section_name -> line_range
    }
    
    # Track sections for line index
    current_section = None
    current_section_start = 1
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Markdown headers
        if ext in ['.md', '.markdown'] and stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            title = stripped.lstrip('#').strip()
            
            # Close previous section
            if current_section:
                summary["line_index"][current_section] = (current_section_start, i - 1)
            
            summary["sections"].append({
                "line": i,
                "level": level,
                "title": title
            })
            current_section = title
            current_section_start = i
        
        # Python
        elif ext == '.py':
            if stripped.startswith(('def ', 'class ', 'async def ')):
                match = re.match(r'(async\s+)?(def|class)\s+(\w+)', stripped)
                if match:
                    summary["definitions"].append({
                        "line": i,
                        "type": match.group(2),
                        "name": match.group(3)
                    })
            elif stripped.startswith(('import ', 'from ')):
                summary["imports"].append(stripped)
        
        # JavaScript/TypeScript
        elif ext in ['.js', '.ts', '.tsx', '.jsx']:
            if re.match(r'^(export\s+)?(async\s+)?function\s+\w+', stripped):
                match = re.search(r'function\s+(\w+)', stripped)
                if match:
                    summary["definitions"].append({
                        "line": i,
                        "type": "function",
                        "name": match.group(1)
                    })
            elif re.match(r'^(export\s+)?class\s+\w+', stripped):
                match = re.search(r'class\s+(\w+)', stripped)
                if match:
                    summary["definitions"].append({
                        "line": i,
                        "type": "class",
                        "name": match.group(1)
                    })
            elif re.match(r'^(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s+)?\(', stripped):
                match = re.search(r'(const|let|var)\s+(\w+)', stripped)
                if match:
                    summary["definitions"].append({
                        "line": i,
                        "type": "arrow_fn",
                        "name": match.group(2)
                    })
            elif stripped.startswith('import '):
                summary["imports"].append(stripped[:100])
    
    # Close final section
    if current_section:
        summary["line_index"][current_section] = (current_section_start, len(lines))
    
    # Extract key terms (frequent capitalized words, excluding common ones)
    common_words = {'The', 'This', 'That', 'There', 'These', 'When', 'Where', 'What', 
                    'How', 'Why', 'If', 'For', 'And', 'But', 'Not', 'With', 'From',
                    'All', 'Any', 'Each', 'Some', 'None', 'True', 'False', 'None'}
    words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', content)
    word_counts = Counter(w for w in words if w not in common_words)
    summary["key_terms"] = [term for term, count in word_counts.most_common(20) if count >= 2]
    
    # Dedupe imports
    summary["imports"] = list(dict.fromkeys(summary["imports"]))[:20]
    
    return summary

def format_summary(summary: dict, verbose: bool = False) -> str:
    """Format summary for display."""
    out = [
        f"# {summary['file']}",
        f"Path: {summary['path']}",
        f"Size: {summary['total_lines']} lines, {summary['size_bytes']:,} bytes",
        ""
    ]
    
    if summary["sections"]:
        out.append("## Structure")
        for sec in summary["sections"]:
            indent = "  " * (sec["level"] - 1)
            out.append(f"{indent}- L{sec['line']}: {sec['title']}")
        out.append("")
    
    if summary["definitions"]:
        out.append("## Definitions")
        for defn in summary["definitions"][:30]:
            out.append(f"- L{defn['line']}: {defn['type']} `{defn['name']}`")
        if len(summary["definitions"]) > 30:
            out.append(f"- ... and {len(summary['definitions']) - 30} more")
        out.append("")
    
    if verbose and summary["imports"]:
        out.append("## Imports")
        for imp in summary["imports"][:10]:
            out.append(f"- {imp}")
        if len(summary["imports"]) > 10:
            out.append(f"- ... and {len(summary['imports']) - 10} more")
        out.append("")
    
    if summary["key_terms"]:
        out.append("## Key Terms")
        out.append(", ".join(summary["key_terms"]))
        out.append("")
    
    if summary["line_index"]:
        out.append("## Section Line Ranges")
        for section, (start, end) in summary["line_index"].items():
            out.append(f"- \"{section}\": lines {start}-{end}")
    
    return '\n'.join(out)

def main():
    parser = argparse.ArgumentParser(description="Generate lightweight file summaries")
    parser.add_argument("filepath", help="File to summarize")
    parser.add_argument("--output", "-o", help="Save summary to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Include more details")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.filepath):
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)
    
    summary = extract_summary(args.filepath)
    
    if args.json:
        import json
        output = json.dumps(summary, indent=2)
    else:
        output = format_summary(summary, args.verbose)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Summary saved to: {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()

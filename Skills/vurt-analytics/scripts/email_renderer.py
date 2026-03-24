#!/usr/bin/env python3
"""Convert VURT daily analytics markdown report to styled HTML email.

Gmail strips <style> blocks — all styles MUST be inlined on each element.
"""

import re

# Inline style constants
S_BODY = "background:#0a0a0a;color:#e0e0e0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;padding:0;"
S_CONTAINER = "max-width:720px;margin:0 auto;padding:32px 24px;background:#0a0a0a;"
S_H1 = "color:#fff;font-size:26px;font-weight:700;margin:0 0 4px 0;"
S_H2 = "color:#fff;font-size:18px;font-weight:600;margin:32px 0 12px 0;border-bottom:1px solid #333;padding-bottom:6px;"
S_P = "margin:8px 0;line-height:1.6;font-size:14px;color:#e0e0e0;"
S_DATE = "color:#888;font-size:14px;margin-bottom:24px;"
S_TABLE = "width:100%;border-collapse:collapse;margin:8px 0 16px 0;font-size:13px;"
S_TH = "background:#1a1a1a;color:#aaa;text-align:left;padding:8px 10px;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;border-bottom:2px solid #333;"
S_TD = "padding:7px 10px;border-bottom:1px solid #1f1f1f;color:#ccc;"
S_TD_BOLD = "color:#fff;font-weight:700;"
S_POSITIVE = "color:#4ade80;"
S_NEGATIVE = "color:#f87171;"
S_INSIGHT = "background:#111;border-left:3px solid #6c63ff;padding:10px 14px;margin:10px 0;border-radius:3px;font-size:14px;line-height:1.65;color:#ccc;"
S_INSIGHT_NUM = "color:#6c63ff;font-weight:700;margin-right:4px;"
S_INSIGHT_BOLD = "color:#fff;"
S_INSIGHT_EM = "color:#a78bfa;font-style:italic;"
S_FOOTER = "margin-top:32px;padding-top:16px;border-top:1px solid #222;color:#555;font-size:12px;"
S_LINK = "color:#818cf8;"


def md_table_to_html(lines):
    """Convert markdown table lines to HTML table with inline styles."""
    if len(lines) < 2:
        return ""
    headers = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    html = f'<table style="{S_TABLE}">\n<thead><tr>'
    for h in headers:
        html += f'<th style="{S_TH}">{h}</th>'
    html += '</tr></thead>\n<tbody>\n'
    for row in rows:
        html += '<tr>'
        for cell in row:
            styled = _style_cell(cell)
            html += f'<td style="{S_TD}">{styled}</td>'
        html += '</tr>\n'
    html += '</tbody></table>\n'
    return html


def _style_cell(cell):
    """Apply inline color styling to cell content."""
    cell = re.sub(r'\*\*(.+?)\*\*', rf'<strong style="{S_TD_BOLD}">\1</strong>', cell)
    match = re.search(r'([+-][\d,.]+%)', cell)
    if match:
        val = match.group(1)
        if val.startswith('+'):
            cell = cell.replace(val, f'<span style="{S_POSITIVE}">{val}</span>')
        elif val.startswith('-'):
            cell = cell.replace(val, f'<span style="{S_NEGATIVE}">{val}</span>')
    return cell


def _style_inline(text, bold_style=S_INSIGHT_BOLD):
    """Convert markdown inline formatting to HTML with inline styles."""
    text = re.sub(r'\*\*(.+?)\*\*', rf'<strong style="{bold_style}">\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', rf'<em style="{S_INSIGHT_EM}">\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rf'<a href="\2" style="{S_LINK}">\1</a>', text)
    return text


def markdown_to_html(md_text):
    """Convert the full markdown report to styled HTML email with all inline styles."""
    lines = md_text.split('\n')
    html_parts = []
    i = 0
    insight_counter = 0

    while i < len(lines):
        line = lines[i]

        # H1
        if line.startswith('# ') and not line.startswith('## '):
            html_parts.append(f'<h1 style="{S_H1}">{line[2:].strip()}</h1>')
            i += 1
            continue

        # Date line
        if line.startswith('**') and line.endswith('**') and i < 3:
            html_parts.append(f'<p style="{S_DATE}">{line.strip("*")}</p>')
            i += 1
            continue

        # H2
        if line.startswith('## '):
            section = line[3:].strip()
            html_parts.append(f'<h2 style="{S_H2}">{section}</h2>')
            if section == "Insights & Actions":
                insight_counter = 0
            i += 1
            continue

        # Table detection
        if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            html_parts.append(md_table_to_html(table_lines))
            continue

        # Numbered insights
        num_match = re.match(r'^(\d+)\.\s+(.+)', line)
        if num_match:
            insight_counter += 1
            content = num_match.group(2)
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r'^\d+\.\s+', lines[i + 1]) and not lines[i + 1].startswith('#') and not lines[i + 1].startswith('|') and not lines[i + 1].startswith('---'):
                i += 1
                content += ' ' + lines[i].strip()
            content = _style_inline(content)
            html_parts.append(f'<div style="{S_INSIGHT}"><span style="{S_INSIGHT_NUM}">{insight_counter}.</span> {content}</div>')
            i += 1
            continue

        # Horizontal rule
        if line.strip() == '---':
            i += 1
            continue

        # Footer
        if line.startswith('*Generated'):
            html_parts.append(f'<div style="{S_FOOTER}">{_style_inline(line.strip("*"))}</div>')
            i += 1
            continue

        # Regular paragraph
        stripped = line.strip()
        if stripped:
            html_parts.append(f'<p style="{S_P}">{_style_inline(stripped)}</p>')

        i += 1

    body = '\n'.join(html_parts)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="{S_BODY}">
<div style="{S_CONTAINER}">
{body}
</div>
</body>
</html>"""


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            md = f.read()
    else:
        md = sys.stdin.read()
    print(markdown_to_html(md))

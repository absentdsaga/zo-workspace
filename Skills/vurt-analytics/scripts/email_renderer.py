#!/usr/bin/env python3
"""Convert VURT daily analytics markdown report to styled HTML email.

Uses a <style> block in the body (supported by Gmail since 2016) to avoid
repeating inline styles on every element, keeping the HTML under Gmail's
102KB clip threshold.
"""

import re

CSS = """
body{background:#0a0a0a;color:#e0e0e0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;padding:0}
.wrap{max-width:720px;margin:0 auto;padding:32px 24px;background:#0a0a0a}
h1{color:#fff;font-size:26px;font-weight:700;margin:0 0 4px 0}
h2{color:#fff;font-size:18px;font-weight:600;margin:32px 0 12px 0;border-bottom:1px solid #333;padding-bottom:6px}
h3{color:#ccc;font-size:14px;font-weight:600;margin:18px 0 6px 0;text-transform:uppercase;letter-spacing:.5px}
p{margin:8px 0;line-height:1.6;font-size:14px;color:#e0e0e0}
.date{color:#888;font-size:14px;margin-bottom:24px}
table{width:100%;border-collapse:collapse;margin:8px 0 16px 0;font-size:13px}
th{background:#1a1a1a;color:#aaa;text-align:left;padding:8px 10px;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid #333}
td{padding:7px 10px;border-bottom:1px solid #1f1f1f;color:#ccc}
.pos{color:#4ade80}
.neg{color:#f87171}
.ins{background:#111;border-left:3px solid #6c63ff;padding:10px 14px;margin:10px 0;border-radius:3px;font-size:14px;line-height:1.65;color:#ccc}
.ins-n{color:#6c63ff;font-weight:700;margin-right:4px}
.ft{margin-top:32px;padding-top:16px;border-top:1px solid #222;color:#555;font-size:12px}
a{color:#818cf8}
strong{color:#fff}
em{color:#a78bfa;font-style:italic}
"""


def md_table_to_html(lines):
    if len(lines) < 2:
        return ""
    headers = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    html = '<table>\n<thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead>\n<tbody>\n'
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{_style_cell(cell)}</td>'
        html += '</tr>\n'
    html += '</tbody></table>\n'
    return html


def _style_cell(cell):
    cell = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', cell)
    match = re.search(r'([+-][\d,.]+%)', cell)
    if match:
        val = match.group(1)
        cls = 'pos' if val.startswith('+') else 'neg'
        cell = cell.replace(val, f'<span class="{cls}">{val}</span>')
    return cell


def _style_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(md_text):
    lines = md_text.split('\n')
    html_parts = []
    i = 0
    insight_counter = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith('# ') and not line.startswith('## '):
            html_parts.append(f'<h1>{line[2:].strip()}</h1>')
            i += 1
            continue

        if line.startswith('**') and line.endswith('**') and i < 3:
            html_parts.append(f'<p class="date">{line.strip("*")}</p>')
            i += 1
            continue

        if line.startswith('## '):
            section = line[3:].strip()
            html_parts.append(f'<h2>{section}</h2>')
            if section == "Insights & Actions":
                insight_counter = 0
            i += 1
            continue

        if line.startswith('### '):
            html_parts.append(f'<h3>{line[4:].strip()}</h3>')
            i += 1
            continue

        if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            html_parts.append(md_table_to_html(table_lines))
            continue

        num_match = re.match(r'^(\d+)\.\s+(.+)', line)
        if num_match:
            insight_counter += 1
            content = num_match.group(2)
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r'^\d+\.\s+', lines[i + 1]) and not lines[i + 1].startswith('#') and not lines[i + 1].startswith('|') and not lines[i + 1].startswith('---'):
                i += 1
                content += ' ' + lines[i].strip()
            html_parts.append(f'<div class="ins"><span class="ins-n">{insight_counter}.</span> {_style_inline(content)}</div>')
            i += 1
            continue

        if line.strip() == '---':
            i += 1
            continue

        if line.startswith('*Generated'):
            html_parts.append(f'<div class="ft">{_style_inline(line.strip("*"))}</div>')
            i += 1
            continue

        stripped = line.strip()
        if stripped:
            html_parts.append(f'<p>{_style_inline(stripped)}</p>')

        i += 1

    body = '\n'.join(html_parts)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
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

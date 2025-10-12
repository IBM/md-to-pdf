#!/usr/bin/env python3
"""
Professional markdown to printable HTML with Mermaid diagram support
Handles tables, lists, and all markdown elements properly
Usage: python3 md2html-pro.py any-file.md
"""

import sys
import re
from pathlib import Path

def convert(md_file):
    with open(md_file, 'r') as f:
        content = f.read()

    # Process markdown - Mermaid blocks first to protect them
    html = content

    # Extract and convert Mermaid blocks first
    html = re.sub(r'```mermaid\n(.*?)```', r'<div class="mermaid">\1</div>', html, flags=re.DOTALL)

    # Convert other code blocks
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)

    # Convert headers (largest to smallest to avoid conflicts)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Convert formatting
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', html)

    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Convert tables
    def convert_table(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 3:
            return match.group(0)

        html_table = '<table>\n<thead>\n<tr>\n'
        headers = [h.strip() for h in lines[0].split('|')[1:-1]]
        for h in headers:
            # Process bold in headers
            h = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', h)
            html_table += f'<th>{h}</th>\n'
        html_table += '</tr>\n</thead>\n<tbody>\n'

        for line in lines[2:]:
            if line.strip() and '|' in line:
                cells = [c.strip() for c in line.split('|')[1:-1]]
                html_table += '<tr>\n'
                for c in cells:
                    # Process bold in cells
                    c = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', c)
                    html_table += f'<td>{c}</td>\n'
                html_table += '</tr>\n'
        html_table += '</tbody>\n</table>'
        return html_table

    # Fix table pattern to be more robust
    table_pattern = r'^\|[^\n]+\|\n\|[\s:\-\|]+\|\n(?:\|[^\n]+\|\n?)+'
    html = re.sub(table_pattern, convert_table, html, flags=re.MULTILINE)

    # Convert lists (handle properly)
    lines = html.split('\n')
    result = []
    in_list = False
    in_ol = False
    ol_counter = 1

    for line in lines:
        # Unordered lists
        if line.strip().startswith('- '):
            if in_ol:
                result.append('</ol>')
                in_ol = False
                ol_counter = 1
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line.strip()[2:]}</li>')
        # Ordered lists
        elif re.match(r'^\d+\.\s', line.strip()):
            if in_list:
                result.append('</ul>')
                in_list = False
            if not in_ol:
                result.append('<ol>')
                in_ol = True
                ol_counter = 1
            content = re.sub(r'^\d+\.\s', '', line.strip())
            result.append(f'<li>{content}</li>')
            ol_counter += 1
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            if in_ol:
                result.append('</ol>')
                in_ol = False
                ol_counter = 1
            result.append(line)

    if in_list:
        result.append('</ul>')
    if in_ol:
        result.append('</ol>')

    html = '\n'.join(result)

    # Add paragraphs to standalone text lines (but not inside mermaid blocks)
    lines = html.split('\n')
    final_result = []
    inside_mermaid = False

    for line in lines:
        if '<div class="mermaid">' in line:
            inside_mermaid = True
            final_result.append(line)
        elif '</div>' in line and inside_mermaid:
            inside_mermaid = False
            final_result.append(line)
        elif inside_mermaid:
            # Don't add paragraph tags inside mermaid blocks
            final_result.append(line)
        elif (line.strip() and
              not line.strip().startswith('<') and
              not line.strip().startswith('|')):
            final_result.append(f'<p>{line}</p>')
        else:
            final_result.append(line)

    html = '\n'.join(final_result)

    title = Path(md_file).stem.replace('-', ' ').replace('_', ' ').title()

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{
    startOnLoad: true,
    theme: 'default',
    themeVariables: {{
        primaryColor: '#fff',
        primaryTextColor: '#000',
        primaryBorderColor: '#333',
        lineColor: '#333',
        background: '#fff'
    }}
}});
window.onload = function() {{
    setTimeout(function() {{
        console.log('✅ Page ready for printing! Press Ctrl+P to save as PDF');
    }}, 2000);
}};
</script>
<style>
@page {{ size: A4; margin: 15mm; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    background: white;
}}
h1 {{
    color: #2c3e50;
    border-bottom: 3px solid #3498db;
    padding-bottom: 12px;
    margin-top: 30px;
    page-break-after: avoid;
}}
h1:first-of-type {{ margin-top: 0; }}
h2 {{
    color: #34495e;
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 8px;
    margin-top: 28px;
    page-break-after: avoid;
}}
h3 {{
    color: #34495e;
    margin-top: 24px;
    font-size: 1.2em;
    page-break-after: avoid;
}}
h4 {{
    color: #555;
    margin-top: 20px;
    page-break-after: avoid;
}}
p {{ margin: 12px 0; }}
ul, ol {{ margin: 12px 0; padding-left: 25px; }}
ul li, ol li {{ margin: 8px 0; }}
strong {{ color: #2c3e50; font-weight: 600; }}
em {{ font-style: italic; }}
.mermaid {{
    text-align: center;
    margin: 25px 0;
    page-break-inside: avoid;
}}
.mermaid svg {{ max-width: 100%; height: auto; }}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    page-break-inside: avoid;
}}
th {{
    background: #3498db;
    color: white;
    padding: 10px;
    text-align: left;
    font-weight: 600;
}}
td {{
    padding: 8px;
    border: 1px solid #ecf0f1;
}}
tr:nth-child(even) {{ background: #f9f9f9; }}
code {{
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}}
pre {{
    background: #f4f4f4;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}}
pre code {{ background: none; padding: 0; }}
hr {{
    border: none;
    border-top: 2px solid #ecf0f1;
    margin: 30px 0;
    page-break-after: avoid;
}}
@media print {{
    body {{ margin: 0; padding: 0; }}
    .mermaid {{ break-inside: avoid; page-break-inside: avoid; }}
    h1 {{ font-size: 24pt; }}
    h2 {{ font-size: 18pt; }}
    h3 {{ font-size: 14pt; }}
}}
</style>
</head>
<body>
{html}
</body>
</html>"""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 md2html-pro.py <file.md>")
        print("\nExample:")
        print("  python3 md2html-pro.py meeting-materials/EXECUTIVE-SUMMARY-V2.md")
        sys.exit(1)

    md_file = Path(sys.argv[1])

    if not md_file.exists():
        print(f"Error: {md_file} not found")
        sys.exit(1)

    html_file = md_file.with_suffix('.html')

    print(f"Converting {md_file} to HTML...")
    try:
        html_content = convert(str(md_file))
        with open(html_file, 'w') as f:
            f.write(html_content)
        print(f"✅ Created: {html_file}")
        print(f"\nTo create PDF:")
        print(f"1. Open in browser: {html_file}")
        print(f"2. Wait 2 seconds for diagrams to render")
        print(f"3. Press Ctrl+P → Save as PDF")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
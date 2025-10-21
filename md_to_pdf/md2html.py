#!/usr/bin/env python3
"""
Enhanced markdown to HTML converter with proper hyperlink support
Handles internal anchors, external links, and table of contents
"""

import sys
import re
from pathlib import Path

def slugify(text):
    """Convert heading text to URL-friendly slug for anchors"""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def convert(md_file):
    """Convert markdown to HTML with proper link handling"""
    with open(md_file, 'r') as f:
        content = f.read()

    html = content

    # Track all headings for anchor generation
    headings = {}

    # First pass: collect all headings and generate IDs
    def process_heading(match, level):
        text = match.group(1)
        slug = slugify(text)
        # Handle duplicate slugs
        if slug in headings:
            counter = 1
            original_slug = slug
            while f"{original_slug}-{counter}" in headings:
                counter += 1
            slug = f"{original_slug}-{counter}"
        headings[slug] = text
        return f'<h{level} id="{slug}">{text}</h{level}>'

    # Extract and protect Mermaid blocks first
    mermaid_blocks = []
    def save_mermaid(match):
        # Extract the content between the mermaid code fence markers
        content = match.group(1).strip()
        # Store the cleaned content
        mermaid_blocks.append(content)
        return f'__MERMAID_BLOCK_{len(mermaid_blocks)-1}__'
    html = re.sub(r'```mermaid\n(.*?)```', save_mermaid, html, flags=re.DOTALL)

    # Extract and protect code blocks
    code_blocks = []
    def save_code(match):
        code_blocks.append(match.group(1))
        return f'__CODE_BLOCK_{len(code_blocks)-1}__'
    html = re.sub(r'```(.*?)```', save_code, html, flags=re.DOTALL)

    # Convert headers with IDs for anchoring
    html = re.sub(r'^#### (.*?)$', lambda m: process_heading(m, 4), html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', lambda m: process_heading(m, 3), html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', lambda m: process_heading(m, 2), html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', lambda m: process_heading(m, 1), html, flags=re.MULTILINE)

    # Convert links - IMPORTANT: Do this before other formatting
    # [text](url) style links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Convert anchor links in table of contents
    for slug, title in headings.items():
        # Replace [Title](#anchor) with proper link
        html = html.replace(f'[{title}](#{slug})', f'<a href="#{slug}">{title}</a>')
        # Also handle variations with different anchor formats
        html = html.replace(f'](#{slug})', f'<a href="#{slug}">{title}</a>')

    # Auto-link URLs
    html = re.sub(r'(?<!href=")(?<!>)(https?://[^\s<]+)', r'<a href="\1">\1</a>', html)

    # Convert email addresses
    html = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'<a href="mailto:\1">\1</a>', html)

    # Convert formatting
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

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
            h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
            html_table += f'<th>{h}</th>\n'
        html_table += '</tr>\n</thead>\n<tbody>\n'

        for line in lines[2:]:
            if line.strip() and '|' in line:
                cells = [c.strip() for c in line.split('|')[1:-1]]
                html_table += '<tr>\n'
                for c in cells:
                    c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
                    html_table += f'<td>{c}</td>\n'
                html_table += '</tr>\n'
        html_table += '</tbody>\n</table>'
        return html_table

    table_pattern = r'^\|[^\n]+\|\n\|[\s:\-\|]+\|\n(?:\|[^\n]+\|\n?)+'
    html = re.sub(table_pattern, convert_table, html, flags=re.MULTILINE)

    # Convert lists
    lines = html.split('\n')
    result = []
    in_ul = False
    in_ol = False

    for line in lines:
        # Unordered lists
        if line.strip().startswith('- '):
            if in_ol:
                result.append('</ol>')
                in_ol = False
            if not in_ul:
                result.append('<ul>')
                in_ul = True
            result.append(f'<li>{line.strip()[2:]}</li>')
        # Ordered lists
        elif re.match(r'^\d+\.\s', line.strip()):
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if not in_ol:
                result.append('<ol>')
                in_ol = True
            content = re.sub(r'^\d+\.\s', '', line.strip())
            result.append(f'<li>{content}</li>')
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if in_ol:
                result.append('</ol>')
                in_ol = False
            result.append(line)

    if in_ul:
        result.append('</ul>')
    if in_ol:
        result.append('</ol>')

    html = '\n'.join(result)

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        html = html.replace(f'__CODE_BLOCK_{i}__', f'<pre><code>{block}</code></pre>')

    # Restore Mermaid blocks - do this AFTER paragraph conversion
    mermaid_placeholders = []
    for i, block in enumerate(mermaid_blocks):
        placeholder = f'__MERMAID_BLOCK_{i}__'
        mermaid_placeholders.append((placeholder, block))

    # Convert paragraphs
    lines = html.split('\n')
    result = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)
        else:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)

    if in_paragraph:
        result.append('</p>')
    
    html = '\n'.join(result)
    
    # Now restore Mermaid blocks after paragraph conversion
    for placeholder, block in mermaid_placeholders:
        html = html.replace(
            placeholder,
            f'''<div class="mermaid-container">
<div class="mermaid-diagram">
<pre class="mermaid">{block}</pre>
</div>
</div>'''
        )
    
    return html

def create_html_document(title, content):
    """Create complete HTML document with enhanced styling and link support"""
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://unpkg.com/mermaid@11.12.0/dist/mermaid.min.js"></script>
<script>
// Wait for document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {{
    // Fix any paragraph tags that might be wrapping Mermaid diagrams
    document.querySelectorAll('p > .mermaid-container, p > .mermaid-diagram, p > .mermaid').forEach(el => {{
        const paragraph = el.parentNode;
        if (paragraph.tagName === 'P') {{
            // Move the mermaid element outside of the paragraph
            paragraph.parentNode.insertBefore(el, paragraph);
            // If paragraph is now empty, remove it
            if (paragraph.innerHTML.trim() === '') {{
                paragraph.parentNode.removeChild(paragraph);
            }}
        }}
    }});
    
    // Initialize Mermaid with specific configuration
    mermaid.initialize({{
        startOnLoad: true,  // Let Mermaid handle initialization
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif',
        flowchart: {{
            htmlLabels: true,
            curve: 'linear'
        }},
        er: {{
            layoutDirection: 'TB',
            minEntityWidth: 100,
            minEntityHeight: 75
        }},
        sequence: {{
            diagramMarginX: 50,
            diagramMarginY: 10,
            actorMargin: 50
        }}
    }});
}});
</script>
<style>
@page {{
    size: A4;
    margin: 15mm;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    background: white;
}}

/* Enhanced link styling for PDF */
a {{
    color: #3498db;
    text-decoration: underline;
}}

a:hover {{
    color: #2980b9;
}}

/* Make links more visible in PDF */
@media print {{
    a {{
        color: #0066cc !important;
        text-decoration: underline !important;
    }}

    /* Show URL after external links in print */
    a[href^="http"]:after {{
        content: " (" attr(href) ")";
        font-size: 0.8em;
        color: #666;
    }}

    /* Don't show URL for internal anchors */
    a[href^="#"]:after {{
        content: "";
    }}
}}

h1, h2, h3, h4 {{
    page-break-after: avoid;
}}

h1 {{
    color: #2c3e50;
    border-bottom: 3px solid #3498db;
    padding-bottom: 12px;
    margin-top: 30px;
}}

h1:first-of-type {{
    margin-top: 0;
}}

h2 {{
    color: #34495e;
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 8px;
    margin-top: 28px;
}}

h3 {{
    color: #34495e;
    margin-top: 24px;
    font-size: 1.2em;
}}

h4 {{
    color: #555;
    margin-top: 20px;
}}

/* Make sure anchor targets have some space */
[id] {{
    scroll-margin-top: 20px;
}}

p {{
    margin: 12px 0;
}}

ul, ol {{
    margin: 12px 0;
    padding-left: 25px;
}}

ul li, ol li {{
    margin: 8px 0;
}}

/* Nested list links */
ul li a, ol li a {{
    color: #3498db;
    text-decoration: none;
}}

ul li a:hover, ol li a:hover {{
    text-decoration: underline;
}}

strong {{
    color: #2c3e50;
    font-weight: 600;
}}

em {{
    font-style: italic;
}}

/* Mermaid diagram styling */
.mermaid-container {{
    text-align: center;
    margin: 25px 0;
    page-break-inside: avoid;
}}

.mermaid-diagram {{
    display: inline-block;
    background-color: white;
    padding: 15px;
    border-radius: 5px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}

/* Remove default pre styling for mermaid */
pre.mermaid {{
    background: none;
    padding: 0;
    overflow: visible;
    white-space: pre-wrap;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.4;
    color: #333;
}}

.mermaid svg {{
    max-width: 100%;
    height: auto;
    margin: 0 auto;
}}

/* Ensure Mermaid diagrams have enough space */
.mermaid > svg {{
    min-height: 150px;
}}

/* Fix for Mermaid text */
.mermaid .label {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    color: #333;
    font-weight: normal;
}}

/* Hide any error messages that might appear */
.mermaid .error-icon, .mermaid .error-text {{
    display: none !important;
}}

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

tr:nth-child(even) {{
    background: #f9f9f9;
}}

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
    page-break-inside: avoid;
}}

pre code {{
    background: none;
    padding: 0;
}}

hr {{
    border: none;
    border-top: 2px solid #ecf0f1;
    margin: 30px 0;
    page-break-after: avoid;
}}
</style>
</head>
<body>
{content}
</body>
</html>'''

def convert_file(md_file, html_file=None):
    """Convert markdown file to HTML file"""
    md_path = Path(md_file)
    
    if html_file is None:
        html_file = md_path.with_suffix('.html')
    else:
        html_file = Path(html_file)
    
    # Convert markdown to HTML
    html_content = convert(md_path)
    
    # Create full HTML document
    html_doc = create_html_document(md_path.stem, html_content)
    
    # Write HTML file
    html_file.write_text(html_doc)
    
    return html_file

def main():
    if len(sys.argv) < 2:
        print("Enhanced Markdown to HTML Converter with Link Support")
        print("=" * 50)
        print("\nUsage: md2html file.md [output.html]")
        sys.exit(1)

    md_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        html_file = sys.argv[2]
    else:
        html_file = None

    if not Path(md_file).exists():
        print(f"❌ Error: File not found: {md_file}")
        sys.exit(1)

    print(f"Converting {md_file} to HTML with hyperlinks...")

    try:
        html_file = convert_file(md_file, html_file)
        print(f"✅ Created: {html_file}")
        print("\nTo create PDF:")
        print(f"1. Open in browser: {html_file}")
        print("2. Wait 2 seconds for diagrams to render")
        print("3. Press Ctrl+P → Save as PDF")
        print("\n✨ Links will be clickable in the PDF!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

# Made with Bob

#!/usr/bin/env python3
# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
# Created with IBM Bob (https://bob.ibm.com)

"""
Enhanced markdown to HTML converter with proper hyperlink support
Handles internal anchors, external links, and table of contents
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import argparse

from md_to_pdf import __version__
import re
from pathlib import Path
from md_to_pdf.fonts import get_google_fonts_url, get_font_css, DEFAULT_PRESET

def slugify(text):
    """Convert heading text to URL-friendly slug for anchors"""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def extract_and_protect_blocks(html, pattern, block_list, block_type):
    """Generic block extraction and protection"""
    def save_block(match):
        content = match.group(1).strip() if block_type == 'mermaid' else match.group(1)
        block_list.append(content)
        return f'__{block_type.upper()}_BLOCK_{len(block_list)-1}__'
    return re.sub(pattern, save_block, html, flags=re.DOTALL)

def convert_blockquotes(html):
    """Convert markdown blockquotes to HTML <blockquote> elements"""
    lines = html.split('\n')
    result = []
    in_blockquote = False

    for line in lines:
        if line.startswith('> ') or line == '>':
            content = line[2:] if line.startswith('> ') else ''
            if not in_blockquote:
                result.append('<blockquote>')
                in_blockquote = True
            result.append(content)
        else:
            if in_blockquote:
                result.append('</blockquote>')
                in_blockquote = False
            result.append(line)

    if in_blockquote:
        result.append('</blockquote>')

    return '\n'.join(result)

def convert_lists(html):
    """Convert markdown lists to HTML with proper nesting and task list support"""
    lines = html.split('\n')
    result = []
    stack = []  # ponytail: (indent, tag) stack — no class needed for this state

    def close_all():
        while stack:
            result.append(f'</{stack.pop()[1]}>')

    for line in lines:
        m = re.match(r'^( *)(- |\d+\. )(.*)', line)
        if not m:
            if stack:
                result.append('</li>')
                close_all()
            result.append(line)
            continue

        indent = len(m.group(1))
        tag = 'ul' if m.group(2) == '- ' else 'ol'
        content = m.group(3)

        # Task list checkbox
        task = re.match(r'^\[(x| )\] (.*)', content, re.IGNORECASE)
        if task:
            checked = ' checked' if task.group(1).lower() == 'x' else ''
            content = f'<input type="checkbox" disabled{checked}> {task.group(2)}'

        # Close deeper levels
        while stack and stack[-1][0] > indent:
            result.append(f'</{stack.pop()[1]}>')
            if stack:
                result.append('</li>')

        if not stack or indent > stack[-1][0]:
            result.append(f'<{tag}>')
            stack.append((indent, tag))
        elif stack[-1][1] != tag:
            result.append(f'</{stack.pop()[1]}>')
            result.append(f'<{tag}>')
            stack.append((indent, tag))
        else:
            result.append('</li>')

        result.append(f'<li>{content}')

    if stack:
        result.append('</li>')
        close_all()

    return '\n'.join(result)

def convert_paragraphs(html):
    """Wrap non-HTML lines in paragraph tags"""
    lines = html.split('\n')
    result = []
    in_paragraph = False
    in_pre_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track if we're inside a <pre> block (check before processing the line)
        if '<pre' in line:
            in_pre_block = True
        
        # Don't wrap content inside pre blocks or HTML tags
        if stripped and not stripped.startswith('<') and not in_pre_block:
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)
        else:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
        
        # Check for closing pre tag after processing the line
        if '</pre>' in line:
            in_pre_block = False
    
    if in_paragraph:
        result.append('</p>')
    
    return '\n'.join(result)

def apply_inline_formatting(html):
    """Apply all inline markdown formatting"""
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = re.sub(r'~~(.+?)~~', r'<s>\1</s>', html)
    return html

def restore_protected_blocks(html, code_blocks, mermaid_blocks):
    """Restore all protected blocks with proper HTML wrapping"""
    # Restore code blocks
    for i, block in enumerate(code_blocks):
        html = html.replace(f'__CODE_BLOCK_{i}__', f'<pre><code>{block}</code></pre>')
    
    # Restore Mermaid blocks
    for i, block in enumerate(mermaid_blocks):
        placeholder = f'__MERMAID_BLOCK_{i}__'
        mermaid_html = f'''<div class="mermaid-container">
<div class="mermaid-diagram">
<pre class="mermaid">{block}</pre>
</div>
</div>'''
        html = html.replace(placeholder, mermaid_html)
    
    return html

def convert_all_headings(html, headings_dict, process_heading_func):
    """Process all heading levels in document order"""
    # Process all headings in a single pass to maintain document order
    def process_any_heading(match):
        # Count the number of # characters to determine level
        heading_marks = match.group(1)
        level = len(heading_marks)
        text = match.group(2)
        # Create a match object-like structure for process_heading_func
        class HeadingMatch:
            def group(self, n):
                return text if n == 1 else None
        return process_heading_func(HeadingMatch(), level)
    
    pattern = r'^(#{1,6}) (.+?)$'
    html = re.sub(pattern, process_any_heading, html, flags=re.MULTILINE)
    return html

def generate_toc(headings, max_depth=3, title="Table of Contents", skip_first_h1=True):
    """
    Generate HTML table of contents
    
    Args:
        headings: List of (slug, level, text) tuples
        max_depth: Maximum heading level (1-6)
        title: TOC section title (will be HTML-escaped for security)
        skip_first_h1: Skip first H1 heading (document title)
    
    Returns:
        HTML string for TOC
    
    Security:
        The title parameter is HTML-escaped to prevent XSS injection attacks.
        Empty or whitespace-only titles fall back to the default.
    """
    import html
    
    if not headings:
        return ""
    
    # Validate and sanitize title
    sanitized_title = title.strip() if title else ""
    if not sanitized_title:
        sanitized_title = "Table of Contents"
    # HTML-escape the title to prevent XSS
    escaped_title = html.escape(sanitized_title)
    
    # Filter headings
    filtered = []
    first_h1_seen = False
    for slug, level, text in headings:
        if level > max_depth:
            continue
        if skip_first_h1 and level == 1 and not first_h1_seen:
            first_h1_seen = True
            continue
        filtered.append((slug, level, text))
    
    if not filtered:
        return ""
    
    # Build TOC HTML with proper nesting
    toc_html = '<div class="table-of-contents">\n'
    toc_html += f'<h2 class="toc-title">{escaped_title}</h2>\n'
    toc_html += '<nav class="toc-nav">\n<ul class="toc-list">\n'
    
    prev_level = filtered[0][1] if filtered else 0  # Start with first item's level
    first_item = True
    
    for slug, level, text in filtered:
        if first_item:
            # First item - just open it
            toc_html += f'<li class="toc-item toc-level-{level}">'
            toc_html += f'<a href="#{slug}" class="toc-link">{text}</a>'
            first_item = False
        elif level > prev_level:
            # Going deeper - open nested list
            toc_html += '\n<ul class="toc-list">\n'
            toc_html += f'<li class="toc-item toc-level-{level}">'
            toc_html += f'<a href="#{slug}" class="toc-link">{text}</a>'
        elif level < prev_level:
            # Going shallower - close nested lists and previous items
            for _ in range(prev_level - level):
                toc_html += '</li>\n</ul>\n'
            toc_html += '</li>\n'  # Close the item at this level
            toc_html += f'<li class="toc-item toc-level-{level}">'
            toc_html += f'<a href="#{slug}" class="toc-link">{text}</a>'
        else:
            # Same level - close previous item and open new one
            toc_html += '</li>\n'
            toc_html += f'<li class="toc-item toc-level-{level}">'
            toc_html += f'<a href="#{slug}" class="toc-link">{text}</a>'
        
        prev_level = level
    
    # Close remaining open tags
    if filtered:
        toc_html += '</li>\n'  # Close last item
        # Close any remaining nested lists
        for _ in range(prev_level - filtered[0][1]):
            toc_html += '</ul>\n</li>\n'
    
    toc_html += '</ul>\n</nav>\n</div>\n'
    return toc_html

def insert_toc(html, toc_html, position='after_title'):
    """
    Insert TOC at specified position
    
    Args:
        html: HTML content
        toc_html: Generated TOC HTML
        position: 'top', 'after_title' (default), or 'custom'
    
    Returns:
        HTML with TOC inserted
    """
    if position == 'after_title':
        # Insert after first h1
        match = re.search(r'(<h1[^>]*>.*?</h1>)', html, re.DOTALL)
        if match:
            pos = match.end()
            return html[:pos] + '\n' + toc_html + '\n' + html[pos:]
        # Fallback to top if no h1
        return toc_html + '\n' + html
    
    elif position == 'top':
        return toc_html + '\n' + html
    
    elif position == 'custom':
        # Replace {{TOC}} marker
        if '{{TOC}}' in html:
            return html.replace('{{TOC}}', toc_html)
        # Fallback to top if no marker
        return toc_html + '\n' + html
    
    return toc_html + '\n' + html

def convert(md_file, generate_toc_flag=False, toc_depth=3, toc_title="Table of Contents",
            toc_position='after_title', toc_include_first=False):
    """Convert markdown to HTML with optional TOC"""
    md_dir = Path(md_file).resolve().parent

    with open(md_file, 'r') as f:
        content = f.read()

    html = content

    # Track all headings for anchor generation - changed to list of tuples
    headings = []

    # Define heading processor closure
    def process_heading(match, level):
        text = match.group(1)
        slug = slugify(text)
        
        # Handle duplicate slugs
        existing_slugs = [h[0] for h in headings]
        if slug in existing_slugs:
            counter = 1
            original_slug = slug
            while f"{original_slug}-{counter}" in existing_slugs:
                counter += 1
            slug = f"{original_slug}-{counter}"
        
        headings.append((slug, level, text))
        return f'<h{level} id="{slug}">{text}</h{level}>'

    # Phase 1: Protect special blocks
    mermaid_blocks = []
    code_blocks = []
    html = extract_and_protect_blocks(html, r'```mermaid\n(.*?)```', mermaid_blocks, 'mermaid')
    html = extract_and_protect_blocks(html, r'```(.*?)```', code_blocks, 'code')

    # Phase 2: Convert structural elements
    html = convert_all_headings(html, headings, process_heading)
    
    # Process both images and links with a single regex
    # ponytail: rewrite local .md hrefs to .pdf — assumes linked .md files are also converted
    def _link_or_img(m):
        if m.group(1):
            src = m.group(3)
            if not src.startswith(('http://', 'https://', 'data:', '/')):
                src = (md_dir / src).as_uri()
            return f'<img src="{src}" alt="{m.group(2)}">'
        href = m.group(3)
        # rewrite local .md links (with optional #anchor) to .pdf
        local_md = re.match(r'^([^#]+\.md)(#.*)?$', href, re.IGNORECASE)
        if local_md and not href.startswith('http'):
            href = local_md.group(1)[:-3] + '.pdf' + (local_md.group(2) or '')
        return f'<a href="{href}">{m.group(2)}</a>'

    html = re.sub(r'(!?)\[([^\]]+)\]\(([^\)]+)\)', _link_or_img, html)

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

    # Phase 3: Convert inline elements
    # Apply inline formatting first so backtick code spans become <code>...</code>
    # before auto-linking — the (?<!>) lookbehind then prevents linking URLs inside <code>
    html = apply_inline_formatting(html)

    # Auto-link URLs (skips URLs already inside href="..." or right after > i.e. inside a tag)
    html = re.sub(r'(?<!href=")(?<!>)(https?://[^\s<]+)', r'<a href="\1">\1</a>', html)

    # Convert email addresses
    html = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'<a href="mailto:\1">\1</a>', html)

    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Phase 4: Convert block elements
    html = convert_blockquotes(html)
    html = convert_lists(html)

    # Phase 5: Restore protected blocks and wrap paragraphs
    html = restore_protected_blocks(html, code_blocks, mermaid_blocks)
    html = convert_paragraphs(html)
    
    # Generate and insert TOC if requested
    if generate_toc_flag and headings:
        toc_html = generate_toc(headings, toc_depth, toc_title, not toc_include_first)
        html = insert_toc(html, toc_html, toc_position)
    
    return html

def create_html_document(title, content, orientation='portrait', font_preset='ibm'):
    """
    Create a complete HTML document with styling and link support.

    Args:
        title: Document title used in <title> and heading.
        content: HTML body content to embed.
        orientation: Page orientation ('portrait' or 'landscape'), default 'portrait'.
        font_preset: Font preset ('ibm', 'system', 'classic', 'modern'), default 'ibm'.

    Returns:
        Complete HTML document as a string.
    """
    # Set page size with orientation
    page_size = f"A4 {orientation}" if orientation == 'landscape' else "A4"
    
    # Calculate content width based on orientation
    # A4 portrait: 210mm width - 30mm margins = 180mm
    # A4 landscape: 297mm width - 30mm margins = 267mm
    content_width = "267mm" if orientation == 'landscape' else "180mm"
    
    # Get font configuration
    fonts = get_font_css(font_preset)
    title_font, title_weight = fonts['title']
    body_font, body_weight = fonts['body']
    code_font, code_weight = fonts['code']
    
    # Get Google Fonts URL if needed
    google_fonts_url = get_google_fonts_url(font_preset)
    google_fonts_links = ''
    if google_fonts_url:
        google_fonts_links = f'''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{google_fonts_url}" rel="stylesheet">'''
    
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
{google_fonts_links}
<script src="https://unpkg.com/mermaid@11.17.2/dist/mermaid.min.js"></script>
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
        fontFamily: '{body_font}, sans-serif',
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
    
    // Auto-detect wide diagrams after Mermaid renders
    // Wait for Mermaid to complete rendering
    setTimeout(function() {{
        detectAndMarkWideDiagrams();
    }}, 1000);
}});

// Function to detect wide diagrams and apply full-width styling
function detectAndMarkWideDiagrams() {{
    const containers = document.querySelectorAll('.mermaid-container');
    
    containers.forEach(container => {{
        const svg = container.querySelector('svg');
        if (!svg) return;
        
        // Get the SVG's natural (intrinsic) width
        const viewBox = svg.getAttribute('viewBox');
        let naturalWidth = 0;
        
        if (viewBox) {{
            // Parse viewBox to get natural width
            const viewBoxValues = viewBox.split(/\\s+|,/);
            naturalWidth = parseFloat(viewBoxValues[2]);
        }} else {{
            // Fallback to width attribute or computed width
            naturalWidth = parseFloat(svg.getAttribute('width')) || svg.getBBox().width;
        }}
        
        // Get the current rendered width
        const renderedWidth = svg.getBoundingClientRect().width;
        
        // If the diagram is being scaled down (natural width > rendered width),
        // it needs more space - mark it as wide
        const scalingThreshold = 0.95; // 95% - if using more than 95% of space, consider it wide
        if (naturalWidth > renderedWidth * scalingThreshold) {{
            container.classList.add('wide-diagram');
            console.log('Wide diagram detected:', {{
                naturalWidth: naturalWidth,
                renderedWidth: renderedWidth,
                ratio: (naturalWidth / renderedWidth).toFixed(2)
            }});
        }}
    }});
}}
</script>
<style>
@page {{
    size: {page_size};
    margin: 15mm;
}}

body {{
    font-family: {body_font}, sans-serif;
    font-weight: {body_weight};
    line-height: 1.6;
    color: #2c3e50;
    max-width: {content_width};  /* Page width minus margins (15mm × 2) */
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
    font-family: {title_font}, sans-serif;
    font-weight: {title_weight};
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

li:has(> input[type="checkbox"]) {{
    list-style: none;
    margin-left: -20px;
}}

input[type="checkbox"] {{
    margin-right: 6px;
    vertical-align: middle;
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

/* Wide diagram styling - expands to full printable width */
.mermaid-container.wide-diagram {{
    /* Break out of body constraint while respecting page margins */
    width: {content_width};  /* Full printable width based on orientation */
    max-width: 100vw;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: calc(-{content_width} / 2);  /* Half of content width to center */
    margin-right: calc(-{content_width} / 2);
}}

.mermaid-container.wide-diagram .mermaid-diagram {{
    width: 100%;
    max-width: {content_width};
    padding: 15px 10px;  /* Slightly reduced horizontal padding for more space */
}}

/* Remove default pre styling for mermaid */
pre.mermaid {{
    background: none;
    padding: 0;
    overflow: visible;
    white-space: pre-wrap;
    font-family: {body_font}, sans-serif;
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
    font-family: {body_font}, sans-serif;
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
    font-family: {code_font}, monospace;
    font-weight: {code_weight};
    font-size: 0.9em;
}}

pre {{
    background: #f4f4f4;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    page-break-inside: avoid;
    font-family: {code_font}, monospace;
    font-weight: {code_weight};
}}

pre code {{
    background: none;
    padding: 0;
}}

blockquote {{
    border-left: 4px solid #3498db;
    margin: 16px 0;
    padding: 8px 16px;
    color: #555;
    background: #f8f9fa;
    border-radius: 0 4px 4px 0;
    page-break-inside: avoid;
}}

blockquote p {{
    margin: 4px 0;
}}

hr {{
    border: none;
    border-top: 2px solid #ecf0f1;
    margin: 30px 0;
    page-break-after: avoid;
}}

/* Image styling */
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    border-radius: 5px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    page-break-inside: avoid;
}}

/* Table of Contents Styling */
.table-of-contents {{
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 20px;
    margin: 30px 0;
    page-break-inside: avoid;
}}

.toc-title {{
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 1.5em;
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}}

.toc-nav {{
    font-size: 0.95em;
}}

.toc-list {{
    list-style: none;
    padding-left: 0;
    margin: 0;
}}

.toc-list .toc-list {{
    padding-left: 20px;
    margin-top: 5px;
}}

.toc-item {{
    margin: 8px 0;
    line-height: 1.6;
}}

.toc-link {{
    color: #3498db;
    text-decoration: none;
    display: block;
    padding: 4px 0;
    transition: color 0.2s;
}}

.toc-link:hover {{
    color: #2980b9;
    text-decoration: underline;
}}

.toc-level-1 > .toc-link {{
    font-weight: 600;
    font-size: 1.05em;
}}

.toc-level-2 > .toc-link {{
    font-weight: 500;
}}

.toc-level-3 > .toc-link {{
    font-weight: normal;
    color: #555;
}}

.toc-level-4 > .toc-link,
.toc-level-5 > .toc-link,
.toc-level-6 > .toc-link {{
    font-weight: normal;
    color: #666;
    font-size: 0.95em;
}}

@media print {{
    .table-of-contents {{
        background: white;
        border: 1px solid #ccc;
    }}
    
    .toc-link {{
        color: #0066cc !important;
    }}
}}
}}
</style>
</head>
<body>
{content}
</body>
</html>'''

def convert_file(md_file, html_file=None, orientation='portrait', font_preset='ibm',
                 generate_toc=False, toc_depth=3, toc_title="Table of Contents",
                 toc_position='after_title', toc_include_first=False):
    """
    Convert a Markdown file to an HTML file.

    Args:
        md_file: Path to the Markdown file.
        html_file: Output HTML file path. Defaults to same name as md_file with .html extension.
        orientation: Page orientation ('portrait' or 'landscape'), default 'portrait'.
        font_preset: Font preset ('ibm', 'system', 'classic', 'modern'), default 'ibm'.
        generate_toc: Whether to generate a table of contents.
        toc_depth: Maximum heading level included in TOC (1-6), default 3.
        toc_title: Heading text for the TOC, default 'Table of Contents'.
        toc_position: Where to insert the TOC ('top', 'after_title', 'custom').
        toc_include_first: Whether to include the first H1 in the TOC.

    Returns:
        Path to the generated HTML file.

    Raises:
        FileNotFoundError: If md_file does not exist.
    """
    md_path = Path(md_file)
    
    if html_file is None:
        html_file = md_path.with_suffix('.html')
    else:
        html_file = Path(html_file)
    
    # Convert markdown to HTML with TOC options
    html_content = convert(md_path, generate_toc, toc_depth, toc_title,
                          toc_position, toc_include_first)
    
    # Create full HTML document with orientation and font preset
    html_doc = create_html_document(md_path.stem, html_content, orientation, font_preset)
    
    # Write HTML file
    html_file.write_text(html_doc)
    
    return html_file

def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to HTML with link and Mermaid diagram support"
    )
    parser.add_argument("input_file", help="Path to the Markdown file")
    parser.add_argument("-o", "--output", help="Path for the output HTML file")

    orientation_group = parser.add_mutually_exclusive_group()
    orientation_group.add_argument(
        "-l", "--landscape",
        action="store_true",
        help="Use landscape orientation (default: portrait)"
    )
    orientation_group.add_argument(
        "-p", "--portrait",
        action="store_true",
        help="Use portrait orientation (default, explicit)"
    )

    parser.add_argument(
        "--font-preset",
        choices=['ibm', 'system', 'classic', 'modern'],
        default='ibm',
        help="Font preset: 'ibm' (default), 'system', 'classic', 'modern'"
    )
    parser.add_argument("--toc", action="store_true", help="Generate table of contents")
    parser.add_argument(
        "--toc-depth",
        type=int, default=3, choices=range(1, 7), metavar="DEPTH",
        help="Maximum heading level for TOC (1-6, default: 3)"
    )
    parser.add_argument(
        "--toc-title", default="Table of Contents",
        help="Title for the table of contents (default: 'Table of Contents')"
    )
    parser.add_argument(
        "--toc-position",
        choices=['top', 'after_title', 'custom'], default='after_title',
        help="TOC position: 'top', 'after_title' (default), or 'custom'"
    )
    parser.add_argument(
        "--toc-include-first", action="store_true",
        help="Include first H1 heading in TOC (default: exclude as document title)"
    )
    parser.add_argument(
        "--strict-images", action="store_true",
        help="Abort if any referenced images are missing (default: warn and continue)"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    md_file = args.input_file
    orientation = "landscape" if args.landscape else "portrait"

    if not Path(md_file).exists():
        print(f"❌ Error: File not found: {md_file}", file=sys.stderr)
        sys.exit(1)

    if args.strict_images:
        from md_to_pdf.image_validator import validate_images
        if not validate_images(Path(md_file), strict_mode=True):
            sys.exit(1)

    print(f"Converting {md_file} to HTML with hyperlinks...")

    try:
        html_file = convert_file(
            md_file, args.output,
            orientation=orientation,
            font_preset=args.font_preset,
            generate_toc=args.toc,
            toc_depth=args.toc_depth,
            toc_title=args.toc_title,
            toc_position=args.toc_position,
            toc_include_first=args.toc_include_first,
        )
        print(f"✅ Created: {html_file}")
        print("\nTo create PDF:")
        print(f"1. Open in browser: {html_file}")
        print("2. Wait 2 seconds for diagrams to render")
        print("3. Press Ctrl+P → Save as PDF")
        print("\n✨ Links will be clickable in the PDF!")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

# Made with Bob

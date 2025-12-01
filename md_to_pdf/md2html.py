#!/usr/bin/env python3
"""
Enhanced markdown to HTML converter with proper hyperlink support
Handles internal anchors, external links, and table of contents
"""

import sys
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

def convert_lists(html):
    """Convert markdown lists to HTML with proper nesting"""
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
    # Convert formatting
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
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
    """Process all heading levels in order (h4 to h1)"""
    for level in range(4, 0, -1):
        pattern = r'^' + '#' * level + r' (.*?)$'
        html = re.sub(pattern, lambda m: process_heading_func(m, level),
                     html, flags=re.MULTILINE)
    return html

def convert(md_file):
    """Convert markdown to HTML with proper link handling"""
    with open(md_file, 'r') as f:
        content = f.read()

    html = content

    # Track all headings for anchor generation
    headings = {}

    # Define heading processor closure
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

    # Phase 1: Protect special blocks
    mermaid_blocks = []
    code_blocks = []
    html = extract_and_protect_blocks(html, r'```mermaid\n(.*?)```', mermaid_blocks, 'mermaid')
    html = extract_and_protect_blocks(html, r'```(.*?)```', code_blocks, 'code')

    # Phase 2: Convert structural elements
    html = convert_all_headings(html, headings, process_heading)
    
    # Process both images and links with a single regex
    html = re.sub(r'(!?)\[([^\]]+)\]\(([^\)]+)\)',
                 lambda m: f'<img src="{m.group(3)}" alt="{m.group(2)}">' if m.group(1) else f'<a href="{m.group(3)}">{m.group(2)}</a>',
                 html)

    # Convert anchor links in table of contents
    for slug, title in headings.items():
        # Replace [Title](#anchor) with proper link
        html = html.replace(f'[{title}](#{slug})', f'<a href="#{slug}">{title}</a>')
        # Also handle variations with different anchor formats
        html = html.replace(f'](#{slug})', f'<a href="#{slug}">{title}</a>')

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
    # Auto-link URLs
    html = re.sub(r'(?<!href=")(?<!>)(https?://[^\s<]+)', r'<a href="\1">\1</a>', html)

    # Convert email addresses
    html = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'<a href="mailto:\1">\1</a>', html)

    # Apply inline formatting
    html = apply_inline_formatting(html)

    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Phase 4: Convert block elements
    html = convert_lists(html)

    # Phase 5: Restore protected blocks and wrap paragraphs
    html = restore_protected_blocks(html, code_blocks, mermaid_blocks)
    html = convert_paragraphs(html)
    
    return html

def create_html_document(title, content, orientation='portrait', font_preset='ibm'):
    """
    Create complete HTML document with enhanced styling and link support
    
    Args:
        title: Document title
        content: HTML content
        orientation: Page orientation ('portrait' or 'landscape'), default 'portrait'
        font_preset: Font preset to use ('ibm', 'system', 'classic', 'modern'), default 'ibm'
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
</style>
</head>
<body>
{content}
</body>
</html>'''

def convert_file(md_file, html_file=None, orientation='portrait', font_preset='ibm'):
    """
    Convert markdown file to HTML file
    
    Args:
        md_file: Path to markdown file
        html_file: Optional output HTML file path
        orientation: Page orientation ('portrait' or 'landscape'), default 'portrait'
        font_preset: Font preset to use ('ibm', 'system', 'classic', 'modern'), default 'ibm'
    """
    md_path = Path(md_file)
    
    if html_file is None:
        html_file = md_path.with_suffix('.html')
    else:
        html_file = Path(html_file)
    
    # Convert markdown to HTML
    html_content = convert(md_path)
    
    # Create full HTML document with orientation and font preset
    html_doc = create_html_document(md_path.stem, html_content, orientation, font_preset)
    
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

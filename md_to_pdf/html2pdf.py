#!/usr/bin/env python3
# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
# Created with IBM Bob (https://bob.ibm.com)

"""
Convert HTML to PDF with clickable hyperlinks using Playwright
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from pathlib import Path
from typing import Optional, Literal, Union, Any
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

# Timeout constants (in milliseconds)
MERMAID_LIBRARY_TIMEOUT_MS = 5000
MERMAID_SVG_RENDER_TIMEOUT_MS = 5000

# PDF configuration constants
PDF_FORMAT = 'A4'
PDF_MARGIN_MM = '15mm'

# Mermaid diagram detection threshold
WIDE_DIAGRAM_THRESHOLD = 0.95

# Valid PDF orientations
VALID_ORIENTATIONS = ('portrait', 'landscape')

# Mermaid selectors
MERMAID_SELECTOR = '.mermaid'
MERMAID_CONTAINER_SELECTOR = '.mermaid-container'
SVG_SELECTOR = 'svg'
WIDE_DIAGRAM_CLASS = 'wide-diagram'

# Status messages
MSG_NO_DIAGRAMS = "    ⟶ No Mermaid diagrams found in document"
MSG_WAITING = "    ⟶ Waiting for Mermaid diagrams to render..."
MSG_LIBRARY_NOT_LOADED = "    ⟶ Warning: Mermaid library not loaded, skipping diagram rendering"
MSG_SVG_TIMEOUT = "    ⟶ Warning: SVG elements not rendered within timeout"
MSG_DIAGRAMS_RENDERED = "    ⟶ {} diagram(s) rendered successfully"
MSG_WIDE_DIAGRAMS = "    ⟶ {} wide diagram(s) using full printable width"
MSG_TEXT_FALLBACK = "    ⟶ Using text representation for diagrams"

# JavaScript code snippets for Mermaid handling
JS_CHECK_MERMAID_EXISTS = '''() => {
    return document.querySelectorAll('.mermaid').length > 0;
}'''

JS_WAIT_FOR_MERMAID = '() => typeof mermaid !== "undefined"'

JS_FIX_PARAGRAPH_WRAPPING = '''() => {
    // Find all mermaid containers that might be wrapped in paragraphs
    document.querySelectorAll('p > .mermaid-container, p > .mermaid-diagram, p > .mermaid').forEach(el => {
        const paragraph = el.parentNode;
        if (paragraph.tagName === 'P') {
            // Move the mermaid element outside of the paragraph
            paragraph.parentNode.insertBefore(el, paragraph);
            // If paragraph is now empty, remove it
            if (paragraph.innerHTML.trim() === '') {
                paragraph.parentNode.removeChild(paragraph);
            }
        }
    });
}'''

JS_INITIALIZE_MERMAID = '''() => {
    if (typeof mermaid !== 'undefined') {
        // Reset configuration
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose'
        });
        
        // Force rendering
        try {
            mermaid.init(undefined, document.querySelectorAll('.mermaid'));
        } catch (e) {
            console.error('Mermaid init error:', e);
        }
    } else {
        console.error('Mermaid library not found');
    }
}'''

JS_DETECT_WIDE_DIAGRAMS = f'''() => {{
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
                const viewBoxValues = viewBox.split(/[\\s,]+/);
                naturalWidth = parseFloat(viewBoxValues[2]);
            }} else {{
                // Fallback to width attribute or computed width
                naturalWidth = parseFloat(svg.getAttribute('width')) || svg.getBBox().width;
            }}
            
            // Get the current rendered width
            const renderedWidth = svg.getBoundingClientRect().width;
            
            // If the diagram is being scaled down, mark it as wide
            const scalingThreshold = {WIDE_DIAGRAM_THRESHOLD};
            if (naturalWidth > renderedWidth * scalingThreshold) {{
                container.classList.add('wide-diagram');
            }}
        }});
    }}
    
    detectAndMarkWideDiagrams();
}}'''

JS_COUNT_SVGS = '''() => {
    return document.querySelectorAll('svg').length;
}'''

JS_COUNT_WIDE_DIAGRAMS = '''() => {
    return document.querySelectorAll('.mermaid-container.wide-diagram').length;
}'''

def _has_mermaid_diagrams(page: Page) -> bool:
    """
    Check if the page contains any Mermaid diagrams.
    
    Args:
        page: Playwright Page object with loaded HTML content
        
    Returns:
        bool: True if Mermaid diagrams are found, False otherwise
    """
    return page.evaluate(JS_CHECK_MERMAID_EXISTS)


def _wait_for_mermaid_library(page: Page) -> bool:
    """
    Wait for the Mermaid library to be loaded and available.
    
    Args:
        page: Playwright Page object with loaded HTML content
        
    Returns:
        bool: True if library loaded successfully, False otherwise
    """
    try:
        page.wait_for_function(
            JS_WAIT_FOR_MERMAID,
            timeout=MERMAID_LIBRARY_TIMEOUT_MS
        )
        return True
    except PlaywrightTimeout:
        print(MSG_LIBRARY_NOT_LOADED)
        return False
    except Exception as e:
        print(f"    ⟶ Unexpected error waiting for Mermaid: {e}")
        return False


def _fix_paragraph_wrapping(page: Page) -> None:
    """
    Fix paragraph tags that might be wrapping Mermaid diagrams.
    
    Some markdown processors wrap diagrams in <p> tags, which can cause
    rendering issues. This function moves diagrams outside of paragraphs.
    
    Args:
        page: Playwright Page object with loaded HTML content
    """
    page.evaluate(JS_FIX_PARAGRAPH_WRAPPING)


def _initialize_and_render_mermaid(page: Page) -> None:
    """
    Initialize Mermaid library and trigger diagram rendering.
    
    Args:
        page: Playwright Page object with loaded HTML content
    """
    page.evaluate(JS_INITIALIZE_MERMAID)


def _wait_for_svg_rendering(page: Page) -> bool:
    """
    Wait for SVG elements to be rendered in the page.
    
    Args:
        page: Playwright Page object with loaded HTML content
        
    Returns:
        bool: True if SVGs rendered successfully, False if timeout
    """
    try:
        page.wait_for_selector(
            SVG_SELECTOR,
            state='attached',
            timeout=MERMAID_SVG_RENDER_TIMEOUT_MS
        )
        return True
    except PlaywrightTimeout:
        print(MSG_SVG_TIMEOUT)
        return False
    except Exception as e:
        print(f"    ⟶ Unexpected error waiting for SVG: {e}")
        return False


def _detect_and_mark_wide_diagrams(page: Page) -> None:
    """
    Auto-detect diagrams that are wider than the page and mark them.
    
    Wide diagrams are marked with the 'wide-diagram' class so they can
    be styled to use the full printable width in landscape orientation.
    
    Args:
        page: Playwright Page object with loaded HTML content
    """
    page.evaluate(JS_DETECT_WIDE_DIAGRAMS)


def _report_rendering_status(page: Page) -> None:
    """
    Report the status of Mermaid diagram rendering to the user.
    
    Args:
        page: Playwright Page object with loaded HTML content
    """
    svg_count = page.evaluate(JS_COUNT_SVGS)
    wide_count = page.evaluate(JS_COUNT_WIDE_DIAGRAMS)
    
    if svg_count > 0:
        print(MSG_DIAGRAMS_RENDERED.format(svg_count))
        if wide_count > 0:
            print(MSG_WIDE_DIAGRAMS.format(wide_count))
    else:
        print(MSG_TEXT_FALLBACK)


def _handle_mermaid_diagrams(page: Page) -> None:
    """
    Handle Mermaid diagram rendering in the page.
    
    This function orchestrates the complete Mermaid diagram handling process:
    1. Checks if Mermaid diagrams exist
    2. Waits for Mermaid library to load
    3. Fixes paragraph wrapping issues
    4. Initializes and renders diagrams
    5. Waits for SVG rendering
    6. Auto-detects and marks wide diagrams
    7. Reports rendering status
    
    Args:
        page: Playwright Page object with loaded HTML content
        
    Note:
        Continues execution even if Mermaid rendering fails,
        falling back to text representation.
    """
    try:
        # Check if there are any Mermaid diagrams
        if not _has_mermaid_diagrams(page):
            print(MSG_NO_DIAGRAMS)
            return
        
        print(MSG_WAITING)
        
        # Wait for Mermaid library to be available
        if not _wait_for_mermaid_library(page):
            return
        
        # Fix any paragraph tags that might be wrapping Mermaid diagrams
        _fix_paragraph_wrapping(page)
        
        # Initialize Mermaid and trigger rendering
        _initialize_and_render_mermaid(page)
        
        # Wait for SVG elements to be rendered
        _wait_for_svg_rendering(page)
        
        # Auto-detect and mark wide diagrams
        _detect_and_mark_wide_diagrams(page)
        
        # Report rendering status
        _report_rendering_status(page)
        
    except Exception as e:
        # Continue even if there are errors with Mermaid rendering
        print(f"    ⟶ Note: {str(e)}")

def _resolve_paths(
    html_file: Union[str, Path],
    pdf_file: Optional[Union[str, Path]]
) -> tuple[Path, Path]:
    """
    Resolve and validate input/output file paths.
    
    Args:
        html_file: Path to the HTML file (string or Path object)
        pdf_file: Optional path for output PDF (string, Path, or None)
        
    Returns:
        tuple: (html_path, pdf_path) as absolute Path objects
        
    Note:
        If pdf_file is None, generates PDF filename from HTML filename
        by replacing the extension with .pdf
    """
    html_path = Path(html_file).absolute()
    
    if pdf_file is None:
        pdf_path = html_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_file).absolute()
    
    return html_path, pdf_path


def _generate_pdf_with_browser(html_path: Path, pdf_path: Path, orientation: str) -> None:
    """
    Generate PDF from HTML using Playwright browser.
    
    Args:
        html_path: Absolute path to the HTML file
        pdf_path: Absolute path for the output PDF file
        orientation: Page orientation ('portrait' or 'landscape')
        
    Raises:
        Exception: Re-raises any browser-related exceptions with file context
    """
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception:
                # Chromium binaries missing — install automatically
                print("    ⟶ Chromium not found, installing automatically...")
                import subprocess
                subprocess.run(
                    ['playwright', 'install', 'chromium'],
                    check=True
                )
                browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()

                # Navigate to the HTML file with proper URL encoding
                # Use as_uri() to handle special characters like #, spaces, etc.
                file_url = html_path.as_uri()
                page.goto(file_url)

                # Wait for page to be fully loaded (network idle state)
                page.wait_for_load_state('networkidle')
                
                # Handle Mermaid diagrams
                _handle_mermaid_diagrams(page)

                # Generate PDF with settings optimized for links
                page.pdf(**_get_pdf_config(pdf_path, orientation))
            finally:
                # Ensure browser is always closed, even if an exception occurs
                browser.close()
    except Exception as e:
        # Add file context to any browser-related errors
        raise Exception(f"Failed to generate PDF from '{html_path.name}': {str(e)}") from e


def _get_pdf_config(pdf_path: Path, orientation: str) -> dict[str, Any]:
    """
    Generate PDF configuration dictionary for Playwright.
    
    Args:
        pdf_path: Absolute path where PDF will be saved
        orientation: Page orientation ('portrait' or 'landscape')
        
    Returns:
        dict: Configuration dictionary for page.pdf() method
        
    Note:
        Uses A4 format with 15mm margins on all sides.
        Preserves background colors and images.
    """
    return {
        'path': str(pdf_path),
        'format': PDF_FORMAT,
        'landscape': (orientation == 'landscape'),
        'print_background': True,
        'margin': {
            'top': PDF_MARGIN_MM,
            'bottom': PDF_MARGIN_MM,
            'left': PDF_MARGIN_MM,
            'right': PDF_MARGIN_MM
        },
        'display_header_footer': False,
        'prefer_css_page_size': False
    }

def html_to_pdf_with_links(
    html_file: Union[str, Path],
    pdf_file: Optional[Union[str, Path]] = None,
    orientation: Literal['portrait', 'landscape'] = 'portrait'
) -> Path:
    """
    Convert HTML to PDF preserving hyperlinks
    
    Args:
        html_file: Path to the HTML file to convert
        pdf_file: Optional path for the output PDF file. If None, uses the same
                  name as html_file with .pdf extension
        orientation: Page orientation for the PDF. Must be either 'portrait' or
                     'landscape'. Defaults to 'portrait' for backward compatibility.
                     
    Returns:
        Path: Path object pointing to the generated PDF file
        
    Raises:
        ValueError: If orientation is not 'portrait' or 'landscape'
        FileNotFoundError: If html_file does not exist
        
    Examples:
        >>> # Create portrait PDF (default)
        >>> html_to_pdf_with_links('document.html')
        
        >>> # Create landscape PDF
        >>> html_to_pdf_with_links('document.html', orientation='landscape')
        
        >>> # Create portrait PDF with custom output name
        >>> html_to_pdf_with_links('input.html', 'output.pdf', orientation='portrait')
    """
    # Validate orientation parameter
    if orientation not in VALID_ORIENTATIONS:
        raise ValueError(
            f"Invalid orientation '{orientation}'. "
            f"Must be one of: {', '.join(VALID_ORIENTATIONS)}"
        )

    # Resolve file paths
    html_path, pdf_path = _resolve_paths(html_file, pdf_file)

    print(f"📄 Converting {html_path.name} to PDF with clickable links...")

    # Generate PDF using browser
    _generate_pdf_with_browser(html_path, pdf_path, orientation)

    return pdf_path

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Convert HTML to PDF with clickable links using Playwright"
    )
    parser.add_argument("input_file", help="Path to the HTML file")
    parser.add_argument("output_file", nargs="?", help="Path for the output PDF file")
    parser.add_argument(
        "-l", "--landscape",
        action="store_true",
        help="Use landscape orientation (default: portrait)"
    )
    args = parser.parse_args()

    html_file = args.input_file
    pdf_file = args.output_file
    orientation = "landscape" if args.landscape else "portrait"

    if not Path(html_file).exists():
        print(f"❌ Error: File not found: {html_file}", file=sys.stderr)
        sys.exit(1)

    if not html_file.endswith('.html'):
        print(f"❌ Error: Input must be an HTML file", file=sys.stderr)
        sys.exit(1)

    try:
        pdf_path = html_to_pdf_with_links(html_file, pdf_file, orientation)
        size = pdf_path.stat().st_size / 1024
        print(f"✅ PDF created: {pdf_path.name} ({size:.1f} KB)")
        print(f"\n✨ All hyperlinks are clickable in the PDF!")
        print(f"   - Table of contents links work")
        print(f"   - Email addresses are clickable")
        print(f"   - External URLs open in browser")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

# Made with Bob

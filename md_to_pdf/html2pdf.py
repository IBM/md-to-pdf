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
import argparse

from md_to_pdf import __version__
from pathlib import Path

from typing import Literal
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

JS_DETECT_WIDE_DIAGRAMS = '''(threshold) => {
    document.querySelectorAll('.mermaid-container').forEach(container => {
        const svg = container.querySelector('svg');
        if (!svg) return;
        const viewBox = svg.getAttribute('viewBox');
        const naturalWidth = viewBox
            ? parseFloat(viewBox.split(/[\\s,]+/)[2])
            : parseFloat(svg.getAttribute('width')) || svg.getBBox().width;
        const renderedWidth = svg.getBoundingClientRect().width;
        if (naturalWidth > renderedWidth * threshold) {
            container.classList.add('wide-diagram');
        }
    });
}'''

JS_COUNT_SVGS = '''() => {
    return document.querySelectorAll('.mermaid-container svg').length;
}'''

JS_COUNT_WIDE_DIAGRAMS = '''() => {
    return document.querySelectorAll('.mermaid-container.wide-diagram').length;
}'''

def _wait_for_mermaid_library(page: Page) -> bool:
    """Wait for the Mermaid JS library to be available. Returns False on timeout."""
    try:
        page.wait_for_function(JS_WAIT_FOR_MERMAID, timeout=MERMAID_LIBRARY_TIMEOUT_MS)
        return True
    except PlaywrightTimeout:
        print(MSG_LIBRARY_NOT_LOADED)
        return False
    except Exception as e:
        print(f"    ⟶ Unexpected error waiting for Mermaid: {e}")
        return False


def _handle_mermaid_diagrams(page: Page) -> None:
    """Orchestrate Mermaid rendering: check, load, fix, init, wait, mark wide, report."""
    try:
        if not page.evaluate(JS_CHECK_MERMAID_EXISTS):
            print(MSG_NO_DIAGRAMS)
            return

        print(MSG_WAITING)

        if not _wait_for_mermaid_library(page):
            return

        page.evaluate(JS_FIX_PARAGRAPH_WRAPPING)
        page.evaluate(JS_INITIALIZE_MERMAID)

        try:
            page.wait_for_selector('.mermaid-container svg', state='attached', timeout=MERMAID_SVG_RENDER_TIMEOUT_MS)
        except PlaywrightTimeout:
            print(MSG_SVG_TIMEOUT)
        except Exception as e:
            print(f"    ⟶ Unexpected error waiting for SVG: {e}")

        page.evaluate(JS_DETECT_WIDE_DIAGRAMS, WIDE_DIAGRAM_THRESHOLD)

        svg_count = page.evaluate(JS_COUNT_SVGS)
        wide_count = page.evaluate(JS_COUNT_WIDE_DIAGRAMS)
        if svg_count > 0:
            print(MSG_DIAGRAMS_RENDERED.format(svg_count))
            if wide_count > 0:
                print(MSG_WIDE_DIAGRAMS.format(wide_count))
        else:
            print(MSG_TEXT_FALLBACK)

    except Exception as e:
        print(f"    ⟶ Note: {str(e)}")

def html_to_pdf_with_links(
    html_file: str | Path,
    pdf_file: str | Path | None = None,
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
    if orientation not in VALID_ORIENTATIONS:
        raise ValueError(f"Invalid orientation '{orientation}'. Must be one of: {', '.join(VALID_ORIENTATIONS)}")

    html_path = Path(html_file).absolute()
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    pdf_path = Path(pdf_file).absolute() if pdf_file is not None else html_path.with_suffix('.pdf')

    print(f"📄 Converting {html_path.name} to PDF with clickable links...")

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception:
                print("    ⟶ Chromium not found, installing automatically...")
                import subprocess
                subprocess.run(['playwright', 'install', 'chromium'], check=True)
                browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(html_path.as_uri())
                page.wait_for_load_state('networkidle')
                _handle_mermaid_diagrams(page)
                page.pdf(
                    path=str(pdf_path),
                    format=PDF_FORMAT,
                    landscape=(orientation == 'landscape'),
                    print_background=True,
                    margin={'top': PDF_MARGIN_MM, 'bottom': PDF_MARGIN_MM, 'left': PDF_MARGIN_MM, 'right': PDF_MARGIN_MM},
                    display_header_footer=False,
                    prefer_css_page_size=False,
                )
            finally:
                browser.close()
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"Failed to generate PDF from '{html_path.name}': {str(e)}") from e

    return pdf_path

def main():
    """Entry point for the html2pdf command."""
    parser = argparse.ArgumentParser(
        description="Convert HTML to PDF with clickable links using Playwright"
    )
    parser.add_argument("input_file", help="Path to the HTML file")
    parser.add_argument("-o", "--output", help="Path for the output PDF file")

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

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    html_file = args.input_file
    pdf_file = args.output
    orientation = "landscape" if args.landscape else "portrait"

    if not Path(html_file).exists():
        print(f"❌ Error: File not found: {html_file}", file=sys.stderr)
        sys.exit(1)

    if Path(html_file).suffix.lower() != '.html':
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

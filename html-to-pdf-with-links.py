#!/usr/bin/env python3
"""
Convert HTML to PDF with clickable hyperlinks using Playwright
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def html_to_pdf_with_links(html_file, pdf_file):
    """Convert HTML to PDF preserving hyperlinks"""

    # Get absolute paths
    html_path = html_file.absolute()
    pdf_path = pdf_file.absolute()

    print(f"📄 Converting {html_file.name} to PDF with clickable links...")

    with sync_playwright() as p:
        # Launch browser (headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the HTML file
        file_url = f"file://{html_path}"
        page.goto(file_url)

        # Wait for content to load
        page.wait_for_timeout(2000)  # 2 seconds for complete rendering

        # Generate PDF with settings optimized for links
        page.pdf(
            path=str(pdf_path),
            format='A4',
            print_background=True,
            margin={
                'top': '15mm',
                'bottom': '15mm',
                'left': '15mm',
                'right': '15mm'
            },
            display_header_footer=False,
            prefer_css_page_size=False
        )

        browser.close()

    return True

def main():
    if len(sys.argv) < 2:
        print("HTML to PDF Converter with Clickable Links")
        print("=" * 45)
        print("\nUsage: python3 html-to-pdf-with-links.py file.html")
        print("\nThis will create a PDF with:")
        print("  ✅ Clickable table of contents")
        print("  ✅ Working internal anchor links")
        print("  ✅ Clickable external URLs")
        print("  ✅ Clickable email addresses")
        sys.exit(1)

    html_file = Path(sys.argv[1])

    if not html_file.exists():
        print(f"❌ Error: File not found: {html_file}")
        sys.exit(1)

    if not html_file.suffix == '.html':
        print(f"❌ Error: Input must be an HTML file")
        sys.exit(1)

    pdf_file = html_file.with_suffix('.pdf')

    try:
        if html_to_pdf_with_links(html_file, pdf_file):
            size = pdf_file.stat().st_size / 1024
            print(f"✅ PDF created: {pdf_file.name} ({size:.1f} KB)")
            print(f"\n✨ All hyperlinks are clickable in the PDF!")
            print(f"   - Table of contents links work")
            print(f"   - Email addresses are clickable")
            print(f"   - External URLs open in browser")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
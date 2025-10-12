#!/usr/bin/env python3
"""
Batch convert all markdown files in a directory to PDF
Finds all .md files and converts them to beautiful PDFs with Mermaid support
"""

import sys
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess

def find_markdown_files(directory):
    """Find all markdown files in directory"""
    md_files = list(Path(directory).glob('*.md'))
    return sorted(md_files)

def md_to_html(md_file):
    """Convert markdown to HTML using our converter"""
    print(f"  📝 Converting {md_file.name} to HTML...")

    result = subprocess.run(
        ['python3', 'md2html-pro.py', str(md_file)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"    ❌ Error converting {md_file}: {result.stderr}")
        return None

    html_file = md_file.with_suffix('.html')
    if html_file.exists():
        print(f"    ✅ HTML created: {html_file.name}")
        return html_file
    return None

def html_to_pdf(html_file, pdf_file):
    """Convert HTML with Mermaid diagrams to PDF"""

    # Get absolute paths
    html_path = html_file.absolute()
    pdf_path = pdf_file.absolute()

    with sync_playwright() as p:
        # Launch browser (headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the HTML file
        file_url = f"file://{html_path}"
        page.goto(file_url)

        # Wait for Mermaid diagrams to render
        page.wait_for_timeout(3000)  # 3 seconds for Mermaid

        # Check for Mermaid diagrams
        try:
            page.wait_for_selector('.mermaid svg', timeout=2000)
        except:
            pass  # No Mermaid diagrams, that's OK

        # Generate PDF with print-friendly settings
        page.pdf(
            path=str(pdf_path),
            format='A4',
            print_background=True,
            margin={
                'top': '15mm',
                'bottom': '15mm',
                'left': '15mm',
                'right': '15mm'
            }
        )

        browser.close()

    return True

def convert_directory(directory):
    """Convert all markdown files in a directory to PDF"""

    directory = Path(directory)
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        return False

    print(f"🔍 Searching for markdown files in: {directory}/")
    md_files = find_markdown_files(directory)

    if not md_files:
        print(f"  ℹ️  No markdown files found in {directory}")
        return False

    print(f"📚 Found {len(md_files)} markdown files to convert:")
    for f in md_files:
        print(f"  • {f.name}")

    print(f"\n🚀 Starting batch conversion...\n")

    successful = 0
    failed = 0

    for i, md_file in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] Processing: {md_file.name}")
        print("=" * 50)

        # Convert MD to HTML
        html_file = md_to_html(md_file)
        if not html_file:
            failed += 1
            print(f"  ⚠️  Skipping PDF generation for {md_file.name}\n")
            continue

        # Convert HTML to PDF
        pdf_file = md_file.with_suffix('.pdf')
        print(f"  🖨️  Generating PDF: {pdf_file.name}...")

        try:
            if html_to_pdf(html_file, pdf_file):
                size = pdf_file.stat().st_size / 1024
                print(f"  ✅ PDF created: {pdf_file.name} ({size:.1f} KB)")
                successful += 1
            else:
                print(f"  ❌ Failed to create PDF for {md_file.name}")
                failed += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1

        print()  # Blank line between files

    # Summary
    print("=" * 50)
    print(f"\n📊 Conversion Complete!")
    print(f"  ✅ Successful: {successful} files")
    if failed > 0:
        print(f"  ❌ Failed: {failed} files")

    # List all PDFs created
    if successful > 0:
        print(f"\n📄 PDF files in {directory}/:")
        pdf_files = sorted(directory.glob('*.pdf'))
        for pdf in pdf_files:
            size = pdf.stat().st_size / 1024
            print(f"  • {pdf.name} ({size:.1f} KB)")

    return successful > 0

def main():
    if len(sys.argv) < 2:
        print("Batch Markdown to PDF Converter")
        print("=" * 40)
        print("\nUsage: python3 convert-all-to-pdf.py <directory>")
        print("\nExamples:")
        print("  python3 convert-all-to-pdf.py meeting-materials")
        print("  python3 convert-all-to-pdf.py .")
        print("  python3 convert-all-to-pdf.py /path/to/markdown/files")
        print("\nThis will:")
        print("  1. Find all .md files in the directory")
        print("  2. Convert each to HTML with Mermaid support")
        print("  3. Generate PDF from each HTML")
        print("  4. Report on success/failure")
        sys.exit(1)

    directory = sys.argv[1]

    print(f"🎯 Batch Markdown to PDF Converter")
    print("=" * 40)

    success = convert_directory(directory)

    if success:
        print("\n✨ All done! Your PDFs are ready.")
        sys.exit(0)
    else:
        print("\n⚠️  Some conversions may have failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
MD to PDF - Command Line Interface

Main entry point for the md-to-pdf package.
Converts Markdown files to PDF with support for Mermaid diagrams and clickable links.
"""

import sys
import os
from pathlib import Path
import argparse
from typing import Optional, List

from md_to_pdf.md2html import convert_file as md_to_html
from md_to_pdf.html2pdf import html_to_pdf_with_links

def convert_md_to_pdf(md_file: str, pdf_file: Optional[str] = None, keep_html: bool = False) -> Path:
    """
    Convert a Markdown file to PDF with clickable links and Mermaid diagrams
    
    Args:
        md_file: Path to the Markdown file
        pdf_file: Optional path for the output PDF file
        keep_html: Whether to keep the intermediate HTML file
        
    Returns:
        Path to the generated PDF file
    """
    md_path = Path(md_file)
    
    if not md_path.exists():
        raise FileNotFoundError(f"File not found: {md_file}")
    
    if not md_file.endswith('.md'):
        raise ValueError(f"Input must be a Markdown (.md) file")
    
    # Generate HTML file path
    html_file = md_path.with_suffix('.html')
    
    # Generate PDF file path if not specified
    pdf_path = md_path.with_suffix('.pdf') if pdf_file is None else Path(pdf_file)
    
    print(f"📄 Converting {md_path.name} to PDF...")
    
    # Step 1: Convert Markdown to HTML
    print(f"   ⟶ Converting Markdown to HTML...")
    html_path = md_to_html(md_path, html_file)
    
    # Step 2: Convert HTML to PDF
    print(f"   ⟶ Converting HTML to PDF with clickable links...")
    pdf_path = html_to_pdf_with_links(html_path, pdf_path)
    
    # Remove intermediate HTML file if not keeping it
    if not keep_html and html_path.exists():
        html_path.unlink()
        print(f"   ⟶ Removed intermediate HTML file")
    
    size = pdf_path.stat().st_size / 1024
    print(f"✅ PDF created: {pdf_path.name} ({size:.1f} KB)")
    print(f"\n✨ All hyperlinks are clickable in the PDF!")
    print(f"   - Table of contents links work")
    print(f"   - Email addresses are clickable")
    print(f"   - External URLs open in browser")
    
    return pdf_path

def main():
    """Main entry point for the md2pdf command"""
    parser = argparse.ArgumentParser(
        description="Convert Markdown to PDF with clickable links and Mermaid diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  md2pdf document.md                 # Creates document.pdf
  md2pdf document.md -o output.pdf   # Creates output.pdf
  md2pdf document.md --keep-html     # Keeps the intermediate HTML file
        """
    )
    
    parser.add_argument(
        "input_file", 
        help="Path to the Markdown file"
    )
    
    parser.add_argument(
        "-o", "--output", 
        help="Path for the output PDF file"
    )
    
    parser.add_argument(
        "--keep-html", 
        action="store_true",
        help="Keep the intermediate HTML file"
    )
    
    parser.add_argument(
        "--version", 
        action="version",
        version="%(prog)s 1.1.0"
    )
    
    args = parser.parse_args()
    
    try:
        convert_md_to_pdf(args.input_file, args.output, args.keep_html)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob

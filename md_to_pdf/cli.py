#!/usr/bin/env python3
# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
# Created with IBM Bob (https://bob.ibm.com)

"""
MD to PDF - Command Line Interface

Main entry point for the md-to-pdf package.
Converts Markdown files to PDF with support for Mermaid diagrams and clickable links.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from pathlib import Path
import argparse
from typing import Optional, Literal

from md_to_pdf import __version__
from md_to_pdf.md2html import convert_file as md_to_html
from md_to_pdf.html2pdf import html_to_pdf_with_links
from md_to_pdf.image_validator import ImageValidator

def convert_md_to_pdf(
    md_file: str,
    pdf_file: Optional[str] = None,
    keep_html: bool = False,
    orientation: Literal['portrait', 'landscape'] = 'portrait',
    font_preset: str = 'ibm',
    generate_toc: bool = False,
    toc_depth: int = 3,
    toc_title: str = "Table of Contents",
    toc_position: str = 'after_title',
    toc_include_first: bool = False,
    strict_images: bool = False
) -> Path:
    """
    Convert a Markdown file to PDF with clickable links and Mermaid diagrams
    
    Args:
        md_file: Path to the Markdown file
        pdf_file: Optional path for the output PDF file
        keep_html: Whether to keep the intermediate HTML file
        orientation: Page orientation for the PDF. Must be either 'portrait' or
                     'landscape'. Defaults to 'portrait' for backward compatibility.
        font_preset: Font preset to use ('ibm', 'system', 'classic', 'modern').
                     Defaults to 'ibm'.
        generate_toc: Generate table of contents
        toc_depth: Maximum heading level for TOC (1-6)
        toc_title: Title for the table of contents
        toc_position: TOC position ('top', 'after_title', 'custom')
        toc_include_first: Include first H1 heading in TOC
        strict_images: If True, abort on missing images. If False, issue warnings.
        
    Returns:
        Path to the generated PDF file
        
    Raises:
        FileNotFoundError: If md_file does not exist
        ValueError: If md_file is not a .md file or orientation is invalid
        SystemExit: If strict_images is True and images are missing
    """
    md_path = Path(md_file)
    
    if not md_path.exists():
        raise FileNotFoundError(f"File not found: {md_file}")
    
    if not md_file.endswith('.md'):
        raise ValueError(f"Input must be a Markdown (.md) file")
    
    # Validate images before processing
    validator = ImageValidator(strict_mode=strict_images)
    validation_result = validator.validate_file(md_path)
    sys.stdout.flush()
    validator.report_results(validation_result)
    if strict_images and validation_result.has_missing_images:
        sys.exit(1)
    
    # Generate PDF file path if not specified
    pdf_path = md_path.with_suffix('.pdf') if pdf_file is None else Path(pdf_file)

    # Generate HTML file path in the same directory as the PDF
    html_file = pdf_path.with_suffix('.html')
    
    print(f"📄 Converting {md_path.name} to PDF...")
    
    # Step 1: Convert Markdown to HTML
    if generate_toc:
        print(f"   ⟶ Converting Markdown to HTML with TOC...")
    else:
        print(f"   ⟶ Converting Markdown to HTML...")
    html_path = md_to_html(md_path, html_file, orientation=orientation, font_preset=font_preset,
                           generate_toc=generate_toc, toc_depth=toc_depth, toc_title=toc_title,
                           toc_position=toc_position, toc_include_first=toc_include_first)
    
    # Step 2: Convert HTML to PDF
    print(f"   ⟶ Converting HTML to PDF with clickable links...")
    pdf_path = html_to_pdf_with_links(html_path, pdf_path, orientation=orientation)
    
    # Remove intermediate HTML file if not keeping it
    if not keep_html and html_path.exists():
        html_path.unlink()
        print(f"   ⟶ Removed intermediate HTML file")
    
    size = pdf_path.stat().st_size / 1024
    print(f"✅ PDF created: {pdf_path.name} ({size:.1f} KB)")
    if validation_result.has_missing_images:
        print(f"⚠️  {validation_result.missing_count} image(s) missing — PDF may be incomplete", file=sys.stderr)
    
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
  md2pdf document.md                              # IBM fonts (default), portrait
  md2pdf document.md -o output.pdf                # IBM fonts, portrait
  md2pdf document.md -l                           # IBM fonts, landscape
  md2pdf document.md --font-preset system         # System fonts, portrait
  md2pdf document.md --font-preset modern -l      # Modern fonts, landscape
  md2pdf document.md --font-preset classic        # Classic fonts, portrait
  md2pdf document.md -l -o wide.pdf               # IBM fonts, landscape, custom output
  md2pdf document.md --keep-html                  # Keeps the intermediate HTML file
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
    
    # Create mutually exclusive group for orientation
    orientation_group = parser.add_mutually_exclusive_group()
    
    orientation_group.add_argument(
        "-l", "--landscape",
        action="store_true",
        help="Use landscape orientation for A4 pages (default: portrait)"
    )
    
    orientation_group.add_argument(
        "-p", "--portrait",
        action="store_true",
        help="Use portrait orientation for A4 pages (default, explicit)"
    )
    
    parser.add_argument(
        "--keep-html",
        action="store_true",
        help="Keep the intermediate HTML file"
    )
    
    parser.add_argument(
        "--font-preset",
        choices=['ibm', 'system', 'classic', 'modern'],
        default='ibm',
        help="Font preset to use: 'ibm' (default, IBM Plex fonts), 'system' (system fonts), 'classic' (Georgia), 'modern' (Roboto)"
    )
    
    parser.add_argument(
        "--toc",
        action="store_true",
        help="Generate table of contents"
    )
    
    parser.add_argument(
        "--toc-depth",
        type=int,
        default=3,
        choices=range(1, 7),
        metavar="DEPTH",
        help="Maximum heading level for TOC (1-6, default: 3)"
    )
    
    parser.add_argument(
        "--toc-title",
        default="Table of Contents",
        help="Title for the table of contents (default: 'Table of Contents')"
    )
    
    parser.add_argument(
        "--toc-position",
        choices=['top', 'after_title', 'custom'],
        default='after_title',
        help="TOC position: 'top' (before title), 'after_title' (default, after first H1), or 'custom' (use {{TOC}} marker in markdown)"
    )
    
    parser.add_argument(
        "--toc-include-first",
        action="store_true",
        help="Include first H1 heading in TOC (default: exclude as document title)"
    )
    
    parser.add_argument(
        "--strict-images",
        action="store_true",
        help="Abort PDF generation if any referenced images are missing (default: show warnings and continue)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    args = parser.parse_args()
    
    # Determine orientation: landscape flag takes precedence, portrait is default
    orientation = 'landscape' if args.landscape else 'portrait'
    
    try:
        convert_md_to_pdf(
            args.input_file,
            args.output,
            args.keep_html,
            orientation,
            args.font_preset,
            args.toc,
            args.toc_depth,
            args.toc_title,
            args.toc_position,
            args.toc_include_first,
            args.strict_images
        )
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob

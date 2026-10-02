#!/usr/bin/env python3
# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
# Created with IBM Bob (https://bob.ibm.com)

"""
MD to PDF - Batch Processing

Batch converter for Markdown to PDF with support for Mermaid diagrams and clickable links.
Processes multiple files or directories at once.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import argparse
from pathlib import Path
from typing import Literal
from concurrent.futures import ThreadPoolExecutor, as_completed

from md_to_pdf import __version__
from md_to_pdf.cli import convert_md_to_pdf
from md_to_pdf.image_validator import validate_images_batch

# Default maximum number of parallel conversions
DEFAULT_MAX_WORKERS = 4

def find_markdown_files(path: str, recursive: bool = False) -> list[Path]:
    """Find all Markdown files in the given path.

    Args:
        path: Directory or file path to search.
        recursive: Search recursively in subdirectories.

    Returns:
        List of Path objects for Markdown files found.
    """
    path_obj = Path(path)
    if path_obj.is_file() and path_obj.suffix.lower() == '.md':
        return [path_obj]
    if path_obj.is_dir():
        return list(path_obj.glob('**/*.md' if recursive else '*.md'))
    return []

def _determine_output_path(md_file: Path, output_dir: Path | None) -> Path:
    # Returns output_dir/stem.pdf or source sibling stem.pdf.
    if output_dir:
        return output_dir / f"{md_file.stem}.pdf"
    return md_file.with_suffix('.pdf')

def batch_convert(
    paths: list[str],
    output_dir: str | None = None,
    recursive: bool = False,
    keep_html: bool = False,
    orientation: Literal['portrait', 'landscape'] = 'portrait',
    font_preset: str = 'ibm',
    max_workers: int = DEFAULT_MAX_WORKERS,
    generate_toc: bool = False,
    toc_depth: int = 3,
    toc_title: str = "Table of Contents",
    toc_position: str = 'after_title',
    toc_include_first: bool = False,
    strict_images: bool = False
) -> list[Path]:
    """Convert multiple Markdown files to PDF in parallel.

    Args:
        paths: File or directory paths to process.
        output_dir: Output directory for PDF files. Defaults to same directory as source.
        recursive: Search recursively in directories.
        keep_html: Keep intermediate HTML files.
        orientation: Page orientation, ``'portrait'`` or ``'landscape'``.
        font_preset: Font preset – ``'ibm'``, ``'system'``, ``'classic'``, or ``'modern'``.
        max_workers: Maximum parallel conversions. Must be >= 1.
        generate_toc: Generate table of contents.
        toc_depth: Maximum heading level for TOC (1–6).
        toc_title: Title for the table of contents.
        toc_position: TOC position – ``'top'``, ``'after_title'``, or ``'custom'``.
        toc_include_first: Include first H1 heading in TOC.
        strict_images: If ``True``, return empty list on missing images instead of warning.

    Returns:
        List of generated PDF file paths.

    Raises:
        ValueError: If ``max_workers`` is less than 1.
    """
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    md_files = []
    for path in paths:
        md_files.extend(find_markdown_files(path, recursive))

    if not md_files:
        print("❌ No Markdown files found")
        return []

    # In strict mode: validate all files upfront before any conversion starts (fail fast).
    # In non-strict mode: per-file validation in cli.py handles warnings.
    if strict_images and not validate_images_batch(md_files, strict_mode=True):
        return []

    print(f"🔍 Found {len(md_files)} Markdown files to convert")

    output_path = None
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_path}")

    pdf_files: list[Path] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                convert_md_to_pdf,
                str(md_file),
                str(_determine_output_path(md_file, output_path)),
                keep_html, orientation, font_preset,
                generate_toc, toc_depth, toc_title, toc_position,
                toc_include_first, strict_images
            ): md_file
            for md_file in md_files
        }
        for future in as_completed(future_to_file):
            md_file = future_to_file[future]
            try:
                pdf_files.append(future.result())
            except Exception as e:
                print(f"❌ Error converting {md_file.name}: {e}")

    if pdf_files:
        print(f"\n✅ Successfully converted {len(pdf_files)} of {len(md_files)} files")
    else:
        print(f"\n❌ Failed to convert any files")

    return pdf_files

def _create_argument_parser() -> argparse.ArgumentParser:
    # Build and return the CLI argument parser for md2pdf-batch.
    parser = argparse.ArgumentParser(
        description="Batch convert Markdown files to PDF with clickable links and Mermaid diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  md2pdf-batch file1.md file2.md                    # IBM fonts (default), portrait
  md2pdf-batch docs/                                # Convert all .md files in docs/
  md2pdf-batch docs/ -l                             # Landscape orientation
  md2pdf-batch docs/ --font-preset system           # System fonts
  md2pdf-batch docs/ --font-preset modern -l        # Modern fonts, landscape
  md2pdf-batch docs/ --recursive                    # Convert recursively
  md2pdf-batch docs/ -r --font-preset classic       # Recursive with classic fonts
  md2pdf-batch docs/ -o output/                     # Save all PDFs to output/
  md2pdf-batch docs/ -o output/ -l                  # Output directory with landscape
  md2pdf-batch docs/ --keep-html                    # Keep intermediate HTML files
        """
    )
    
    parser.add_argument(
        "paths",
        nargs='+',
        help="Paths to Markdown files or directories containing Markdown files"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory for PDF files"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively search for Markdown files in directories"
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
        help="Keep intermediate HTML files"
    )
    
    parser.add_argument(
        "--font-preset",
        choices=['ibm', 'system', 'classic', 'modern'],
        default='ibm',
        help="Font preset to use: 'ibm' (default, IBM Plex fonts), 'system' (system fonts), 'classic' (Georgia), 'modern' (Roboto)"
    )
    
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=DEFAULT_MAX_WORKERS,
        help=f"Maximum number of parallel conversions (default: {DEFAULT_MAX_WORKERS})"
    )
    
    parser.add_argument(
        '--toc',
        action='store_true',
        help='Generate table of contents for all files'
    )
    
    parser.add_argument(
        '--toc-depth',
        type=int,
        default=3,
        choices=range(1, 7),
        metavar='DEPTH',
        help='Maximum heading level for TOC (1-6, default: 3)'
    )
    
    parser.add_argument(
        '--toc-title',
        default='Table of Contents',
        help='Title for the table of contents'
    )
    
    parser.add_argument(
        '--toc-position',
        choices=['top', 'after_title', 'custom'],
        default='after_title',
        help='TOC position: top, after_title (default), or custom'
    )
    
    parser.add_argument(
        '--toc-include-first',
        action='store_true',
        help='Include first H1 heading in TOC'
    )
    
    parser.add_argument(
        '--strict-images',
        action='store_true',
        help='Abort PDF generation if any referenced images are missing (default: show warnings and continue)'
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    return parser

def main():
    """Main entry point for the md2pdf-batch command."""
    parser = _create_argument_parser()
    args = parser.parse_args()

    orientation = 'landscape' if args.landscape else 'portrait'

    try:
        pdf_files = batch_convert(
            args.paths,
            args.output_dir,
            args.recursive,
            args.keep_html,
            orientation,
            args.font_preset,
            args.jobs,
            args.toc,
            args.toc_depth,
            args.toc_title,
            args.toc_position,
            args.toc_include_first,
            args.strict_images
        )
        if not pdf_files:
            sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob

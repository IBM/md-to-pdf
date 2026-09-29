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
import argparse
from pathlib import Path
from typing import List, Optional, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed

from md_to_pdf import __version__
from md_to_pdf.cli import convert_md_to_pdf
from md_to_pdf.image_validator import validate_images_batch

# Default maximum number of parallel conversions
DEFAULT_MAX_WORKERS = 4

def find_markdown_files(path: str, recursive: bool = False) -> List[Path]:
    """
    Find all Markdown files in the given path
    
    Args:
        path: Directory or file path to search
        recursive: Whether to search recursively in subdirectories
        
    Returns:
        List of Path objects for Markdown files
    """
    path_obj = Path(path)
    
    # If path is a file and it's a markdown file, return it
    if path_obj.is_file() and path_obj.suffix.lower() == '.md':
        return [path_obj]
    
    # If path is a directory, find all markdown files
    if path_obj.is_dir():
        if recursive:
            # Recursive search
            return list(path_obj.glob('**/*.md'))
        else:
            # Non-recursive search
            return list(path_obj.glob('*.md'))
    
    return []

def _determine_output_path(md_file: Path, output_dir: Optional[Path]) -> Path:
    """
    Determine the output PDF path for a markdown file
    
    Args:
        md_file: Path to the markdown file
        output_dir: Optional output directory
        
    Returns:
        Path object for the output PDF file
    """
    if output_dir:
        return output_dir / f"{md_file.stem}.pdf"
    return md_file.with_suffix('.pdf')

def _submit_conversion_tasks(
    executor: ThreadPoolExecutor,
    md_files: List[Path],
    output_path: Optional[Path],
    keep_html: bool,
    orientation: Literal['portrait', 'landscape'],
    font_preset: str,
    generate_toc: bool,
    toc_depth: int,
    toc_title: str,
    toc_position: str,
    toc_include_first: bool,
    strict_images: bool
) -> dict:
    """
    Submit conversion tasks to the executor
    
    Args:
        executor: ThreadPoolExecutor instance
        md_files: List of markdown files to convert
        output_path: Optional output directory
        keep_html: Whether to keep intermediate HTML files
        orientation: Page orientation
        font_preset: Font preset to use
        generate_toc: Whether to generate table of contents
        toc_depth: Maximum heading level for TOC (1-6)
        toc_title: Title for the table of contents
        toc_position: TOC position ('top', 'after_title', 'custom')
        toc_include_first: Include first H1 heading in TOC
        strict_images: If True, abort on missing images
        
    Returns:
        Dictionary mapping futures to (md_file, pdf_file) tuples
    """
    future_to_file = {}
    for md_file in md_files:
        pdf_file = _determine_output_path(md_file, output_path)
        
        future = executor.submit(
            convert_md_to_pdf,
            str(md_file),
            str(pdf_file),
            keep_html,
            orientation,
            font_preset,
            generate_toc,
            toc_depth,
            toc_title,
            toc_position,
            toc_include_first,
            strict_images
        )
        future_to_file[future] = (md_file, pdf_file)
    
    return future_to_file

def _process_conversion_results(future_to_file: dict) -> List[Path]:
    """
    Process completed conversion tasks and collect results
    
    Args:
        future_to_file: Dictionary mapping futures to (md_file, pdf_file) tuples
        
    Returns:
        List of successfully generated PDF files
    """
    pdf_files: List[Path] = []
    for future in as_completed(future_to_file):
        md_file, pdf_file = future_to_file[future]
        try:
            pdf_path = future.result()
            # Ensure we return Path objects for type consistency
            if isinstance(pdf_path, str):
                pdf_path = Path(pdf_path)
            pdf_files.append(pdf_path)
        except Exception as e:
            print(f"❌ Error converting {md_file.name}: {e}")
    
    return pdf_files

def batch_convert(
    paths: List[str],
    output_dir: Optional[str] = None,
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
) -> List[Path]:
    """
    Convert multiple Markdown files to PDF
    
    Args:
        paths: List of file or directory paths to process
        output_dir: Optional output directory for PDF files
        recursive: Whether to search recursively in directories
        keep_html: Whether to keep intermediate HTML files
        orientation: Page orientation ('portrait' or 'landscape'), default 'portrait'
        font_preset: Font preset to use ('ibm', 'system', 'classic', 'modern'), default 'ibm'
        max_workers: Maximum number of parallel conversions (must be >= 1)
        generate_toc: Whether to generate table of contents
        toc_depth: Maximum heading level for TOC (1-6), default 3
        toc_title: Title for the table of contents, default "Table of Contents"
        toc_position: TOC position ('top', 'after_title', 'custom'), default 'after_title'
        toc_include_first: Include first H1 heading in TOC, default False
        strict_images: If True, abort on missing images. If False, issue warnings.
        
    Returns:
        List of generated PDF files
        
    Raises:
        ValueError: If max_workers is less than 1
        SystemExit: If strict_images is True and images are missing
    """
    # Validate max_workers parameter
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    
    # Find all markdown files
    md_files = []
    for path in paths:
        md_files.extend(find_markdown_files(path, recursive))
    
    if not md_files:
        print("❌ No Markdown files found")
        return []
    
    print(f"🔍 Found {len(md_files)} Markdown files to convert")
    
    # Validate images in all files before processing
    if not validate_images_batch(md_files, strict_mode=strict_images):
        # In strict mode, validation failed
        sys.exit(1)
    
    # Create output directory if specified
    output_path = None
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_path}")
    
    # Convert files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit conversion tasks
        future_to_file = _submit_conversion_tasks(
            executor,
            md_files,
            output_path,
            keep_html,
            orientation,
            font_preset,
            generate_toc,
            toc_depth,
            toc_title,
            toc_position,
            toc_include_first,
            strict_images
        )
        
        # Process results as they complete
        pdf_files = _process_conversion_results(future_to_file)
    
    # Print summary
    if pdf_files:
        print(f"\n✅ Successfully converted {len(pdf_files)} of {len(md_files)} files")
    else:
        print(f"\n❌ Failed to convert any files")
    
    return pdf_files

def _create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the batch converter
    
    Returns:
        Configured ArgumentParser instance
    """
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
    """Main entry point for the md2pdf-batch command"""
    parser = _create_argument_parser()
    args = parser.parse_args()
    
    # Determine orientation
    orientation = 'landscape' if args.landscape else 'portrait'
    
    try:
        batch_convert(
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
    except ValueError as e:
        # Handle validation errors (e.g., invalid max_workers)
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob

#!/usr/bin/env python3
"""
MD to PDF - Batch Processing

Batch converter for Markdown to PDF with support for Mermaid diagrams and clickable links.
Processes multiple files or directories at once.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from md_to_pdf import __version__
from md_to_pdf.cli import convert_md_to_pdf

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

def batch_convert(
    paths: List[str], 
    output_dir: Optional[str] = None, 
    recursive: bool = False,
    keep_html: bool = False,
    max_workers: int = 4
) -> List[Path]:
    """
    Convert multiple Markdown files to PDF
    
    Args:
        paths: List of file or directory paths to process
        output_dir: Optional output directory for PDF files
        recursive: Whether to search recursively in directories
        keep_html: Whether to keep intermediate HTML files
        max_workers: Maximum number of parallel conversions
        
    Returns:
        List of generated PDF files
    """
    # Find all markdown files
    md_files = []
    for path in paths:
        md_files.extend(find_markdown_files(path, recursive))
    
    if not md_files:
        print("❌ No Markdown files found")
        return []
    
    print(f"🔍 Found {len(md_files)} Markdown files to convert")
    
    # Create output directory if specified
    output_path = None
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_path}")
    
    # Convert files in parallel
    pdf_files = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create conversion tasks
        future_to_file = {}
        for md_file in md_files:
            # Determine output PDF path
            if output_path:
                pdf_file = output_path / f"{md_file.stem}.pdf"
            else:
                pdf_file = md_file.with_suffix('.pdf')
            
            # Submit conversion task
            future = executor.submit(
                convert_md_to_pdf, 
                str(md_file), 
                str(pdf_file), 
                keep_html
            )
            future_to_file[future] = (md_file, pdf_file)
        
        # Process results as they complete
        for future in as_completed(future_to_file):
            md_file, pdf_file = future_to_file[future]
            try:
                pdf_path = future.result()
                pdf_files.append(pdf_path)
            except Exception as e:
                print(f"❌ Error converting {md_file.name}: {e}")
    
    # Print summary
    if pdf_files:
        print(f"\n✅ Successfully converted {len(pdf_files)} of {len(md_files)} files")
    else:
        print(f"\n❌ Failed to convert any files")
    
    return pdf_files

def main():
    """Main entry point for the md2pdf-batch command"""
    parser = argparse.ArgumentParser(
        description="Batch convert Markdown files to PDF with clickable links and Mermaid diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  md2pdf-batch file1.md file2.md           # Convert specific files
  md2pdf-batch docs/                       # Convert all .md files in docs/
  md2pdf-batch docs/ --recursive           # Convert all .md files in docs/ and subdirectories
  md2pdf-batch docs/ -o output/            # Save all PDFs to output/ directory
  md2pdf-batch docs/ --keep-html           # Keep intermediate HTML files
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
    
    parser.add_argument(
        "--keep-html", 
        action="store_true",
        help="Keep intermediate HTML files"
    )
    
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=4,
        help="Maximum number of parallel conversions (default: 4)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    args = parser.parse_args()
    
    try:
        batch_convert(
            args.paths, 
            args.output_dir, 
            args.recursive, 
            args.keep_html,
            args.jobs
        )
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob

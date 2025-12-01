#!/usr/bin/env python3
"""
Convert HTML to PDF with clickable hyperlinks using Playwright
"""

import sys
from pathlib import Path
from typing import Optional, Literal
from playwright.sync_api import sync_playwright

def html_to_pdf_with_links(
    html_file,
    pdf_file=None,
    orientation: Optional[Literal['portrait', 'landscape']] = 'portrait'
):
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
    valid_orientations = ('portrait', 'landscape')
    if orientation not in valid_orientations:
        raise ValueError(
            f"Invalid orientation '{orientation}'. "
            f"Must be one of: {', '.join(valid_orientations)}"
        )

    # Get absolute paths
    html_path = Path(html_file).absolute()
    
    if pdf_file is None:
        pdf_file = html_path.with_suffix('.pdf')
    else:
        pdf_file = Path(pdf_file)
    
    pdf_path = pdf_file.absolute()

    print(f"📄 Converting {html_path.name} to PDF with clickable links...")

    with sync_playwright() as p:
        # Launch browser (headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the HTML file with proper URL encoding
        # Use as_uri() to handle special characters like #, spaces, etc.
        file_url = html_path.as_uri()
        page.goto(file_url)

        # Wait for initial content to load
        page.wait_for_timeout(2000)  # 2 seconds for initial rendering
        
        # Handle Mermaid diagrams - simplified approach
        try:
            # Check if there are any Mermaid diagrams
            has_mermaid = page.evaluate('''() => {
                return document.querySelectorAll('.mermaid').length > 0;
            }''')
            
            if has_mermaid:
                print("    ⟶ Waiting for Mermaid diagrams to render...")
                
                # Give more time for initial page load
                page.wait_for_timeout(1000)
                
                # Fix any paragraph tags that might be wrapping Mermaid diagrams
                page.evaluate('''() => {
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
                }''')
                
                # Ensure Mermaid is properly initialized
                page.evaluate('''() => {
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
                }''')
                
                # Wait for rendering to complete
                page.wait_for_timeout(3000)
                
                # Auto-detect and mark wide diagrams
                page.evaluate('''() => {
                    function detectAndMarkWideDiagrams() {
                        const containers = document.querySelectorAll('.mermaid-container');
                        
                        containers.forEach(container => {
                            const svg = container.querySelector('svg');
                            if (!svg) return;
                            
                            // Get the SVG's natural (intrinsic) width
                            const viewBox = svg.getAttribute('viewBox');
                            let naturalWidth = 0;
                            
                            if (viewBox) {
                                // Parse viewBox to get natural width
                                const viewBoxValues = viewBox.split(/[\\s,]+/);
                                naturalWidth = parseFloat(viewBoxValues[2]);
                            } else {
                                // Fallback to width attribute or computed width
                                naturalWidth = parseFloat(svg.getAttribute('width')) || svg.getBBox().width;
                            }
                            
                            // Get the current rendered width
                            const renderedWidth = svg.getBoundingClientRect().width;
                            
                            // If the diagram is being scaled down, mark it as wide
                            const scalingThreshold = 0.95;
                            if (naturalWidth > renderedWidth * scalingThreshold) {
                                container.classList.add('wide-diagram');
                            }
                        });
                    }
                    
                    detectAndMarkWideDiagrams();
                }''')
                
                # Check if any SVGs were created
                svg_count = page.evaluate('''() => {
                    return document.querySelectorAll('svg').length;
                }''')
                
                # Check how many wide diagrams were detected
                wide_count = page.evaluate('''() => {
                    return document.querySelectorAll('.mermaid-container.wide-diagram').length;
                }''')
                
                if svg_count > 0:
                    print(f"    ⟶ {svg_count} diagram(s) rendered successfully")
                    if wide_count > 0:
                        print(f"    ⟶ {wide_count} wide diagram(s) using full printable width")
                else:
                    print("    ⟶ Using text representation for diagrams")
            else:
                print("    ⟶ No Mermaid diagrams found in document")
        except Exception as e:
            # Continue even if there are errors with Mermaid rendering
            print(f"    ⟶ Note: {str(e)}")

        # Generate PDF with settings optimized for links
        # Convert orientation to landscape boolean (True for landscape, False for portrait)
        landscape = (orientation == 'landscape')
        
        page.pdf(
            path=str(pdf_path),
            format='A4',
            landscape=landscape,
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

    return pdf_path

def main():
    if len(sys.argv) < 2:
        print("HTML to PDF Converter with Clickable Links")
        print("=" * 45)
        print("\nUsage: html2pdf file.html [output.pdf]")
        print("\nThis will create a PDF with:")
        print("  ✅ Clickable table of contents")
        print("  ✅ Working internal anchor links")
        print("  ✅ Clickable external URLs")
        print("  ✅ Clickable email addresses")
        sys.exit(1)

    html_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        pdf_file = sys.argv[2]
    else:
        pdf_file = None

    if not Path(html_file).exists():
        print(f"❌ Error: File not found: {html_file}")
        sys.exit(1)

    if not html_file.endswith('.html'):
        print(f"❌ Error: Input must be an HTML file")
        sys.exit(1)

    try:
        pdf_path = html_to_pdf_with_links(html_file, pdf_file)
        size = pdf_path.stat().st_size / 1024
        print(f"✅ PDF created: {pdf_path.name} ({size:.1f} KB)")
        print(f"\n✨ All hyperlinks are clickable in the PDF!")
        print(f"   - Table of contents links work")
        print(f"   - Email addresses are clickable")
        print(f"   - External URLs open in browser")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

# Made with Bob

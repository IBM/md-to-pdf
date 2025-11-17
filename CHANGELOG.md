# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-11-17

### Added
- **Page orientation support** for A4 pages (portrait and landscape)
  - Added `-l`/`--landscape` flag to `md2pdf` command for landscape orientation
  - Added `-p`/`--portrait` flag to `md2pdf` command for explicit portrait orientation
  - Added orientation flags to `md2pdf-batch` command for batch processing
  - Portrait orientation (210mm × 297mm) remains the default for backward compatibility
  - Landscape orientation (297mm × 210mm) provides 48% more horizontal space
- **Automatic content width optimization** based on page orientation
  - Portrait mode: 180mm content width (optimal for reading)
  - Landscape mode: 267mm content width (ideal for wide tables and diagrams)
- **Enhanced Mermaid diagram support** with automatic width detection
  - Diagrams automatically utilize full printable width when needed
  - Wide diagram detection and optimization for better rendering
- **Comprehensive CLI help** with orientation usage examples
- **Detailed documentation** for page orientation feature in README.md

### Changed
- Updated [`convert_md_to_pdf()`](md_to_pdf/cli.py:18) function to accept `orientation` parameter
- Updated [`html_to_pdf_with_links()`](md_to_pdf/html2pdf.py:11) function to support orientation
- Updated [`create_html_document()`](md_to_pdf/md2html.py:221) to generate orientation-aware CSS
- Updated [`batch_convert()`](md_to_pdf/batch.py:46) function to support orientation in batch processing
- Enhanced CSS `@page` rules to properly handle A4 portrait and landscape formats
- Improved content width calculations for optimal layout in both orientations

### Technical Details
- Modified files: [`cli.py`](md_to_pdf/cli.py:1), [`md2html.py`](md_to_pdf/md2html.py:1), [`html2pdf.py`](md_to_pdf/html2pdf.py:1), [`batch.py`](md_to_pdf/batch.py:1)
- Added mutually exclusive argument groups for orientation flags
- Implemented proper A4 page size specifications with orientation
- Maintained backward compatibility with existing scripts and workflows

## [1.1.2] - 2025-11-11

### Added
- **Future Roadmap**: Added `FUTURE_IDEAS.md` with 140 lines documenting planned features and enhancements for future releases
- **Expanded Test Coverage**: Added comprehensive test cases in `test.md` to validate conversion functionality

### Changed
- **Enhanced HTML to PDF Conversion**: Improved `html2pdf.py` with additional features and better error handling (43 new lines)
- **Enhanced Markdown to HTML Conversion**: Significant improvements to `md2html.py` with enhanced parsing and formatting capabilities (66 new lines)
- **Package Metadata**: Updated `PKG-INFO` with latest package information

### Maintenance
- **Version Bump**: Updated version number to 1.1.2 across all source files
  - Updated `setup.py`
  - Updated `md_to_pdf/__init__.py`
  - Updated installation instructions in `README.md`
- **Distribution**: Built and included new wheel distribution file

### Files Changed
- 5 files modified with 279 insertions and 1 deletion
- Core improvements to HTML and Markdown conversion modules
- Enhanced documentation and testing infrastructure

## [1.1.1] - 2025-11-11

### Summary
Major cleanup by removing deprecated scripts and files, consolidating the codebase to use only the Python package structure.

### Changed
- **Version bump**: 1.1.0 → 1.1.1
- **Cleaned up dependencies**: Dependencies now managed exclusively through `setup.py`
- **Dynamic versioning**: CLI tools now use version from package `__version__` constant

### Removed
- `convert-all-to-pdf.py` - Replaced by `md_to_pdf.batch` module
- `convert-to-pdf.sh` - Replaced by Python-based approach with Playwright
- `html-to-pdf-with-links.py` - Integrated into `md_to_pdf.html2pdf` module
- `md-to-pdf` - Replaced by `md2pdf` CLI command
- `md2html-pro.py` - Merged into `md_to_pdf.md2html` module
- `md2html-with-links.py` - Features merged into main module
- `requirements.txt` - Dependencies managed through `setup.py`

### Benefits
- Cleaner codebase with single source of truth
- Simplified maintenance and updates
- Better package structure following Python best practices
- Reduced code duplication

## [1.1.0] - 2025-10-21

### Added
- **Image Support**: Properly renders Markdown image syntax (`![alt](url)`) in generated PDFs
- **Image Styling**: Added responsive CSS styling for images with proper margins and borders

### Changed
- **Build System**: Updated `.gitignore` to exclude build artifacts
- **Version Consistency**: Aligned version numbers across all source files

### Technical Details
- Modified regex pattern to correctly identify and process image syntax
- Added HTML image tag generation with alt text support
- Added CSS styling for images with responsive sizing and proper page breaks

## [1.0.0] - 2025-10-21

### Added
- Initial release of MD to PDF Converter
- Professional PDF formatting with consistent styling
- Full support for Mermaid diagrams rendering
- Clickable table of contents and navigation
- Working hyperlinks and email addresses in generated PDFs
- Batch conversion capabilities for multiple files
- Custom styling and formatting options
- Multiple conversion workflows for different needs
- Compatible with Apple Silicon (M1/M2/M3)

### Command-Line Tools
- `md2pdf` - Convert Markdown to PDF in one step
- `md2html` - Convert Markdown to HTML
- `html2pdf` - Convert HTML to PDF
- `md2pdf-batch` - Batch convert multiple Markdown files

### Legacy Support
- `convert-to-pdf.sh` - Shell script using pandoc
- `convert-all-to-pdf.py` - Python batch converter
- `md2html-pro.py` - Advanced Markdown to HTML converter
- `md2html-with-links.py` - HTML converter optimized for links
- `html-to-pdf-with-links.py` - HTML to PDF converter preserving links

### Requirements
- Python 3.6+
- Playwright >= 1.40.0
- Markdown >= 3.5.0
- BeautifulSoup4 >= 4.12.0
- Chromium browser (installed via Playwright)

### Documentation
- Comprehensive README.md with installation, usage examples, workflows, troubleshooting, and best practices
- MIT License
- Based on [md-to-pdf](https://github.com/crarau/md-to-pdf) and enhanced using IBM Bob

---

## Migration Guide

### Upgrading to 1.2.0

The orientation feature is fully backward compatible. No changes are required to existing scripts or workflows.

**New capabilities:**
```bash
# Old way (still works, defaults to portrait)
md2pdf document.md

# New way with landscape orientation
md2pdf document.md -l

# Batch processing with orientation
md2pdf-batch docs/ --landscape
```

**Benefits:**
- Wide tables and diagrams now have 48% more horizontal space in landscape mode
- Automatic content width optimization
- Better rendering for complex Mermaid diagrams
- No breaking changes to existing functionality

### Upgrading to 1.1.1

Version 1.1.1 removed legacy scripts in favor of the unified Python package. If you were using legacy scripts:

**Migration:**
- Replace `convert-to-pdf.sh` → `md2pdf`
- Replace `convert-all-to-pdf.py` → `md2pdf-batch`
- Replace `md2html-pro.py` → `md2html`
- Replace `html-to-pdf-with-links.py` → `html2pdf`

All functionality is preserved in the new commands with improved features.

---

## Links

- [Repository](https://github.ibm.com/technology-garage-dach/md-to-pdf)
- [Implementation Plan](IMPLEMENTATION_PLAN_ORIENTATION.md)
- [Deployment Summary](ORIENTATION_FEATURE_DEPLOYMENT_SUMMARY.md)
- [Future Ideas](FUTURE_IDEAS.md)
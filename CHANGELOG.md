# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.2] - 2026-07-27

### Fixed
- URLs inside inline code spans (backticks) are no longer auto-linked, fixing code blocks not closing visually in PDF output

## [1.6.1] - 2026-07-25

### Changed
- Updated README installation section: wheel install recommended, removed manual `playwright install chromium` step
- Clarified auto-install behavior for Chromium on first launch

## [1.6.0] - 2026-07-23

### Added
- **Blockquote support**: Lines starting with `> ` are converted to HTML `<blockquote>` elements with left-border styling
- **Nested list support**: Stack-based parser handles arbitrarily nested unordered and ordered lists
- **Task list support**: Items with `- [ ]` and `- [x]` render as disabled checkboxes
- **Strikethrough support**: `~~text~~` syntax renders as `<s>` HTML elements
- **Auto-install Chromium**: On first launch, missing Chromium binary is detected and installed automatically via `playwright install chromium` — no manual setup required

### Changed
- Rewrote list parsing in [`convert_lists()`](md_to_pdf/md2html.py) to use a stack-based approach for proper nesting
- Added CSS for task list items (hidden bullet, checkbox alignment)

### Technical Details
- Modified files: [`md2html.py`](md_to_pdf/md2html.py), [`html2pdf.py`](md_to_pdf/html2pdf.py)

## [1.5.0] - 2026-01-27

### Added
- **Image validation** with warning and strict modes
  - New [`ImageValidator`](md_to_pdf/image_validator.py:44) class for comprehensive image reference validation
  - Added `--strict-images` flag to `md2pdf` and `md2pdf-batch` commands
  - **Warning mode (default)**: Scans markdown for image references and issues warnings to stderr for missing images while continuing PDF generation
  - **Strict mode**: Aborts PDF generation if any referenced images are missing, exits with non-zero status code
  - Support for both inline (`![alt](path)`) and reference-style (`![alt][ref]`) markdown images
  - Automatic URL detection and skipping (http/https images not validated)
  - Validation caching for performance optimization
  - Detailed error reporting with file names and line numbers
- **Batch processing support** for image validation
  - Full integration in both single-file and batch processing modes
  - Consolidated validation results across multiple files
  - Per-file and aggregate error reporting

### Changed
- Updated [`convert_md_to_pdf()`](md_to_pdf/cli.py:19) to accept `strict_images` parameter
- Updated [`batch_convert()`](md_to_pdf/batch.py:126) to support image validation in batch operations
- Enhanced CLI with `--strict-images` argument for both single and batch commands

### Technical Details
- New file: [`md_to_pdf/image_validator.py`](md_to_pdf/image_validator.py:1) - Image validation module (363 lines)
- Modified files: [`cli.py`](md_to_pdf/cli.py:1), [`batch.py`](md_to_pdf/batch.py:1), [`README.md`](README.md:1)
- Uses dataclasses for clean result handling (`ImageReference`, `ValidationResult`)
- Regex-based image extraction with proper path resolution
- Filesystem caching to avoid repeated validation checks
- Maintained backward compatibility - validation is non-breaking in warning mode

### Documentation
- Added comprehensive "Image Validation" section to README.md (100+ lines)
- Usage examples for both warning and strict modes
- CI/CD pipeline integration guidance
- Batch processing examples with validation
- Detailed output examples for both modes

### Use Cases
- **Development workflow**: Warning mode helps identify broken image references during iterative work
- **CI/CD pipelines**: Strict mode ensures production builds have all required images before deployment
- **Batch processing**: Validates all files before starting PDF generation to catch issues early
- **Quality assurance**: Prevents broken image references in final PDFs

## [1.4.0] - 2025-12-15

### Added
- **Auto-generated table of contents** with customizable options
  - Added `--toc` flag to enable automatic TOC generation
  - Added `--toc-depth` option to control heading levels (1-6, default: 3)
  - Added `--toc-title` option for customizable TOC title (default: "Table of Contents")
  - Added `--toc-position` option with three modes:
    - `after_title` (default): Places TOC after first H1 heading
    - `top`: Places TOC at document beginning
    - `custom`: Places TOC at `{{TOC}}` marker location
  - Added `--toc-include-first` flag to optionally include first H1 in TOC
- **Internationalization support** for TOC titles
  - Support for any language (German, French, Spanish, Japanese, Chinese, Arabic, etc.)
  - HTML escaping for security (XSS prevention)
- **Professional TOC styling** with CSS
  - Properly nested lists based on heading hierarchy
  - Clickable links to all sections
  - Print-optimized design
  - Responsive indentation for different heading levels

### Changed
- Updated [`generate_toc()`](md_to_pdf/md2html.py:140) to create nested HTML lists from heading structure
- Updated [`insert_toc()`](md_to_pdf/md2html.py:216) to handle three positioning modes
- Updated [`convert_md_to_pdf()`](md_to_pdf/cli.py:19) to accept TOC parameters
- Updated [`batch_convert()`](md_to_pdf/batch.py:126) to support TOC in batch operations
- Modified heading tracking from dict to list of tuples for proper document order
- Enhanced [`create_html_document()`](md_to_pdf/md2html.py:727) with TOC CSS styling

### Fixed
- **HTML output location**: HTML files now correctly placed in output directory when using `-o` flag with `--keep-html`
  - Previously, HTML files were created in source directory instead of output directory
  - Fixed by determining HTML file path from PDF path instead of markdown path

### Technical Details
- Modified files: [`cli.py`](md_to_pdf/cli.py:1), [`md2html.py`](md_to_pdf/md2html.py:1), [`batch.py`](md_to_pdf/batch.py:1)
- TOC generation uses proper HTML escaping for security
- Heading tracking changed from `dict` to `list` of tuples `(slug, level, text)`
- All TOC features are opt-in via `--toc` flag
- Maintained backward compatibility with existing workflows

### Documentation
- Updated README.md with comprehensive TOC documentation
- Added usage examples for all TOC options
- Added internationalization examples in 10+ languages
- Added TOC positioning guide with examples

## [1.3.1] - 2025-12-02

### Changed
- **Code quality improvements**: Refactored codebase for better maintainability and type safety
  - Improved batch module structure with extracted helper functions
  - Enhanced type safety in batch processing operations
  - Extracted browser operations for better code organization
  - Added validation constants for improved code clarity
- **Bug fixes**: Fixed Mermaid diagram rendering issues

### Technical Details
- Modified files: [`batch.py`](md_to_pdf/batch.py:1), [`cli.py`](md_to_pdf/cli.py:1), [`html2pdf.py`](md_to_pdf/html2pdf.py:1)
- Refactored `main()` function in batch module for better structure
- Extracted helper functions from `convert()` for improved readability
- No breaking changes or new features

### Distribution
- Binary wheel: `dist/md_to_pdf_1.3.1-py3-none-any.whl`

## [1.3.0] - 2025-12-01

### Added
- **Custom font presets** for professional typography
  - Added `--font-preset` option to `md2pdf` and `md2pdf-batch` commands
  - **IBM preset** (new default): IBM Plex Sans (Light/Bold) + IBM Plex Mono (Regular)
  - **System preset**: Platform-native fonts (previous default behavior)
  - **Classic preset**: Georgia serif fonts for traditional documents
  - **Modern preset**: Roboto sans-serif fonts for contemporary look
- **Google Fonts integration** for IBM and Modern presets
  - Automatic font loading from Google Fonts CDN
  - Proper font weight specifications (300, 400, 700)
  - Fallback fonts for offline/compatibility scenarios
- **Font configuration module** ([`md_to_pdf/fonts.py`](md_to_pdf/fonts.py:1))
  - Centralized font preset definitions
  - Google Fonts URL generation with proper encoding
  - Font CSS configuration helpers

### Changed
- **Default fonts**: Changed from system fonts to IBM Plex fonts for modern, professional appearance
- Updated [`convert_md_to_pdf()`](md_to_pdf/cli.py:18) to accept `font_preset` parameter
- Updated [`create_html_document()`](md_to_pdf/md2html.py:221) to generate font-aware CSS
- Updated [`convert_file()`](md_to_pdf/md2html.py:582) to support font preset selection
- Updated [`batch_convert()`](md_to_pdf/batch.py:46) to apply fonts consistently across batch operations
- Enhanced HTML templates with Google Fonts `<link>` tags when needed
- Updated CLI help text and examples to showcase font preset options

### Fixed
- **Special character handling in filenames**: Fixed `ERR_FILE_NOT_FOUND` errors for files with `#`, spaces, and other special characters
  - Changed file URL construction in [`html_to_pdf_with_links()`](md_to_pdf/html2pdf.py:11) to use `Path.as_uri()` for proper URL encoding
  - Files like `ENHANCEMENT #5 ORIENTATION.md` now convert successfully

### Technical Details
- New file: [`md_to_pdf/fonts.py`](md_to_pdf/fonts.py:1) - Font configuration and management
- Modified files: [`cli.py`](md_to_pdf/cli.py:1), [`md2html.py`](md_to_pdf/md2html.py:1), [`html2pdf.py`](md_to_pdf/html2pdf.py:1), [`batch.py`](md_to_pdf/batch.py:1)
- Font presets use CSS `font-family` and `font-weight` properties
- Google Fonts loaded with `&display=swap` for optimal performance
- Maintained backward compatibility via `system` preset

### Documentation
- Updated README.md with comprehensive font preset documentation
- Added font preset comparison table
- Updated all usage examples to show font options
- Added font loading information and best practices

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
- **Future Roadmap**: Added `FUTURE_IDEAS.md` with 140 lines documenting possible features and enhancements for future releases
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

### Upgrading to 1.6.0

Version 1.6.0 adds new Markdown rendering features and removes the manual Chromium install step.

**What's new:**
- Blockquotes, nested lists, task lists (`- [ ]` / `- [x]`), and strikethrough (`~~text~~`)
- Chromium is installed automatically on first run — no `playwright install chromium` needed

**Migration:**
No changes required. All new features are handled transparently during conversion.

### Upgrading to 1.5.0

Version 1.5.0 introduces image validation to catch missing image references before PDF generation. The feature is fully backward compatible and non-breaking.

**What's new:**
- Image validation with warning mode (default) and strict mode
- `--strict-images` flag for CI/CD pipelines
- Support for inline and reference-style markdown images
- Detailed error reporting with file and line numbers

**Usage:**
```bash
# Default behavior - shows warnings but continues
md2pdf document.md

# Strict mode - aborts on missing images (ideal for CI/CD)
md2pdf document.md --strict-images

# Batch processing with strict validation
md2pdf-batch docs/ --strict-images -o output/
```

**Benefits:**
- Catch broken image references early in development
- Prevent PDFs with missing images in production
- Detailed error messages with exact file locations
- Performance-optimized with validation caching
- No breaking changes - warning mode is default

**Migration:**
No changes required. Existing scripts continue to work as before. The new validation runs automatically in warning mode, providing helpful feedback without breaking your workflow.

### Upgrading to 1.4.0

Version 1.4.0 introduces automatic table of contents generation. The feature is fully backward compatible and opt-in.

**What's new:**
- Auto-generated table of contents with `--toc` flag
- Customizable TOC title for internationalization
- Three positioning modes (top, after_title, custom)
- Configurable depth (1-6 heading levels)

**Usage:**
```bash
# Enable TOC with defaults (after first H1, depth 3)
md2pdf document.md --toc

# Customize TOC title for different languages
md2pdf document.md --toc --toc-title "Inhaltsverzeichnis"  # German
md2pdf document.md --toc --toc-title "目次"                 # Japanese

# Control TOC depth
md2pdf document.md --toc --toc-depth 2  # Only H1 and H2

# Position TOC at top of document
md2pdf document.md --toc --toc-position top

# Use custom position with {{TOC}} marker
md2pdf document.md --toc --toc-position custom

# Include first H1 in TOC
md2pdf document.md --toc --toc-include-first

# Batch conversion with TOC
md2pdf-batch docs/ --toc --toc-title "Contents" -o output/
```

**Benefits:**
- Automatic navigation for long documents
- Clickable links to all sections
- Professional styling that prints well
- Support for any language
- No breaking changes - feature is opt-in

**Bug fix:**
- HTML files now correctly placed in output directory when using `-o` with `--keep-html`

### Upgrading to 1.3.0

Version 1.3.0 introduces custom font presets with IBM Plex fonts as the new default. The change is backward compatible.

**What changed:**
- Default fonts changed from system fonts to IBM Plex fonts
- New `--font-preset` option available for font selection

**Migration:**
```bash
# Old behavior (system fonts) - now requires explicit flag
md2pdf document.md --font-preset system

# New default (IBM Plex fonts) - no changes needed
md2pdf document.md

# New font options
md2pdf document.md --font-preset classic   # Georgia
md2pdf document.md --font-preset modern    # Roboto
```

**Benefits:**
- Professional IBM Plex typography by default
- Consistent appearance across platforms
- Four preset options for different document styles
- Google Fonts integration for IBM and Modern presets
- No breaking changes - system fonts still available

**Note:** IBM and Modern presets require internet connection on first use to download fonts from Google Fonts. Fonts are cached by the browser afterward.

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
# MD to PDF Converter

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/IBM/md-to-pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/IBM/md-to-pdf/actions/workflows/ci.yml)
[![GitHub Release](https://img.shields.io/github/v/release/IBM/md-to-pdf)](https://github.com/IBM/md-to-pdf/releases/latest)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://github.com/IBM/md-to-pdf/actions/workflows/ci.yml)

Professional Markdown to PDF converter with support for Mermaid diagrams, clickable links, page orientation control, and beautiful formatting.

## Features

- ✅ Convert Markdown to PDF with professional formatting
- ✅ **Image validation** with warning and strict modes
- ✅ **Auto-generated table of contents** with customizable depth, title, and positioning
- ✅ **Custom font presets** (IBM Plex, system fonts, Georgia, Roboto)
- ✅ **Page orientation control** (portrait/landscape for A4 pages)
- ✅ Mermaid diagrams with auto-scaling
- ✅ Clickable links and navigation
- ✅ Batch conversion with parallel processing
- ✅ Custom styling and formatting

## Quick Start

```bash
# Install
pip install .

# Convert a document (IBM Plex fonts, portrait)
md2pdf document.md

# Generate table of contents
md2pdf document.md --toc

# Use different fonts
md2pdf document.md --font-preset modern

# Landscape orientation
md2pdf document.md -l

# Combine features
md2pdf document.md --toc --font-preset modern -l

# Validate images (strict mode - abort on missing images)
md2pdf document.md --strict-images

# Batch convert with TOC and custom fonts
md2pdf-batch docs/ --toc --font-preset classic -o output/
```

## Installation

### From Wheel (recommended)

Download the latest wheel from the [GitHub Releases page](https://github.com/IBM/md-to-pdf/releases/latest) and install it:

```bash
pip install md_to_pdf-*.whl
```

To upgrade an existing installation:

```bash
pip install md_to_pdf-*.whl --force-reinstall
```

Chromium is installed automatically on first run — no extra setup needed.

### From Source

```bash
git clone https://github.com/IBM/md-to-pdf.git
cd md-to-pdf
pip install .
```

## Commands

### `md2pdf` - Single File Conversion

Convert Markdown files to PDF with one command.

```bash
# Basic usage (IBM Plex fonts, portrait)
md2pdf document.md

# Choose font preset
md2pdf document.md --font-preset system    # System fonts
md2pdf document.md --font-preset classic   # Georgia
md2pdf document.md --font-preset modern    # Roboto

# Landscape orientation
md2pdf document.md -l

# Combine options
md2pdf document.md --font-preset modern -l -o output.pdf

# Validate images strictly (abort on missing images)
md2pdf document.md --strict-images

# Keep HTML file
md2pdf document.md --keep-html
```

### `md2pdf-batch` - Batch Conversion

Convert multiple files at once with parallel processing.

```bash
# Convert directory (IBM Plex fonts)
md2pdf-batch docs/

# Use different fonts
md2pdf-batch docs/ --font-preset classic

# Recursive with landscape
md2pdf-batch docs/ -r -l

# Strict image validation
md2pdf-batch docs/ --strict-images

# Combine options
md2pdf-batch docs/ --font-preset modern -r -o output/
```

### `md2html` - Markdown to HTML

Convert Markdown to HTML for inspection or modification.

```bash
md2html document.md                        # default output: document.html
md2html document.md -o output.html         # custom output file
md2html document.md -l                     # landscape orientation
md2html document.md --font-preset modern   # custom font preset
md2html document.md --toc                  # generate table of contents
md2html document.md --strict-images        # abort on missing images
```

| Option | Description |
|--------|-------------|
| `-o`, `--output` | Output HTML file path |
| `-l`, `--landscape` | Landscape orientation (default: portrait) |
| `-p`, `--portrait` | Portrait orientation (explicit) |
| `--font-preset` | Font preset: `ibm` (default), `system`, `classic`, `modern` |
| `--toc` | Generate table of contents |
| `--toc-depth` | Max heading level in TOC (1–6, default: 3) |
| `--toc-title` | TOC heading text (default: `Table of Contents`) |
| `--toc-position` | TOC placement: `after_title` (default), `top`, `custom` |
| `--toc-include-first` | Include first H1 in TOC (default: excluded as document title) |
| `--strict-images` | Abort if referenced images are missing |

### `html2pdf` - HTML to PDF

Convert HTML files to PDF.

```bash
html2pdf document.html                     # default output: document.pdf
html2pdf document.html -o output.pdf       # custom output file
html2pdf document.html -l                  # landscape orientation
```

| Option | Description |
|--------|-------------|
| `-o`, `--output` | Output PDF file path |
| `-l`, `--landscape` | Landscape orientation (default: portrait) |
| `-p`, `--portrait` | Portrait orientation (explicit) |

## Page Orientation

Choose between portrait and landscape orientation for optimal content display.

### Portrait (Default)
- **Size**: 210mm × 297mm
- **Content width**: 180mm
- **Best for**: Text-heavy documents, reports, articles

### Landscape
- **Size**: 297mm × 210mm  
- **Content width**: 267mm (48% more space)
- **Best for**: Wide tables, large diagrams, code blocks

### Usage

```bash
# Portrait (default)
md2pdf document.md

# Landscape
md2pdf document.md -l
md2pdf document.md --landscape

# Batch landscape
md2pdf-batch diagrams/ -l -o output/
```

### When to Use Landscape

- Wide tables with many columns
- Large Mermaid diagrams (flowcharts, ER diagrams, sequence diagrams)
- Code blocks with long lines
- Wide images or screenshots
- Presentation-style content

## Font Presets

Choose from professional font combinations optimized for different document types.

### Available Presets

| Preset | Title Font | Body Font | Code Font | Best For |
|--------|-----------|-----------|-----------|----------|
| **ibm** (default) | IBM Plex Sans Bold | IBM Plex Sans Light | IBM Plex Mono Regular | Modern technical docs, IBM branding |
| **system** | System fonts | System fonts | Monospace | Maximum compatibility, fast rendering |
| **classic** | Georgia Bold | Georgia Regular | Courier New | Traditional documents, academic papers |
| **modern** | Roboto Bold | Roboto Light | Roboto Mono Regular | Clean contemporary look, web-style docs |

### Usage

```bash
# Default IBM Plex fonts
md2pdf document.md

# System fonts (old behavior)
md2pdf document.md --font-preset system

# Classic serif fonts
md2pdf document.md --font-preset classic

# Modern sans-serif
md2pdf document.md --font-preset modern

# Batch with custom fonts
md2pdf-batch docs/ --font-preset classic -r
```

### Font Loading

- **IBM & Modern presets**: Fonts loaded from Google Fonts (requires internet on first use)
- **System & Classic presets**: Use locally installed fonts (no internet required)
- All fonts include fallbacks for offline/compatibility

## Table of Contents

Generate an automatic table of contents with customizable depth, title, and positioning.

### Basic Usage

```bash
# Generate TOC with default settings
md2pdf document.md --toc

# Custom depth (default: 3, shows H1-H3)
md2pdf document.md --toc --toc-depth 2

# Custom title (for internationalization)
md2pdf document.md --toc --toc-title "Contents"
md2pdf document.md --toc --toc-title "Inhaltsverzeichnis"  # German
md2pdf document.md --toc --toc-title "目次"                 # Japanese
md2pdf document.md --toc --toc-title "Contenido"           # Spanish

# Position at top (before document title)
md2pdf document.md --toc --toc-position top

# Include first H1 in TOC (by default it's excluded as document title)
md2pdf document.md --toc --toc-include-first
```

### TOC Positioning

Three positioning options are available:

| Position | Description | Use Case |
|----------|-------------|----------|
| **after_title** (default) | After first H1 heading | Standard documents with title |
| **top** | At the very beginning | Documents without H1 title |
| **custom** | At `{{TOC}}` marker | Manual placement control |

#### Custom Position Example

Add `{{TOC}}` marker in your Markdown where you want the TOC:

```markdown
# My Document

Introduction paragraph...

{{TOC}}

## Chapter 1
Content...
```

Then convert with:

```bash
md2pdf document.md --toc --toc-position custom
```

### Batch Conversion with TOC

Apply TOC settings to all files in batch conversion:

```bash
# Basic batch with TOC
md2pdf-batch docs/ --toc

# Custom settings for all files
md2pdf-batch docs/ --toc --toc-depth 2 --toc-title "Contents"

# Recursive with German TOC
md2pdf-batch docs/ -r --toc --toc-title "Inhaltsverzeichnis"

# Combine with other options
md2pdf-batch docs/ --toc --font-preset modern -l -o output/
```

### TOC Features

- **Automatic nesting** - Properly nested lists based on heading levels
- **Clickable links** - All TOC entries link to their sections
- **Customizable depth** - Control which heading levels appear (1-6)
- **Skip first H1** - By default, first H1 is treated as document title
- **HTML escaping** - Safe handling of special characters in titles
- **Professional styling** - Clean, readable design that prints well

### Internationalization Examples

The `--toc-title` flag allows you to match the TOC title to your document's language:

```bash
# English (default)
md2pdf document.md --toc

# German
md2pdf document.md --toc --toc-title "Inhaltsverzeichnis"

# French
md2pdf document.md --toc --toc-title "Table des matières"

# Spanish
md2pdf document.md --toc --toc-title "Índice"

# Italian
md2pdf document.md --toc --toc-title "Indice"

# Portuguese
md2pdf document.md --toc --toc-title "Índice"

# Japanese
md2pdf document.md --toc --toc-title "目次"

# Chinese (Simplified)
md2pdf document.md --toc --toc-title "目录"

# Korean
md2pdf document.md --toc --toc-title "목차"

# Russian
md2pdf document.md --toc --toc-title "Содержание"

# Arabic
md2pdf document.md --toc --toc-title "جدول المحتويات"
```

## Image Validation

Validate image references in markdown files before PDF generation to catch missing images early.

### Validation Modes

#### Warning Mode (Default)
- Scans markdown for image references
- Issues warnings to stderr for missing images
- Continues with PDF generation
- Useful for development and iterative work

```bash
# Default behavior - shows warnings but continues
md2pdf document.md
```

**Example output:**
```
Warning: Image not found: ./images/diagram.png (referenced in document.md:15)
Warning: Image not found: ../assets/logo.jpg (referenced in document.md:42)
Successfully generated: document.pdf
```

#### Strict Mode
- Performs the same validation as warning mode
- Aborts PDF generation if any images are missing
- Exits with non-zero status code
- Ideal for CI/CD pipelines and production builds

```bash
# Strict mode - aborts on missing images
md2pdf document.md --strict-images
```

**Example output:**
```
Error: Image not found: ./images/diagram.png (referenced in document.md:15)
Error: Image not found: ../assets/logo.jpg (referenced in document.md:42)

Error: Image validation failed
  - Total images checked: 5
  - Missing images: 2
  - Files affected: 1
PDF generation aborted due to missing images
```

### Batch Processing with Validation

Image validation works seamlessly with batch processing:

```bash
# Warning mode (default) - processes all files, shows warnings
md2pdf-batch docs/ -r

# Strict mode - validates all files before processing
md2pdf-batch docs/ -r --strict-images
```

In batch mode with strict validation:
- All files are validated before any PDF generation starts
- If any images are missing, the entire batch is aborted
- Provides a complete list of all missing images across all files

### Supported Image Formats

The validator checks for:
- **Inline images**: `![alt text](path/to/image.png)`
- **Reference-style images**: `![alt text][ref]` with `[ref]: path/to/image.png`
- **Relative paths**: `./images/`, `../assets/`
- **Absolute paths**: `/full/path/to/image.png`

**Note:** URL references (http/https) are skipped and not validated.

### Use Cases

#### Development Workflow
Use warning mode during development to see issues without blocking:
```bash
md2pdf document.md
```

#### CI/CD Pipeline
Use strict mode in automated builds to ensure quality:
```bash
md2pdf document.md --strict-images || exit 1
```

#### Pre-Release Validation
Validate all documentation before release:
```bash
md2pdf-batch docs/ -r --strict-images
```

### Benefits

1. **Early Detection** - Find missing images before PDF generation
2. **Quality Assurance** - Prevent distribution of PDFs with broken images
3. **Batch Efficiency** - Validate all files before processing
4. **CI/CD Integration** - Strict mode enables automated validation
5. **Clear Feedback** - Detailed error messages with file names and line numbers

## Two-Step Workflow

For HTML inspection or modification:

```bash
# Step 1: Generate HTML
md2html document.md

# Step 2: Convert to PDF
html2pdf document.html
```

This leads to the same result as:

```bash
md2pdf document.md --keep-html
```

## Troubleshooting

### Playwright / Chromium Error

Chromium is installed automatically on first run. If you still see errors, install it manually:

```bash
playwright install chromium
```

### Mermaid Diagrams Not Rendering

Ensure you're using the `md2pdf` command, which handles Mermaid automatically. Verify your Mermaid syntax is correct.

### Links Not Clickable

All commands preserve links by default. If links aren't working, ensure you're using the latest version.

## Requirements

**Automatically Installed:**
- Python 3.10+
- playwright >= 1.40.0
- markdown >= 3.5.0
- beautifulsoup4 >= 4.12.0
- Chromium browser (via Playwright)

## Tips & Best Practices

1. **Choose the right font preset** - IBM for modern tech docs, Classic for traditional documents, System for maximum compatibility
2. **Use portrait for text-heavy documents** - Better readability for standard content
3. **Use landscape for wide content** - Tables, diagrams, and code benefit from extra width
4. **Batch processing** - Use `md2pdf-batch` for multiple files with parallel processing
5. **Two-step conversion** - Use `md2html` then `html2pdf` when you need to inspect HTML
6. **Mermaid diagrams** - Automatically scale to use available width
7. **Large documents** - Consider splitting into chapters for easier navigation

## File Formats

**Input:**
- `.md` - Markdown files
- `.html` - HTML files

**Output:**
- `.pdf` - PDF with formatting, links, and diagrams

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

Based on [md-to-pdf](https://github.com/crarau/md-to-pdf) (MIT). Enhanced and extended using [IBM Bob](https://bob.ibm.com/).

## Contributing

Submit issues and pull requests via [GitHub](https://github.com/IBM/md-to-pdf/issues).
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

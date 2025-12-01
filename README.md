# MD to PDF Converter

Professional Markdown to PDF converter with support for Mermaid diagrams, clickable links, page orientation control, and beautiful formatting.

## Features

- ✅ Convert Markdown to PDF with professional formatting
- ✅ **Custom font presets** (IBM Plex, system fonts, Georgia, Roboto)
- ✅ **Page orientation control** (portrait/landscape for A4 pages)
- ✅ Mermaid diagrams with auto-scaling
- ✅ Clickable table of contents and hyperlinks
- ✅ Batch conversion with parallel processing
- ✅ Custom styling and formatting

## Quick Start

```bash
# Install
pip install .
playwright install chromium

# Convert a document (IBM Plex fonts, portrait)
md2pdf document.md

# Use different fonts
md2pdf document.md --font-preset modern

# Landscape orientation
md2pdf document.md -l

# Batch convert with custom fonts
md2pdf-batch docs/ --font-preset classic -o output/
```

## Installation

### From Source

```bash
git clone https://github.ibm.com/technology-garage-dach/md-to-pdf.git
cd md-to-pdf
pip install .
playwright install chromium
```

### From Wheel

```bash
pip wheel . --no-deps
pip install md_to_pdf-1.3.0-py3-none-any.whl
playwright install chromium
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

# Combine options
md2pdf-batch docs/ --font-preset modern -r -o output/
```

### `md2html` - Markdown to HTML

Convert Markdown to HTML for inspection or modification.

```bash
md2html document.md
md2html document.md output.html
```

### `html2pdf` - HTML to PDF

Convert HTML files to PDF.

```bash
html2pdf document.html
html2pdf document.html output.pdf
```

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

### Playwright Error

```bash
playwright install chromium
```

### Mermaid Diagrams Not Rendering

Ensure you're using the `md2pdf` command, which handles Mermaid automatically. Verify your Mermaid syntax is correct.

### Links Not Clickable

All commands preserve links by default. If links aren't working, ensure you're using the latest version.

## Requirements

**Automatically Installed:**
- Python 3.6+
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

MIT

Based on [md-to-pdf](https://github.com/crarau/md-to-pdf). Enhanced using [IBM Bob](https://www.ibm.com/products/bob).

## Contributing

Submit issues and enhancement requests via GitHub.

# MD to PDF Converter

Professional Markdown to PDF converter with support for Mermaid diagrams, clickable links, page orientation control, and beautiful formatting.

## Features

- ✅ Convert Markdown to PDF with professional formatting
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

# Convert a document
md2pdf document.md

# Convert with landscape orientation
md2pdf document.md -l

# Batch convert
md2pdf-batch docs/ -o output/
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
pip install md_to_pdf-1.2.0-py3-none-any.whl
playwright install chromium
```

## Commands

### `md2pdf` - Single File Conversion

Convert Markdown files to PDF with one command.

```bash
# Basic usage (portrait)
md2pdf document.md

# Landscape orientation
md2pdf document.md -l

# Custom output
md2pdf document.md -o output.pdf

# Keep HTML file
md2pdf document.md --keep-html
```

### `md2pdf-batch` - Batch Conversion

Convert multiple files at once with parallel processing.

```bash
# Convert directory
md2pdf-batch docs/

# Recursive with landscape
md2pdf-batch docs/ -r -l

# Custom output directory
md2pdf-batch docs/ -o output/
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

1. **Use portrait for text-heavy documents** - Better readability for standard content
2. **Use landscape for wide content** - Tables, diagrams, and code benefit from extra width
3. **Batch processing** - Use `md2pdf-batch` for multiple files with parallel processing
4. **Two-step conversion** - Use `md2html` then `html2pdf` when you need to inspect HTML
5. **Mermaid diagrams** - Automatically scale to use available width
6. **Large documents** - Consider splitting into chapters for easier navigation

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

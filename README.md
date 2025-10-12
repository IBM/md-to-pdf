# MD to PDF Converter

Professional Markdown to PDF converter with support for Mermaid diagrams, clickable links, and beautiful formatting.

## Features

- ✅ Convert Markdown to PDF with professional formatting
- ✅ Support for Mermaid diagrams
- ✅ Clickable table of contents
- ✅ Working hyperlinks and email addresses
- ✅ Batch conversion of multiple files
- ✅ Custom styling and formatting options

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip3 install playwright markdown beautifulsoup4

# Install Playwright browsers
python3 -m playwright install chromium

# Optional: Install pandoc for direct MD→PDF (fallback)
# macOS: brew install pandoc
# Linux: apt-get install pandoc texlive-xelatex
```

### Basic Usage

**Convert a single Markdown file:**

```bash
./convert-to-pdf.sh your-document.md
```

**Batch convert all Markdown files in a directory:**

```bash
python3 convert-all-to-pdf.py /path/to/markdown/files
```

## Tools Included

### 1. `convert-to-pdf.sh`

Generic shell script using pandoc for direct Markdown to PDF conversion. Works with any markdown file.

**Features:**
- Table of contents generation
- Nice formatting (11pt, 1-inch margins)
- Clickable links
- Professional styling
- Accepts any markdown file as argument
- Creates PDF in same directory as input file

**Usage:**
```bash
# Convert a file in current directory
./convert-to-pdf.sh document.md

# Convert a file in another directory
./convert-to-pdf.sh /path/to/document.md

# Convert a file using relative path
./convert-to-pdf.sh ../other-folder/notes.md
```

**Output:**
- Creates `document.pdf` in the same directory as the input markdown file

**Customization:**
Edit the script to change:
- Font size (`-V fontsize=11pt`)
- Margins (`-V geometry:margin=1in`)
- Document class (`-V documentclass=report`)

---

### 2. `convert-all-to-pdf.py`

Batch converter for multiple Markdown files with Mermaid diagram support.

**Features:**
- Converts all `.md` files in a directory
- Supports Mermaid diagrams
- Progress reporting
- Error handling with summary

**Usage:**
```bash
# Convert all MD files in current directory
python3 convert-all-to-pdf.py .

# Convert files in specific directory
python3 convert-all-to-pdf.py /path/to/markdown/files
```

**Process:**
1. Finds all `.md` files in directory
2. Converts each to HTML (with Mermaid rendering)
3. Generates PDF from HTML
4. Reports success/failure for each file

---

### 3. `md2html-pro.py`

Advanced Markdown to HTML converter with Mermaid support.

**Features:**
- Full Markdown syntax support
- Mermaid diagram rendering
- Code syntax highlighting
- Table support
- Custom CSS styling

**Usage:**
```bash
python3 md2html-pro.py document.md
```

**Output:** Creates `document.html` in the same directory

---

### 4. `md2html-with-links.py`

HTML converter optimized for preserving hyperlinks.

**Features:**
- Clickable internal anchor links
- Working table of contents
- External URL linking
- Email address linking

**Usage:**
```bash
python3 md2html-with-links.py document.md
```

---

### 5. `html-to-pdf-with-links.py`

HTML to PDF converter that preserves all hyperlinks.

**Features:**
- Clickable links in PDF
- Working table of contents navigation
- Professional formatting
- Print-friendly styling

**Usage:**
```bash
python3 html-to-pdf-with-links.py document.html
```

**Output:** Creates `document.pdf` with clickable links

---

## Workflows

### Workflow 1: Simple Conversion (Pandoc)

**Best for:** Quick conversions without Mermaid diagrams

```bash
# Convert any markdown file to PDF
./convert-to-pdf.sh my-document.md

# Works with files in other directories
./convert-to-pdf.sh /path/to/notes/meeting-notes.md

# Works with relative paths
./convert-to-pdf.sh ../docs/api-guide.md
```

**Pros:**
- Fast
- Good formatting
- Table of contents included
- Works with any file, anywhere

**Cons:**
- No Mermaid diagram support
- Requires pandoc + LaTeX

---

### Workflow 2: Mermaid-Enabled Conversion

**Best for:** Documents with Mermaid diagrams

```bash
# Step 1: Convert MD to HTML with Mermaid rendering
python3 md2html-pro.py my-document.md

# Step 2: Convert HTML to PDF
python3 html-to-pdf-with-links.py my-document.html
```

**Pros:**
- Mermaid diagrams render beautifully
- Clickable links preserved
- Full Markdown support

**Cons:**
- Two-step process
- Requires Playwright

---

### Workflow 3: Batch Conversion

**Best for:** Converting multiple documents at once

```bash
python3 convert-all-to-pdf.py /path/to/documents/
```

**Features:**
- Automatic MD→HTML→PDF pipeline
- Mermaid support
- Progress tracking
- Success/failure summary

---

## Advanced Usage

### Custom Styling

**For Pandoc conversions**, edit `convert-to-pdf.sh`:

```bash
pandoc "document.md" \
    -o "document.pdf" \
    -V fontsize=12pt \              # Change font size
    -V geometry:margin=0.75in \     # Adjust margins
    -V mainfont="Helvetica" \       # Change font
    --toc-depth=3                   # TOC depth
```

**For HTML conversions**, edit the CSS in `md2html-pro.py` or create a custom CSS file.

---

### Converting with Links

To ensure all links work in the final PDF:

```bash
# Use the "with-links" versions
python3 md2html-with-links.py document.md
python3 html-to-pdf-with-links.py document.html
```

This ensures:
- ✅ Table of contents links are clickable
- ✅ Internal anchors work (`#section-name`)
- ✅ External URLs open in browser
- ✅ Email addresses are clickable

---

## Troubleshooting

### "pandoc: command not found"

Install pandoc:

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc texlive-xelatex

# Windows
# Download from pandoc.org
```

---

### "playwright._impl._api_types.Error"

Install Playwright browsers:

```bash
python3 -m playwright install chromium
```

---

### Mermaid diagrams not rendering

1. Check that you're using `md2html-pro.py` (not basic markdown conversion)
2. Verify Mermaid syntax is correct
3. Ensure JavaScript is enabled (Playwright handles this automatically)

---

### PDF has no clickable links

Use the "with-links" versions:
- `md2html-with-links.py`
- `html-to-pdf-with-links.py`

---

## Examples

### Example 1: Technical Documentation

```bash
# Document with code blocks and diagrams
python3 md2html-pro.py api-documentation.md
python3 html-to-pdf-with-links.py api-documentation.html
```

### Example 2: Meeting Notes

```bash
# Simple document, no diagrams
./convert-to-pdf.sh meeting-notes-2025-10-07.md
```

### Example 3: Batch Process Reports

```bash
# Convert all reports in a directory
python3 convert-all-to-pdf.py ./reports/
```

---

## File Formats Supported

**Input:**
- `.md` - Markdown files
- `.html` - HTML files (for HTML→PDF conversion)

**Output:**
- `.pdf` - PDF with formatting, links, and diagrams

---

## Requirements

**Python Packages:**
- `playwright` - For HTML to PDF conversion
- `markdown` - For Markdown parsing
- `beautifulsoup4` - For HTML processing

**System Tools:**
- `pandoc` (optional) - For direct MD→PDF
- `xelatex` (optional) - For pandoc PDF generation

**Install all:**
```bash
pip3 install playwright markdown beautifulsoup4
python3 -m playwright install chromium

# Optional
brew install pandoc  # macOS
```

---

## Tips & Best Practices

1. **For quick docs without diagrams:** Use `convert-to-pdf.sh` (fastest)

2. **For docs with Mermaid diagrams:** Use the Python scripts

3. **For batch processing:** Use `convert-all-to-pdf.py`

4. **For maximum link preservation:** Use the "with-links" versions

5. **Custom styling:** Edit CSS in Python scripts or pandoc options in shell script

6. **Large documents:** Consider splitting into chapters for easier navigation

---

## License

MIT

---

## Contributing

Feel free to submit issues and enhancement requests!

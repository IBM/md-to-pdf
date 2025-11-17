# MD to PDF Converter

Professional Markdown to PDF converter with support for Mermaid diagrams, clickable links, page orientation control, and beautiful formatting.

## Installation

### Option 1: Install from Source

```bash
# Clone the repository
git clone https://github.ibm.com/technology-garage-dach/md-to-pdf.git
cd md-to-pdf

# Install the package
pip install .

# Install Playwright browsers
playwright install chromium
```

### Option 2: Install from Wheel

Please note: you can find the wheel files in the `dist` directory of this repository.

```bash
# Generate the wheel file
pip wheel . --no-deps

# Install the generated wheel file
pip install md_to_pdf-1.2.0-py3-none-any.whl

# Install Playwright browsers
playwright install chromium
```

## Command-Line Tools

After installation, the following commands will be available:

### 1. `md2pdf` - Convert Markdown to PDF

```bash
# Basic usage (portrait, default)
md2pdf document.md

# Specify output file
md2pdf document.md -o output.pdf

# Landscape orientation
md2pdf document.md -l
md2pdf document.md --landscape

# Explicit portrait orientation
md2pdf document.md -p
md2pdf document.md --portrait

# Landscape with custom output
md2pdf document.md -l -o wide-document.pdf

# Keep intermediate HTML file
md2pdf document.md --keep-html
```

### 2. `md2html` - Convert Markdown to HTML

```bash
# Basic usage
md2html document.md

# Specify output file
md2html document.md output.html
```

### 3. `html2pdf` - Convert HTML to PDF

```bash
# Basic usage
html2pdf document.html

# Specify output file
html2pdf document.html output.pdf
```

### 4. `md2pdf-batch` - Batch Convert Multiple Files

```bash
# Convert all Markdown files in a directory (portrait, default)
md2pdf-batch docs/

# Convert all files in landscape orientation
md2pdf-batch docs/ -l
md2pdf-batch docs/ --landscape

# Convert recursively
md2pdf-batch docs/ --recursive

# Convert recursively in landscape
md2pdf-batch docs/ -r -l

# Specify output directory
md2pdf-batch docs/ -o output/

# Output directory with landscape orientation
md2pdf-batch docs/ -o output/ -l

# Keep intermediate HTML files
md2pdf-batch docs/ --keep-html
```

## Features

- ✅ Convert Markdown to PDF with professional formatting
- ✅ **Page orientation control** (portrait/landscape for A4 pages)
- ✅ Support for Mermaid diagrams with auto-scaling
- ✅ Clickable table of contents
- ✅ Working hyperlinks and email addresses
- ✅ Batch conversion of multiple files
- ✅ Parallel processing for faster batch conversions
- ✅ Custom styling and formatting options
## Page Orientation

The converter supports both **portrait** (default) and **landscape** orientations for A4 pages. This is particularly useful for documents with wide content such as tables, diagrams, or code blocks.

### Orientation Options

- **Portrait** (default): 210mm × 297mm (A4 standard)
  - Content width: 180mm (after 15mm margins)
  - Best for: Regular documents, text-heavy content, standard reports
  
- **Landscape**: 297mm × 210mm (A4 rotated)
  - Content width: 267mm (after 15mm margins)
  - Best for: Wide tables, large diagrams, code with long lines, presentations

### Usage Examples

#### Single File Conversion

```bash
# Portrait (default) - no flag needed
md2pdf document.md

# Landscape - use -l or --landscape flag
md2pdf document.md -l
md2pdf document.md --landscape

# Explicit portrait - use -p or --portrait flag
md2pdf document.md -p
md2pdf document.md --portrait

# Landscape with custom output name
md2pdf wide-table-document.md -l -o tables.pdf
```

#### Batch Conversion

```bash
# Convert all files in landscape
md2pdf-batch diagrams/ -l

# Recursive conversion in landscape
md2pdf-batch docs/ --recursive --landscape

# Batch with output directory and landscape
md2pdf-batch reports/ -o pdf-output/ -l
```

### When to Use Landscape Orientation

Consider using landscape orientation when your document contains:

- **Wide tables** with many columns
- **Large Mermaid diagrams** (flowcharts, ER diagrams, sequence diagrams)
- **Code blocks** with long lines that would wrap in portrait
- **Wide images** or screenshots
- **Presentation-style** content

### Automatic Content Optimization

The converter automatically optimizes content width based on orientation:

- **Portrait mode**: Content uses 180mm width (optimal for reading)
- **Landscape mode**: Content uses 267mm width (48% more horizontal space)
- **Mermaid diagrams**: Automatically detect and utilize full printable width when needed
- **Tables and code**: Benefit from increased horizontal space in landscape mode

### Backward Compatibility

Portrait orientation remains the default when no orientation flag is specified, ensuring backward compatibility with existing scripts and workflows.

- ✅ Automatic content width optimization based on orientation

## Legacy Scripts

The package also includes the original scripts for backward compatibility:

```bash
# Convert a single Markdown file using the shell script
./convert-to-pdf.sh your-document.md

# Batch convert all Markdown files in a directory
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

### Workflow 1: Simple Conversion (Recommended)

**Best for:** Most documents, including those with Mermaid diagrams

```bash
# Convert any markdown file to PDF
md2pdf my-document.md

# Specify output file
md2pdf my-document.md -o output.pdf

# Keep intermediate HTML file
md2pdf my-document.md --keep-html
```

**Pros:**
- Fast and simple
- Good formatting
- Mermaid diagrams support
- Clickable links preserved
- Works with any file, anywhere

---

### Workflow 2: Two-Step Conversion

**Best for:** When you need to inspect or modify the HTML before PDF generation

```bash
# Step 1: Convert MD to HTML with Mermaid rendering
md2html my-document.md

# Step 2: Convert HTML to PDF
html2pdf my-document.html
```

**Pros:**
- Allows HTML inspection/modification between steps
- Mermaid diagrams render beautifully
- Clickable links preserved
- Full Markdown support

---

### Workflow 3: Batch Conversion

**Best for:** Converting multiple documents at once

```bash
# Convert all Markdown files in a directory
md2pdf-batch docs/

# Convert recursively with output directory
md2pdf-batch docs/ --recursive -o output/
```

**Features:**
- Automatic MD→HTML→PDF pipeline
- Mermaid support
- Progress tracking
- Success/failure summary
- Parallel processing for faster conversion

---

### Workflow 4: Legacy Conversion (Pandoc)

**Best for:** Quick conversions using pandoc (if installed)

```bash
# Convert any markdown file to PDF using pandoc
./convert-to-pdf.sh my-document.md
```

**Pros:**
- Uses pandoc directly
- Good formatting
- Table of contents included

**Cons:**
- No Mermaid diagram support
- Requires pandoc + LaTeX

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
md2pdf api-documentation.md
```

### Example 2: Meeting Notes

```bash
# Simple document, no diagrams
md2pdf meeting-notes-2025-10-07.md
```

### Example 3: Batch Process Reports

```bash
# Convert all reports in a directory
md2pdf-batch ./reports/ --recursive
```

### Example 4: Custom Output Directory

```bash
# Convert all markdown files and save PDFs to a specific directory
md2pdf-batch ./docs/ -o ./generated-pdfs/
```

### Example 5: Wide Tables in Landscape

```bash
# Document with wide tables or data
md2pdf data-analysis.md -l
```

### Example 6: Mermaid Diagrams in Landscape

```bash
# Architecture diagrams that need more horizontal space
md2pdf system-architecture.md --landscape
```

### Example 7: Batch Convert Diagrams to Landscape

```bash
# Convert all diagram files in landscape orientation
md2pdf-batch ./diagrams/ -l -o ./pdf-diagrams/
```

### Example 8: Two-Step Process with HTML Inspection

```bash
# Convert to HTML first (with orientation)
md2html technical-spec.md

# Manually inspect or modify the HTML if needed
# Then convert to PDF
html2pdf technical-spec.html
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

### Package Dependencies (Automatically Installed)

**Python Packages:**
- `playwright` - For HTML to PDF conversion
- `markdown` - For Markdown parsing
- `beautifulsoup4` - For HTML processing

**Additional Requirements:**
- Chromium browser (installed via Playwright)

### Optional Tools

**System Tools:**
- `pandoc` (optional) - For direct MD→PDF using the legacy scripts
- `xelatex` (optional) - For pandoc PDF generation

**Install optional tools:**
```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc texlive-xelatex

# Windows
# Download from pandoc.org
```

---

## Tips & Best Practices

1. **For quick docs without diagrams:** Use `md2pdf` command (or legacy `convert-to-pdf.sh`)

2. **For docs with Mermaid diagrams:** Use `md2pdf` command (handles Mermaid diagrams automatically)

3. **For batch processing:** Use `md2pdf-batch` command

4. **For maximum link preservation:** All commands preserve links by default

5. **Choose the right orientation:**
   - Use **portrait** (default) for text-heavy documents and standard reports
   - Use **landscape** (`-l` flag) for wide tables, large diagrams, or code with long lines
   - Landscape provides 48% more horizontal space (267mm vs 180mm content width)

6. **Two-step conversion if needed:** Use `md2html` followed by `html2pdf` for manual control

7. **Custom styling:** Edit CSS in Python scripts or pandoc options in shell script

8. **Large documents:** Consider splitting into chapters for easier navigation

9. **Wide content optimization:** Mermaid diagrams automatically detect and use full printable width when needed

10. **Apple M1/M2/M3 compatibility:** The package is fully compatible with Apple Silicon

---

## License

MIT

This project is based on [md-to-pdf](https://github.com/crarau/md-to-pdf). It was cloned on October 14 2025. The original license is MIT. The code of the original project was modified and enhanced using [IBM Bob](https://www.ibm.com/products/bob). 

---

## Contributing

Feel free to submit issues and enhancement requests!

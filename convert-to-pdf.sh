#!/bin/bash

# Generic Markdown to PDF converter using pandoc with nice formatting
# Usage: ./convert-to-pdf.sh <markdown-file.md>

# Check if file argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <markdown-file.md>"
    echo ""
    echo "Examples:"
    echo "  $0 document.md"
    echo "  $0 /path/to/document.md"
    echo "  $0 ../other-folder/notes.md"
    exit 1
fi

INPUT_FILE="$1"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Error: File not found: $INPUT_FILE"
    exit 1
fi

# Check if input file is markdown
if [[ ! "$INPUT_FILE" =~ \.md$ ]]; then
    echo "❌ Error: File must have .md extension"
    exit 1
fi

# Get absolute path of input file
INPUT_FILE_ABS=$(realpath "$INPUT_FILE")

# Extract directory, filename, and base name
INPUT_DIR=$(dirname "$INPUT_FILE_ABS")
INPUT_FILENAME=$(basename "$INPUT_FILE_ABS")
INPUT_BASENAME="${INPUT_FILENAME%.md}"

# Output PDF will be in the same directory as input
OUTPUT_PDF="${INPUT_DIR}/${INPUT_BASENAME}.pdf"

echo "Converting Markdown to PDF..."
echo "Input:  $INPUT_FILE_ABS"
echo "Output: $OUTPUT_PDF"
echo ""

# Convert using pandoc with nice formatting options
pandoc "$INPUT_FILE_ABS" \
    -o "$OUTPUT_PDF" \
    --pdf-engine=xelatex \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    -V linkcolor=blue \
    -V urlcolor=blue \
    -V toccolor=black \
    --toc \
    --toc-depth=2 \
    -V documentclass=report \
    -V papersize=letter \
    -V colorlinks=true \
    2>/dev/null || {
    # Fallback to basic pandoc if xelatex not available
    echo "XeLaTeX not found, using basic pandoc conversion..."
    pandoc "$INPUT_FILE_ABS" \
        -o "$OUTPUT_PDF" \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --toc \
        -V documentclass=article
}

if [ -f "$OUTPUT_PDF" ]; then
    echo ""
    echo "✅ PDF created successfully!"
    echo "📄 File: $OUTPUT_PDF"
    ls -lh "$OUTPUT_PDF"
else
    echo ""
    echo "❌ PDF conversion failed"
    exit 1
fi

# Release 1.3.0 - Custom Font Presets

**Release Date**: December 1, 2025

## 🎨 Highlights

This release introduces **custom font presets** with professional typography, featuring **IBM Plex fonts** as the new default for a modern, polished appearance.

## ✨ New Features

### Custom Font Presets
Choose from four professionally designed font combinations:

- **IBM** (default): IBM Plex Sans + IBM Plex Mono - Modern technical documentation
- **System**: Platform-native fonts - Maximum compatibility
- **Classic**: Georgia serif fonts - Traditional documents
- **Modern**: Roboto fonts - Contemporary web-style

### Usage
```bash
# Use default IBM fonts
md2pdf document.md

# Choose a different preset
md2pdf document.md --font-preset classic
md2pdf document.md --font-preset modern
md2pdf document.md --font-preset system

# Batch conversion with fonts
md2pdf-batch docs/ --font-preset modern -r
```

### Google Fonts Integration
- Automatic font loading from Google Fonts CDN for IBM and Modern presets
- Proper font weight specifications (300, 400, 700)
- Fallback fonts for offline scenarios

## 🔧 Improvements

### IBM Plex Font Weights (Optimized for Readability)
- **Titles**: IBM Plex Sans Bold (700)
- **Body**: IBM Plex Sans Light (300)
- **Code**: IBM Plex Mono Regular (400)

### Enhanced CLI
- Added `--font-preset` option to `md2pdf` command
- Added `--font-preset` option to `md2pdf-batch` command
- Updated help text with font examples

## 🐛 Bug Fixes

### Special Character Handling
Fixed critical issue where files with special characters in names (like `#`, spaces) failed to convert:
- **Before**: `ENHANCEMENT #5 ORIENTATION.md` → Error
- **After**: `ENHANCEMENT #5 ORIENTATION.md` → Success ✅

Technical fix: Proper URL encoding using `Path.as_uri()` for file:// URLs

## 📦 What's Changed

### New Files
- `md_to_pdf/fonts.py` - Font configuration and management module

### Modified Files
- `md_to_pdf/cli.py` - Added font preset CLI support
- `md_to_pdf/md2html.py` - Font-aware HTML generation
- `md_to_pdf/html2pdf.py` - Fixed URL encoding for special characters
- `md_to_pdf/batch.py` - Font preset support in batch processing
- `md_to_pdf/__init__.py` - Version bump to 1.3.0
- `setup.py` - Version update
- `README.md` - Comprehensive font documentation
- `CHANGELOG.md` - Detailed release notes

## 📊 Statistics

- **9 files changed**
- **377 insertions**
- **51 deletions**
- **1 new module** (fonts.py)

## 🔄 Migration Guide

### Backward Compatibility
This release is fully backward compatible. Existing scripts continue to work without changes.

### Font Change
The default font has changed from system fonts to IBM Plex. To use the old behavior:
```bash
md2pdf document.md --font-preset system
```

### Internet Requirement
IBM and Modern presets require internet connection on first use to download fonts from Google Fonts. Fonts are cached afterward.

## 📚 Documentation

- Updated README with font preset comparison table
- Added font selection best practices
- Comprehensive CHANGELOG with migration guide
- Updated all CLI examples

## 🙏 Acknowledgments

Enhanced using [IBM Bob](https://www.ibm.com/products/bob) for AI-assisted development.

## 📥 Installation

```bash
pip install md-to-pdf==1.3.0
playwright install chromium
```

Or from source:
```bash
git clone https://github.ibm.com/technology-garage-dach/md-to-pdf.git
cd md-to-pdf
pip install .
playwright install chromium
```

## 🔗 Links

- [Full Changelog](CHANGELOG.md)
- [Implementation Plan](IMPLEMENTATION_PLAN_CUSTOM_FONTS.md)
- [Repository](https://github.ibm.com/technology-garage-dach/md-to-pdf)
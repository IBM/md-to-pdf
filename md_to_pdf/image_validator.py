#!/usr/bin/env python3
# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
# Created with IBM Bob (https://bob.ibm.com)

"""
Image Validator for Markdown to PDF Converter

Validates image references in markdown files before PDF generation.
Supports both warning mode (default) and strict mode (abort on missing images).
"""

import re
import sys
from pathlib import Path

from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Results of image validation"""
    total_images: int
    missing_images: list[tuple[str, int, str]]  # (path, line_number, markdown_file)
    files_with_issues: set[str] = field(default_factory=set)

    @property
    def has_missing_images(self) -> bool:
        return len(self.missing_images) > 0

    @property
    def missing_count(self) -> int:
        return len(self.missing_images)


class ImageValidator:
    """Validates image references in markdown files"""

    # Regex patterns for image detection
    INLINE_IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^\)]+)\)'
    REFERENCE_IMAGE_PATTERN = r'!\[([^\]]*)\]\[([^\]]+)\]'
    REFERENCE_DEFINITION_PATTERN = r'^\[([^\]]+)\]:\s*(.+)$'

    # URL patterns to skip
    URL_PATTERN = r'^https?://'

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self._validation_cache: dict = {}

    def _is_url(self, path: str) -> bool:
        return bool(re.match(self.URL_PATTERN, path.strip()))

    def _extract_inline_images(self, lines: list[str]) -> list[tuple[str, int, str]]:
        """Extract inline image references from markdown lines."""
        images = []
        for line_num, line in enumerate(lines, start=1):
            for match in re.finditer(self.INLINE_IMAGE_PATTERN, line):
                images.append((match.group(2).strip(), line_num, match.group(1)))
        return images

    def _extract_reference_definitions(self, lines: list[str]) -> dict:
        """Extract reference-style image definitions."""
        references = {}
        for line in lines:
            match = re.match(self.REFERENCE_DEFINITION_PATTERN, line.strip())
            if match:
                references[match.group(1).strip().lower()] = match.group(2).strip()
        return references

    def _extract_reference_images(self, lines: list[str], references: dict) -> list[tuple[str, int, str]]:
        """Extract reference-style image references from markdown lines."""
        images = []
        for line_num, line in enumerate(lines, start=1):
            for match in re.finditer(self.REFERENCE_IMAGE_PATTERN, line):
                ref_id = match.group(2).strip().lower()
                if ref_id in references:
                    images.append((references[ref_id], line_num, match.group(1)))
        return images

    def _check_image_exists(self, image_path: str, md_file_path: Path) -> bool:
        """Check if an image file exists (URLs are considered valid)."""
        cache_key = (image_path, str(md_file_path))
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]

        if self._is_url(image_path):
            self._validation_cache[cache_key] = True
            return True

        resolved_path = (md_file_path.parent / image_path).resolve()
        exists = resolved_path.exists() and resolved_path.is_file()
        self._validation_cache[cache_key] = exists
        return exists

    def validate_file(self, md_file: Path) -> ValidationResult:
        """Validate all image references in a markdown file."""
        if not md_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {md_file}")

        lines = md_file.read_text(encoding='utf-8').split('\n')

        references = self._extract_reference_definitions(lines)
        all_images = self._extract_inline_images(lines) + self._extract_reference_images(lines, references)

        missing_images = []
        files_with_issues = set()

        for image_path, line_num, _alt_text in all_images:
            if not self._is_url(image_path) and not self._check_image_exists(image_path, md_file):
                missing_images.append((image_path, line_num, str(md_file)))
                files_with_issues.add(str(md_file))

        return ValidationResult(
            total_images=len(all_images),
            missing_images=missing_images,
            files_with_issues=files_with_issues,
        )

    def validate_files(self, md_files: list[Path]) -> ValidationResult:
        """Validate image references in multiple markdown files."""
        total_images = 0
        all_missing = []
        all_files_with_issues = set()

        for md_file in md_files:
            result = self.validate_file(md_file)
            total_images += result.total_images
            all_missing.extend(result.missing_images)
            all_files_with_issues.update(result.files_with_issues)

        return ValidationResult(
            total_images=total_images,
            missing_images=all_missing,
            files_with_issues=all_files_with_issues,
        )

    def report_results(self, result: ValidationResult) -> None:
        """Report validation results to stderr."""
        if not result.has_missing_images:
            return

        prefix = "Error" if self.strict_mode else "Warning"
        for image_path, line_num, md_file in result.missing_images:
            print(f"{prefix}: Image not found: {image_path} (referenced in {Path(md_file).name}:{line_num})",
                  file=sys.stderr)

        if self.strict_mode:
            print(f"\nError: Image validation failed", file=sys.stderr)
            print(f"  - Total images checked: {result.total_images}", file=sys.stderr)
            print(f"  - Missing images: {result.missing_count}", file=sys.stderr)
            print(f"  - Files affected: {len(result.files_with_issues)}", file=sys.stderr)
            print(f"PDF generation aborted due to missing images", file=sys.stderr)
        else:
            print(f"\nWarning: Found {result.missing_count} missing image reference(s)", file=sys.stderr)


def validate_images(md_file: Path, strict_mode: bool = False) -> tuple[bool, "ValidationResult"]:
    """Validate images in a single Markdown file and report results.

    Args:
        md_file: Path to the Markdown file to validate.
        strict_mode: If True, treat missing images as errors.

    Returns:
        Tuple of (passed, result) where passed is False only when strict_mode
        is True and images are missing.
    """
    validator = ImageValidator(strict_mode=strict_mode)
    result = validator.validate_file(md_file)
    validator.report_results(result)
    return not (strict_mode and result.has_missing_images), result


def validate_images_batch(md_files: list[Path], strict_mode: bool = False) -> bool:
    """
    Validate images in multiple markdown files and report results.

    Returns:
        True if validation passed (or warnings only), False if strict mode and images missing
    """
    validator = ImageValidator(strict_mode=strict_mode)
    result = validator.validate_files(md_files)
    validator.report_results(result)
    return not (strict_mode and result.has_missing_images)

# Made with Bob

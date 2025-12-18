#!/usr/bin/env python3
"""
Image Validator for Markdown to PDF Converter

Validates image references in markdown files before PDF generation.
Supports both warning mode (default) and strict mode (abort on missing images).
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class ImageReference:
    """Represents an image reference found in a markdown file"""
    path: str
    line_number: int
    alt_text: str
    is_url: bool = False


@dataclass
class ValidationResult:
    """Results of image validation"""
    total_images: int
    missing_images: List[Tuple[str, int, str]]  # (path, line_number, markdown_file)
    existing_images: List[str]
    files_with_issues: Set[str]
    
    @property
    def has_missing_images(self) -> bool:
        """Check if any images are missing"""
        return len(self.missing_images) > 0
    
    @property
    def missing_count(self) -> int:
        """Count of missing images"""
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
        """
        Initialize the image validator
        
        Args:
            strict_mode: If True, abort on missing images. If False, issue warnings.
        """
        self.strict_mode = strict_mode
        self._validation_cache: dict = {}
    
    def _is_url(self, path: str) -> bool:
        """Check if a path is a URL"""
        return bool(re.match(self.URL_PATTERN, path.strip()))
    
    def _extract_inline_images(self, content: str) -> List[Tuple[str, int, str]]:
        """
        Extract inline image references from markdown content
        
        Returns:
            List of (image_path, line_number, alt_text) tuples
        """
        images = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            matches = re.finditer(self.INLINE_IMAGE_PATTERN, line)
            for match in matches:
                alt_text = match.group(1)
                image_path = match.group(2).strip()
                images.append((image_path, line_num, alt_text))
        
        return images
    
    def _extract_reference_definitions(self, content: str) -> dict:
        """
        Extract reference-style image definitions
        
        Returns:
            Dictionary mapping reference IDs to image paths
        """
        references = {}
        lines = content.split('\n')
        
        for line in lines:
            match = re.match(self.REFERENCE_DEFINITION_PATTERN, line.strip())
            if match:
                ref_id = match.group(1).strip().lower()
                ref_path = match.group(2).strip()
                references[ref_id] = ref_path
        
        return references
    
    def _extract_reference_images(self, content: str, references: dict) -> List[Tuple[str, int, str]]:
        """
        Extract reference-style image references from markdown content
        
        Args:
            content: Markdown content
            references: Dictionary of reference definitions
            
        Returns:
            List of (image_path, line_number, alt_text) tuples
        """
        images = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            matches = re.finditer(self.REFERENCE_IMAGE_PATTERN, line)
            for match in matches:
                alt_text = match.group(1)
                ref_id = match.group(2).strip().lower()
                
                # Look up the reference
                if ref_id in references:
                    image_path = references[ref_id]
                    images.append((image_path, line_num, alt_text))
        
        return images
    
    def _resolve_image_path(self, image_path: str, md_file_path: Path) -> Optional[Path]:
        """
        Resolve image path relative to markdown file
        
        Args:
            image_path: Image path from markdown
            md_file_path: Path to the markdown file
            
        Returns:
            Resolved Path object or None if it's a URL
        """
        # Skip URLs
        if self._is_url(image_path):
            return None
        
        # Get the directory containing the markdown file
        md_dir = md_file_path.parent
        
        # Resolve the image path relative to the markdown file
        resolved_path = (md_dir / image_path).resolve()
        
        return resolved_path
    
    def _check_image_exists(self, image_path: str, md_file_path: Path) -> bool:
        """
        Check if an image file exists
        
        Args:
            image_path: Image path from markdown
            md_file_path: Path to the markdown file
            
        Returns:
            True if image exists or is a URL, False otherwise
        """
        # Use cache to avoid repeated filesystem checks
        cache_key = (image_path, str(md_file_path))
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        
        # URLs are considered valid (we can't validate them)
        if self._is_url(image_path):
            self._validation_cache[cache_key] = True
            return True
        
        # Resolve and check if file exists
        resolved_path = self._resolve_image_path(image_path, md_file_path)
        if resolved_path is None:
            self._validation_cache[cache_key] = True
            return True
        
        exists = resolved_path.exists() and resolved_path.is_file()
        self._validation_cache[cache_key] = exists
        return exists
    
    def validate_file(self, md_file: Path) -> ValidationResult:
        """
        Validate all image references in a markdown file
        
        Args:
            md_file: Path to the markdown file
            
        Returns:
            ValidationResult object with validation details
        """
        if not md_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {md_file}")
        
        # Read markdown content
        content = md_file.read_text(encoding='utf-8')
        
        # Extract all image references
        inline_images = self._extract_inline_images(content)
        references = self._extract_reference_definitions(content)
        reference_images = self._extract_reference_images(content, references)
        
        # Combine all images
        all_images = inline_images + reference_images
        
        # Validate each image
        missing_images = []
        existing_images = []
        files_with_issues = set()
        
        for image_path, line_num, alt_text in all_images:
            # Skip URLs
            if self._is_url(image_path):
                existing_images.append(image_path)
                continue
            
            if not self._check_image_exists(image_path, md_file):
                missing_images.append((image_path, line_num, str(md_file)))
                files_with_issues.add(str(md_file))
            else:
                existing_images.append(image_path)
        
        return ValidationResult(
            total_images=len(all_images),
            missing_images=missing_images,
            existing_images=existing_images,
            files_with_issues=files_with_issues
        )
    
    def validate_files(self, md_files: List[Path]) -> ValidationResult:
        """
        Validate image references in multiple markdown files
        
        Args:
            md_files: List of markdown file paths
            
        Returns:
            Combined ValidationResult for all files
        """
        total_images = 0
        all_missing = []
        all_existing = []
        all_files_with_issues = set()
        
        for md_file in md_files:
            result = self.validate_file(md_file)
            total_images += result.total_images
            all_missing.extend(result.missing_images)
            all_existing.extend(result.existing_images)
            all_files_with_issues.update(result.files_with_issues)
        
        return ValidationResult(
            total_images=total_images,
            missing_images=all_missing,
            existing_images=all_existing,
            files_with_issues=all_files_with_issues
        )
    
    def report_results(self, result: ValidationResult, file_context: str = "") -> None:
        """
        Report validation results to stderr
        
        Args:
            result: ValidationResult object
            file_context: Optional context string (e.g., "single file" or "batch")
        """
        if not result.has_missing_images:
            return
        
        # Print warnings or errors
        for image_path, line_num, md_file in result.missing_images:
            if self.strict_mode:
                print(f"Error: Image not found: {image_path} (referenced in {Path(md_file).name}:{line_num})", 
                      file=sys.stderr)
            else:
                print(f"Warning: Image not found: {image_path} (referenced in {Path(md_file).name}:{line_num})", 
                      file=sys.stderr)
        
        # Print summary
        if self.strict_mode:
            print(f"\nError: Image validation failed", file=sys.stderr)
            print(f"  - Total images checked: {result.total_images}", file=sys.stderr)
            print(f"  - Missing images: {result.missing_count}", file=sys.stderr)
            print(f"  - Files affected: {len(result.files_with_issues)}", file=sys.stderr)
            print(f"PDF generation aborted due to missing images", file=sys.stderr)
        else:
            # Only print summary if there are missing images
            if result.missing_count > 0:
                print(f"\nWarning: Found {result.missing_count} missing image reference(s)", file=sys.stderr)
    
    def validate_and_report(self, md_file: Path) -> bool:
        """
        Validate a single file and report results
        
        Args:
            md_file: Path to markdown file
            
        Returns:
            True if validation passed (or warnings only), False if strict mode and images missing
        """
        result = self.validate_file(md_file)
        self.report_results(result, "single file")
        
        if self.strict_mode and result.has_missing_images:
            return False
        
        return True
    
    def validate_and_report_batch(self, md_files: List[Path]) -> bool:
        """
        Validate multiple files and report results
        
        Args:
            md_files: List of markdown file paths
            
        Returns:
            True if validation passed (or warnings only), False if strict mode and images missing
        """
        result = self.validate_files(md_files)
        self.report_results(result, "batch")
        
        if self.strict_mode and result.has_missing_images:
            return False
        
        return True


def validate_images(md_file: Path, strict_mode: bool = False) -> bool:
    """
    Convenience function to validate images in a markdown file
    
    Args:
        md_file: Path to markdown file
        strict_mode: If True, abort on missing images
        
    Returns:
        True if validation passed, False if strict mode and images missing
    """
    validator = ImageValidator(strict_mode=strict_mode)
    return validator.validate_and_report(md_file)


def validate_images_batch(md_files: List[Path], strict_mode: bool = False) -> bool:
    """
    Convenience function to validate images in multiple markdown files
    
    Args:
        md_files: List of markdown file paths
        strict_mode: If True, abort on missing images
        
    Returns:
        True if validation passed, False if strict mode and images missing
    """
    validator = ImageValidator(strict_mode=strict_mode)
    return validator.validate_and_report_batch(md_files)

# Made with Bob

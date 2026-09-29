#!/usr/bin/env python3
# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
# Created with IBM Bob (https://bob.ibm.com)

"""
Font configuration module for MD to PDF converter
Provides font presets and helper functions for Google Fonts integration
"""

from typing import Dict, Tuple, Optional
from urllib.parse import quote_plus

# Font preset definitions
# Each preset contains: (font_family, font_weight) tuples for title, body, and code
FONT_PRESETS: Dict[str, Dict[str, Tuple[str, int]]] = {
    'ibm': {
        'title': ('IBM Plex Sans', 700),      # Bold
        'body': ('IBM Plex Sans', 300),       # Light
        'code': ('IBM Plex Mono', 400)        # Regular
    },
    'system': {
        'title': ('-apple-system, BlinkMacSystemFont, "Segoe UI", Arial', 600),
        'body': ('-apple-system, BlinkMacSystemFont, "Segoe UI", Arial', 400),
        'code': ('Consolas, Monaco, monospace', 400)
    },
    'classic': {
        'title': ('Georgia', 700),
        'body': ('Georgia', 400),
        'code': ('Courier New', 400)
    },
    'modern': {
        'title': ('Roboto', 700),
        'body': ('Roboto', 300),
        'code': ('Roboto Mono', 400)
    }
}

# Default preset
DEFAULT_PRESET = 'ibm'

# Presets that require Google Fonts
GOOGLE_FONTS_PRESETS = {'ibm', 'modern'}


def get_google_fonts_url(preset_name: str) -> Optional[str]:
    """
    Generate Google Fonts URL for the specified preset
    
    Args:
        preset_name: Name of the font preset
        
    Returns:
        Google Fonts URL string, or None if preset doesn't use Google Fonts
        
    Examples:
        >>> get_google_fonts_url('ibm')
        'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@200;600&family=IBM+Plex+Mono:wght@300&display=swap'
        
        >>> get_google_fonts_url('system')
        None
    """
    if preset_name not in GOOGLE_FONTS_PRESETS:
        return None
    
    if preset_name not in FONT_PRESETS:
        raise ValueError(f"Unknown font preset: {preset_name}")
    
    preset = FONT_PRESETS[preset_name]
    
    # Collect unique font families and their weights
    font_families: Dict[str, set] = {}
    
    for font_type in ['title', 'body', 'code']:
        font_family, weight = preset[font_type]
        if font_family not in font_families:
            font_families[font_family] = set()
        font_families[font_family].add(weight)
    
    # Build Google Fonts URL
    base_url = "https://fonts.googleapis.com/css2?"
    family_params = []
    
    for family, weights in sorted(font_families.items()):
        # URL encode the font family name
        encoded_family = quote_plus(family)
        # Sort weights and join with semicolon
        weights_str = ';'.join(str(w) for w in sorted(weights))
        family_params.append(f"family={encoded_family}:wght@{weights_str}")
    
    # Join all family parameters with & and add display=swap
    url = base_url + '&'.join(family_params) + "&display=swap"
    
    return url


def get_font_css(preset_name: str) -> Dict[str, Tuple[str, int]]:
    """
    Get font CSS configuration for the specified preset
    
    Args:
        preset_name: Name of the font preset
        
    Returns:
        Dictionary with 'title', 'body', and 'code' keys, each containing
        a tuple of (font_family, font_weight)
        
    Raises:
        ValueError: If preset_name is not recognized
        
    Examples:
        >>> get_font_css('ibm')
        {
            'title': ('IBM Plex Sans', 600),
            'body': ('IBM Plex Sans', 200),
            'code': ('IBM Plex Mono', 300)
        }
    """
    if preset_name not in FONT_PRESETS:
        raise ValueError(
            f"Unknown font preset: {preset_name}. "
            f"Available presets: {', '.join(FONT_PRESETS.keys())}"
        )
    
    return FONT_PRESETS[preset_name].copy()


def get_available_presets() -> list:
    """
    Get list of available font preset names
    
    Returns:
        List of preset names
    """
    return list(FONT_PRESETS.keys())


def validate_preset(preset_name: str) -> bool:
    """
    Check if a preset name is valid
    
    Args:
        preset_name: Name of the font preset to validate
        
    Returns:
        True if preset exists, False otherwise
    """
    return preset_name in FONT_PRESETS


# Made with Bob
"""
Color space conversion utilities for Apple IIgs.

Handles conversion between:
- 24-bit RGB (8 bits per channel)
- 12-bit Apple IIgs RGB (4 bits per channel)
- sRGB <-> Linear RGB conversion for perceptually correct processing
"""

import numpy as np
from typing import Tuple, Union


def rgb24_to_iigs12(rgb: Union[Tuple[int, int, int], np.ndarray]) -> int:
    """
    Convert 24-bit RGB to Apple IIgs 12-bit color format.
    
    Args:
        rgb: Tuple of (r, g, b) with values 0-255, or numpy array
        
    Returns:
        16-bit integer with format: 0000_BBBB_GGGG_RRRR
        
    Example:
        >>> rgb24_to_iigs12((255, 255, 255))  # White
        4095  # 0x0FFF
        >>> rgb24_to_iigs12((255, 0, 0))  # Red
        15  # 0x000F
    """
    if isinstance(rgb, np.ndarray):
        r, g, b = rgb[0], rgb[1], rgb[2]
    else:
        r, g, b = rgb
    
    # Round to nearest 4-bit value
    r4 = int(r / 255.0 * 15 + 0.5)
    g4 = int(g / 255.0 * 15 + 0.5)
    b4 = int(b / 255.0 * 15 + 0.5)
    
    # Pack into Apple IIgs format: 0000_BBBB_GGGG_RRRR
    return (b4 << 8) | (g4 << 4) | r4


def iigs12_to_rgb24(color: int) -> Tuple[int, int, int]:
    """
    Convert Apple IIgs 12-bit color to 24-bit RGB.
    
    Args:
        color: 16-bit integer with format 0000_BBBB_GGGG_RRRR
        
    Returns:
        Tuple of (r, g, b) with values 0-255
        
    Example:
        >>> iigs12_to_rgb24(0x0FFF)  # White
        (255, 255, 255)
        >>> iigs12_to_rgb24(0x000F)  # Red
        (255, 0, 0)
    """
    r4 = color & 0x0F
    g4 = (color >> 4) & 0x0F
    b4 = (color >> 8) & 0x0F
    
    # Scale from 4-bit to 8-bit
    r = int(r4 / 15.0 * 255)
    g = int(g4 / 15.0 * 255)
    b = int(b4 / 15.0 * 255)
    
    return (r, g, b)


def srgb_to_linear(srgb: np.ndarray) -> np.ndarray:
    """
    Convert sRGB color space to linear RGB for perceptually correct processing.
    
    Linear RGB is necessary for proper color mixing, blending, and error calculations
    in dithering algorithms.
    
    Args:
        srgb: Array with values 0-255
        
    Returns:
        Array with linear RGB values 0.0-1.0
    """
    srgb_normalized = srgb / 255.0
    
    # Apply sRGB gamma correction formula
    linear = np.where(
        srgb_normalized <= 0.04045,
        srgb_normalized / 12.92,
        ((srgb_normalized + 0.055) / 1.055) ** 2.4
    )
    
    return linear


def linear_to_srgb(linear: np.ndarray) -> np.ndarray:
    """
    Convert linear RGB back to sRGB color space.
    
    Args:
        linear: Array with linear RGB values 0.0-1.0
        
    Returns:
        Array with sRGB values 0-255 as uint8
    """
    # Apply inverse sRGB gamma correction
    srgb_normalized = np.where(
        linear <= 0.0031308,
        linear * 12.92,
        1.055 * (linear ** (1.0 / 2.4)) - 0.055
    )
    
    # Clamp and convert to 8-bit
    srgb_normalized = np.clip(srgb_normalized, 0.0, 1.0)
    return (srgb_normalized * 255).astype(np.uint8)


def quantize_to_iigs_colorspace(rgb: np.ndarray) -> np.ndarray:
    """
    Quantize RGB colors to Apple IIgs 12-bit color space.
    
    This reduces each 8-bit channel to 4 bits, simulating the Apple IIgs
    color precision. Useful for preview and understanding color limitations.
    
    Args:
        rgb: Array with values 0-255
        
    Returns:
        Array with values quantized to 4-bit per channel (0, 17, 34, ..., 255)
    """
    # Round to nearest multiple of 17 (255/15 ≈ 17)
    quantized = np.round(rgb / 17.0) * 17.0
    return np.clip(quantized, 0, 255).astype(np.uint8)


def find_closest_palette_color(pixel: np.ndarray, palette: np.ndarray) -> int:
    """
    Find the index of the closest color in a palette.
    
    Uses Euclidean distance in RGB space.
    
    Args:
        pixel: Single pixel as [r, g, b] array
        palette: Array of shape (n_colors, 3) with palette colors
        
    Returns:
        Index of closest color in palette
    """
    # Calculate squared Euclidean distance to all palette colors
    distances = np.sum((palette - pixel) ** 2, axis=1)
    return np.argmin(distances)

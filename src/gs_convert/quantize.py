"""
Color quantization algorithms for palette generation.

Implements median cut and other quantization methods to find optimal
palette colors for Apple IIgs per-scanline conversion.
"""

import numpy as np
from typing import List, Tuple


def median_cut_quantize(pixels: np.ndarray, num_colors: int = 16) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply median cut algorithm to find optimal palette colors.
    
    The median cut algorithm works by:
    1. Starting with all pixels in one bucket
    2. Finding the color channel with widest range
    3. Sorting by that channel and splitting at median
    4. Repeating until desired number of colors reached
    5. Computing representative color for each bucket (mean)
    
    Args:
        pixels: Array of shape (n_pixels, 3) with RGB values
        num_colors: Number of palette colors to generate (default 16 for Apple IIgs)
        
    Returns:
        Tuple of (palette, indices):
            - palette: Array of shape (num_colors, 3) with RGB colors
            - indices: Array of shape (n_pixels,) mapping pixels to palette
    """
    # Handle edge case of fewer unique colors than requested
    unique_colors = np.unique(pixels.reshape(-1, 3), axis=0)
    if len(unique_colors) <= num_colors:
        # Pad palette with duplicates if needed
        palette = np.zeros((num_colors, 3), dtype=np.uint8)
        palette[:len(unique_colors)] = unique_colors
        if len(unique_colors) < num_colors:
            # Fill remaining slots with black
            palette[len(unique_colors):] = 0
        
        # Map pixels to palette
        indices = np.array([_find_color_index(pixel, palette) for pixel in pixels])
        return palette, indices
    
    # Start with all pixels in one bucket
    buckets = [pixels.copy()]
    
    # Split until we have num_colors buckets
    while len(buckets) < num_colors:
        # Find bucket with largest range
        largest_bucket_idx = _find_largest_bucket(buckets)
        largest_bucket = buckets.pop(largest_bucket_idx)
        
        # Split this bucket at median
        bucket1, bucket2 = _median_cut_split(largest_bucket)
        
        # Handle edge case where split failed (all identical colors)
        if len(bucket1) == 0 or len(bucket2) == 0:
            buckets.append(largest_bucket)
            break
            
        buckets.extend([bucket1, bucket2])
    
    # Calculate representative color for each bucket (mean)
    palette = np.array([bucket.mean(axis=0) for bucket in buckets], dtype=np.uint8)
    
    # Map each pixel to nearest palette color
    indices = np.array([_find_color_index(pixel, palette) for pixel in pixels])
    
    return palette, indices


def _find_largest_bucket(buckets: List[np.ndarray]) -> int:
    """Find the bucket with the largest color range."""
    max_range = -1
    max_idx = 0
    
    for idx, bucket in enumerate(buckets):
        color_range = _get_color_range(bucket)
        if color_range > max_range:
            max_range = color_range
            max_idx = idx
    
    return max_idx


def _get_color_range(bucket: np.ndarray) -> float:
    """Calculate the total range across all color channels."""
    if len(bucket) == 0:
        return 0
    ranges = bucket.max(axis=0) - bucket.min(axis=0)
    return ranges.sum()


def _median_cut_split(bucket: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Split a bucket at the median of its widest color channel.
    
    Args:
        bucket: Array of shape (n_pixels, 3)
        
    Returns:
        Tuple of (bucket1, bucket2) split at median
    """
    if len(bucket) <= 1:
        return bucket, np.array([])
    
    # Find channel with widest range
    ranges = bucket.max(axis=0) - bucket.min(axis=0)
    split_channel = ranges.argmax()
    
    # Sort by that channel
    sorted_indices = bucket[:, split_channel].argsort()
    sorted_bucket = bucket[sorted_indices]
    
    # Split at median
    mid = len(sorted_bucket) // 2
    
    return sorted_bucket[:mid], sorted_bucket[mid:]


def _find_color_index(pixel: np.ndarray, palette: np.ndarray) -> int:
    """Find index of closest color in palette using Euclidean distance."""
    distances = np.sum((palette - pixel) ** 2, axis=1)
    return np.argmin(distances)


def quantize_scanline(scanline_pixels: np.ndarray, num_colors: int = 16) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function to quantize a single scanline.
    
    Args:
        scanline_pixels: Array of shape (width, 3) for one scanline
        num_colors: Number of palette colors (16 for Apple IIgs)
        
    Returns:
        Tuple of (palette, indices)
    """
    return median_cut_quantize(scanline_pixels, num_colors)


def global_quantize(image: np.ndarray, num_palettes: int = 16, colors_per_palette: int = 16) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Create a global set of palettes for the entire image.

    This is an alternative to per-scanline quantization. It creates a set
    of palettes that can be reused across multiple scanlines.

    Args:
        image: Array of shape (height, width, 3)
        num_palettes: Number of different palettes to create
        colors_per_palette: Colors per palette (16 for Apple IIgs)

    Returns:
        Tuple of (palettes, palette_indices):
            - palettes: List of num_palettes arrays, each (colors_per_palette, 3)
            - palette_indices: Array of shape (height,) indicating which palette for each line
    """
    # Flatten all pixels
    all_pixels = image.reshape(-1, 3)

    # Create a large palette using median cut
    total_colors = num_palettes * colors_per_palette
    large_palette, _ = median_cut_quantize(all_pixels, total_colors)

    # Split into smaller palettes
    palettes = []
    for i in range(num_palettes):
        start_idx = i * colors_per_palette
        end_idx = start_idx + colors_per_palette
        palettes.append(large_palette[start_idx:end_idx])

    # For each scanline, find the best matching palette
    # (This is a simplified approach; could be optimized)
    height = image.shape[0]
    palette_indices = np.zeros(height, dtype=np.uint8)

    for y in range(height):
        scanline = image[y]
        best_palette_idx = 0
        min_error = float('inf')

        for palette_idx, palette in enumerate(palettes):
            # Calculate total error for this scanline with this palette
            error = 0
            for pixel in scanline:
                closest_idx = _find_color_index(pixel, palette)
                error += np.sum((pixel - palette[closest_idx]) ** 2)

            if error < min_error:
                min_error = error
                best_palette_idx = palette_idx

        palette_indices[y] = best_palette_idx

    return palettes, palette_indices


def optimized_quantize(
    image: np.ndarray,
    num_colors: int = 16,
    error_threshold: float = 2000.0
) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Intelligent palette generation with reuse across adjacent scanlines.

    This method eliminates banding in solid-color areas by reusing palettes
    across adjacent scanlines when possible, while still allowing palette
    changes where needed for complex imagery.

    Algorithm:
    1. Generate optimal palette for first scanline
    2. For each subsequent scanline:
       - Try previous scanline's palette
       - Calculate quantization error
       - If error is low enough, reuse the palette
       - Otherwise, generate a new palette
    3. Result: Solid areas share palettes (no banding), complex areas get unique palettes

    Args:
        image: Array of shape (height, width, 3)
        num_colors: Colors per palette (16 for Apple IIgs)
        error_threshold: Maximum acceptable error for palette reuse
                        Lower = more new palettes (better quality, more banding)
                        Higher = more reuse (less banding, possible quality loss)
                        Default 2000.0 works well for most images

    Returns:
        Tuple of (palettes, scb_bytes):
            - palettes: List of unique palettes (up to 16 max)
            - scb_bytes: Array of shape (200,) mapping scanlines to palette indices
    """
    height, width = image.shape[:2]
    palettes = []
    scb_bytes = np.zeros(height, dtype=np.uint8)
    palette_map = {}  # Maps palette bytes to index for deduplication

    for y in range(height):
        scanline = image[y]

        # Try to reuse previous palette if it exists
        should_create_new = True

        if y > 0:
            # Get previous scanline's palette
            prev_palette_idx = scb_bytes[y - 1]
            prev_palette = palettes[prev_palette_idx]

            # Calculate error if we use previous palette
            error = _calculate_palette_error(scanline, prev_palette)

            # If error is acceptable, reuse the palette
            if error <= error_threshold:
                scb_bytes[y] = prev_palette_idx
                should_create_new = False

        # Create new palette if needed
        if should_create_new:
            # Generate optimal palette for this scanline
            palette, _ = median_cut_quantize(scanline, num_colors)

            # Check if we've already created this exact palette
            palette_key = palette.tobytes()
            if palette_key in palette_map:
                # Reuse existing identical palette
                palette_idx = palette_map[palette_key]
            else:
                # Add new palette (if we haven't hit the limit)
                if len(palettes) < 16:
                    palette_idx = len(palettes)
                    palettes.append(palette)
                    palette_map[palette_key] = palette_idx
                else:
                    # Hit 16 palette limit - find best existing palette
                    palette_idx = _find_best_existing_palette(scanline, palettes)

            scb_bytes[y] = palette_idx

    # Pad to 16 palettes if needed
    while len(palettes) < 16:
        palettes.append(np.zeros((num_colors, 3), dtype=np.uint8))

    return palettes, scb_bytes


def _calculate_palette_error(scanline: np.ndarray, palette: np.ndarray) -> float:
    """
    Calculate total quantization error for a scanline using a given palette.

    Args:
        scanline: Array of shape (width, 3) with RGB values
        palette: Array of shape (num_colors, 3) with palette colors

    Returns:
        Total squared error across all pixels
    """
    total_error = 0.0

    for pixel in scanline:
        # Find closest palette color
        distances = np.sum((palette - pixel) ** 2, axis=1)
        min_distance = np.min(distances)
        total_error += min_distance

    return total_error


def _find_best_existing_palette(scanline: np.ndarray, palettes: List[np.ndarray]) -> int:
    """
    Find the best existing palette for a scanline when palette limit is reached.

    Args:
        scanline: Array of shape (width, 3)
        palettes: List of existing palettes

    Returns:
        Index of best matching palette
    """
    min_error = float('inf')
    best_idx = 0

    for idx, palette in enumerate(palettes):
        error = _calculate_palette_error(scanline, palette)
        if error < min_error:
            min_error = error
            best_idx = idx

    return best_idx

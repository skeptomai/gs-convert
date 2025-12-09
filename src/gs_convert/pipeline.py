"""
Main conversion pipeline for Apple IIgs image conversion.

Orchestrates the entire process from input image to .3200 output.
"""

import numpy as np
from PIL import Image
from typing import Optional, Tuple, List
from pathlib import Path

from .color import srgb_to_linear, linear_to_srgb, rgb24_to_iigs12, iigs12_to_rgb24
from .quantize import median_cut_quantize, global_quantize, optimized_quantize
from .dither import DITHERING_ALGORITHMS, Ditherer
from .format_writer import write_3200_file, generate_scb_bytes


def convert_image(
    input_path: str,
    output_path: str,
    dither_method: str = 'atkinson',
    quantize_method: str = 'median-cut',
    aspect_correct: float = 1.2,
    resize_filter: str = 'lanczos',
    use_linear_rgb: bool = True,
    optimize_palettes: bool = False,
    error_threshold: float = 2000.0,
) -> None:
    """
    Convert an image to Apple IIgs .3200 format.

    Args:
        input_path: Path to input image (PNG, JPEG, etc.)
        output_path: Path for output .3200 file
        dither_method: Dithering algorithm ('atkinson', 'floyd-steinberg', 'ordered', 'none', etc.)
        quantize_method: Quantization method ('median-cut', 'global', or 'optimized')
        aspect_correct: Horizontal aspect ratio correction (1.0 = none, 1.2 = standard)
        resize_filter: PIL resize filter ('lanczos', 'bilinear', 'nearest')
        use_linear_rgb: Use linear RGB color space for processing (recommended)
        optimize_palettes: Use intelligent palette reuse to reduce banding (recommended for solid areas)
        error_threshold: Error threshold for palette reuse (only used with optimize_palettes)
    """
    # Load and preprocess image
    print(f"Loading {input_path}...")
    img = load_and_resize_image(input_path, aspect_correct, resize_filter)
    pixels = np.array(img)

    # Convert to linear RGB if requested
    if use_linear_rgb:
        print("Converting to linear RGB color space...")
        pixels = (srgb_to_linear(pixels) * 255).astype(np.uint8)

    # Generate palettes and pixel indices
    if optimize_palettes or quantize_method == 'optimized':
        print(f"Generating palettes using optimized quantization (threshold={error_threshold})...")
        palettes, scb_bytes = generate_optimized_palettes(pixels, error_threshold)
    elif quantize_method == 'median-cut':
        print(f"Generating palettes using {quantize_method}...")
        palettes, scb_bytes = generate_per_scanline_palettes(pixels)
    elif quantize_method == 'global':
        print(f"Generating palettes using {quantize_method}...")
        palettes, scb_bytes = generate_global_palettes(pixels)
    else:
        raise ValueError(f"Unknown quantization method: {quantize_method}")

    # Convert palettes to Apple IIgs 12-bit color space
    print("Converting palettes to Apple IIgs 12-bit color space...")
    palettes_12bit = convert_palettes_to_iigs(palettes)
    palettes_rgb = convert_palettes_to_rgb(palettes_12bit)

    # Apply dithering
    print(f"Applying {dither_method} dithering...")
    pixel_indices = apply_per_scanline_dithering(
        pixels, palettes_rgb, scb_bytes, dither_method
    )

    # Write output file
    print(f"Writing {output_path}...")
    write_3200_file(output_path, pixel_indices, scb_bytes, palettes_12bit)

    print(f"Conversion complete! Output: {output_path}")


def load_and_resize_image(
    input_path: str,
    aspect_correct: float,
    resize_filter: str
) -> Image.Image:
    """
    Load image and resize to 320×200 with optional aspect ratio correction.
    
    Args:
        input_path: Path to input image
        aspect_correct: Horizontal stretch factor for pixel aspect ratio
        resize_filter: Resampling filter name
        
    Returns:
        PIL Image at 320×200
    """
    img = Image.open(input_path).convert('RGB')
    
    # Apply aspect ratio correction if requested
    if aspect_correct != 1.0:
        # Stretch horizontally to compensate for non-square pixels
        width = int(320 * aspect_correct)
        img = img.resize((width, 200), getattr(Image.Resampling, resize_filter.upper()))
        # Then scale back to 320 for final output
        img = img.resize((320, 200), getattr(Image.Resampling, resize_filter.upper()))
    else:
        img = img.resize((320, 200), getattr(Image.Resampling, resize_filter.upper()))
    
    return img


def generate_optimized_palettes(pixels: np.ndarray, error_threshold: float = 2000.0) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Generate palettes with intelligent reuse to minimize banding.

    Args:
        pixels: Array of shape (200, 320, 3)
        error_threshold: Maximum error for palette reuse

    Returns:
        Tuple of (palettes, scb_bytes)
    """
    return optimized_quantize(pixels, num_colors=16, error_threshold=error_threshold)


def generate_per_scanline_palettes(pixels: np.ndarray) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Generate optimal 16-color palette for each scanline using median cut.

    Args:
        pixels: Array of shape (200, 320, 3)

    Returns:
        Tuple of (palettes, scb_bytes):
            - palettes: List of up to 200 unique palettes (16 colors each)
            - scb_bytes: Array of shape (200,) mapping scanlines to palettes
    """
    palettes = []
    palette_map = {}  # Cache identical palettes
    scb_bytes = np.zeros(200, dtype=np.uint8)

    for y in range(200):
        scanline = pixels[y]

        # Generate palette for this scanline
        palette, _ = median_cut_quantize(scanline, num_colors=16)

        # Check if we've seen this palette before (to save space)
        palette_key = palette.tobytes()
        if palette_key in palette_map:
            palette_idx = palette_map[palette_key]
        else:
            palette_idx = len(palettes)
            if palette_idx < 16:  # Apple IIgs limit
                palettes.append(palette)
                palette_map[palette_key] = palette_idx
            else:
                # Reuse closest existing palette if we hit the limit
                palette_idx = find_closest_palette_index(palette, palettes)
        
        scb_bytes[y] = palette_idx
    
    # Pad to 16 palettes if needed
    while len(palettes) < 16:
        palettes.append(np.zeros((16, 3), dtype=np.uint8))
    
    return palettes, scb_bytes


def generate_global_palettes(pixels: np.ndarray) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Generate a global set of 16 palettes for entire image.
    
    Args:
        pixels: Array of shape (200, 320, 3)
        
    Returns:
        Tuple of (palettes, scb_bytes)
    """
    palettes, scb_bytes = global_quantize(pixels, num_palettes=16, colors_per_palette=16)
    return palettes, scb_bytes


def convert_palettes_to_iigs(palettes: List[np.ndarray]) -> List[np.ndarray]:
    """
    Convert palettes to Apple IIgs 12-bit color format.
    
    This simulates the color precision loss of the Apple IIgs.
    
    Args:
        palettes: List of RGB palettes (24-bit)
        
    Returns:
        List of palettes in 12-bit format (still as RGB tuples for compatibility)
    """
    iigs_palettes = []
    for palette in palettes:
        iigs_palette = np.zeros((16, 3), dtype=np.uint8)
        for i, color in enumerate(palette):
            color_12bit = rgb24_to_iigs12(color)
            iigs_palette[i] = iigs12_to_rgb24(color_12bit)
        iigs_palettes.append(iigs_palette)
    return iigs_palettes


def convert_palettes_to_rgb(palettes: List[np.ndarray]) -> List[np.ndarray]:
    """Convert palettes to RGB format (no-op if already RGB)."""
    return palettes


def apply_per_scanline_dithering(
    pixels: np.ndarray,
    palettes: List[np.ndarray],
    scb_bytes: np.ndarray,
    dither_method: str
) -> np.ndarray:
    """
    Apply dithering with per-scanline palette selection.
    
    Args:
        pixels: Array of shape (200, 320, 3)
        palettes: List of palettes
        scb_bytes: Array of shape (200,) with palette indices
        dither_method: Name of dithering algorithm
        
    Returns:
        Array of shape (200, 320) with pixel indices
    """
    if dither_method not in DITHERING_ALGORITHMS:
        raise ValueError(f"Unknown dithering method: {dither_method}")
    
    ditherer_class = DITHERING_ALGORITHMS[dither_method]
    ditherer = ditherer_class()
    
    # For per-scanline palettes, we need to dither the entire image
    # but use the correct palette for each scanline
    # This is tricky because error can diffuse across scanlines
    
    # Simple approach: treat each scanline independently (no cross-line diffusion)
    pixel_indices = np.zeros((200, 320), dtype=np.uint8)
    
    for y in range(200):
        palette_idx = scb_bytes[y]
        palette = palettes[palette_idx]
        scanline = pixels[y:y+1]  # Keep 3D shape for ditherer
        
        indices = ditherer.dither(scanline, palette)
        pixel_indices[y] = indices[0]
    
    return pixel_indices


def find_closest_palette_index(target: np.ndarray, palettes: List[np.ndarray]) -> int:
    """Find the index of the most similar palette."""
    min_distance = float('inf')
    best_idx = 0
    
    for idx, palette in enumerate(palettes):
        distance = np.sum((palette.astype(float) - target.astype(float)) ** 2)
        if distance < min_distance:
            min_distance = distance
            best_idx = idx
    
    return best_idx


def generate_preview_image(
    pixel_indices: np.ndarray,
    palettes: List[np.ndarray],
    scb_bytes: np.ndarray,
    output_path: str
) -> None:
    """
    Generate a PNG preview of the converted image.
    
    Useful for visualizing results without loading into an emulator.
    
    Args:
        pixel_indices: Array of shape (200, 320) with palette indices
        palettes: List of palettes
        scb_bytes: Array mapping scanlines to palettes
        output_path: Path for preview PNG
    """
    preview = np.zeros((200, 320, 3), dtype=np.uint8)
    
    for y in range(200):
        palette_idx = scb_bytes[y]
        palette = palettes[palette_idx]
        
        for x in range(320):
            color_idx = pixel_indices[y, x]
            preview[y, x] = palette[color_idx]
    
    img = Image.fromarray(preview)
    img.save(output_path)
    print(f"Preview saved to {output_path}")

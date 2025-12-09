"""
Apple IIgs file format writers.

Implements writing to .3200 (unpacked SHR) format.
"""

import numpy as np
from typing import List
from pathlib import Path


def write_3200_file(
    output_path: str,
    pixel_indices: np.ndarray,
    scb_bytes: np.ndarray,
    palettes: List[np.ndarray]
) -> None:
    """
    Write image data to Apple IIgs .3200 format.
    
    The .3200 format structure:
    - Bytes 0-31999 (32000 bytes): Pixel data (160 bytes × 200 scanlines)
    - Bytes 32000-32255 (256 bytes): SCB bytes (200 used + 56 padding)
    - Bytes 32256-32767 (512 bytes): Palette data (16 palettes × 16 colors × 2 bytes)
    
    Total: 32768 bytes (32 KB)
    
    Args:
        output_path: Path to output .3200 file
        pixel_indices: Array of shape (200, 320) with palette indices 0-15
        scb_bytes: Array of shape (200,) with SCB values (palette selections)
        palettes: List of up to 16 palettes, each array of shape (16, 3) RGB colors
    """
    if pixel_indices.shape != (200, 320):
        raise ValueError(f"pixel_indices must be (200, 320), got {pixel_indices.shape}")
    
    if scb_bytes.shape != (200,):
        raise ValueError(f"scb_bytes must be (200,), got {scb_bytes.shape}")
    
    if len(palettes) > 16:
        raise ValueError(f"Maximum 16 palettes allowed, got {len(palettes)}")
    
    # Initialize 32KB buffer
    data = bytearray(32768)
    
    # Write pixel data (32000 bytes)
    pixel_data = pack_pixel_data(pixel_indices)
    data[0:32000] = pixel_data
    
    # Write SCB bytes (256 bytes, only first 200 used)
    data[32000:32200] = scb_bytes.tobytes()
    # Remaining 56 bytes are padding (already zero)
    
    # Write palette data (512 bytes)
    palette_data = pack_palette_data(palettes)
    data[32256:32768] = palette_data
    
    # Write to file
    Path(output_path).write_bytes(data)


def pack_pixel_data(pixel_indices: np.ndarray) -> bytes:
    """
    Pack pixel indices into Apple IIgs format.
    
    Each byte contains 2 pixels (4 bits each):
    - Low nibble: even pixel (0, 2, 4, ...)
    - High nibble: odd pixel (1, 3, 5, ...)
    
    Args:
        pixel_indices: Array of shape (200, 320) with values 0-15
        
    Returns:
        Bytes object of length 32000 (160 bytes per scanline × 200)
    """
    packed = bytearray(32000)
    offset = 0
    
    for y in range(200):
        for x in range(0, 320, 2):
            pixel0 = int(pixel_indices[y, x]) & 0x0F
            pixel1 = int(pixel_indices[y, x + 1]) & 0x0F
            
            # Pack two pixels into one byte: [pixel1:4bits][pixel0:4bits]
            packed[offset] = (pixel1 << 4) | pixel0
            offset += 1
    
    return bytes(packed)


def pack_palette_data(palettes: List[np.ndarray]) -> bytes:
    """
    Pack palette data into Apple IIgs format.
    
    Each palette has 16 colors, each color is 2 bytes (16-bit):
    - Format: 0000_BBBB_GGGG_RRRR (12-bit color)
    
    Args:
        palettes: List of up to 16 palettes, each (16, 3) RGB array
        
    Returns:
        Bytes object of length 512 (16 palettes × 16 colors × 2 bytes)
    """
    from .color import rgb24_to_iigs12
    
    packed = bytearray(512)
    offset = 0
    
    # Pack each palette
    for palette_idx in range(16):
        if palette_idx < len(palettes):
            palette = palettes[palette_idx]
            
            # Each palette has 16 colors
            for color_idx in range(16):
                if color_idx < len(palette):
                    rgb = palette[color_idx]
                    color_12bit = rgb24_to_iigs12(rgb)
                else:
                    color_12bit = 0  # Black for missing colors
                
                # Write as little-endian 16-bit value
                packed[offset] = color_12bit & 0xFF
                packed[offset + 1] = (color_12bit >> 8) & 0xFF
                offset += 2
        else:
            # Fill unused palette slots with black
            for color_idx in range(16):
                packed[offset] = 0
                packed[offset + 1] = 0
                offset += 2
    
    return bytes(packed)


def generate_scb_bytes(palette_indices: np.ndarray) -> np.ndarray:
    """
    Generate SCB (Scan Line Control Bytes) for per-scanline palette selection.
    
    Args:
        palette_indices: Array of shape (200,) with palette numbers 0-15 for each line
        
    Returns:
        Array of shape (200,) with SCB bytes
    """
    scb = np.zeros(200, dtype=np.uint8)
    
    for y in range(200):
        palette_num = int(palette_indices[y]) & 0x0F
        # SCB format: 0000_PPPP where PPPP is palette number
        # (Bits 4-7 control fill mode, interrupts, etc. - we use 0 for standard 320 mode)
        scb[y] = palette_num
    
    return scb


def read_3200_file(input_path: str) -> tuple:
    """
    Read an Apple IIgs .3200 format file.
    
    Useful for validation and testing.
    
    Args:
        input_path: Path to .3200 file
        
    Returns:
        Tuple of (pixel_indices, scb_bytes, palettes)
    """
    data = Path(input_path).read_bytes()
    
    if len(data) != 32768:
        raise ValueError(f"Invalid .3200 file size: {len(data)} bytes (expected 32768)")
    
    # Unpack pixel data
    pixel_indices = unpack_pixel_data(data[0:32000])
    
    # Extract SCB bytes
    scb_bytes = np.frombuffer(data[32000:32200], dtype=np.uint8)
    
    # Unpack palette data
    palettes = unpack_palette_data(data[32256:32768])
    
    return pixel_indices, scb_bytes, palettes


def unpack_pixel_data(data: bytes) -> np.ndarray:
    """
    Unpack pixel data from Apple IIgs format.
    
    Args:
        data: 32000 bytes of packed pixel data
        
    Returns:
        Array of shape (200, 320) with pixel indices
    """
    from .color import iigs12_to_rgb24
    
    pixel_indices = np.zeros((200, 320), dtype=np.uint8)
    offset = 0
    
    for y in range(200):
        for x in range(0, 320, 2):
            byte = data[offset]
            pixel0 = byte & 0x0F
            pixel1 = (byte >> 4) & 0x0F
            pixel_indices[y, x] = pixel0
            pixel_indices[y, x + 1] = pixel1
            offset += 1
    
    return pixel_indices


def unpack_palette_data(data: bytes) -> List[np.ndarray]:
    """
    Unpack palette data from Apple IIgs format.
    
    Args:
        data: 512 bytes of packed palette data
        
    Returns:
        List of 16 palettes, each array of shape (16, 3) RGB
    """
    from .color import iigs12_to_rgb24
    
    palettes = []
    offset = 0
    
    for palette_idx in range(16):
        palette = np.zeros((16, 3), dtype=np.uint8)
        
        for color_idx in range(16):
            # Read little-endian 16-bit value
            color_12bit = data[offset] | (data[offset + 1] << 8)
            rgb = iigs12_to_rgb24(color_12bit)
            palette[color_idx] = rgb
            offset += 2
        
        palettes.append(palette)
    
    return palettes

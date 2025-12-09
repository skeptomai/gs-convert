# Apple IIgs Image Conversion Guide

## Overview

This guide covers the graphics capabilities of the Apple IIgs and approaches for converting modern image formats (JPEG, PNG) to Apple IIgs-compatible formats.

## Apple IIgs Graphics Capabilities

### Super High-Resolution (SHR) Graphics

The Apple IIgs's primary graphics mode is **Super High-Resolution** (SHR), which offers:

**Resolution Options:**
- **320x200 pixels** - Standard SHR mode (most common)
- **640x200 pixels** - Available in limited color modes

**Color Depth:**
- **12-bit color palette** - 4096 possible colors (4 bits each for red, green, blue)
- Colors are selected from this 4096-color palette, not arbitrary 24-bit RGB

**Color Limitations:**
- **320x200 mode**: Up to 16 colors per scanline (out of 4096 possible)
- **640x200 mode**: 4 colors per scanline or 16 colors total (dithering mode)

**Palette Structure:**
- 16 color palettes total (numbered 0-15)
- Each scanline can use a different palette
- Each palette contains 16 colors selected from the 4096-color space

### Fill Modes

The Apple IIgs supports two primary fill modes:

1. **320 mode** - Standard color mode with full 16-color palette per line
2. **640 mode** - Higher resolution but with color restrictions

## Common Apple IIgs Image Formats

### 1. **APF (Apple Preferred Format)**
- Most common packed SHR format
- Contains palette and pixel data
- Typical extension: `.APF`
- Includes SCB (Scan Line Control Bytes) for per-line palette selection

### 2. **3200 / $C1 Format**
- Unpacked SHR format
- Exactly 32,000 bytes ($7D00)
- Contains raw pixel data and palette tables
- Sometimes called "Paintworks format"
- Typical extensions: `.3200`, `.PIC`, `.SHR`

### 3. **Packed SHR (PNT, BIN)**
- PackBytes compression
- Various subtypes depending on the creating application
- Common extensions: `.PNT`, `.BIN`, `.PIC`

### 4. **DreamGrafix (3201)**
- Similar to 3200 format with additional data
- 32,001 bytes
- Includes QuickDraw II auxiliary information

## Color Representation

### 12-bit Color Breakdown

Apple IIgs colors are stored in 16-bit words with the following format:
```
Bit:  15  14  13  12  11  10   9   8   7   6   5   4   3   2   1   0
     [--][---- Blue ----][--- Green ----][---- Red -----]
      ^
      |
      Reserved (always 0)
```

Each color component (R, G, B) uses 4 bits, giving 16 intensity levels (0-15).

**Example color values:**
- `0x0FFF` = White (R=15, G=15, B=15)
- `0x0000` = Black (R=0, G=0, B=0)
- `0x0F00` = Bright Red (R=15, G=0, B=0)
- `0x00F0` = Bright Green (R=0, G=15, B=0)
- `0x000F` = Bright Blue (R=0, G=0, B=15)

## Conversion Approaches

### Approach 1: Direct Palette Mapping with Dithering

**Strategy:**
1. Resize source image to 320x200
2. Convert from 24-bit RGB to 12-bit RGB color space
3. For each scanline, find the best 16 colors from the 4096 palette
4. Apply Floyd-Steinberg or ordered dithering to map pixels to available colors
5. Generate SCB bytes to select appropriate palette for each line

**Tools/Libraries:**
- ImageMagick (for resizing and color quantization)
- Python with PIL/Pillow (for custom dithering algorithms)
- Custom C/C++ code for precise control

**Command-line example (ImageMagick):**
```bash
# Resize and reduce to limited color palette
convert input.jpg \
  -resize 320x200! \
  -ordered-dither o8x8,16 \
  -colors 256 \
  output.png
```

### Approach 2: Median Cut Algorithm per Scanline

**Strategy:**
1. Process image scanline by scanline
2. For each of the 200 scanlines:
   - Extract the 320 pixels
   - Apply median cut algorithm to find best 16 colors
   - Map pixels to those 16 colors
3. Store palette selections in SCB bytes

**Advantages:**
- Better color fidelity per scanline
- Optimal use of per-line palette changes

**Disadvantages:**
- May create visible palette shifts between lines
- More complex to implement

### Approach 3: Global 256-Color Palette with Best-Fit

**Strategy:**
1. Reduce entire image to 256 colors using advanced quantization
2. Map the 256-color image to 16 palettes of 16 colors each
3. For each scanline, choose the palette that minimizes error
4. Dither pixels to available colors in chosen palette

**Tools:**
- `pnmquant` or ImageMagick's `-colors` option
- Custom palette assignment algorithm

### Approach 4: Use Existing Conversion Tools

**Recommended Tools:**

1. **JACE (Java Apple Computer Emulator)**
   - Can import modern images
   - Exports to Apple IIgs formats

2. **GSPort / KEGS Emulator**
   - Supports image conversion utilities
   - Can mount disk images with converted graphics

3. **Brutal Deluxe's Cadius**
   - Disk image utility for Apple II
   - Can work with ProDOS disk images containing graphics

4. **Apple IIgs Image Converter (Python-based)**
   - Several open-source Python scripts exist on GitHub
   - Look for `apple2-image-converter` or similar projects

5. **SuperConvert (vintage tool)**
   - Runs on actual Apple IIgs
   - Can import from various sources

## Recommended Conversion Pipeline

### Phase 1: Image Preprocessing
```bash
# 1. Resize to target resolution
convert input.jpg -resize 320x200! resized.png

# 2. Reduce color depth to 12-bit equivalent
convert resized.png -depth 4 -colorspace RGB reduced.png

# 3. Apply dithering
convert reduced.png -ordered-dither o8x8,16 dithered.png
```

### Phase 2: Custom Conversion Script

Create a script (Python, C, etc.) that:
1. Reads the preprocessed image
2. Analyzes each scanline for optimal color selection
3. Builds palette tables (16 palettes × 16 colors each)
4. Generates SCB bytes for palette selection
5. Creates pixel data in Apple IIgs format
6. Outputs to `.3200` or `.APF` format

### Phase 3: Transfer to Apple IIgs

1. Create a ProDOS disk image using `Cadius` or `CiderPress`
2. Copy the converted image file to the disk image
3. Mount in emulator (GSPort, MAME) or transfer to real hardware

## File Format Specifications

### 3200 Format Structure

```
Offset   Size    Description
------   ----    -----------
$0000    32000   Pixel data (160 bytes × 200 scanlines)
$7D00      256   SCB bytes (200 used + 56 padding)
$7E00      512   Palette data (16 palettes × 16 colors × 2 bytes)
```

**Total Size:** 32,768 bytes (exactly 32KB)

### Pixel Data Organization

- Each scanline is 160 bytes
- Each byte contains 2 pixels (4 bits per pixel)
- Pixels are packed: `[pixel1:4bits][pixel0:4bits]`
- Pixel values index into the active palette (0-15)

### SCB (Scan Line Control Byte)

Each scanline has an SCB byte that controls:
- **Bits 0-3:** Palette number (0-15)
- **Bit 4:** Fill mode (0=320 mode, 1=640 mode)
- **Bit 5:** Interrupt enable
- **Bits 6-7:** Reserved

Most SHR images use simple SCB: `0x00` to `0x0F` for palette selection.

## Implementation Considerations

### Color Quantization Quality

- The jump from 24-bit to 12-bit color is significant
- Each channel loses precision (256 levels → 16 levels)
- Dithering is essential for good results
- Consider the intended viewing distance and display

### Dithering Algorithms

**Ordered Dithering:**
- Faster, more predictable
- Works well for retro aesthetic
- Pattern-based (Bayer matrix)

**Error Diffusion (Floyd-Steinberg):**
- Higher quality for photographs
- Slower computation
- Better for gradients and subtle transitions

### Aspect Ratio Correction

The Apple IIgs pixels are not square:
- Physical aspect ratio is approximately 4:3 for the display
- Pixel aspect ratio in 320x200 mode is roughly 1.2:1
- Consider pre-stretching images horizontally by ~20% before conversion

### Testing and Iteration

1. Start with simple test images (gradients, color charts)
2. Test on emulator before real hardware
3. Iterate on dithering and palette selection parameters
4. Compare against original to tune conversion quality

## Example Python Pseudocode

```python
from PIL import Image
import numpy as np

def convert_to_iigs(input_path, output_path):
    # Load and resize image
    img = Image.open(input_path)
    img = img.resize((320, 200), Image.LANCZOS)
    
    # Convert to RGB and reduce to 12-bit color space
    img = img.convert('RGB')
    pixels = np.array(img)
    pixels = (pixels // 16) * 16  # Reduce to 4-bit per channel
    
    # For each scanline, find best 16 colors
    palettes = []
    scb_bytes = []
    pixel_data = []
    
    for y in range(200):
        scanline = pixels[y]
        
        # Quantize to 16 colors (simplified)
        palette = find_best_16_colors(scanline)
        palettes.append(palette)
        scb_bytes.append(len(palettes) - 1)  # Use this palette
        
        # Map pixels to palette indices
        line_pixels = map_to_palette(scanline, palette)
        pixel_data.append(pack_pixels(line_pixels))
    
    # Write to .3200 format
    write_3200_file(output_path, pixel_data, scb_bytes, palettes)

def rgb24_to_iigs12(r, g, b):
    """Convert 24-bit RGB to Apple IIgs 12-bit color"""
    r4 = r >> 4  # Take top 4 bits
    g4 = g >> 4
    b4 = b >> 4
    return (b4 << 8) | (g4 << 4) | r4
```

## Resources and Further Reading

### Online Resources
- **Apple IIgs Technical Reference Manual** - Official documentation
- **Brutal Deluxe Software** - Tools and file format specifications
- **AppleWin/GSPort Source Code** - Reference implementations
- **comp.sys.apple2** newsgroup archives - Historical discussions

### GitHub Projects
- Search for "apple2 image converter" or "apple iigs graphics"
- Many Python and C implementations available
- Some include full file format parsing

### Emulators for Testing
- **GSPort** - Excellent Apple IIgs emulator (Windows, macOS, Linux)
- **MAME** - Multi-system emulator with Apple IIgs support
- **Sweet16** - macOS-specific emulator

## Summary

Converting modern images to Apple IIgs format requires:
1. Understanding the 12-bit color space and per-scanline palette limitations
2. Careful color quantization and dithering
3. Proper formatting to .3200, .APF, or similar formats
4. Testing on emulator or real hardware

The best approach balances automation (ImageMagick preprocessing) with custom code for Apple IIgs-specific format generation. Starting with existing open-source converters and modifying them for your needs is often the most practical path.

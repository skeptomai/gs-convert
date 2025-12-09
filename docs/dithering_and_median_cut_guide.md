# Advanced Color Quantization for Apple IIgs: Dithering Algorithms and Median Cut

## Overview

This guide explores various dithering algorithms and the median cut quantization technique, with specific application to Apple IIgs image conversion. Understanding these approaches helps you choose the best method for different image types and achieve optimal results.

## Dithering Algorithms

Dithering creates the illusion of color depth by distributing quantization error to neighboring pixels. Different algorithms vary in how they distribute this error, affecting the final image quality, processing time, and visual characteristics.

### Error Diffusion Dithering

Error diffusion algorithms work by:
1. Quantizing a pixel to the nearest available color
2. Calculating the quantization error (difference between original and quantized color)
3. Distributing this error to neighboring unprocessed pixels
4. Processing pixels in a specific order (usually left-to-right, top-to-bottom)

#### 1. Floyd-Steinberg Dithering

**Developed:** 1976 by Robert Floyd and Louis Steinberg

**Error Distribution:**
```
         X   7/16
   3/16 5/16 1/16
```

Where `X` is the current pixel, and fractions show how error is distributed to neighbors.

**Characteristics:**
- Most widely used error diffusion algorithm
- Good balance of quality and simplicity
- Can create diagonal artifacts in some images
- Diffuses error to 4 neighboring pixels
- Total error distributed: 16/16 (100%)

**Strengths:**
- Excellent for photographs and natural images
- Smooth gradients
- Well-tested and reliable

**Weaknesses:**
- Can create "worm" artifacts in flat areas
- Diagonal patterns in some images
- Error accumulation can cause banding

**Implementation:**
```python
def floyd_steinberg_dither(image, palette):
    height, width = image.shape[:2]
    output = image.copy().astype(float)
    
    for y in range(height):
        for x in range(width):
            old_pixel = output[y, x]
            new_pixel = find_closest_color(old_pixel, palette)
            output[y, x] = new_pixel
            
            error = old_pixel - new_pixel
            
            if x + 1 < width:
                output[y, x + 1] += error * 7/16
            if y + 1 < height:
                if x > 0:
                    output[y + 1, x - 1] += error * 3/16
                output[y + 1, x] += error * 5/16
                if x + 1 < width:
                    output[y + 1, x + 1] += error * 1/16
    
    return output
```

#### 2. Atkinson Dithering

**Developed:** 1984 by Bill Atkinson for the original Macintosh

**Error Distribution:**
```
         X   1/8 1/8
   1/8 1/8 1/8
       1/8
```

**Characteristics:**
- Only distributes 6/8 (75%) of error, discarding 2/8
- Creates high-contrast, artistic results
- More "crispy" appearance than Floyd-Steinberg
- Diffuses error to 6 neighboring pixels across 2 rows
- Distinctive aesthetic associated with early Mac graphics

**Strengths:**
- Excellent for line art and illustrations
- High contrast, sharp details
- Less "muddy" than Floyd-Steinberg
- Distinctive retro aesthetic (perfect for Apple II!)
- Tends to preserve highlights better
- Good for text and diagrams

**Weaknesses:**
- Can lose shadow detail (error discarding)
- May appear too harsh for photographs
- Potential for banding in gradients
- Error loss can cause brightness shifts

**Why It Works for Apple IIgs:**
- The aesthetic matches the retro computing era
- High contrast compensates for limited color palette
- Preserves sharp details that might be lost with other methods
- The "incomplete" error distribution actually helps with per-scanline palette changes

**Implementation:**
```python
def atkinson_dither(image, palette):
    height, width = image.shape[:2]
    output = image.copy().astype(float)
    
    for y in range(height):
        for x in range(width):
            old_pixel = output[y, x]
            new_pixel = find_closest_color(old_pixel, palette)
            output[y, x] = new_pixel
            
            error = old_pixel - new_pixel
            
            # Distribute only 6/8 of error
            if x + 1 < width:
                output[y, x + 1] += error * 1/8
            if x + 2 < width:
                output[y, x + 2] += error * 1/8
            
            if y + 1 < height:
                if x > 0:
                    output[y + 1, x - 1] += error * 1/8
                output[y + 1, x] += error * 1/8
                if x + 1 < width:
                    output[y + 1, x + 1] += error * 1/8
            
            if y + 2 < height:
                output[y + 2, x] += error * 1/8
    
    return output
```

#### 3. Jarvis-Judice-Ninke (JJN) Dithering

**Developed:** 1976 by J.F. Jarvis, C.N. Judice, and W.H. Ninke

**Error Distribution:**
```
         X   7/48 5/48
   3/48 5/48 7/48 5/48 3/48
   1/48 3/48 5/48 3/48 1/48
```

**Characteristics:**
- Distributes error to 12 neighboring pixels
- Very smooth results with minimal artifacts
- Slower processing due to larger kernel
- Best for high-quality conversions

**Strengths:**
- Exceptional smoothness
- Minimal visible patterns
- Excellent for photographs

**Weaknesses:**
- Computationally expensive
- Can be "too smooth" for retro aesthetic
- Slower processing time

#### 4. Stucki Dithering

**Developed:** 1981 by P. Stucki

**Error Distribution:**
```
         X   8/42 4/42
   2/42 4/42 8/42 4/42 2/42
   1/42 2/42 4/42 2/42 1/42
```

**Characteristics:**
- Similar to JJN but with different weights
- 12 neighbor distribution
- Slightly more contrast than JJN

**Best For:**
- High-quality photographic conversions
- When processing time is not critical

#### 5. Burkes Dithering

**Developed:** 1988 by Daniel Burkes

**Error Distribution:**
```
         X   8/32 4/32
   2/32 4/32 8/32 4/32 2/32
```

**Characteristics:**
- Simplified version of Stucki
- Only 2 rows instead of 3
- Good balance of quality and speed

**Best For:**
- General-purpose dithering
- Faster alternative to JJN/Stucki

#### 6. Sierra Dithering

**Multiple Variants:**

**Sierra-3 (Two-Row Sierra):**
```
         X   5/32 3/32
   2/32 4/32 5/32 4/32 2/32
   0    2/32 3/32 2/32 0
```

**Sierra-2 (Sierra Lite):**
```
         X   4/16 3/16
   1/16 2/16 3/16 2/16 1/16
```

**Sierra-2-4A (Filter Lite):**
```
         X   2/4
   1/4  1/4
```

**Characteristics:**
- Sierra-3 provides high quality with reasonable speed
- Sierra-2 is faster with good results
- Sierra-2-4A is very fast but lower quality

### Ordered Dithering (Bayer Matrix)

**Approach:**
- Uses a predetermined threshold map (Bayer matrix)
- No error diffusion between pixels
- Deterministic and parallelizable
- Creates characteristic crosshatch patterns

**Bayer Matrix 2×2:**
```
[0  2]   / 4
[3  1]
```

**Bayer Matrix 4×4:**
```
[ 0  8  2 10]   / 16
[12  4 14  6]
[ 3 11  1  9]
[15  7 13  5]
```

**Characteristics:**
- Very fast (no error propagation)
- Predictable, regular patterns
- Good for retro aesthetic
- Can be computed in parallel
- Creates visible texture/grain

**Best For:**
- Retro/pixel art aesthetic
- Real-time processing
- When speed is critical
- Textures and patterns

**Implementation:**
```python
def bayer_dither(image, palette, matrix_size=8):
    bayer_matrix = generate_bayer_matrix(matrix_size)
    height, width = image.shape[:2]
    output = np.zeros_like(image)
    
    for y in range(height):
        for x in range(width):
            threshold = bayer_matrix[y % matrix_size, x % matrix_size] / (matrix_size**2)
            pixel = image[y, x] + threshold - 0.5
            output[y, x] = find_closest_color(pixel, palette)
    
    return output
```

## Comparison Table: Dithering Algorithms

| Algorithm | Speed | Quality | Artifacts | Best For |
|-----------|-------|---------|-----------|----------|
| Floyd-Steinberg | Fast | High | Diagonal worms | General purpose, photos |
| Atkinson | Fast | Medium-High | Brightness loss | Line art, retro aesthetic |
| JJN | Slow | Very High | Minimal | High-quality photos |
| Stucki | Slow | Very High | Minimal | High-quality photos |
| Burkes | Medium | High | Minimal | Good compromise |
| Sierra-3 | Medium | High | Minimal | Photos, natural images |
| Sierra-2 | Fast | Medium | Some patterns | Faster alternative |
| Bayer/Ordered | Very Fast | Medium | Regular patterns | Retro, real-time |

## Median Cut Algorithm

### What Is Median Cut?

Median cut is a **color quantization** algorithm, not a dithering algorithm. It solves a different problem:

- **Dithering:** How to represent an image using a fixed palette
- **Median Cut:** How to choose the best colors for a palette

### How Median Cut Works

**Algorithm Steps:**

1. **Start with all pixels** in the image in a single "bucket"

2. **Find the color channel** (R, G, or B) with the widest range in this bucket

3. **Sort pixels** by their value in that channel

4. **Split at the median** - divide the bucket into two buckets of equal pixel count

5. **Repeat steps 2-4** on each bucket until you have the desired number of colors

6. **Calculate representative color** for each final bucket (usually the mean or median)

**Example for 4 colors:**
```
Start: [All pixels]
  ↓ Split on Red (widest range)
[Half pixels] [Half pixels]
  ↓ Split each         ↓ Split each
[Quarter]  [Quarter]  [Quarter]  [Quarter]
```

Result: 4 representative colors, each representing a roughly equal number of pixels.

### Median Cut vs. Other Quantization Methods

**Median Cut Advantages:**
- Adaptive to image content
- Guarantees good coverage of color space
- Balances color frequency with color diversity
- Fast and efficient

**Alternatives:**

1. **Popularity Algorithm**
   - Simply picks the N most common colors
   - Fast but can miss important but rare colors
   - Poor for images with many similar colors

2. **Octree Quantization**
   - Uses a tree structure in RGB space
   - Can be faster for large palettes
   - Similar quality to median cut

3. **K-Means Clustering**
   - Iteratively refines color centers
   - Can produce better results than median cut
   - Slower and non-deterministic

### Median Cut for Apple IIgs

**Per-Scanline Application:**

For Apple IIgs with 16 colors per scanline, you can apply median cut individually to each scanline:

```python
def quantize_scanline_median_cut(scanline_pixels, num_colors=16):
    """
    Apply median cut to a single scanline.
    
    Args:
        scanline_pixels: Array of RGB pixels (320 pixels × 3 channels)
        num_colors: Number of colors in palette (16 for Apple IIgs)
    
    Returns:
        palette: 16 RGB colors
        indices: 320 indices into the palette
    """
    # Start with all pixels in one bucket
    buckets = [scanline_pixels.copy()]
    
    # Split until we have 16 buckets
    while len(buckets) < num_colors:
        # Find bucket with largest range
        largest_bucket = max(buckets, key=lambda b: get_color_range(b))
        buckets.remove(largest_bucket)
        
        # Split this bucket
        bucket1, bucket2 = median_cut_split(largest_bucket)
        buckets.extend([bucket1, bucket2])
    
    # Calculate representative color for each bucket
    palette = [bucket.mean(axis=0) for bucket in buckets]
    
    # Map each pixel to nearest palette color
    indices = [find_nearest_palette_index(pixel, palette) 
               for pixel in scanline_pixels]
    
    return palette, indices

def median_cut_split(bucket):
    """Split a bucket at the median of its widest channel."""
    # Find channel with widest range
    ranges = bucket.max(axis=0) - bucket.min(axis=0)
    split_channel = ranges.argmax()
    
    # Sort by that channel and split at median
    sorted_bucket = bucket[bucket[:, split_channel].argsort()]
    mid = len(sorted_bucket) // 2
    
    return sorted_bucket[:mid], sorted_bucket[mid:]
```

**Advantages for Apple IIgs:**
- Each scanline gets optimal colors for its content
- No dithering needed if median cut creates good palette
- Clean, posterized look
- Faster than error diffusion

**Disadvantages:**
- Visible banding between color regions
- Sharp transitions between palette boundaries
- May not be smooth enough for gradients
- Palette changes between scanlines can be jarring

### Median Cut + Dithering: The Best of Both Worlds

**Combined Approach:**

1. **Use median cut** to find optimal palette
2. **Apply dithering** when mapping pixels to palette

```python
def convert_with_median_cut_and_dither(image):
    """
    Use median cut for palette selection and Atkinson for rendering.
    """
    output_pixels = []
    scb_bytes = []
    palettes = []
    
    for y in range(200):
        scanline = image[y, :]
        
        # Step 1: Find best 16 colors using median cut
        palette, _ = quantize_scanline_median_cut(scanline, 16)
        
        # Convert to Apple IIgs 12-bit color space
        palette_12bit = [rgb24_to_iigs12(c) for c in palette]
        palettes.append(palette_12bit)
        scb_bytes.append(len(palettes) - 1)
        
        # Step 2: Use Atkinson dithering to map pixels
        # (Would need to integrate with full image dithering)
        line_pixels = atkinson_dither_scanline(scanline, palette)
        output_pixels.append(pack_pixels(line_pixels))
    
    return output_pixels, scb_bytes, palettes
```

**Why This Works:**
- Median cut ensures palette colors are actually present in the image
- Dithering smooths transitions between palette colors
- Combines optimal color selection with optimal rendering
- Better than dithering with a fixed global palette
- Better than median cut alone without dithering

## When to Use Each Approach

### Use Median Cut Alone When:
- You want a clean, posterized look
- The image has distinct color regions
- Processing speed is critical
- You're converting graphics/illustrations (not photos)
- You want to avoid dithering artifacts

### Use Dithering Alone When:
- You have a pre-defined palette (e.g., global 256-color palette)
- You need smooth gradients
- Working with photographs
- The image has subtle color variations

### Use Median Cut + Dithering When:
- You want the best quality (recommended for Apple IIgs)
- Converting photographs
- You need smooth results but want optimal color selection
- Processing time is not critical

### Use Ordered Dithering When:
- You want a retro aesthetic
- Speed is crucial
- The image will be viewed at small size
- You're creating tile-based graphics

### Use Atkinson Dithering When:
- Converting for vintage computers (perfect era match)
- Working with line art or illustrations
- You want high-contrast, sharp results
- The image has text or fine details
- You want the classic Macintosh aesthetic

## Practical Recommendations for Apple IIgs

### For Photographs:
**Approach:** Median Cut + Floyd-Steinberg or Atkinson
```
1. Resize to 320×200
2. Apply per-scanline median cut to find 16 colors/line
3. Use Atkinson dithering for retro look OR Floyd-Steinberg for smoother result
4. Generate .3200 file
```

### For Pixel Art/Graphics:
**Approach:** Median Cut alone or with minimal dithering
```
1. Resize to 320×200 with nearest-neighbor
2. Apply median cut per scanline
3. No dithering OR light ordered dithering
4. Generate .3200 file
```

### For Line Art/Comics:
**Approach:** Atkinson Dithering with optimized palette
```
1. Resize to 320×200
2. Apply median cut to whole image for global palette
3. Use Atkinson dithering throughout
4. High contrast works well here
```

### For Mixed Content:
**Approach:** Adaptive per region
```
1. Detect regions (photo vs. text vs. graphics)
2. Apply different algorithms to different regions
3. Blend results
4. More complex but best quality
```

## Implementation Tips

### Color Space Considerations

**Work in Linear RGB:**
```python
def srgb_to_linear(srgb):
    """Convert sRGB to linear RGB for better quantization."""
    srgb = srgb / 255.0
    linear = np.where(srgb <= 0.04045,
                      srgb / 12.92,
                      ((srgb + 0.055) / 1.055) ** 2.4)
    return linear

def linear_to_srgb(linear):
    """Convert linear RGB back to sRGB."""
    srgb = np.where(linear <= 0.0031308,
                    linear * 12.92,
                    1.055 * (linear ** (1/2.4)) - 0.055)
    return (srgb * 255).astype(np.uint8)
```

Working in linear RGB ensures perceptually uniform color mixing and error calculations.

### Apple IIgs 12-bit Color Precision

```python
def rgb24_to_iigs12(rgb):
    """Convert 24-bit RGB to Apple IIgs 12-bit format."""
    r, g, b = rgb
    r4 = int(r / 255.0 * 15 + 0.5)  # Round to nearest
    g4 = int(g / 255.0 * 15 + 0.5)
    b4 = int(b / 255.0 * 15 + 0.5)
    return (b4 << 8) | (g4 << 4) | r4

def iigs12_to_rgb24(color):
    """Convert Apple IIgs 12-bit to 24-bit RGB."""
    r4 = color & 0x0F
    g4 = (color >> 4) & 0x0F
    b4 = (color >> 8) & 0x0F
    r = int(r4 / 15.0 * 255)
    g = int(g4 / 15.0 * 255)
    b = int(b4 / 15.0 * 255)
    return (r, g, b)
```

### Optimizing Per-Scanline Processing

```python
def optimize_palette_transitions(palettes, scb_bytes):
    """
    Smooth palette transitions between scanlines to reduce flicker.
    """
    # For each adjacent scanline pair
    for i in range(len(scb_bytes) - 1):
        palette_curr = palettes[scb_bytes[i]]
        palette_next = palettes[scb_bytes[i + 1]]
        
        # Try to reorder palette_next colors to match palette_curr
        # This minimizes visual discontinuity
        palette_next_reordered = reorder_to_match(palette_curr, palette_next)
        palettes[scb_bytes[i + 1]] = palette_next_reordered
```

## Example Complete Pipeline

```python
from PIL import Image
import numpy as np

def convert_image_to_iigs(input_path, output_path, method='median_cut_atkinson'):
    # Load image
    img = Image.open(input_path).convert('RGB')
    
    # Resize with aspect ratio correction
    img = img.resize((320, 200), Image.LANCZOS)
    pixels = np.array(img)
    
    # Convert to linear RGB for better processing
    pixels_linear = srgb_to_linear(pixels)
    
    output_data = []
    palettes = []
    scb_bytes = []
    
    for y in range(200):
        scanline = pixels_linear[y]
        
        # Find optimal 16 colors using median cut
        palette_linear, _ = quantize_scanline_median_cut(scanline, 16)
        
        # Convert palette to Apple IIgs 12-bit
        palette_srgb = linear_to_srgb(palette_linear)
        palette_12bit = [rgb24_to_iigs12(c) for c in palette_srgb]
        
        palettes.append(palette_12bit)
        scb_bytes.append(len(palettes) - 1)
    
    # Now apply dithering with per-scanline palettes
    pixels_dithered = atkinson_dither_with_palettes(pixels_linear, palettes, scb_bytes)
    
    # Pack pixel data
    for y in range(200):
        line_pixels = pixels_dithered[y]
        output_data.append(pack_pixels(line_pixels))
    
    # Write to .3200 format
    write_3200_file(output_path, output_data, scb_bytes, palettes)
```

## Summary

### Key Takeaways

1. **Atkinson dithering** is ideal for Apple IIgs due to its era-appropriate aesthetic and high-contrast results that work well with limited palettes

2. **Median cut** is a color quantization algorithm that finds optimal palette colors, complementing rather than replacing dithering

3. **Best approach:** Combine median cut (for palette selection) with Atkinson or Floyd-Steinberg (for rendering)

4. **For speed:** Use ordered/Bayer dithering

5. **For quality:** Use JJN or Stucki dithering

6. **For retro aesthetic:** Use Atkinson or ordered dithering

7. **Per-scanline processing** leverages the Apple IIgs's unique capability to change palettes 200 times

### Recommended Workflow

```
Input Image (JPEG/PNG)
    ↓
Resize to 320×200 with aspect ratio correction
    ↓
Convert to linear RGB color space
    ↓
For each scanline:
  - Apply median cut → get 16 optimal colors
  - Convert to Apple IIgs 12-bit color
  - Store palette and SCB byte
    ↓
Apply Atkinson dithering with per-scanline palettes
    ↓
Pack pixels to 4-bit indices
    ↓
Write .3200 format file
    ↓
Test on emulator (GSPort/MAME)
```

This combined approach provides the best color fidelity and appropriate retro aesthetic for the Apple IIgs platform.

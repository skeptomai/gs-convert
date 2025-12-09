# Palette Optimization Feature

## The Banding Problem

When converting images with large solid-color areas using per-scanline quantization, you may notice horizontal banding artifacts. This happens because each scanline generates its own 16-color palette, and even slight variations in palette selection between adjacent lines creates visible bands.

### Example of Banding

```
Scanline 1: Blue area → Palette finds "Blue A" (RGB 100, 150, 200)
Scanline 2: Blue area → Palette finds "Blue B" (RGB 101, 149, 201)  
Scanline 3: Blue area → Palette finds "Blue C" (RGB 99, 151, 199)
                                ↓
                    Visible horizontal bands
```

## The Solution: Palette Optimization

The `--optimize-palettes` flag enables intelligent palette reuse across adjacent scanlines:

1. Generate optimal palette for first scanline
2. For each subsequent scanline:
   - Try using the previous scanline's palette
   - Calculate quantization error
   - If error is acceptable, **reuse the palette** (no banding!)
   - If error is too high, generate a new palette

### Result

- **Solid areas**: Same palette across many scanlines → No banding
- **Complex areas**: New palettes where needed → Good quality
- **Best of both worlds**: Eliminates banding while preserving quality

## Usage

### Basic Usage

```bash
# Enable palette optimization
gs-convert convert image.jpg output.3200 --optimize-palettes --preview preview.png

# Or use the 'optimized' quantization method
gs-convert convert image.jpg output.3200 --quantize optimized --preview preview.png
```

### Adjusting the Error Threshold

The `--error-threshold` parameter controls when a new palette is created:

```bash
# More aggressive reuse (less banding, possible quality loss)
gs-convert convert image.jpg output.3200 --optimize-palettes --error-threshold 5000.0

# More conservative (more new palettes, better quality, some banding)
gs-convert convert image.jpg output.3200 --optimize-palettes --error-threshold 1000.0

# Default (good balance)
gs-convert convert image.jpg output.3200 --optimize-palettes --error-threshold 2000.0
```

**Threshold Guidelines:**
- **500-1000**: Very conservative, many palettes, minimal reuse
- **2000** (default): Good balance for most images
- **5000-10000**: Aggressive reuse, fewer palettes, more banding reduction

## Comparison

### Test Image: Solid Color Areas

```bash
# Create test image
python examples/generate_test_image.py

# Default per-scanline (will show banding)
gs-convert convert examples/test_solid_areas.png default.3200 --preview default.png

# With palette optimization (eliminates banding)
gs-convert convert examples/test_solid_areas.png optimized.3200 --optimize-palettes --preview optimized.png

# Compare
open default.png optimized.png
```

### Results

**Default (per-scanline)**:
- Palettes used: 10-15 unique palettes
- Visible horizontal bands in solid areas
- Each scanline gets its own palette

**Optimized (palette reuse)**:
- Palettes used: 3-5 unique palettes
- Smooth solid areas, no banding
- Palettes shared across similar scanlines

## When to Use Palette Optimization

### ✅ Use --optimize-palettes when:

- Image has large solid-color areas (backgrounds, skies, etc.)
- You notice horizontal banding in converted images
- Working with illustrations, graphics, or UI elements
- Converting images with gradual color transitions

### ⚠️ May not be needed when:

- Using `--quantize global` (already shares palettes globally)
- Image is highly detailed everywhere (photos with lots of texture)
- Using `--dither none` with global quantization
- Already getting good results with default settings

## Technical Details

### Algorithm

```python
for each scanline:
    if first scanline:
        create new palette
    else:
        try previous palette
        calculate error
        if error <= threshold:
            reuse previous palette  # No new palette needed!
        else:
            create new palette      # Content changed enough
```

### Error Calculation

Error is the sum of squared distances between each pixel and its nearest palette color:

```
error = Σ(min_distance(pixel, palette)²) for all pixels in scanline
```

Lower error = palette matches scanline well → safe to reuse
Higher error = palette doesn't match well → need new palette

### Palette Limit

Apple IIgs supports maximum 16 unique palettes. The optimization algorithm:
1. Reuses palettes when possible (reduces count)
2. Deduplicates identical palettes
3. Falls back to best-fit when limit is reached

## Examples

### Example 1: Sky in Photo

```bash
# Photo with large blue sky area
gs-convert convert landscape.jpg landscape.3200 \
  --optimize-palettes \
  --dither atkinson \
  --preview landscape.png

# Result: Smooth sky, no horizontal bands
```

### Example 2: UI Screenshot

```bash
# Screenshot with solid backgrounds
gs-convert convert screenshot.png screenshot.3200 \
  --optimize-palettes \
  --dither none \
  --preview screenshot.png

# Result: Clean solid colors, professional look
```

### Example 3: Sunset Gradient

```bash
# Gradual color transition
gs-convert convert sunset.jpg sunset.3200 \
  --optimize-palettes \
  --error-threshold 3000 \
  --dither floyd-steinberg \
  --preview sunset.png

# Result: Smooth gradient with minimal banding
```

### Example 4: Complex Photo

```bash
# Highly detailed photo (may not need optimization)
gs-convert convert portrait.jpg portrait.3200 \
  --dither atkinson \
  --preview portrait.png

# Default works fine - lots of color variation anyway
```

## Combining with Other Options

### Best Combinations

```bash
# For solid areas with some detail
gs-convert convert image.jpg output.3200 \
  --optimize-palettes \
  --dither atkinson \
  --preview preview.png

# For very smooth results
gs-convert convert image.jpg output.3200 \
  --optimize-palettes \
  --dither floyd-steinberg \
  --error-threshold 2500 \
  --preview preview.png

# For clean graphics/illustrations
gs-convert convert image.jpg output.3200 \
  --optimize-palettes \
  --dither none \
  --error-threshold 5000 \
  --preview preview.png
```

### What NOT to do

```bash
# Don't combine with global quantization (redundant)
gs-convert convert image.jpg output.3200 \
  --quantize global \
  --optimize-palettes  # ← Not needed, global already shares palettes

# Instead, just use global
gs-convert convert image.jpg output.3200 --quantize global
```

## Troubleshooting

### Still seeing banding?

Try increasing the error threshold:
```bash
gs-convert convert image.jpg output.3200 \
  --optimize-palettes \
  --error-threshold 5000  # ← Increase from default 2000
```

### Colors look washed out?

Try lowering the error threshold or use default per-scanline:
```bash
gs-convert convert image.jpg output.3200 \
  --optimize-palettes \
  --error-threshold 1000  # ← More conservative
```

### Want to see how many palettes are used?

```bash
gs-convert info output.3200
# Shows: "Unique palettes used: X/16"
```

## Summary

**Problem**: Horizontal banding in solid-color areas

**Solution**: `--optimize-palettes`

**How it works**: Intelligently reuses palettes across similar scanlines

**When to use**: Images with solid areas, backgrounds, gradients

**Default threshold**: 2000 (adjust with `--error-threshold`)

**Result**: Smooth solid areas while maintaining quality in detailed regions

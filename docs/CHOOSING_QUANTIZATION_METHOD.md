# Choosing the Right Quantization Method

## Overview

gs-convert supports three quantization methods:
1. **median-cut** (default) - Per-scanline palette generation
2. **optimized** - Intelligent palette reuse across scanlines
3. **global** - Shared palettes across entire image

This guide helps you choose the right method for your image type.

## Quick Decision Guide

### Use `--quantize global` when:
- ✅ Animation artwork, cel-shaded graphics
- ✅ Images with limited color palettes
- ✅ Illustrations, logos, UI screenshots
- ✅ Solid-color backgrounds (but simple color schemes)
- ✅ You want consistent colors across the entire image

### Use `--optimize-palettes` (or `--quantize optimized`) when:
- ✅ Photographs with large solid areas (sky, walls, floors)
- ✅ Images with gradual color transitions
- ✅ You see horizontal banding with default settings
- ✅ Mixed content (some solid areas, some detailed areas)

### Use default (median-cut) when:
- ✅ Highly detailed photographs
- ✅ Images with lots of color variation throughout
- ✅ Every scanline has significantly different content
- ✅ Maximum quality is priority over banding reduction

## Detailed Analysis

### Method 1: Default (median-cut per-scanline)

**How it works:**
```
For each of 200 scanlines:
  - Analyze the 320 pixels in that line
  - Find optimal 16 colors using median cut
  - Create new palette for this scanline
```

**Advantages:**
- Each scanline gets optimal colors for its content
- Maximum quality for complex images
- Leverages Apple IIgs's unique per-scanline capability

**Disadvantages:**
- Can create banding in solid-color areas
- Uses up to 16 unique palettes quickly
- Adjacent scanlines may have slightly different palettes

**Best for:**
- Detailed photographs
- Images with high color variation
- When quality is more important than banding

**Example:**
```bash
gs-convert convert photo.jpg output.3200
# or explicitly:
gs-convert convert photo.jpg output.3200 --quantize median-cut
```

---

### Method 2: Optimized (palette reuse)

**How it works:**
```
For first scanline:
  - Generate optimal 16-color palette
  
For each subsequent scanline:
  - Try previous scanline's palette
  - Calculate error (how well it fits)
  - If error <= threshold: REUSE palette
  - If error > threshold: Generate new palette
```

**Advantages:**
- Eliminates banding in solid-color areas
- Still allows palette changes where needed
- Balances quality and consistency
- Adjustable via --error-threshold

**Disadvantages:**
- May still use all 16 palettes on complex images
- Slightly slower than default
- Threshold tuning may be needed

**Best for:**
- Photos with solid backgrounds (sky, walls)
- Images with gradual transitions
- When you see banding with default method
- Mixed content (solid + detailed areas)

**Example:**
```bash
gs-convert convert photo.jpg output.3200 --optimize-palettes
# or
gs-convert convert photo.jpg output.3200 --quantize optimized

# Adjust threshold for more/less reuse
gs-convert convert photo.jpg output.3200 --optimize-palettes --error-threshold 5000
```

**Threshold guidelines:**
- **1000**: Conservative (many palettes, less reuse)
- **2000**: Default (balanced)
- **5000**: Aggressive (fewer palettes, more reuse)
- **10000**: Very aggressive (minimal palettes)

---

### Method 3: Global (shared palettes)

**How it works:**
```
1. Analyze entire image (all 64,000 pixels)
2. Create 16 optimal palettes (16 colors each = 256 total colors)
3. For each scanline, choose best-fitting palette from the 16
```

**Advantages:**
- Consistent colors across entire image
- Often uses fewer than 16 palettes
- Best for limited-palette images
- No banding in solid areas
- Perfect for animation artwork

**Disadvantages:**
- May not be optimal for any single scanline
- Less adaptive to local color variation
- Can lose detail in highly varied images

**Best for:**
- Animation artwork, cel-shaded graphics
- Illustrations, comics
- Images with limited color schemes
- Logo/UI screenshots
- When consistency matters more than local quality

**Example:**
```bash
gs-convert convert artwork.jpg output.3200 --quantize global

# Often best combined with no dithering for clean look
gs-convert convert artwork.jpg output.3200 --quantize global --dither none
```

---

## Real-World Case Study: Star Trek Animated Series

### The Image
- Animation artwork (cel-style)
- Large solid blue background (space)
- Distinct character colors (red, yellow, blue uniforms)
- Limited overall palette

### Test Results

| Method | Palettes Used | Result |
|--------|---------------|--------|
| Default (median-cut) | 16/16 | Visible banding in blue background |
| Optimized | 16/16 | Still uses all palettes, some banding |
| **Global** | **6/16** | Clean, consistent, no banding |

### Why Global Won

The animation artwork had:
1. Limited color palette overall (good for global)
2. Large solid areas (benefits from shared palettes)
3. Cel-style shading (doesn't need per-scanline precision)

**Result**: Global quantization only needed 6 palettes vs 16, eliminating banding.

### Recommended Command
```bash
gs-convert convert star_trek_animated.jpeg output.3200 \
  --quantize global \
  --dither none \
  --preview preview.png
```

---

## Comparison Matrix

| Image Type | Recommended | Alternative | Avoid |
|------------|-------------|-------------|-------|
| **Detailed Photo** | Default | Optimized | - |
| **Photo with Sky** | Optimized | Global | - |
| **Animation Art** | **Global** | Optimized | Default |
| **Pixel Art** | Global + no dither | Default + no dither | - |
| **Illustration** | Global | Optimized | - |
| **UI Screenshot** | Global + no dither | - | - |
| **Mixed Content** | Optimized | Default | - |
| **High Contrast** | Default | Optimized | - |

---

## Testing Your Image

Run these three commands to compare:

```bash
# Test 1: Default
gs-convert convert your_image.jpg test_default.3200 --preview test_default.png

# Test 2: Optimized
gs-convert convert your_image.jpg test_optimized.3200 \
  --optimize-palettes \
  --preview test_optimized.png

# Test 3: Global
gs-convert convert your_image.jpg test_global.3200 \
  --quantize global \
  --preview test_global.png

# Compare
open test_*.png

# Check palette usage
gs-convert info test_default.3200 | grep "Unique palettes"
gs-convert info test_optimized.3200 | grep "Unique palettes"
gs-convert info test_global.3200 | grep "Unique palettes"
```

**Look for:**
- Horizontal banding in solid areas → Try optimized or global
- Lost detail in complex areas → Use default
- Fewer palettes used → Better consistency
- More palettes used → More local adaptation

---

## Combining with Dithering

### For Animation/Graphics (Global)
```bash
# Clean, posterized (recommended for animation)
gs-convert convert image.jpg output.3200 --quantize global --dither none

# Smooth with subtle dithering
gs-convert convert image.jpg output.3200 --quantize global --dither atkinson

# Very smooth
gs-convert convert image.jpg output.3200 --quantize global --dither floyd-steinberg
```

### For Photos (Optimized)
```bash
# Retro look (recommended)
gs-convert convert photo.jpg output.3200 --optimize-palettes --dither atkinson

# Smooth gradients
gs-convert convert photo.jpg output.3200 --optimize-palettes --dither floyd-steinberg

# High quality
gs-convert convert photo.jpg output.3200 --optimize-palettes --dither jjn
```

### For Detailed Photos (Default)
```bash
# Retro, high contrast
gs-convert convert photo.jpg output.3200 --dither atkinson

# Smooth, photographic
gs-convert convert photo.jpg output.3200 --dither floyd-steinberg

# Maximum quality
gs-convert convert photo.jpg output.3200 --dither jjn
```

---

## Understanding Palette Usage

When you run `gs-convert info output.3200`, you'll see:

```
Unique palettes used: X/16
```

### What This Means

- **1-4 palettes**: Very consistent image, limited colors, global worked well
- **6-10 palettes**: Moderate variation, good balance
- **12-16 palettes**: High variation, lots of color diversity

### Interpreting Results

**If you used default/optimized and see 16/16:**
- Image is complex enough to need all 16 palettes
- This is normal for detailed photos
- Try global if you see banding

**If you used global and see 6/16:**
- Image has limited color palette
- Global was the right choice
- Should have minimal banding

**If you used optimized and see 16/16:**
- Even with reuse, image needs all palettes
- Adjacent scanlines are quite different
- Consider global if banding is still visible

---

## Common Scenarios

### Scenario 1: Banding in Sky
**Problem**: Horizontal bands in solid blue sky
**Solution**: 
```bash
gs-convert convert photo.jpg output.3200 --optimize-palettes
```

### Scenario 2: Animation Artwork Looks Wrong
**Problem**: Colors inconsistent, banding throughout
**Solution**:
```bash
gs-convert convert artwork.jpg output.3200 --quantize global --dither none
```

### Scenario 3: Detailed Photo Losing Quality
**Problem**: Details washed out, colors muddy
**Solution**:
```bash
gs-convert convert photo.jpg output.3200  # Use default
# or
gs-convert convert photo.jpg output.3200 --quantize median-cut
```

### Scenario 4: Logo/UI with Banding
**Problem**: Solid color areas have bands
**Solution**:
```bash
gs-convert convert logo.png output.3200 --quantize global --dither none
```

---

## Advanced: Combining Methods

You can also pre-process your image to reduce colors before conversion:

```bash
# Reduce to 64 colors first (helps with banding)
convert input.jpg -colors 64 reduced.png
gs-convert convert reduced.png output.3200 --optimize-palettes

# Or even more aggressive
convert input.jpg -colors 32 reduced.png
gs-convert convert reduced.png output.3200 --quantize global
```

---

## Summary

**Quick reference:**

| Goal | Command |
|------|---------|
| Maximum quality | `gs-convert convert img.jpg out.3200` |
| Reduce banding | `gs-convert convert img.jpg out.3200 --optimize-palettes` |
| Animation art | `gs-convert convert img.jpg out.3200 --quantize global --dither none` |
| Smooth photo | `gs-convert convert img.jpg out.3200 --optimize-palettes --dither floyd-steinberg` |
| Clean graphics | `gs-convert convert img.jpg out.3200 --quantize global --dither none` |

**The three key questions:**

1. **Is it animation/illustration?** → Use `--quantize global`
2. **Does it have banding in solid areas?** → Use `--optimize-palettes`
3. **Is it highly detailed throughout?** → Use default (no flags)

When in doubt, test all three and compare!

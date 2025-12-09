# Palette Optimization Feature - Quick Reference

## New Feature Added! ✨

Intelligent palette reuse to eliminate horizontal banding in images with solid-color areas.

## Quick Usage

```bash
# Enable palette optimization (recommended for images with solid areas)
gs-convert convert image.jpg output.3200 --optimize-palettes --preview preview.png

# Or use as quantization method
gs-convert convert image.jpg output.3200 --quantize optimized --preview preview.png
```

## The Problem It Solves

**Before** (default per-scanline):
- Each scanline gets its own palette
- Slight variations in solid-color areas
- Visible horizontal banding

**After** (with --optimize-palettes):
- Palettes reused across similar scanlines  
- Solid areas stay solid
- No banding!

## Test It Now

```bash
# Create test image with solid areas
python << 'PYTHON'
from PIL import Image, ImageDraw
img = Image.new('RGB', (640, 400))
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, 640, 133], fill=(100, 150, 200))  # Blue
draw.rectangle([0, 133, 640, 266], fill=(80, 180, 100))  # Green
draw.rectangle([0, 266, 640, 400], fill=(200, 80, 100))  # Red
img.save('test_banding.png')
PYTHON

# Convert without optimization (will show banding)
gs-convert convert test_banding.png without_opt.3200 --preview without_opt.png

# Convert with optimization (smooth!)
gs-convert convert test_banding.png with_opt.3200 --optimize-palettes --preview with_opt.png

# Compare the previews
open without_opt.png with_opt.png
```

## Options

### --optimize-palettes
Enable intelligent palette reuse

### --quantize optimized
Use optimized quantization method (same as --optimize-palettes)

### --error-threshold VALUE
Control when new palettes are created:
- **1000**: Conservative (more palettes, less reuse)
- **2000**: Default (balanced)
- **5000**: Aggressive (fewer palettes, more reuse)

## When to Use

✅ **Use it when:**
- Images have solid-color areas (skies, backgrounds)
- You notice horizontal banding
- Working with illustrations or UI screenshots

❌ **Not needed when:**
- Already using `--quantize global`
- Image is highly detailed everywhere
- Getting good results without it

## Examples

```bash
# Photo with sky
gs-convert convert photo.jpg photo.3200 --optimize-palettes

# UI screenshot
gs-convert convert ui.png ui.3200 --optimize-palettes --dither none

# Adjust threshold for more aggressive reuse
gs-convert convert image.jpg output.3200 --optimize-palettes --error-threshold 5000
```

## Full Documentation

See `docs/PALETTE_OPTIMIZATION.md` for complete details, examples, and technical information.

## Summary

**One flag to eliminate banding:** `--optimize-palettes`

Try it on your images with solid-color areas and see the difference!

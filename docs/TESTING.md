# Testing Guide for gs-convert

This guide provides sample command-line invocations to test gs-convert's various features and options.

## Basic Conversions

```bash
# 1. Simplest possible conversion (uses all defaults: Atkinson dithering, median-cut)
gs-convert convert examples/test_gradient.png test_output_1.3200

# 2. With preview to see the result
gs-convert convert examples/test_photo.png test_output_2.3200 --preview test_preview_2.png

# 3. Check the file info
gs-convert info test_output_1.3200
```

## Different Dithering Algorithms

Try each dithering algorithm on the same image to compare:

```bash
# Atkinson (default - high contrast, retro aesthetic)
gs-convert convert examples/test_photo.png photo_atkinson.3200 --dither atkinson --preview preview_atkinson.png

# Floyd-Steinberg (smooth, photographic)
gs-convert convert examples/test_photo.png photo_floyd.3200 --dither floyd-steinberg --preview preview_floyd.png

# No dithering (clean, posterized)
gs-convert convert examples/test_photo.png photo_none.3200 --dither none --preview preview_none.png

# Ordered/Bayer (fast, retro patterns)
gs-convert convert examples/test_photo.png photo_ordered.3200 --dither ordered --preview preview_ordered.png

# JJN (very smooth, high quality)
gs-convert convert examples/test_photo.png photo_jjn.3200 --dither jjn --preview preview_jjn.png

# Now compare all the preview_*.png files to see the differences!
open preview_*.png  # macOS - opens all in Preview
```

## Different Image Types

```bash
# Gradient (should show smooth color transitions)
gs-convert convert examples/test_gradient.png gradient_result.3200 --preview gradient_preview.png

# Color chart (discrete colors)
gs-convert convert examples/test_colors.png colors_result.3200 --preview colors_preview.png --dither none

# Photo simulation
gs-convert convert examples/test_photo.png photo_result.3200 --preset photo --preview photo_preview.png
```

## Using Presets

```bash
# Photo preset (Atkinson + median-cut + Lanczos)
gs-convert convert examples/test_photo.png preset_photo.3200 --preset photo --preview preset_photo_preview.png

# Pixel art preset (no dithering + nearest neighbor)
gs-convert convert examples/test_colors.png preset_pixel.3200 --preset pixel-art --preview preset_pixel_preview.png

# Line art preset
gs-convert convert examples/test_gradient.png preset_line.3200 --preset line-art --preview preset_line_preview.png
```

## Aspect Ratio Experiments

```bash
# No aspect correction (square pixels)
gs-convert convert examples/test_photo.png aspect_none.3200 --aspect 1.0 --preview aspect_none_preview.png

# Standard aspect correction (1.2x horizontal stretch)
gs-convert convert examples/test_photo.png aspect_standard.3200 --aspect 1.2 --preview aspect_standard_preview.png

# Custom aspect ratio
gs-convert convert examples/test_photo.png aspect_custom.3200 --aspect 1.5 --preview aspect_custom_preview.png

# Compare the previews to see the difference
```

## Different Resize Filters

```bash
# Lanczos (highest quality, default)
gs-convert convert examples/test_gradient.png resize_lanczos.3200 --resize-filter lanczos --preview resize_lanczos.png

# Bilinear (faster, slightly softer)
gs-convert convert examples/test_gradient.png resize_bilinear.3200 --resize-filter bilinear --preview resize_bilinear.png

# Nearest neighbor (pixel art, hard edges)
gs-convert convert examples/test_colors.png resize_nearest.3200 --resize-filter nearest --preview resize_nearest.png
```

## Quantization Methods

```bash
# Per-scanline median cut (default, best for Apple IIgs)
gs-convert convert examples/test_photo.png quant_median.3200 --quantize median-cut --preview quant_median.png

# Global palette
gs-convert convert examples/test_photo.png quant_global.3200 --quantize global --preview quant_global.png

# Compare to see palette differences
gs-convert info quant_median.3200
gs-convert info quant_global.3200
```

## Linear RGB vs sRGB

```bash
# With linear RGB (default, more accurate)
gs-convert convert examples/test_photo.png linear_yes.3200 --linear --preview linear_yes.png

# Without linear RGB
gs-convert convert examples/test_photo.png linear_no.3200 --no-linear --preview linear_no.png

# Subtle difference, but linear is more perceptually correct
```

## Batch Processing

```bash
# Convert all test images at once
gs-convert batch examples/test_*.png --output-dir batch_results/

# Check what was created
ls -lh batch_results/
gs-convert info batch_results/test_photo.3200

# Batch with specific settings
gs-convert batch examples/test_*.png --output-dir batch_atkinson/ --dither atkinson

# Batch with preset
gs-convert batch examples/test_*.png --output-dir batch_photo_preset/ --preset photo
```

## Comparing Results

```bash
# Create multiple versions of same image with different settings
gs-convert convert examples/test_photo.png compare_1.3200 --dither atkinson --preview compare_1.png
gs-convert convert examples/test_photo.png compare_2.3200 --dither floyd-steinberg --preview compare_2.png
gs-convert convert examples/test_photo.png compare_3.3200 --dither none --preview compare_3.png

# Open all previews side-by-side
open compare_*.png
```

## File Info Commands

```bash
# Basic info
gs-convert info examples/test_gradient.3200

# Check palette usage on different conversions
gs-convert info photo_atkinson.3200
gs-convert info photo_floyd.3200
gs-convert info photo_none.3200

# You'll see different palette usage patterns!
```

## Real-World Test (if you have your own image)

```bash
# Convert your own photo
gs-convert convert ~/Pictures/your_photo.jpg my_photo.3200 --preview my_photo_preview.png

# Try different algorithms on your photo
gs-convert convert ~/Pictures/your_photo.jpg my_atkinson.3200 --dither atkinson --preview my_atkinson.png
gs-convert convert ~/Pictures/your_photo.jpg my_floyd.3200 --dither floyd-steinberg --preview my_floyd.png
gs-convert convert ~/Pictures/your_photo.jpg my_jjn.3200 --dither jjn --preview my_jjn.png

# Compare which looks best for your image
open my_*.png
```

## Recommended Test Sequence

Start with this sequence to get a good feel:

```bash
# 1. Test basic functionality
gs-convert convert examples/test_photo.png test1.3200 --preview test1.png
gs-convert info test1.3200
open test1.png

# 2. Compare dithering algorithms on same image
gs-convert convert examples/test_photo.png dither_atkinson.3200 --dither atkinson --preview dither_atkinson.png
gs-convert convert examples/test_photo.png dither_floyd.3200 --dither floyd-steinberg --preview dither_floyd.png
gs-convert convert examples/test_photo.png dither_none.3200 --dither none --preview dither_none.png
open dither_*.png

# 3. Try batch processing
gs-convert batch examples/test_*.png --output-dir my_batch_test/
ls -lh my_batch_test/

# 4. Check file details
gs-convert info dither_atkinson.3200
gs-convert info dither_floyd.3200
gs-convert info dither_none.3200

# 5. Use presets
gs-convert convert examples/test_photo.png preset_test.3200 --preset photo --preview preset_test.png
```

## What to Look For

### When Comparing Previews

- **Atkinson**: High contrast, crispy, retro look - notice the "incomplete" error diffusion creates bright highlights
- **Floyd-Steinberg**: Smoother gradients, more "muddy" but photographic
- **JJN**: Very smooth, minimal patterns, but slower
- **Stucki**: Similar to JJN with slightly different weight distribution
- **Burkes**: Faster than JJN/Stucki, still high quality
- **Ordered**: Visible crosshatch pattern, very retro
- **None**: Clean color blocks, posterized look

### When Checking Info

- **Palette usage**: How many unique palettes were used (out of 16 maximum)
- **Per-scanline distribution**: Which palettes are used where
- **Palette efficiency**: Images with similar colors might reuse palettes

### File Size Verification

All `.3200` files should be exactly **32,768 bytes** (32 KB):

```bash
ls -l *.3200
# Every file should show: 32768 bytes
```

## Quick Comparison Script

Want to see all algorithms at once? Run this:

```bash
# Test all dithering algorithms on one image
for algo in atkinson floyd-steinberg jjn stucki burkes ordered none; do
  echo "Testing $algo..."
  gs-convert convert examples/test_photo.png "compare_${algo}.3200" \
    --dither "$algo" \
    --preview "compare_${algo}.png"
done

echo "Opening all previews for comparison..."
open compare_*.png
```

## Performance Testing

Time different algorithms to see speed differences:

```bash
# Fastest: Ordered dithering
time gs-convert convert examples/test_photo.png perf_ordered.3200 --dither ordered

# Fast: Atkinson, Floyd-Steinberg, Burkes
time gs-convert convert examples/test_photo.png perf_atkinson.3200 --dither atkinson
time gs-convert convert examples/test_photo.png perf_floyd.3200 --dither floyd-steinberg
time gs-convert convert examples/test_photo.png perf_burkes.3200 --dither burkes

# Slower: JJN, Stucki (larger kernel, more neighbors)
time gs-convert convert examples/test_photo.png perf_jjn.3200 --dither jjn
time gs-convert convert examples/test_photo.png perf_stucki.3200 --dither stucki

# Fastest of all: No dithering
time gs-convert convert examples/test_photo.png perf_none.3200 --dither none
```

Typical times on modern hardware:
- No dithering: < 0.5 seconds
- Ordered: < 0.5 seconds
- Atkinson/Floyd-Steinberg: 1-2 seconds
- JJN/Stucki: 2-3 seconds

## Algorithm Combinations Worth Testing

### Best for Photographs

```bash
# Recommended: Atkinson for retro feel
gs-convert convert photo.jpg photo_best.3200 --preset photo

# Alternative: Floyd-Steinberg for smoother look
gs-convert convert photo.jpg photo_smooth.3200 --dither floyd-steinberg --quantize median-cut

# High quality: JJN for maximum smoothness
gs-convert convert photo.jpg photo_quality.3200 --dither jjn --quantize median-cut
```

### Best for Pixel Art

```bash
# Recommended: No dithering, nearest neighbor
gs-convert convert sprite.png sprite_best.3200 --preset pixel-art

# Or manually:
gs-convert convert sprite.png sprite_manual.3200 --dither none --resize-filter nearest
```

### Best for Line Art / Comics

```bash
# Recommended: Atkinson for high contrast
gs-convert convert comic.png comic_best.3200 --preset line-art

# Alternative: Ordered for classic halftone look
gs-convert convert comic.png comic_halftone.3200 --dither ordered
```

### Experimental Combinations

```bash
# Global palette with no dithering (very posterized)
gs-convert convert photo.jpg experimental_1.3200 --quantize global --dither none --preview exp1.png

# Ordered dithering with global palette (retro texture)
gs-convert convert photo.jpg experimental_2.3200 --quantize global --dither ordered --preview exp2.png

# No aspect correction with JJN (square pixels, smooth)
gs-convert convert photo.jpg experimental_3.3200 --aspect 1.0 --dither jjn --preview exp3.png
```

## Batch Testing Different Settings

Create test matrix of multiple images × multiple algorithms:

```bash
#!/bin/bash
# Save as: test_matrix.sh

images=("examples/test_photo.png" "examples/test_gradient.png" "examples/test_colors.png")
algorithms=("atkinson" "floyd-steinberg" "jjn" "ordered" "none")

mkdir -p test_matrix

for img in "${images[@]}"; do
  basename=$(basename "$img" .png)
  
  for algo in "${algorithms[@]}"; do
    output="test_matrix/${basename}_${algo}.3200"
    preview="test_matrix/${basename}_${algo}_preview.png"
    
    echo "Converting $basename with $algo..."
    gs-convert convert "$img" "$output" --dither "$algo" --preview "$preview"
  done
done

echo "Done! Check test_matrix/ directory"
ls -lh test_matrix/
```

## Verification Tests

Ensure conversions are valid:

```bash
# 1. Verify file size (should be exactly 32768 bytes)
ls -l test_output_1.3200 | awk '{print $5}'  # Should print: 32768

# 2. Verify info command works
gs-convert info test_output_1.3200

# 3. Verify round-trip (convert, read info, should not error)
gs-convert convert examples/test_photo.png roundtrip.3200
gs-convert info roundtrip.3200

# 4. Verify preview generation
gs-convert convert examples/test_photo.png verify.3200 --preview verify.png
file verify.png  # Should say: PNG image data, 320 x 200
```

## Edge Cases to Test

```bash
# Very simple image (all one color)
convert -size 640x400 xc:blue simple_blue.png
gs-convert convert simple_blue.png simple_blue.3200 --preview simple_blue_preview.png
gs-convert info simple_blue.3200

# Checkerboard pattern
convert -size 640x400 pattern:checkerboard checkerboard.png
gs-convert convert checkerboard.png checkerboard.3200 --preview checkerboard_preview.png

# Gradient (smooth transitions)
convert -size 640x400 gradient:red-blue gradient.png
gs-convert convert gradient.png gradient.3200 --preview gradient_preview.png
```

## Common Issues to Check For

### Check 1: File Size
```bash
# All .3200 files must be exactly 32768 bytes
find . -name "*.3200" -exec ls -l {} \; | awk '{print $5, $9}' | grep -v "32768"
# Should return nothing (empty) - any output means wrong size
```

### Check 2: Preview Dimensions
```bash
# All previews should be 320×200
file *_preview.png | grep -v "320 x 200"
# Should return nothing - any output means wrong dimensions
```

### Check 3: Info Command
```bash
# Info should work on all .3200 files
for f in *.3200; do
  echo "Checking $f..."
  gs-convert info "$f" > /dev/null || echo "ERROR: $f failed info check"
done
```

## Cleanup

After testing, clean up temporary files:

```bash
# Remove all test outputs
rm -f test_*.3200 test_*.png
rm -f photo_*.3200 preview_*.png
rm -f compare_*.3200 compare_*.png
rm -f dither_*.3200 dither_*.png
rm -f aspect_*.3200 aspect_*.png
rm -f resize_*.3200 resize_*.png
rm -f quant_*.3200 quant_*.png
rm -f linear_*.3200 linear_*.png
rm -rf batch_results/ batch_atkinson/ batch_photo_preset/
rm -rf my_batch_test/ test_matrix/

# Or keep only the good ones and remove the rest
mkdir -p keepers
mv photo_atkinson.3200 preview_atkinson.png keepers/
# ... move others you want to keep
# Then delete the rest
```

## Summary

**Quick test**: Run the "Recommended Test Sequence" above

**Deep dive**: Try all dithering algorithms on same image and compare

**Real world**: Test with your own photos using different presets

**Verification**: All .3200 files should be 32,768 bytes

All the preview PNG files let you see what the images will look like on an Apple IIgs without needing an emulator!

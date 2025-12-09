# Getting Started with gs-convert

## Installation

The package has been installed in development mode. You can now use the `gs-convert` command from anywhere.

## Quick Test

We've created test images and successfully converted them! Check the `examples/` directory:

```bash
# View the test images and conversions
ls -lh examples/

# View information about a converted file
gs-convert info examples/test_gradient.3200
```

## Basic Usage

### Convert a Single Image

```bash
# Basic conversion (uses Atkinson dithering, median cut quantization)
gs-convert convert input.jpg output.3200

# With preview generation
gs-convert convert input.jpg output.3200 --preview preview.png

# Try different dithering algorithms
gs-convert convert input.jpg output.3200 --dither floyd-steinberg
gs-convert convert input.jpg output.3200 --dither ordered
gs-convert convert input.jpg output.3200 --dither none
```

### Batch Convert Multiple Files

```bash
# Convert all JPG files in a directory
gs-convert batch *.jpg --output-dir converted/

# Use presets for common configurations
gs-convert batch *.png --output-dir converted/ --preset photo
```

### Use Presets

Presets configure multiple settings at once:

- **photo**: Atkinson dithering, Lanczos resize (best for photographs)
- **pixel-art**: No dithering, nearest-neighbor resize (preserves pixel art)
- **line-art**: Atkinson dithering, optimized for drawings

```bash
gs-convert convert photo.jpg output.3200 --preset photo
gs-convert convert sprite.png output.3200 --preset pixel-art
```

## Algorithm Options

### Dithering Algorithms

Try different dithering methods to see what works best for your images:

```bash
# Atkinson (default) - High contrast, retro aesthetic
gs-convert convert img.jpg out.3200 --dither atkinson

# Floyd-Steinberg - Smooth, photographic quality
gs-convert convert img.jpg out.3200 --dither floyd-steinberg

# JJN - Very smooth, high quality (slower)
gs-convert convert img.jpg out.3200 --dither jjn

# Ordered/Bayer - Fast, retro patterns
gs-convert convert img.jpg out.3200 --dither ordered

# None - Clean, posterized look
gs-convert convert img.jpg out.3200 --dither none
```

### Quantization Methods

- **median-cut** (default): Per-scanline optimal palette (recommended)
- **global**: Global palette across entire image

```bash
gs-convert convert img.jpg out.3200 --quantize median-cut
gs-convert convert img.jpg out.3200 --quantize global
```

## Testing Your Conversions

### Generate Previews

Always generate a preview to see how your image will look:

```bash
gs-convert convert photo.jpg output.3200 --preview preview.png
```

Then open `preview.png` to see how it will appear on the Apple IIgs.

### Test on Emulator

To test your .3200 files on an Apple IIgs emulator:

1. **GSPort** (Recommended, cross-platform)
   - Download from: https://gsport.github.io/
   - Copy .3200 files to a ProDOS disk image
   - Load in emulator

2. **MAME** (Apple IIgs support)
   - `mame apple2gs`

3. **Sweet16** (macOS only)
   - Available on Mac App Store

## Comparing Results

Try converting the same image with different settings:

```bash
# Atkinson dithering
gs-convert convert test.jpg test_atkinson.3200 --dither atkinson --preview preview_atkinson.png

# Floyd-Steinberg dithering
gs-convert convert test.jpg test_floyd.3200 --dither floyd-steinberg --preview preview_floyd.png

# No dithering
gs-convert convert test.jpg test_none.3200 --dither none --preview preview_none.png
```

Then compare the preview images to see which looks best for your use case.

## Common Workflows

### High-Quality Photo Conversion

```bash
gs-convert convert photo.jpg output.3200 \
  --preset photo \
  --preview preview.png
```

### Pixel Art / Sprites

```bash
gs-convert convert sprite.png output.3200 \
  --preset pixel-art \
  --preview preview.png
```

### Batch Processing Photos

```bash
gs-convert batch vacation/*.jpg \
  --output-dir converted_vacation/ \
  --preset photo
```

## Next Steps

1. **Try your own images**: Convert some of your photos or artwork
2. **Experiment with settings**: Try different dithering algorithms and see what you prefer
3. **Test on emulator**: Load your .3200 files on GSPort or MAME
4. **Share with community**: Post your results to Apple II forums/communities
5. **Contribute**: If you find bugs or want features, open an issue on GitHub

## File Format Details

The .3200 format is the Apple IIgs Super High-Resolution unpacked format:
- **Size**: Exactly 32,768 bytes (32 KB)
- **Resolution**: 320×200 pixels
- **Colors**: 16 colors per scanline, from 4096 color palette
- **Palettes**: Up to 16 different 16-color palettes

Each scanline can use a different palette, which is what makes the Apple IIgs so unique!

## Performance

Typical conversion times on modern hardware:
- **Simple images**: < 1 second
- **Complex photographs**: 1-2 seconds
- **Batch processing**: ~1-2 seconds per image

The Atkinson and Floyd-Steinberg algorithms are fastest. JJN and Stucki are slower but produce smoother results.

## Troubleshooting

### Image looks wrong
- Try different dithering algorithms
- Adjust aspect ratio correction: `--aspect 1.0` or `--aspect 1.2`
- Try `--no-linear` to disable linear RGB processing

### Colors are washed out
- This is normal due to 12-bit color quantization
- Try Atkinson dithering for higher contrast

### File won't load in emulator
- Verify file size is exactly 32768 bytes: `ls -l output.3200`
- Check file info: `gs-convert info output.3200`

## Getting Help

```bash
# View command help
gs-convert --help
gs-convert convert --help
gs-convert batch --help

# View version
gs-convert --version
```

For more information, see:
- `README.md` - Project overview and reference
- `docs/apple_iigs_image_conversion_guide.md` - Technical details
- `docs/dithering_and_median_cut_guide.md` - Algorithm explanations

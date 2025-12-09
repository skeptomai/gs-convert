# Star Trek Animated Series - Corrected Analysis

## What I Got Wrong

I recommended `--quantize global` based on **technical metrics** (fewer palettes = less banding) rather than **visual quality** (what actually looks good to humans).

**The truth**: Global quantization destroyed the image, making it unrecognizable with static/noise across the entire image.

## What Actually Matters

**Human-recognizable quality** > Technical palette optimization

The per-scanline methods (default, optimized) use all 16 palettes because **the image needs them** to preserve:
- Character details
- Uniform colors (red, yellow, blue)
- Facial features
- The starship
- Text legibility

## Actual Best Options for Star Trek Image

Based on visual quality (what humans can actually see):

### Top Recommendations

1. **Default + Atkinson** (01_default.png)
   ```bash
   gs-convert convert star_trek_animated.jpeg output.3200 --preview preview.png
   ```
   - Uses all 16 palettes to preserve detail
   - May have some banding, but image is recognizable
   - Good balance of retro aesthetic and clarity

2. **Optimized + Floyd-Steinberg** (05_opt_floyd.png)
   ```bash
   gs-convert convert star_trek_animated.jpeg output.3200 \
     --optimize-palettes \
     --dither floyd-steinberg \
     --preview preview.png
   ```
   - Smooth gradients
   - Reduces banding where possible
   - Preserves character details

3. **Optimized + JJN** (08_opt_jjn.png)
   ```bash
   gs-convert convert star_trek_animated.jpeg output.3200 \
     --optimize-palettes \
     --dither jjn \
     --preview preview.png
   ```
   - Highest quality dithering
   - Very smooth
   - Best for maximum detail preservation

4. **Default + Floyd-Steinberg** (try this if default looks too harsh)
   ```bash
   gs-convert convert star_trek_animated.jpeg output.3200 \
     --dither floyd-steinberg \
     --preview preview.png
   ```

### What NOT to Do

❌ **Do NOT use `--quantize global`** for this image
- Results in unrecognizable static
- Destroys character details
- Makes text unreadable
- Palette sharing is too aggressive for complex images

## Why Global Failed

Global quantization assumes:
- Limited color palette throughout
- Colors can be shared across entire image
- Consistency matters more than local detail

Star Trek image reality:
- Complex color variation (characters + background + text)
- Each area needs different colors
- Detail preservation is critical
- Using only 6 palettes loses too much information

## The Correct Rule

**Use global quantization ONLY for:**
- Simple logos with 3-5 solid colors
- Flat graphics with no gradients
- UI elements with consistent colors

**Use per-scanline (default or optimized) for:**
- Animation artwork with characters and detail (like Star Trek)
- Photographs
- Complex illustrations
- Anything where you need to see what it is!

## Recommendation for Your Image

Try these in order and pick whichever looks best to your eye:

```bash
# 1. Default (good balance)
gs-convert convert star_trek_animated.jpeg output1.3200 --preview preview1.png

# 2. Smoother
gs-convert convert star_trek_animated.jpeg output2.3200 \
  --dither floyd-steinberg --preview preview2.png

# 3. Optimized (if you see banding)
gs-convert convert star_trek_animated.jpeg output3.3200 \
  --optimize-palettes --dither floyd-steinberg --preview preview3.png

# 4. Maximum quality
gs-convert convert star_trek_animated.jpeg output4.3200 \
  --optimize-palettes --dither jjn --preview preview4.png

# Compare visually
open preview*.png
```

## Lesson Learned

**Technical metrics lie.**

- Fewer palettes ≠ Better quality
- More palette reuse ≠ Better results
- Lower "error" ≠ More recognizable

**Trust your eyes**, not the numbers.

If the image is unrecognizable, it doesn't matter how "optimized" the palette usage is.

# Apple IIgs Image Converter Project

## Project Overview

This project aims to create a modern image conversion tool that transforms high-resolution PNG and JPEG images into Apple IIgs Super High-Resolution (SHR) format, specifically targeting the .3200 format.

## Project Goals

### Primary Objectives

1. **Format Conversion**: Convert modern image formats (PNG, JPEG) to Apple IIgs .3200 format
   - Handle arbitrary input resolutions and aspect ratios
   - Resize to 320×200 pixels with proper aspect ratio correction
   - Support the Apple IIgs 12-bit color space (4096 colors)

2. **Color Quantization**: Implement intelligent palette generation
   - Per-scanline palette optimization (16 colors per line)
   - Support for multiple quantization algorithms (median cut, k-means, octree)
   - Optimal use of the 200 independent palette selections

3. **Dithering Options**: Provide multiple dithering algorithms
   - Atkinson dithering (era-appropriate, high contrast)
   - Floyd-Steinberg (smooth, photographic quality)
   - Ordered/Bayer dithering (fast, retro aesthetic)
   - JJN, Stucki, Burkes (high-quality alternatives)
   - Option for no dithering (clean, posterized look)

4. **Quality & Flexibility**: Allow users to choose conversion strategies
   - Preset profiles for different image types (photos, pixel art, line art)
   - Manual control over dithering and quantization parameters
   - Preview capabilities before final conversion

### Secondary Objectives

1. **Command-Line Tool**: Create a efficient CLI for batch processing and automation
2. **GUI Application**: Develop user-friendly interface for interactive conversion
3. **Testing & Validation**: Ensure output works correctly on emulators (GSPort, MAME)
4. **Documentation**: Provide clear usage guides and examples

## Technical Requirements

### Input
- Image formats: PNG, JPEG (potentially GIF, BMP, TIFF)
- Arbitrary resolutions and color depths
- Batch processing capability

### Output
- Primary format: .3200 (32,768 bytes)
  - 32,000 bytes pixel data (160 bytes × 200 scanlines)
  - 256 bytes SCB data (Scan Line Control Bytes)
  - 512 bytes palette data (16 palettes × 16 colors × 2 bytes)
- Optional: APF format (packed format)

### Processing Pipeline

1. **Image Preprocessing**
   - Load source image
   - Resize to 320×200 with aspect ratio correction (optional 1.2:1 horizontal stretch)
   - Convert to appropriate color space (linear RGB for processing)

2. **Color Quantization**
   - Per-scanline median cut (recommended default)
   - Alternative: global palette with per-line optimization
   - Convert to Apple IIgs 12-bit color format

3. **Dithering Application**
   - Apply selected dithering algorithm
   - Work with per-scanline palettes
   - Handle error diffusion across scanline boundaries

4. **Format Generation**
   - Pack pixels (2 per byte, 4-bit indices)
   - Generate SCB bytes
   - Format palette data in Apple IIgs structure
   - Write .3200 file

## Success Criteria

- Successfully convert variety of image types (photos, graphics, art)
- Output files load and display correctly on Apple IIgs emulators
- Provide visually pleasing results appropriate to retro aesthetic
- Fast enough for interactive use (< 2 seconds per image on modern hardware)
- Clear documentation and examples
- Clean, maintainable codebase

## Future Enhancements (Out of Scope for v1.0)

- Animated GIF → SHR slideshow conversion
- 640×200 mode support
- Batch optimization (sharing palettes across multiple images)
- Custom palette import/export
- Real-time preview with different algorithm combinations
- Integration with disk image creation tools

---

## Current Development

### Active Tasks

See **ONGOING_TASKS.md** for current implementation work, including:
- Flask Web UI implementation plan
- Feature roadmaps
- Integration details

### Documentation

- **docs/UI_OPTIONS.md** - Comprehensive overview of UI architecture options (Flask, Electron, Qt, Tkinter, TUI)

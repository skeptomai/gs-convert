"""
Command-line interface for gs-convert.

Provides user-friendly CLI for converting images to Apple IIgs format.
"""

import click
from pathlib import Path
from typing import Optional

from .pipeline import convert_image, generate_preview_image
from .format_writer import read_3200_file


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    gs-convert - Apple IIgs Image Converter
    
    Convert modern images to Apple IIgs Super High-Resolution (.3200) format.
    """
    pass


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option(
    '--dither', '-d',
    type=click.Choice([
        'atkinson', 'floyd-steinberg', 'jjn', 'stucki', 
        'burkes', 'ordered', 'bayer', 'none'
    ], case_sensitive=False),
    default='atkinson',
    help='Dithering algorithm to use (default: atkinson)'
)
@click.option(
    '--quantize', '-q',
    type=click.Choice(['median-cut', 'global', 'optimized'], case_sensitive=False),
    default='median-cut',
    help='Palette quantization method (default: median-cut)'
)
@click.option(
    '--optimize-palettes/--no-optimize-palettes',
    default=False,
    help='Use intelligent palette reuse to reduce banding in solid areas'
)
@click.option(
    '--error-threshold',
    type=float,
    default=2000.0,
    help='Error threshold for palette reuse (lower=more palettes, higher=more reuse)'
)
@click.option(
    '--aspect', '-a',
    type=float,
    default=1.2,
    help='Horizontal aspect ratio correction (default: 1.2 for non-square pixels)'
)
@click.option(
    '--resize-filter', '-r',
    type=click.Choice(['lanczos', 'bilinear', 'nearest'], case_sensitive=False),
    default='lanczos',
    help='Image resize filter (default: lanczos)'
)
@click.option(
    '--linear/--no-linear',
    default=True,
    help='Use linear RGB color space for processing (default: on)'
)
@click.option(
    '--preview', '-p',
    type=click.Path(),
    default=None,
    help='Generate PNG preview at specified path'
)
@click.option(
    '--preset',
    type=click.Choice(['photo', 'pixel-art', 'line-art'], case_sensitive=False),
    default=None,
    help='Use preset configuration for image type'
)
def convert(
    input_path: str,
    output_path: str,
    dither: str,
    quantize: str,
    optimize_palettes: bool,
    error_threshold: float,
    aspect: float,
    resize_filter: str,
    linear: bool,
    preview: Optional[str],
    preset: Optional[str]
):
    """
    Convert an image to Apple IIgs .3200 format.
    
    Examples:
    
        # Basic conversion with defaults (Atkinson dithering)
        gs-convert photo.jpg output.3200
        
        # Use Floyd-Steinberg dithering for photographs
        gs-convert photo.jpg output.3200 --dither floyd-steinberg
        
        # Pixel art with no dithering
        gs-convert sprite.png output.3200 --dither none --resize-filter nearest
        
        # Generate preview PNG
        gs-convert photo.jpg output.3200 --preview preview.png
        
        # Use preset for common configurations
        gs-convert photo.jpg output.3200 --preset photo
    """
    # Apply preset configurations
    if preset:
        dither, quantize, resize_filter = apply_preset(preset)
        click.echo(f"Using preset: {preset}")
    
    # Validate output path
    output_path = str(Path(output_path))
    if not output_path.endswith('.3200'):
        click.echo("Warning: Output file should have .3200 extension", err=True)
    
    try:
        # Perform conversion
        convert_image(
            input_path=input_path,
            output_path=output_path,
            dither_method=dither.lower(),
            quantize_method=quantize.lower(),
            aspect_correct=aspect,
            resize_filter=resize_filter.lower(),
            use_linear_rgb=linear,
            optimize_palettes=optimize_palettes,
            error_threshold=error_threshold
        )
        
        # Generate preview if requested
        if preview:
            click.echo(f"Generating preview...")
            pixel_indices, scb_bytes, palettes_12bit = read_3200_file(output_path)
            
            # Convert palettes back to RGB for preview
            from .color import iigs12_to_rgb24
            import numpy as np
            
            palettes_rgb = []
            for palette_12bit in palettes_12bit:
                palette_rgb = np.zeros((16, 3), dtype=np.uint8)
                for i in range(16):
                    # Palette is stored as RGB tuples already from read_3200_file
                    palette_rgb[i] = palette_12bit[i]
                palettes_rgb.append(palette_rgb)
            
            generate_preview_image(pixel_indices, palettes_rgb, scb_bytes, preview)
        
        click.echo(f"✓ Conversion successful!")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('input_files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    required=True,
    help='Output directory for converted files'
)
@click.option(
    '--dither', '-d',
    type=click.Choice([
        'atkinson', 'floyd-steinberg', 'jjn', 'stucki', 
        'burkes', 'ordered', 'bayer', 'none'
    ], case_sensitive=False),
    default='atkinson',
    help='Dithering algorithm to use'
)
@click.option(
    '--preset',
    type=click.Choice(['photo', 'pixel-art', 'line-art'], case_sensitive=False),
    default=None,
    help='Use preset configuration'
)
def batch(input_files, output_dir, dither, preset):
    """
    Batch convert multiple images to .3200 format.
    
    Example:
        gs-convert batch *.jpg --output-dir converted/
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Apply preset if specified
    if preset:
        dither, quantize, resize_filter = apply_preset(preset)
    else:
        quantize = 'median-cut'
        resize_filter = 'lanczos'
    
    total = len(input_files)
    click.echo(f"Converting {total} files...")
    
    for idx, input_file in enumerate(input_files, 1):
        input_name = Path(input_file).stem
        output_file = output_path / f"{input_name}.3200"
        
        click.echo(f"[{idx}/{total}] {input_file} -> {output_file}")
        
        try:
            convert_image(
                input_path=input_file,
                output_path=str(output_file),
                dither_method=dither.lower(),
                quantize_method=quantize,
                aspect_correct=1.2,
                resize_filter=resize_filter,
                use_linear_rgb=True
            )
        except Exception as e:
            click.echo(f"  Error: {e}", err=True)
            continue
    
    click.echo(f"✓ Batch conversion complete! {total} files processed.")


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
def info(input_path: str):
    """
    Display information about a .3200 file.
    
    Example:
        gs-convert info output.3200
    """
    try:
        pixel_indices, scb_bytes, palettes = read_3200_file(input_path)
        
        click.echo(f"File: {input_path}")
        click.echo(f"Size: 32768 bytes (32 KB)")
        click.echo(f"Resolution: 320×200 pixels")
        click.echo(f"\nPalettes:")
        
        # Count unique palettes
        unique_palettes = len(set(scb_bytes))
        click.echo(f"  Unique palettes used: {unique_palettes}/16")
        
        # Show palette usage
        for i in range(16):
            usage = (scb_bytes == i).sum()
            if usage > 0:
                click.echo(f"  Palette {i:2d}: used by {usage:3d} scanlines")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


def apply_preset(preset: str) -> tuple:
    """
    Apply preset configurations.
    
    Returns:
        Tuple of (dither, quantize, resize_filter)
    """
    presets = {
        'photo': ('atkinson', 'median-cut', 'lanczos'),
        'pixel-art': ('none', 'median-cut', 'nearest'),
        'line-art': ('atkinson', 'median-cut', 'lanczos'),
    }
    
    return presets.get(preset.lower(), ('atkinson', 'median-cut', 'lanczos'))


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()

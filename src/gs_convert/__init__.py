"""
gs_convert - Apple IIgs Image Converter

Convert modern image formats to Apple IIgs Super High-Resolution format.
"""

__version__ = "0.1.0"

from .color import rgb24_to_iigs12, iigs12_to_rgb24, srgb_to_linear, linear_to_srgb
from .quantize import median_cut_quantize
from .dither import AtkinsonDitherer, FloydSteinbergDitherer, OrderedDitherer
from .format_writer import write_3200_file
from .pipeline import convert_image

__all__ = [
    "rgb24_to_iigs12",
    "iigs12_to_rgb24",
    "srgb_to_linear",
    "linear_to_srgb",
    "median_cut_quantize",
    "AtkinsonDitherer",
    "FloydSteinbergDitherer",
    "OrderedDitherer",
    "write_3200_file",
    "convert_image",
]

"""
Dithering algorithms for Apple IIgs image conversion.

Implements various dithering techniques:
- Error diffusion: Floyd-Steinberg, Atkinson, JJN, Stucki, Burkes, Sierra
- Ordered dithering: Bayer matrix
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional


class Ditherer(ABC):
    """Base class for dithering algorithms."""
    
    @abstractmethod
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        """
        Apply dithering to an image with a given palette.
        
        Args:
            image: Array of shape (height, width, 3) with RGB values
            palette: Array of shape (n_colors, 3) with palette colors
            
        Returns:
            Array of shape (height, width) with palette indices
        """
        pass
    
    def _find_closest_color(self, pixel: np.ndarray, palette: np.ndarray) -> int:
        """Find index of closest color in palette."""
        distances = np.sum((palette - pixel) ** 2, axis=1)
        return np.argmin(distances)


class AtkinsonDitherer(Ditherer):
    """
    Atkinson dithering - developed by Bill Atkinson for the original Macintosh.
    
    Only distributes 6/8 (75%) of error, creating high-contrast results perfect
    for the retro aesthetic of Apple IIgs.
    
    Error distribution:
             X   1/8 1/8
       1/8 1/8 1/8
           1/8
    """
    
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        output = image.astype(float).copy()
        indices = np.zeros((height, width), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                old_pixel = output[y, x]
                new_idx = self._find_closest_color(old_pixel, palette)
                new_pixel = palette[new_idx]
                indices[y, x] = new_idx
                output[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                # Distribute 6/8 of error (Atkinson only uses 6/8)
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
        
        return indices


class FloydSteinbergDitherer(Ditherer):
    """
    Floyd-Steinberg dithering - most widely used error diffusion algorithm.
    
    Distributes 100% of error to 4 neighboring pixels.
    
    Error distribution:
             X   7/16
       3/16 5/16 1/16
    """
    
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        output = image.astype(float).copy()
        indices = np.zeros((height, width), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                old_pixel = output[y, x]
                new_idx = self._find_closest_color(old_pixel, palette)
                new_pixel = palette[new_idx]
                indices[y, x] = new_idx
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
        
        return indices


class JarvisJudiceNinkeDitherer(Ditherer):
    """
    Jarvis-Judice-Ninke (JJN) dithering.
    
    Distributes error to 12 neighboring pixels for very smooth results.
    
    Error distribution:
             X   7/48 5/48
       3/48 5/48 7/48 5/48 3/48
       1/48 3/48 5/48 3/48 1/48
    """
    
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        output = image.astype(float).copy()
        indices = np.zeros((height, width), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                old_pixel = output[y, x]
                new_idx = self._find_closest_color(old_pixel, palette)
                new_pixel = palette[new_idx]
                indices[y, x] = new_idx
                output[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                # Row 0 (current row)
                if x + 1 < width:
                    output[y, x + 1] += error * 7/48
                if x + 2 < width:
                    output[y, x + 2] += error * 5/48
                
                # Row 1
                if y + 1 < height:
                    if x > 1:
                        output[y + 1, x - 2] += error * 3/48
                    if x > 0:
                        output[y + 1, x - 1] += error * 5/48
                    output[y + 1, x] += error * 7/48
                    if x + 1 < width:
                        output[y + 1, x + 1] += error * 5/48
                    if x + 2 < width:
                        output[y + 1, x + 2] += error * 3/48
                
                # Row 2
                if y + 2 < height:
                    if x > 1:
                        output[y + 2, x - 2] += error * 1/48
                    if x > 0:
                        output[y + 2, x - 1] += error * 3/48
                    output[y + 2, x] += error * 5/48
                    if x + 1 < width:
                        output[y + 2, x + 1] += error * 3/48
                    if x + 2 < width:
                        output[y + 2, x + 2] += error * 1/48
        
        return indices


class StuckiDitherer(Ditherer):
    """
    Stucki dithering - similar to JJN with different weights.
    
    Error distribution:
             X   8/42 4/42
       2/42 4/42 8/42 4/42 2/42
       1/42 2/42 4/42 2/42 1/42
    """
    
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        output = image.astype(float).copy()
        indices = np.zeros((height, width), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                old_pixel = output[y, x]
                new_idx = self._find_closest_color(old_pixel, palette)
                new_pixel = palette[new_idx]
                indices[y, x] = new_idx
                output[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                if x + 1 < width:
                    output[y, x + 1] += error * 8/42
                if x + 2 < width:
                    output[y, x + 2] += error * 4/42
                
                if y + 1 < height:
                    if x > 1:
                        output[y + 1, x - 2] += error * 2/42
                    if x > 0:
                        output[y + 1, x - 1] += error * 4/42
                    output[y + 1, x] += error * 8/42
                    if x + 1 < width:
                        output[y + 1, x + 1] += error * 4/42
                    if x + 2 < width:
                        output[y + 1, x + 2] += error * 2/42
                
                if y + 2 < height:
                    if x > 1:
                        output[y + 2, x - 2] += error * 1/42
                    if x > 0:
                        output[y + 2, x - 1] += error * 2/42
                    output[y + 2, x] += error * 4/42
                    if x + 1 < width:
                        output[y + 2, x + 1] += error * 2/42
                    if x + 2 < width:
                        output[y + 2, x + 2] += error * 1/42
        
        return indices


class BurkesDitherer(Ditherer):
    """
    Burkes dithering - simplified version of Stucki, only 2 rows.
    
    Error distribution:
             X   8/32 4/32
       2/32 4/32 8/32 4/32 2/32
    """
    
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        output = image.astype(float).copy()
        indices = np.zeros((height, width), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                old_pixel = output[y, x]
                new_idx = self._find_closest_color(old_pixel, palette)
                new_pixel = palette[new_idx]
                indices[y, x] = new_idx
                output[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                if x + 1 < width:
                    output[y, x + 1] += error * 8/32
                if x + 2 < width:
                    output[y, x + 2] += error * 4/32
                
                if y + 1 < height:
                    if x > 1:
                        output[y + 1, x - 2] += error * 2/32
                    if x > 0:
                        output[y + 1, x - 1] += error * 4/32
                    output[y + 1, x] += error * 8/32
                    if x + 1 < width:
                        output[y + 1, x + 1] += error * 4/32
                    if x + 2 < width:
                        output[y + 1, x + 2] += error * 2/32
        
        return indices


class OrderedDitherer(Ditherer):
    """
    Ordered (Bayer matrix) dithering - fast, deterministic, retro aesthetic.
    
    Uses a threshold map rather than error diffusion.
    """
    
    def __init__(self, matrix_size: int = 8):
        """
        Initialize with Bayer matrix size.
        
        Args:
            matrix_size: Size of Bayer matrix (2, 4, or 8)
        """
        self.matrix_size = matrix_size
        self.bayer_matrix = self._generate_bayer_matrix(matrix_size)
    
    def _generate_bayer_matrix(self, n: int) -> np.ndarray:
        """Generate a Bayer matrix of size n×n."""
        if n == 2:
            return np.array([[0, 2], [3, 1]], dtype=float) / 4
        elif n == 4:
            return np.array([
                [0,  8,  2, 10],
                [12, 4, 14,  6],
                [3, 11,  1,  9],
                [15, 7, 13,  5]
            ], dtype=float) / 16
        elif n == 8:
            # Recursive construction of 8×8 Bayer matrix
            m4 = self._generate_bayer_matrix(4)
            m8 = np.zeros((8, 8))
            m8[0:4, 0:4] = m4 * 4
            m8[0:4, 4:8] = m4 * 4 + 2
            m8[4:8, 0:4] = m4 * 4 + 3
            m8[4:8, 4:8] = m4 * 4 + 1
            return m8 / 4
        else:
            raise ValueError(f"Unsupported Bayer matrix size: {n}")
    
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        indices = np.zeros((height, width), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                # Get threshold from Bayer matrix
                threshold = self.bayer_matrix[y % self.matrix_size, x % self.matrix_size]
                
                # Apply threshold
                pixel = image[y, x].astype(float)
                pixel = pixel + (threshold - 0.5) * 32  # Scale threshold
                pixel = np.clip(pixel, 0, 255)
                
                # Find closest color
                indices[y, x] = self._find_closest_color(pixel, palette)
        
        return indices


class NoDitherer(Ditherer):
    """
    No dithering - just maps each pixel to nearest palette color.
    
    Useful for clean, posterized look or when palette is already optimal.
    """
    
    def dither(self, image: np.ndarray, palette: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        indices = np.zeros((height, width), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                indices[y, x] = self._find_closest_color(image[y, x], palette)
        
        return indices


# Convenience dictionary for algorithm selection
DITHERING_ALGORITHMS = {
    'atkinson': AtkinsonDitherer,
    'floyd-steinberg': FloydSteinbergDitherer,
    'jjn': JarvisJudiceNinkeDitherer,
    'stucki': StuckiDitherer,
    'burkes': BurkesDitherer,
    'ordered': OrderedDitherer,
    'bayer': OrderedDitherer,
    'none': NoDitherer,
}

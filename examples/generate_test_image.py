#!/usr/bin/env python3
"""
Generate test images for converter testing.
"""

from PIL import Image, ImageDraw
import numpy as np


def create_gradient_test():
    """Create a simple gradient test image."""
    img = Image.new('RGB', (640, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Horizontal gradient
    for x in range(640):
        color = int(x / 640 * 255)
        draw.line([(x, 0), (x, 133)], fill=(color, 0, 0))
        draw.line([(x, 133), (x, 266)], fill=(0, color, 0))
        draw.line([(x, 266), (x, 400)], fill=(0, 0, color))
    
    img.save('examples/test_gradient.png')
    print("Created: examples/test_gradient.png")


def create_color_chart():
    """Create a color chart with primary colors."""
    img = Image.new('RGB', (640, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    colors = [
        ('Red', (255, 0, 0)),
        ('Green', (0, 255, 0)),
        ('Blue', (0, 0, 255)),
        ('Cyan', (0, 255, 255)),
        ('Magenta', (255, 0, 255)),
        ('Yellow', (255, 255, 0)),
        ('White', (255, 255, 255)),
        ('Black', (0, 0, 0)),
    ]
    
    box_width = 640 // 4
    box_height = 400 // 2
    
    for idx, (name, color) in enumerate(colors):
        x = (idx % 4) * box_width
        y = (idx // 4) * box_height
        draw.rectangle([x, y, x + box_width, y + box_height], fill=color)
    
    img.save('examples/test_colors.png')
    print("Created: examples/test_colors.png")


def create_photo_simulation():
    """Create a simulated photo with smooth gradients."""
    img = Image.new('RGB', (640, 400))
    pixels = np.zeros((400, 640, 3), dtype=np.uint8)
    
    # Create radial gradient
    for y in range(400):
        for x in range(640):
            # Distance from center
            dx = (x - 320) / 320
            dy = (y - 200) / 200
            dist = np.sqrt(dx*dx + dy*dy)
            
            # Sky to ground gradient
            sky = np.array([100, 150, 255])
            ground = np.array([139, 90, 43])
            
            t = (y / 400.0)
            color = (1 - t) * sky + t * ground
            
            # Add some variation
            color = color * (1 - dist * 0.3)
            
            pixels[y, x] = np.clip(color, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(pixels)
    img.save('examples/test_photo.png')
    print("Created: examples/test_photo.png")


if __name__ == '__main__':
    import os
    os.makedirs('examples', exist_ok=True)
    
    create_gradient_test()
    create_color_chart()
    create_photo_simulation()
    
    print("\nTest images created! Try converting them:")
    print("  python -m gs_convert.cli convert examples/test_gradient.png output.3200")

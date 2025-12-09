"""Utility functions for Flask UI."""

import base64
import uuid
from pathlib import Path
from typing import Dict, Optional
import time
import shutil

from PIL import Image
import numpy as np

from .config import UPLOAD_FOLDER, SESSION_TIMEOUT_SECONDS, ALLOWED_EXTENSIONS


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_session_folder(session_id: str) -> Path:
    """Get the folder path for a session."""
    folder = UPLOAD_FOLDER / session_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def image_to_base64(image_path: Path) -> str:
    """Convert image file to base64 data URL."""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Determine MIME type from extension
    ext = image_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
    }
    mime_type = mime_types.get(ext, 'image/png')
    
    b64_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{b64_data}"


def pil_image_to_base64(img: Image.Image) -> str:
    """Convert PIL Image to base64 data URL."""
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    b64_data = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{b64_data}"


def get_conversion_stats(output_3200_path: Path) -> Dict:
    """
    Extract statistics from a .3200 file.
    
    Returns dictionary with:
    - unique_palettes: Number of unique palettes used
    - file_size: Size of the .3200 file
    - dimensions: [width, height]
    """
    from gs_convert.format_writer import read_3200_file
    
    if not output_3200_path.exists():
        return {
            "unique_palettes": 0,
            "file_size": 0,
            "dimensions": [320, 200]
        }
    
    # Read the file
    pixel_indices, scb_bytes, palettes = read_3200_file(str(output_3200_path))
    
    # Count unique palettes
    unique_palette_indices = set(scb_bytes)
    unique_palettes = len(unique_palette_indices)

    # Get file size
    file_size = output_3200_path.stat().st_size

    return {
        "unique_palettes": int(unique_palettes),
        "file_size": int(file_size),
        "dimensions": [320, 200],
        "palette_indices_used": [int(x) for x in sorted(unique_palette_indices)]
    }


def cleanup_session(session_id: str) -> bool:
    """Remove all temporary files for a session."""
    session_folder = UPLOAD_FOLDER / session_id
    if session_folder.exists():
        shutil.rmtree(session_folder)
        return True
    return False


def cleanup_old_sessions():
    """Remove sessions older than SESSION_TIMEOUT_SECONDS."""
    if not UPLOAD_FOLDER.exists():
        return
    
    current_time = time.time()
    
    for session_folder in UPLOAD_FOLDER.iterdir():
        if not session_folder.is_dir():
            continue
        
        # Check folder modification time
        folder_mtime = session_folder.stat().st_mtime
        age = current_time - folder_mtime
        
        if age > SESSION_TIMEOUT_SECONDS:
            try:
                shutil.rmtree(session_folder)
                print(f"Cleaned up old session: {session_folder.name}")
            except Exception as e:
                print(f"Error cleaning up session {session_folder.name}: {e}")


def get_image_info(image_path: Path) -> Dict:
    """Get basic information about an image."""
    try:
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "file_size": image_path.stat().st_size
            }
    except Exception as e:
        return {
            "error": str(e)
        }

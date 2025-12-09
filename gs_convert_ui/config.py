"""Configuration for Flask UI."""

import os
from pathlib import Path

# Base directory for uploads and temporary files
UPLOAD_FOLDER = Path("/tmp/gs_convert_uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Maximum file size (16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif'}

# Session timeout (1 hour)
SESSION_TIMEOUT_SECONDS = 3600

# Flask secret key (change in production)
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

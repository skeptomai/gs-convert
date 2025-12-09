# GS-Convert Web UI

A browser-based interface for converting modern images to Apple IIgs Super High-Resolution format.

## Features

- 🖼️ **Drag-and-drop** image upload
- 👁️ **Side-by-side preview** of original and converted images
- ⚙️ **Full control** over all conversion options
- 📊 **Real-time statistics** (palette usage, file size, processing time)
- 💾 **Download** converted .3200 files
- 📱 **Responsive design** works on desktop and mobile

## Installation

### 1. Install Dependencies

The Web UI requires Flask and Flask-CORS. Install using the virtual environment:

```bash
# Activate your virtual environment first
source .venv/bin/activate

# Install with UI dependencies
pip install -e ".[ui]"

# Or if using uv:
uv pip install -e ".[ui]"
```

### 2. Run the Server

```bash
# Method 1: Run directly
python -m gs_convert_ui.app

# Method 2: Use Flask CLI
export FLASK_APP=gs_convert_ui.app
flask run --debug

# Method 3: From Python
python
>>> from gs_convert_ui import main
>>> main()
```

The UI will be available at: **http://localhost:5000**

## Usage

1. **Upload an Image**
   - Drag and drop an image onto the upload zone
   - Or click to browse and select a file
   - Supported formats: PNG, JPEG, GIF, BMP, TIFF

2. **Configure Options**
   - **Dithering Algorithm**: How colors blend (Atkinson, Floyd-Steinberg, JJN, etc.)
   - **Quantization Method**: How colors are chosen per scanline
   - **Optimize Palettes**: Enable palette reuse to reduce banding
   - **Error Threshold**: Controls how aggressively palettes are reused
   - **Aspect Ratio Correction**: Compensate for non-square Apple IIgs pixels
   - **Linear RGB**: Use perceptually correct color processing

3. **Convert**
   - Click "Convert to Apple IIgs Format"
   - View the preview and statistics
   - Download the .3200 file

4. **Download**
   - Click "Download .3200 File" to save the converted image

## API Endpoints

The web UI exposes a REST API:

### POST /api/upload
Upload an image file.

**Request**: `multipart/form-data` with `image` file

**Response**:
```json
{
  "id": "session-uuid",
  "preview_url": "data:image/png;base64,...",
  "info": {
    "width": 1920,
    "height": 1080,
    "format": "JPEG",
    "file_size": 245678
  }
}
```

### POST /api/convert
Convert uploaded image with options.

**Request**:
```json
{
  "id": "session-uuid",
  "options": {
    "dither": "atkinson",
    "quantize": "median-cut",
    "optimize_palettes": false,
    "error_threshold": 2000.0,
    "aspect_correct": true,
    "use_linear_rgb": true
  }
}
```

**Response**:
```json
{
  "preview_url": "data:image/png;base64,...",
  "stats": {
    "unique_palettes": 16,
    "file_size": 32768,
    "dimensions": [320, 200],
    "processing_time": 0.45
  },
  "download_url": "/api/download/session-uuid"
}
```

### GET /api/download/{session_id}
Download the converted .3200 file.

### GET /api/stats/{session_id}
Get detailed statistics for a conversion.

### DELETE /api/cleanup/{session_id}
Clean up temporary files for a session.

## Architecture

The Web UI uses **library integration** - it directly imports and calls functions from the `gs_convert` package:

```python
from gs_convert.pipeline import convert_image

# Direct function call - no CLI subprocess
convert_image(
    input_path=input_path,
    output_path=output_path,
    dither_method=dither,
    quantize_method=quantize
)
```

**Benefits**:
- ✅ Fast (no process startup overhead)
- ✅ Better error handling (Python exceptions vs parsing CLI output)
- ✅ Access to intermediate results
- ✅ Detailed statistics
- ✅ In-memory processing

## File Structure

```
gs_convert_ui/
├── __init__.py         # Package initialization
├── app.py              # Flask application and API routes
├── config.py           # Configuration settings
├── utils.py            # Helper functions
├── static/
│   ├── css/
│   │   └── style.css   # UI styling
│   └── js/
│       └── app.js      # Frontend JavaScript
└── templates/
    └── index.html      # Main UI template
```

## Configuration

### Environment Variables

- `FLASK_SECRET_KEY`: Secret key for Flask sessions (default: development key)
- `FLASK_DEBUG`: Enable debug mode (default: False in production)

### Settings (config.py)

- `UPLOAD_FOLDER`: Directory for temporary files (default: `/tmp/gs_convert_uploads`)
- `MAX_CONTENT_LENGTH`: Maximum upload size (default: 16MB)
- `SESSION_TIMEOUT_SECONDS`: Auto-cleanup old sessions (default: 1 hour)

## Development

### Running in Debug Mode

```bash
export FLASK_APP=gs_convert_ui.app
flask run --debug
```

Debug mode provides:
- Auto-reload on code changes
- Detailed error pages
- Debug toolbar

### Production Deployment

For production, use a proper WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn gs_convert_ui.app:app -b 0.0.0.0:5000 -w 4
```

Options:
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `-w 4`: Use 4 worker processes
- `--timeout 120`: Increase timeout for long conversions

## Security Considerations

### Development vs Production

**⚠️ The default setup is for development only!**

For production deployment:

1. **Set a secure secret key**:
   ```bash
   export FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

2. **Disable debug mode**:
   ```python
   app.run(debug=False)
   ```

3. **Use HTTPS**: Deploy behind a reverse proxy (nginx, Apache) with SSL

4. **File validation**: The UI validates file types and sizes, but consider additional security measures

5. **Rate limiting**: Add rate limiting to prevent abuse:
   ```bash
   pip install flask-limiter
   ```

## Troubleshooting

### Port Already in Use

If port 5000 is already in use:

```bash
# Use a different port
flask run --port 5001

# Or with Python
python -m gs_convert_ui.app
# Edit app.py to change: app.run(port=5001)
```

### Upload Fails

- Check file size (must be < 16MB)
- Check file type (PNG, JPEG, GIF, BMP, TIFF only)
- Check disk space in `/tmp` directory

### Conversion Errors

Check the browser console (F12) for detailed error messages. Common issues:

- Missing dependencies: Install with `pip install -e ".[ui]"`
- Permission issues: Check `/tmp/gs_convert_uploads` directory permissions
- Memory issues: Large images may require more RAM

### Old Sessions Not Cleaning Up

The UI automatically cleans up sessions older than 1 hour. To manually clean:

```bash
rm -rf /tmp/gs_convert_uploads/*
```

## Browser Compatibility

Tested and working on:

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

Requires:
- Modern browser with ES6+ support
- JavaScript enabled
- Canvas API support

## Tips for Best Results

### For Photos
- Use **Floyd-Steinberg** or **JJN** dithering for smooth gradients
- Enable **Optimize Palettes** to reduce banding
- Keep **Linear RGB** enabled for accurate colors

### For Animation/Graphics
- Try **Global** quantization method
- Use **Atkinson** dithering for retro look
- Or **None** for clean, posterized appearance

### For Pixel Art
- Use **Median Cut** quantization
- Try **Ordered** dithering for retro patterns
- Or **None** for clean edges

### Reducing Banding
- Enable **Optimize Palettes**
- Increase **Error Threshold** (try 5000-10000)
- Try **Global** quantization for graphics with limited colors

## Future Enhancements

Planned features:

- [ ] Real-time preview (convert on option change)
- [ ] Comparison slider (before/after)
- [ ] Batch processing (multiple images)
- [ ] Preset management (save favorite settings)
- [ ] Advanced statistics (palette visualization, color histograms)
- [ ] Export preview as PNG
- [ ] WebSocket support for progress updates

## License

Part of the gs-convert project. See main repository for license information.

## Credits

Built using:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Flask-CORS](https://flask-cors.readthedocs.io/) - CORS support
- gs-convert library - Image conversion engine

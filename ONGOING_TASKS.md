# Ongoing Tasks

## ✅ Completed: Flask Web UI Implementation

**Status**: COMPLETE - Committed and pushed to GitHub

**Goal**: Build a browser-based UI for gs-convert that provides real-time preview and easy access to all conversion options.

**Approach**: Library integration (direct imports from `gs_convert` package)

**Repository**: https://github.com/skeptomai/gs-convert

---

## Current Tasks: Post-Launch Improvements

### GitHub Repository Enhancement

- [ ] Add topics/tags on GitHub (apple-iigs, retro-computing, image-conversion, dithering, python)
- [ ] Add screenshots to README.md showing the Web UI in action
- [ ] Add example conversions (before/after images)
- [ ] Create GitHub repository social preview image

### Release Management

- [ ] Create first release (v0.1.0)
- [ ] Write release notes highlighting features
- [ ] Tag the release in git

### Community Outreach

- [ ] Share on retro computing forums
- [ ] Post on Reddit (r/retrobattlestations, r/apple2, r/vintageapple)
- [ ] Share on social media / Mastodon / etc.
- [ ] Add to awesome-retro-computing lists

### CI/CD & Testing

- [ ] Set up GitHub Actions for automated testing
- [ ] Add pytest test suite
- [ ] Set up code coverage reporting
- [ ] Add pre-commit hooks

### PyPI Publishing

- [ ] Test installation from source
- [ ] Create PyPI account/token
- [ ] Publish to PyPI test server first
- [ ] Publish official release to PyPI
- [ ] Add installation instructions: `pip install gs-convert`

### Homebrew Distribution

- [ ] Create Homebrew formula
- [ ] Test formula locally
- [ ] Submit to homebrew-core or create tap
- [ ] Add installation instructions: `brew install gs-convert`

### Future Features (Web UI)

- [ ] Real-time preview on option change (with debouncing)
- [ ] Comparison slider (before/after)
- [ ] Batch processing (multiple images)
- [ ] Preset management (save favorite settings)
- [ ] Advanced statistics (palette visualization, color histograms)
- [ ] Export preview as PNG
- [ ] WebSocket support for progress updates
- [ ] Drag-to-reorder for batch processing

### Future Features (Core)

- [ ] Region-based priority weighting (prioritize faces over backgrounds)
- [ ] 640×200 mode support
- [ ] Batch optimization (share palettes across multiple images)
- [ ] Custom palette import/export
- [ ] Integration with disk image creation tools
- [ ] Animation support (GIF to SHR slideshow)

---

## Implementation Plan

### Phase 1: Backend API (Flask Server)

#### 1.1 Project Structure
```
gs_convert_ui/
├── __init__.py
├── app.py                 # Flask application and API routes
├── config.py              # Configuration (temp directories, etc.)
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   ├── js/
│   │   └── app.js         # Frontend JavaScript
│   └── images/
│       └── placeholder.png
├── templates/
│   └── index.html         # Main UI template
└── utils.py               # Helper functions
```

#### 1.2 Dependencies to Add
Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
ui = [
    "flask>=3.0.0",
    "flask-cors>=4.0.0"
]
```

#### 1.3 Flask Routes

**app.py** - Main application with routes:

```python
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
import base64

from gs_convert.pipeline import convert_image
from gs_convert.format_writer import read_3200_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/gs_convert_uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# API Routes:
# GET  /                     - Main UI page
# POST /api/upload           - Upload image, return preview
# POST /api/convert          - Convert with options, return preview + stats
# GET  /api/download/<id>    - Download .3200 file
# GET  /api/stats/<id>       - Get conversion statistics
# DELETE /api/cleanup/<id>   - Clean up temporary files
```

**Endpoints**:

1. **GET /** - Serve main HTML page
2. **POST /api/upload** - Accept image file, return scaled preview
   - Input: multipart/form-data with image file
   - Output: `{"id": "abc123", "preview_url": "data:image/png;base64,..."}`

3. **POST /api/convert** - Run conversion with options
   - Input:
     ```json
     {
       "id": "abc123",
       "options": {
         "dither": "atkinson",
         "quantize": "median-cut",
         "optimize_palettes": false,
         "error_threshold": 2000.0,
         "aspect_correct": 1.2,
         "use_linear_rgb": true
       }
     }
     ```
   - Output:
     ```json
     {
       "preview_url": "data:image/png;base64,...",
       "stats": {
         "unique_palettes": 16,
         "file_size": 32768,
         "dimensions": [320, 200],
         "processing_time": 0.45
       },
       "download_url": "/api/download/abc123"
     }
     ```

4. **GET /api/download/<id>** - Download .3200 file
   - Returns: Binary .3200 file with appropriate headers

5. **GET /api/stats/<id>** - Get detailed statistics
   - Returns: Palette information, SCB data, color analysis

6. **DELETE /api/cleanup/<id>** - Remove temporary files

#### 1.4 Helper Functions (utils.py)

```python
def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 data URL"""

def generate_session_id() -> str:
    """Generate unique session ID for file tracking"""

def get_conversion_stats(output_3200_path: str) -> dict:
    """Extract detailed statistics from .3200 file"""

def cleanup_session(session_id: str):
    """Remove all temporary files for a session"""
```

---

### Phase 2: Frontend (HTML/CSS/JavaScript)

#### 2.1 Main HTML Template (templates/index.html)

**Layout**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>GS-Convert Web UI</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>GS-Convert</h1>
            <p>Apple IIgs Image Converter</p>
        </header>

        <main>
            <!-- File Upload Area -->
            <div class="upload-section">
                <input type="file" id="imageUpload" accept="image/*">
                <div id="dropZone" class="drop-zone">
                    Drop image here or click to select
                </div>
            </div>

            <!-- Image Comparison -->
            <div class="preview-section">
                <div class="image-panel">
                    <h3>Original</h3>
                    <canvas id="originalCanvas" width="320" height="200"></canvas>
                    <p id="originalInfo"></p>
                </div>

                <div class="image-panel">
                    <h3>Apple IIgs Preview</h3>
                    <canvas id="previewCanvas" width="320" height="200"></canvas>
                    <p id="conversionInfo"></p>
                </div>
            </div>

            <!-- Options Panel -->
            <div class="options-section">
                <h3>Conversion Options</h3>

                <div class="option-group">
                    <label for="dither">Dithering Algorithm:</label>
                    <select id="dither">
                        <option value="atkinson" selected>Atkinson (Retro)</option>
                        <option value="floyd-steinberg">Floyd-Steinberg (Smooth)</option>
                        <option value="jjn">Jarvis-Judice-Ninke (High Quality)</option>
                        <option value="stucki">Stucki</option>
                        <option value="burkes">Burkes</option>
                        <option value="ordered">Ordered (Pattern)</option>
                        <option value="none">None (Clean)</option>
                    </select>
                </div>

                <div class="option-group">
                    <label for="quantize">Quantization Method:</label>
                    <select id="quantize">
                        <option value="median-cut" selected>Median Cut (Default)</option>
                        <option value="optimized">Optimized (Reduce Banding)</option>
                        <option value="global">Global (Animation/Graphics)</option>
                    </select>
                </div>

                <div class="option-group">
                    <label for="optimizePalettes">
                        <input type="checkbox" id="optimizePalettes">
                        Optimize Palettes (Reduce Banding)
                    </label>
                </div>

                <div class="option-group">
                    <label for="errorThreshold">Error Threshold:</label>
                    <input type="range" id="errorThreshold" min="500" max="10000" value="2000" step="500">
                    <span id="thresholdValue">2000</span>
                </div>

                <div class="option-group">
                    <label for="aspectCorrect">
                        <input type="checkbox" id="aspectCorrect" checked>
                        Aspect Ratio Correction (1.2x)
                    </label>
                </div>

                <div class="option-group">
                    <label for="linearRgb">
                        <input type="checkbox" id="linearRgb" checked>
                        Use Linear RGB (Perceptually Correct)
                    </label>
                </div>

                <button id="convertBtn" class="btn-primary">Convert</button>
                <button id="downloadBtn" class="btn-secondary" disabled>Download .3200 File</button>
            </div>

            <!-- Statistics Panel -->
            <div class="stats-section">
                <h3>Conversion Statistics</h3>
                <div id="stats">
                    <p>Upload an image to begin</p>
                </div>
            </div>
        </main>
    </div>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

#### 2.2 CSS Styling (static/css/style.css)

**Design Goals**:
- Clean, modern interface
- Responsive layout
- Clear visual hierarchy
- Retro-inspired color scheme (to match Apple IIgs aesthetic)

**Key Styles**:
```css
/* Modern, clean design with retro color accents */
:root {
    --primary-color: #0066cc;
    --iigs-green: #00ff00;    /* Classic Apple IIgs green */
    --iigs-amber: #ff8800;    /* Classic monitor amber */
    --background: #f5f5f5;
    --panel-bg: #ffffff;
    --text: #333333;
    --border: #dddddd;
}

/* Layout: Flexbox for responsive design */
/* Image panels: Side-by-side on desktop, stacked on mobile */
/* Options: Clear grouping with visual separation */
/* Drop zone: Drag-and-drop with visual feedback */
```

#### 2.3 JavaScript Frontend (static/js/app.js)

**Functionality**:

1. **File Upload Handling**
   - Drag-and-drop support
   - File validation (image types, size limits)
   - Display original image preview

2. **Options Management**
   - Live updates when options change
   - Enable/disable related controls
   - Show/hide conditional options

3. **Conversion Process**
   - Show loading spinner
   - Call /api/convert endpoint
   - Display preview image
   - Show statistics

4. **Download Management**
   - Enable download button after conversion
   - Track session ID for file access

**Key Functions**:
```javascript
// File upload and preview
function handleFileUpload(file) { ... }
function displayOriginalImage(imageData) { ... }

// Conversion
async function convertImage() { ... }
function displayConversionResult(result) { ... }

// Statistics
function updateStats(stats) { ... }
function formatPaletteInfo(paletteCount) { ... }

// Download
function downloadFile(sessionId) { ... }

// UI updates
function showLoading() { ... }
function hideLoading() { ... }
function showError(message) { ... }
```

---

### Phase 3: Integration and Testing

#### 3.1 Integration Points

**Backend ↔ gs_convert library**:
```python
# Direct imports
from gs_convert.pipeline import convert_image
from gs_convert.quantize import median_cut_quantize, optimized_quantize, global_quantize
from gs_convert.dither import (AtkinsonDitherer, FloydSteinbergDitherer,
                                JJNDitherer, StuckiDitherer, BurkesDitherer,
                                OrderedDitherer, NoneDitherer)
from gs_convert.format_writer import write_3200_file, read_3200_file
from gs_convert.color import rgb24_to_iigs12, iigs12_to_rgb24
```

**Frontend ↔ Backend API**:
- Fetch API for all HTTP requests
- Base64 encoding for image previews
- JSON for configuration and stats

#### 3.2 File Management

**Temporary File Strategy**:
```
/tmp/gs_convert_uploads/
├── {session_id}/
│   ├── original.{ext}       # Uploaded image
│   ├── resized.png          # 320x200 scaled version
│   ├── output.3200          # Converted file
│   └── preview.png          # Preview image
```

**Cleanup Strategy**:
- Auto-cleanup after 1 hour
- Manual cleanup via DELETE endpoint
- Cleanup on server restart

#### 3.3 Error Handling

**Backend**:
- File validation (type, size)
- Conversion errors (catch and return helpful messages)
- Missing session IDs
- Disk space issues

**Frontend**:
- Network errors
- Invalid file types
- Server errors (display user-friendly messages)
- Loading timeouts

---

### Phase 4: Advanced Features (Future Enhancements)

#### 4.1 Real-time Preview Updates
- WebSocket connection for live updates
- Convert on option change (with debounce)
- Progress updates during conversion

#### 4.2 Comparison Features
- Side-by-side slider (before/after)
- Difference view (highlight changes)
- Zoom and pan for detail inspection

#### 4.3 Batch Processing
- Upload multiple images
- Apply same settings to all
- Download as .zip

#### 4.4 Preset Management
- Save favorite settings
- Load presets (e.g., "Animation", "Photo", "Pixel Art")
- Share presets as JSON

#### 4.5 Advanced Statistics
- Palette visualization (show actual colors)
- Scanline-by-scanline palette map
- Color histogram
- Quality metrics

#### 4.6 Export Options
- Export preview as PNG
- Export comparison images
- Generate conversion report

---

## Implementation Order

### Week 1: Core Functionality
1. ✅ Set up Flask application structure
2. ✅ Implement upload endpoint
3. ✅ Implement convert endpoint with library integration
4. ✅ Implement download endpoint
5. ✅ Create basic HTML template
6. ✅ Add CSS styling
7. ✅ Implement JavaScript upload handling
8. ✅ Implement JavaScript conversion handling

### Week 2: Polish and Features
1. ✅ Add all conversion options to UI
2. ✅ Implement statistics display
3. ✅ Add error handling and validation
4. ✅ Implement drag-and-drop
5. ✅ Add loading states and spinners
6. ✅ Responsive design for mobile
7. ✅ Testing and bug fixes

### Future: Advanced Features
1. ⬜ Real-time preview on option change
2. ⬜ Comparison slider
3. ⬜ Batch processing
4. ⬜ Preset management
5. ⬜ Advanced statistics visualizations

---

## Running the UI

### Development Mode
```bash
# Install with UI dependencies
uv pip install -e ".[ui]"

# Run Flask development server
python -m gs_convert_ui.app

# Or with Flask CLI
export FLASK_APP=gs_convert_ui.app
flask run --debug
```

Access at: http://localhost:5000

### Production Mode
```bash
# Use production WSGI server
uv pip install gunicorn
gunicorn gs_convert_ui.app:app -b 0.0.0.0:5000
```

### Desktop App (Future)
- Use PyWebView to wrap Flask app as desktop application
- Single executable, no browser needed
- Native file dialogs

---

## Testing Strategy

### Backend Testing
- Unit tests for each endpoint
- Test library integration
- Test file cleanup
- Test error conditions

### Frontend Testing
- Manual testing in multiple browsers
- Responsive design testing
- File upload edge cases
- Network error handling

### Integration Testing
- Full conversion workflow
- All dithering algorithms
- All quantization methods
- Various image formats and sizes

---

## Documentation

### User Documentation
- Quick start guide
- Option explanations
- Tips for different image types
- Troubleshooting

### Developer Documentation
- API endpoint reference
- Architecture overview
- Adding new features
- Deployment guide

---

## Success Criteria

**Minimum Viable Product (MVP)**:
- ✅ Upload image
- ✅ Display original preview
- ✅ Select dithering and quantization options
- ✅ Convert and display Apple IIgs preview
- ✅ Download .3200 file
- ✅ Show basic statistics (palette count, file size)

**Complete Implementation**:
- ✅ All conversion options exposed in UI
- ✅ Comprehensive error handling
- ✅ Responsive design
- ✅ Drag-and-drop support
- ✅ Real-time statistics
- ✅ Clean, polished interface

**Advanced (Future)**:
- ⬜ Real-time preview updates
- ⬜ Comparison tools
- ⬜ Batch processing
- ⬜ Preset management

---

## Notes

- **Library integration** is key - no CLI subprocess overhead
- **Temporary file management** is important for cleanup
- **Error handling** must be comprehensive for good UX
- **Responsive design** ensures usability on all devices
- **Statistics** help users understand conversion results

---

## References

- Flask documentation: https://flask.palletsprojects.com/
- Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- HTML Canvas: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- CSS Flexbox: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout

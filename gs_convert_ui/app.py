"""Flask web UI for gs-convert."""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import time

from gs_convert.pipeline import convert_image, generate_preview_image
from gs_convert.format_writer import read_3200_file

from .config import (
    UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH,
    SECRET_KEY,
    ALLOWED_EXTENSIONS
)
from .utils import (
    generate_session_id,
    allowed_file,
    get_session_folder,
    image_to_base64,
    get_conversion_stats,
    cleanup_session,
    cleanup_old_sessions,
    get_image_info
)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app)

# Clean up old sessions on startup
cleanup_old_sessions()


@app.route('/')
def index():
    """Serve the main UI page."""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    Upload an image and return a session ID and preview.
    
    Expected: multipart/form-data with 'image' file
    Returns: {"id": "session_id", "preview_url": "data:image/...", "info": {...}}
    """
    # Clean up old sessions periodically
    cleanup_old_sessions()
    
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Generate session ID and create folder
    session_id = generate_session_id()
    session_folder = get_session_folder(session_id)
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    file_ext = Path(filename).suffix
    original_path = session_folder / f"original{file_ext}"
    file.save(str(original_path))
    
    # Get image info
    info = get_image_info(original_path)
    
    # Return session ID and preview
    try:
        preview_url = image_to_base64(original_path)
        return jsonify({
            "id": session_id,
            "preview_url": preview_url,
            "info": info
        })
    except Exception as e:
        cleanup_session(session_id)
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500


@app.route('/api/convert', methods=['POST'])
def convert():
    """
    Convert the uploaded image with specified options.
    
    Expected JSON:
    {
        "id": "session_id",
        "options": {
            "dither": "atkinson",
            "quantize": "median-cut",
            "optimize_palettes": false,
            "error_threshold": 2000.0,
            "aspect_correct": true,
            "use_linear_rgb": true
        }
    }
    
    Returns:
    {
        "preview_url": "data:image/...",
        "stats": {...},
        "download_url": "/api/download/session_id",
        "processing_time": 0.45
    }
    """
    data = request.json
    
    if not data or 'id' not in data:
        return jsonify({"error": "Session ID required"}), 400
    
    session_id = data['id']
    session_folder = get_session_folder(session_id)
    
    # Find original file
    original_files = list(session_folder.glob("original.*"))
    if not original_files:
        return jsonify({"error": "Original image not found. Please upload again."}), 404
    
    original_path = original_files[0]
    
    # Get options
    options = data.get('options', {})
    dither = options.get('dither', 'atkinson')
    quantize = options.get('quantize', 'median-cut')
    optimize_palettes = options.get('optimize_palettes', False)
    error_threshold = float(options.get('error_threshold', 2000.0))
    aspect_correct = 1.2 if options.get('aspect_correct', True) else 1.0
    use_linear_rgb = options.get('use_linear_rgb', True)
    gamma = float(options.get('gamma', 1.0))
    brightness = float(options.get('brightness', 1.0))

    # Output paths
    output_path = session_folder / "output.3200"
    preview_path = session_folder / "preview.png"

    # Run conversion
    start_time = time.time()

    try:
        # Run conversion
        convert_image(
            input_path=str(original_path),
            output_path=str(output_path),
            dither_method=dither,
            quantize_method=quantize,
            aspect_correct=aspect_correct,
            use_linear_rgb=use_linear_rgb,
            optimize_palettes=optimize_palettes,
            error_threshold=error_threshold,
            gamma=gamma,
            brightness=brightness
        )

        # Generate preview from the .3200 file
        pixel_indices, scb_bytes, palettes = read_3200_file(str(output_path))
        generate_preview_image(pixel_indices, palettes, scb_bytes, str(preview_path))

        processing_time = time.time() - start_time

        # Get statistics
        stats = get_conversion_stats(output_path)
        stats['processing_time'] = round(processing_time, 2)

        # Return preview and stats
        preview_url = image_to_base64(preview_path)
        
        return jsonify({
            "preview_url": preview_url,
            "stats": stats,
            "download_url": f"/api/download/{session_id}",
            "processing_time": round(processing_time, 2)
        })
        
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500


@app.route('/api/download/<session_id>', methods=['GET'])
def download(session_id):
    """Download the converted .3200 file."""
    session_folder = UPLOAD_FOLDER / session_id
    output_path = session_folder / "output.3200"
    
    if not output_path.exists():
        return jsonify({"error": "Converted file not found"}), 404
    
    return send_file(
        str(output_path),
        as_attachment=True,
        download_name='converted.3200',
        mimetype='application/octet-stream'
    )


@app.route('/api/stats/<session_id>', methods=['GET'])
def get_stats(session_id):
    """Get detailed statistics for a conversion."""
    session_folder = UPLOAD_FOLDER / session_id
    output_path = session_folder / "output.3200"
    
    if not output_path.exists():
        return jsonify({"error": "Converted file not found"}), 404
    
    stats = get_conversion_stats(output_path)
    return jsonify(stats)


@app.route('/api/cleanup/<session_id>', methods=['DELETE'])
def cleanup(session_id):
    """Clean up temporary files for a session."""
    success = cleanup_session(session_id)
    
    if success:
        return jsonify({"message": "Session cleaned up successfully"})
    else:
        return jsonify({"error": "Session not found"}), 404


def main():
    """Run the Flask development server."""
    import os
    port = int(os.environ.get('FLASK_PORT', 5001))
    print("Starting GS-Convert Web UI...")
    print(f"Access at: http://localhost:{port}")
    print("(Press CTRL+C to quit)")
    app.run(debug=True, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()

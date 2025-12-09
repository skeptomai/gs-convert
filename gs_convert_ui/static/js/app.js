// GS-Convert Web UI - Frontend JavaScript

// State
let sessionId = null;
let convertedData = null;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const imageUpload = document.getElementById('imageUpload');
const previewSection = document.getElementById('previewSection');
const optionsSection = document.getElementById('optionsSection');
const statsSection = document.getElementById('statsSection');
const originalCanvas = document.getElementById('originalCanvas');
const previewCanvas = document.getElementById('previewCanvas');
const originalInfo = document.getElementById('originalInfo');
const conversionInfo = document.getElementById('conversionInfo');
const convertBtn = document.getElementById('convertBtn');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const errorMessage = document.getElementById('errorMessage');

// Option elements
const ditherSelect = document.getElementById('dither');
const quantizeSelect = document.getElementById('quantize');
const optimizePalettes = document.getElementById('optimizePalettes');
const errorThreshold = document.getElementById('errorThreshold');
const thresholdValue = document.getElementById('thresholdValue');
const aspectCorrect = document.getElementById('aspectCorrect');
const linearRgb = document.getElementById('linearRgb');

// Stats elements
const statPalettes = document.getElementById('statPalettes');
const statFileSize = document.getElementById('statFileSize');
const statDimensions = document.getElementById('statDimensions');
const statTime = document.getElementById('statTime');

// Event Listeners
dropZone.addEventListener('click', function() { imageUpload.click(); });
dropZone.addEventListener('dragover', handleDragOver);
dropZone.addEventListener('dragleave', handleDragLeave);
dropZone.addEventListener('drop', handleDrop);
imageUpload.addEventListener('change', handleFileSelect);
convertBtn.addEventListener('click', handleConvert);
downloadBtn.addEventListener('click', handleDownload);
resetBtn.addEventListener('click', handleReset);
errorThreshold.addEventListener('input', function(e) {
    thresholdValue.textContent = e.target.value;
});

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// File Upload
async function handleFile(file) {
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/tiff'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file type. Please upload a PNG, JPEG, GIF, BMP, or TIFF image.');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File too large. Maximum size is 16MB.');
        return;
    }
    
    hideError();
    showLoading('Uploading...');
    
    try {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const data = await response.json();
        sessionId = data.id;
        
        // Display original image
        displayOriginalImage(data.preview_url, data.info);
        
        // Show UI sections
        previewSection.style.display = 'grid';
        optionsSection.style.display = 'block';
        
        hideLoading();
        
    } catch (error) {
        hideLoading();
        showError('Upload failed: ' + error.message);
    }
}

// Display original image
function displayOriginalImage(imageData, info) {
    const img = new Image();
    img.onload = function() {
        const ctx = originalCanvas.getContext('2d');
        ctx.drawImage(img, 0, 0, 320, 200);
        
        // Show image info
        const infoText = 'Original: ' + info.width + 'x' + info.height + ' • ' + info.format + ' • ' + formatFileSize(info.file_size);
        originalInfo.textContent = infoText;
    };
    img.src = imageData;
}

// Convert Image
async function handleConvert() {
    if (!sessionId) {
        showError('No image uploaded');
        return;
    }
    
    hideError();
    showLoading('Converting to Apple IIgs format...');
    convertBtn.disabled = true;
    downloadBtn.disabled = true;
    
    try {
        const options = {
            dither: ditherSelect.value,
            quantize: quantizeSelect.value,
            optimize_palettes: optimizePalettes.checked,
            error_threshold: parseFloat(errorThreshold.value),
            aspect_correct: aspectCorrect.checked,
            use_linear_rgb: linearRgb.checked
        };
        
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: sessionId,
                options: options
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Conversion failed');
        }
        
        const data = await response.json();
        convertedData = data;
        
        // Display preview
        displayPreview(data.preview_url);
        
        // Update stats
        updateStats(data.stats);
        
        // Enable download
        downloadBtn.disabled = false;
        
        // Show stats section
        statsSection.style.display = 'block';
        
        hideLoading();
        convertBtn.disabled = false;
        
        conversionInfo.textContent = 'Converted in ' + data.processing_time + 's';
        
    } catch (error) {
        hideLoading();
        convertBtn.disabled = false;
        showError('Conversion failed: ' + error.message);
    }
}

// Display preview
function displayPreview(imageData) {
    const img = new Image();
    img.onload = function() {
        const ctx = previewCanvas.getContext('2d');
        ctx.clearRect(0, 0, 320, 200);
        ctx.drawImage(img, 0, 0, 320, 200);
    };
    img.src = imageData;
}

// Update statistics
function updateStats(stats) {
    statPalettes.textContent = stats.unique_palettes + '/16';
    statFileSize.textContent = formatFileSize(stats.file_size);
    statDimensions.textContent = stats.dimensions[0] + 'x' + stats.dimensions[1];
    statTime.textContent = stats.processing_time + 's';
}

// Download converted file
function handleDownload() {
    if (!sessionId) return;
    
    window.location.href = '/api/download/' + sessionId;
}

// Reset UI
function handleReset() {
    // Clean up session if exists
    if (sessionId) {
        fetch('/api/cleanup/' + sessionId, { method: 'DELETE' })
            .catch(function(err) { console.error('Cleanup failed:', err); });
    }
    
    // Reset state
    sessionId = null;
    convertedData = null;
    
    // Clear canvases
    const ctx1 = originalCanvas.getContext('2d');
    ctx1.clearRect(0, 0, 320, 200);
    const ctx2 = previewCanvas.getContext('2d');
    ctx2.clearRect(0, 0, 320, 200);
    
    // Hide sections
    previewSection.style.display = 'none';
    optionsSection.style.display = 'none';
    statsSection.style.display = 'none';
    
    // Reset file input
    imageUpload.value = '';
    
    // Reset buttons
    downloadBtn.disabled = true;
    convertBtn.disabled = false;
    
    // Clear info
    originalInfo.textContent = '';
    conversionInfo.textContent = '';
    
    hideError();
}

// UI Helper Functions
function showLoading(message) {
    if (!message) message = 'Processing...';
    loadingSpinner.style.display = 'flex';
    loadingSpinner.querySelector('p').textContent = message;
}

function hideLoading() {
    loadingSpinner.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto-hide after 10 seconds
    setTimeout(function() {
        hideError();
    }, 10000);
}

function hideError() {
    errorMessage.style.display = 'none';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Initialize
console.log('GS-Convert Web UI loaded');

# UI Options for GS-Convert

This document outlines various UI approaches for building a graphical interface for the gs-convert tool.

## Overview

All options below can drive the conversion engine either by:
- **Library integration**: Importing and calling Python functions directly
- **CLI subprocess**: Invoking the `gs-convert` command-line tool

**Recommendation**: Library integration is faster, more flexible, and easier to debug.

---

## Option 1: Flask Web UI ⭐ (Recommended for Quick Start)

**Technology**: Python + Flask/FastAPI + HTML/JavaScript

### Architecture
- Backend: Lightweight Python web server (Flask or FastAPI)
- Frontend: HTML/CSS/JavaScript for interactivity
- Integration: Direct imports from `gs_convert` package
- Access: Browser-based (localhost:5000)

### Pros
- ✅ Fast to implement
- ✅ Cross-platform (runs in any modern browser)
- ✅ Can reuse all existing Python code directly
- ✅ Live preview updates without page reload
- ✅ Easy to share and demo (just visit a URL)
- ✅ No new programming language needed
- ✅ Can add advanced features (WebSockets for progress, comparison sliders)
- ✅ Responsive design works on different screen sizes

### Cons
- ❌ Requires browser
- ❌ Not a native desktop app feel
- ❌ Need to keep server running (but can package as desktop app with PyWebView)
- ❌ Less suitable for offline/air-gapped environments

### Example Structure
```
gs_convert_ui/
├── app.py              # Flask server with API endpoints
├── static/
│   ├── style.css       # Styling
│   └── app.js          # Client-side interactivity
├── templates/
│   └── index.html      # Main UI
└── uploads/            # Temporary file storage
```

### Integration Approach
```python
from gs_convert.pipeline import convert_image

@app.post("/api/convert")
def convert():
    convert_image(
        input_path=input_path,
        output_path=output_path,
        dither_method=request.form['dither'],
        quantize_method=request.form['quantize']
    )
    return {"preview_url": "/preview.png"}
```

### UI Layout
```
┌─────────────────────────────────────────────────┐
│  GS-Convert Web UI                              │
├──────────────┬──────────────────────────────────┤
│              │  Options Panel:                  │
│  Original    │  • Dither: [dropdown]            │
│  Image       │  • Quantize: [dropdown]          │
│              │  • Error threshold: [slider]     │
│  320x200     │  • Aspect correct: [checkbox]    │
│              │  [Convert] button                │
├──────────────┼──────────────────────────────────┤
│              │  Stats:                          │
│  Preview     │  • Palettes used: 16/16          │
│  (Apple IIgs)│  • File size: 32,768 bytes       │
│              │  [Download .3200] button         │
│  320x200     │                                  │
└──────────────┴──────────────────────────────────┘
```

---

## Option 2: Electron Desktop App

**Technology**: Electron (JavaScript/TypeScript) + React/Vue/Svelte

### Architecture
- Frontend: Modern JavaScript framework (React, Vue, or Svelte)
- Backend: Node.js process
- Integration: Either CLI subprocess or Python bindings (pynode)
- Packaging: Native executable for macOS/Windows/Linux

### Pros
- ✅ True native desktop app experience
- ✅ Rich UI possibilities with modern web frameworks
- ✅ Large ecosystem of components and libraries
- ✅ Excellent drag-and-drop file handling
- ✅ Can bundle Python tool inside the app
- ✅ Auto-update capabilities
- ✅ System tray integration
- ✅ Native file dialogs and notifications

### Cons
- ❌ Need to learn JavaScript/TypeScript if not familiar
- ❌ Large app size (~100-200MB minimum)
- ❌ More complex build and packaging process
- ❌ CLI subprocess overhead (unless using Python bindings)
- ❌ Two separate codebases to maintain (JS frontend + Python backend)
- ❌ Memory overhead from Chromium

### Integration Approach
```javascript
// Calls CLI as subprocess
const { exec } = require('child_process');

exec('gs-convert convert input.jpg output.3200 --preview preview.png',
     (error, stdout, stderr) => {
       if (error) {
         handleError(stderr);
       } else {
         updatePreview('preview.png');
       }
     });
```

### Distribution
- macOS: `.app` bundle or `.dmg` installer
- Windows: `.exe` installer or portable `.exe`
- Linux: `.AppImage`, `.deb`, or `.rpm`

---

## Option 3: Native Python GUI (Tkinter)

**Technology**: Python + Tkinter (built into Python standard library)

### Architecture
- Single Python application
- Tkinter for GUI widgets and layout
- Direct function calls to gs_convert modules
- No external dependencies beyond Python stdlib

### Pros
- ✅ No additional dependencies (Tkinter is built-in)
- ✅ Same language as existing code
- ✅ Tight integration with conversion functions
- ✅ Fast preview updates (no subprocess)
- ✅ Easy to distribute as Python package
- ✅ Small footprint
- ✅ Quick to prototype

### Cons
- ❌ Tkinter UI looks dated and less polished
- ❌ Less flexible for modern, attractive designs
- ❌ Limited built-in widgets
- ❌ Image handling can be clunky
- ❌ Not ideal for complex layouts
- ❌ Platform inconsistencies in appearance

### Example Code
```python
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from gs_convert import convert_image

class ConverterUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GS-Convert")

        # Original image preview
        self.original_canvas = tk.Canvas(width=320, height=200)
        self.original_canvas.pack()

        # Converted preview
        self.preview_canvas = tk.Canvas(width=320, height=200)
        self.preview_canvas.pack()

        # Options
        self.dither_var = tk.StringVar(value="atkinson")
        dither_dropdown = ttk.Combobox(
            textvariable=self.dither_var,
            values=["atkinson", "floyd-steinberg", "jjn", "none"]
        )
        dither_dropdown.pack()

        # Convert button
        convert_btn = tk.Button(text="Convert", command=self.convert)
        convert_btn.pack()

    def convert(self):
        convert_image(
            self.input_path,
            self.output_path,
            dither_method=self.dither_var.get()
        )
        self.update_preview()
```

---

## Option 4: Modern Python GUI (Qt/PySide6) ⭐ (Best User Experience)

**Technology**: Python + Qt framework (PySide6 or PyQt6)

### Architecture
- Professional, native-looking cross-platform GUI
- Qt widgets and layouts
- Direct Python integration with gs_convert
- Rich graphics view for image display

### Pros
- ✅ Professional, native look and feel on all platforms
- ✅ Very powerful and flexible widget system
- ✅ Same language as existing code (Python)
- ✅ Direct function integration (no subprocess)
- ✅ Excellent image preview capabilities
- ✅ Can create professional installer packages
- ✅ Drag-and-drop support
- ✅ Rich styling with Qt Style Sheets (CSS-like)
- ✅ Built-in layouts that adapt to window resizing
- ✅ Extensive documentation and community

### Cons
- ❌ Steeper learning curve than Tkinter or Flask
- ❌ Additional dependency (PySide6: ~50MB)
- ❌ Licensing considerations:
  - PySide6: LGPL (free for all uses)
  - PyQt6: GPL or commercial license required
- ❌ More complex than web UI for simple cases

### Example Code
```python
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
                               QHBoxLayout, QVBoxLayout, QLabel,
                               QComboBox, QPushButton)
from PySide6.QtGui import QPixmap
from gs_convert import convert_image

class ConverterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GS-Convert")

        # Central widget with layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Image views
        self.original_view = QLabel()
        self.original_view.setFixedSize(320, 200)
        layout.addWidget(self.original_view)

        self.preview_view = QLabel()
        self.preview_view.setFixedSize(320, 200)
        layout.addWidget(self.preview_view)

        # Options panel
        options = QVBoxLayout()

        self.dither_combo = QComboBox()
        self.dither_combo.addItems(["atkinson", "floyd-steinberg", "jjn"])
        options.addWidget(self.dither_combo)

        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self.convert)
        options.addWidget(convert_btn)

        layout.addLayout(options)

    def convert(self):
        convert_image(
            self.input_path,
            self.output_path,
            dither_method=self.dither_combo.currentText()
        )
        self.update_preview()
```

### Distribution
- Can use `PyInstaller` or `cx_Freeze` to create standalone executables
- Relatively small (~30-50MB with PySide6 bundled)

---

## Option 5: Terminal UI (TUI)

**Technology**: Python + Textual or Rich

### Architecture
- Runs entirely in the terminal with rich text interface
- Direct Python integration
- Image preview using terminal graphics protocols (iTerm2, kitty, WezTerm)
- Keyboard-driven navigation

### Pros
- ✅ Stays in terminal environment (appeals to CLI users)
- ✅ Lightweight and fast
- ✅ Modern terminal features (colors, unicode, mouse support)
- ✅ Same language (Python)
- ✅ Cool factor for retro computing community
- ✅ Works over SSH (with appropriate terminal)
- ✅ Fast to build with Textual framework

### Cons
- ❌ Limited to terminal capabilities
- ❌ Image preview quality varies greatly by terminal emulator
- ❌ Not all terminals support image protocols
- ❌ Less intuitive for non-technical users
- ❌ Limited layout flexibility compared to GUI

### Example Code
```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Select, Button, Static
from textual.containers import Container

class ConverterTUI(App):
    CSS = """
    Container {
        layout: horizontal;
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static(id="original")
            yield Static(id="preview")
            yield Select(
                options=[("Atkinson", "atkinson"),
                        ("Floyd-Steinberg", "floyd-steinberg")],
                id="dither"
            )
            yield Button("Convert", id="convert")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "convert":
            self.convert_image()
```

### Terminal Image Support
- **iTerm2** (macOS): Excellent inline image support
- **kitty** (cross-platform): Good graphics protocol
- **WezTerm** (cross-platform): Sixel and iTerm2 protocols
- **Standard terminals**: Fallback to ASCII art or block characters

---

## Comparison Matrix

| Feature | Flask Web | Electron | Tkinter | Qt/PySide6 | TUI |
|---------|-----------|----------|---------|------------|-----|
| **Time to Build** | Fast | Moderate | Fast | Moderate | Fast |
| **Learning Curve** | Low | Moderate | Low | Moderate | Low |
| **UI Quality** | Good | Excellent | Basic | Excellent | Good |
| **Cross-platform** | ✅ | ✅ | ✅ | ✅ | ✅* |
| **Library Integration** | Direct | Subprocess | Direct | Direct | Direct |
| **Distribution Size** | Small | Large | Small | Medium | Small |
| **Native Feel** | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Image Preview** | Excellent | Excellent | Basic | Excellent | Limited |
| **Offline Use** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Auto-update** | Easy | Built-in | Manual | Manual | Manual |
| **Extra Dependencies** | Flask | Node.js | None | PySide6 | Textual |

*TUI cross-platform support depends on terminal capabilities

---

## Recommendations by Use Case

### Quick MVP / Personal Use
**Flask Web UI** - Fastest to build, good enough for immediate use

### Professional Distribution
**Qt/PySide6** - Best user experience, professional appearance

### Retro/Hacker Appeal
**Terminal UI (Textual)** - Fits the retro computing aesthetic

### Maximum Reach
**Electron** - If you need Windows/Mac/Linux with identical experience and don't mind the size

### No Dependencies
**Tkinter** - If you absolutely cannot add dependencies

---

## Implementation Priorities

### Phase 1: Core Functionality (All Options)
1. Image upload/selection
2. Preview display (original + converted)
3. Basic options (dither, quantize)
4. Download .3200 file

### Phase 2: Enhanced Features
1. Side-by-side comparison slider
2. Real-time stats (palette usage, file size)
3. All conversion options exposed
4. Preset management

### Phase 3: Advanced Features
1. Batch processing
2. Conversion history
3. Advanced stats and visualizations
4. Drag-and-drop support

---

## Library vs CLI Integration

### Library Integration (Recommended)

```python
from gs_convert.pipeline import convert_image

# Direct function call - fast, full control
convert_image(input_path, output_path,
              dither_method="atkinson",
              quantize_method="median-cut")
```

**Advantages**:
- Much faster (no process startup)
- Better error handling (Python exceptions)
- Access to intermediate results
- Can get detailed stats
- Progress callbacks
- In-memory processing

### CLI Subprocess (Not Recommended)

```python
import subprocess

# Spawn CLI process
result = subprocess.run([
    "gs-convert", "convert", input_path, output_path,
    "--dither", "atkinson"
], capture_output=True)
```

**Disadvantages**:
- Slower (process overhead)
- Harder to debug
- Limited to CLI-exposed features
- No progress updates
- Requires parsing output

---

## Next Steps

Choose an option based on your priorities:

1. **Want it fast?** → Flask Web UI
2. **Want it polished?** → Qt/PySide6
3. **Want it unique?** → Terminal UI (Textual)
4. **Want maximum distribution?** → Electron

All options can use the same conversion engine via library integration.

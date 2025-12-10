#!/bin/bash
# Development environment setup script

set -e

echo "🚀 Setting up gs-convert development environment..."
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Platform: $PLATFORM"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 uv not found. Installing..."
    echo ""

    if [ "$PLATFORM" = "Mac" ] && command -v brew &> /dev/null; then
        echo "Choose installation method:"
        echo "  1) Homebrew (recommended for macOS)"
        echo "  2) Official installer"
        read -p "Enter choice [1-2]: " choice

        case $choice in
            1)
                brew install uv
                ;;
            2)
                curl -LsSf https://astral.sh/uv/install.sh | sh
                # Add to PATH for current session
                export PATH="$HOME/.local/bin:$PATH"
                ;;
            *)
                echo "Invalid choice. Please run again."
                exit 1
                ;;
        esac
    else
        # Linux or no Homebrew - use official installer
        echo "Installing uv via official installer..."
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"

        # Verify installation
        if ! command -v uv &> /dev/null; then
            echo "⚠️  uv installed but not in PATH yet."
            echo "Please add to your shell profile:"
            echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo ""
            echo "For this session, running: export PATH=\"\$HOME/.local/bin:\$PATH\""
        fi
    fi
    echo ""
fi

# Set UV path if not in PATH yet
UV_BIN="$(command -v uv || echo "$HOME/.local/bin/uv")"

if [ ! -x "$UV_BIN" ]; then
    echo "❌ uv installation failed or not found at $UV_BIN"
    exit 1
fi

echo "Using uv at: $UV_BIN"
echo ""

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔨 Creating virtual environment..."
    "$UV_BIN" venv --python python3
    echo ""
fi

# Activate and install
echo "📚 Installing dependencies..."
source .venv/bin/activate

# Ensure pip is available in venv (uv sometimes doesn't include it)
if ! command -v pip &> /dev/null; then
    echo "⚠️  pip not found in venv, installing pip..."
    "$UV_BIN" pip install pip
    echo ""
fi

# Ask if user wants UI dependencies
echo ""
echo "Install Web UI dependencies? (Flask, Flask-CORS)"
read -p "Install Web UI? [y/N]: " install_ui

if [[ "$install_ui" =~ ^[Yy]$ ]]; then
    echo "Installing with dev and UI dependencies..."
    "$UV_BIN" pip install -e ".[dev,ui]"
else
    echo "Installing with dev dependencies only..."
    "$UV_BIN" pip install -e ".[dev]"
fi

echo ""
echo "✅ Setup complete!"
echo ""

# Check if uv is in PATH permanently
if [ "$PLATFORM" = "Linux" ] && [ ! -f "$HOME/.local/bin/uv" ]; then
    echo "⚠️  NOTE: uv was installed to ~/.local/bin/"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "To activate the development environment:"
echo "  source .venv/bin/activate"
echo ""
echo "Then you can run:"
echo "  gs-convert convert image.jpg output.3200"
echo "  pytest  # Run tests"
echo "  black src/  # Format code"

if [[ "$install_ui" =~ ^[Yy]$ ]]; then
    echo "  python -m gs_convert_ui.app  # Run Web UI"
fi

echo ""

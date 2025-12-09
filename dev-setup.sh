#!/bin/bash
# Development environment setup script

set -e

echo "🚀 Setting up gs-convert development environment..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 uv not found. Installing..."
    echo ""
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
            ;;
        *)
            echo "Invalid choice. Please run again."
            exit 1
            ;;
    esac
    echo ""
fi

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔨 Creating virtual environment..."
    uv venv
    echo ""
fi

# Activate and install
echo "📚 Installing dependencies..."
source .venv/bin/activate

# Ask if user wants UI dependencies
echo ""
echo "Install Web UI dependencies? (Flask, Flask-CORS)"
read -p "Install Web UI? [y/N]: " install_ui

if [[ "$install_ui" =~ ^[Yy]$ ]]; then
    echo "Installing with dev and UI dependencies..."
    uv pip install -e ".[dev,ui]"
else
    echo "Installing with dev dependencies only..."
    uv pip install -e ".[dev]"
fi

echo ""
echo "✅ Setup complete!"
echo ""
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

# Development Setup Guide

## Understanding Python Package Development vs Distribution

### The Big Picture

There are **three different contexts** for Python packages:

1. **Development** (you, working on the code)
2. **User Installation** (end users installing your package)
3. **Distribution** (PyPI, Homebrew, etc.)

These are **independent** - your choice of development tools doesn't affect how users install your package.

---

## Development Setup with `uv`

### Why Use `uv` for Development?

- **Isolation**: Keep project dependencies separate from system Python
- **Speed**: Much faster than pip/venv (10-100x)
- **Reproducibility**: Lock files ensure consistent environments
- **Cleanliness**: System Python stays pristine

### Installing `uv`

```bash
# Option 1: Official installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Option 2: Homebrew
brew install uv

# Option 3: pipx
pipx install uv
```

### Setting Up Development Environment

```bash
# Navigate to project
cd /Users/christopherbrown/Projects/gs_convert

# Create virtual environment with uv
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install package in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Or in one command:
uv pip install -e ".[dev]" --python 3.11
```

### Daily Development Workflow

```bash
# Start working (activate venv)
source .venv/bin/activate

# Run your tool
gs-convert convert test.jpg output.3200

# Run tests
pytest

# Format code
black src/

# Deactivate when done
deactivate
```

---

## How This Relates to Package Distribution

### Key Insight: Development Tools ≠ Installation Method

**Your development setup (uv) does NOT affect:**
- ❌ How users install your package
- ❌ PyPI publishing
- ❌ Homebrew formula
- ❌ Package dependencies

**Your `pyproject.toml` defines:**
- ✅ What dependencies users need
- ✅ What gets published to PyPI
- ✅ What Homebrew installs

### Example Scenarios

#### Scenario 1: You (Developer)
```bash
# You use uv for development
cd gs_convert
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### Scenario 2: User Installing from PyPI
```bash
# User installs with pip (they don't need uv)
pip install gs-convert

# Or with uv (their choice)
uv pip install gs-convert

# Or with pipx (isolated)
pipx install gs-convert
```

#### Scenario 3: User Installing from Homebrew
```bash
# Homebrew handles everything
brew install gs-convert
```

---

## Publishing to PyPI

### Your package can be published to PyPI regardless of development setup:

```bash
# Build distribution (from your uv venv)
source .venv/bin/activate
python -m build

# Publish to PyPI
twine upload dist/*
```

Users install with:
```bash
pip install gs-convert
# or
uv pip install gs-convert
# or
pipx install gs-convert
```

**They never know you used `uv` for development!**

---

## Homebrew Formula

### Homebrew is completely independent of your dev setup

Homebrew formulas typically:
1. Download source from PyPI or GitHub
2. Build in their own isolated environment
3. Install into Homebrew's Python

Example Homebrew formula for gs-convert:

```ruby
class GsConvert < Formula
  include Language::Python::Virtualenv

  desc "Apple IIgs image converter"
  homepage "https://github.com/yourusername/gs_convert"
  url "https://files.pythonhosted.org/packages/.../gs-convert-0.1.0.tar.gz"
  sha256 "..."

  depends_on "python@3.11"

  resource "pillow" do
    url "https://files.pythonhosted.org/packages/.../Pillow-10.0.0.tar.gz"
    sha256 "..."
  end

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/.../numpy-1.24.0.tar.gz"
    sha256 "..."
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/.../click-8.1.0.tar.gz"
    sha256 "..."
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/gs-convert", "--version"
  end
end
```

**Key Points:**
- Homebrew reads dependencies from `pyproject.toml`
- Homebrew creates its own virtualenv
- Users just run `brew install gs-convert`
- Your use of `uv` during development is invisible

---

## Recommended Project Setup

### 1. Clean Up Current Installation

```bash
# Uninstall from system Python
pip uninstall gs-convert

# Or if installed with homebrew python
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip uninstall gs-convert
```

### 2. Set Up uv Development Environment

```bash
cd /Users/christopherbrown/Projects/gs_convert

# Install uv if needed
brew install uv

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate

# Install package in editable mode
uv pip install -e ".[dev]"
```

### 3. Add to .gitignore

```bash
cat >> .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# uv
uv.lock
GITIGNORE
```

### 4. Optional: Add uv.lock for Reproducibility

```bash
# Generate lock file
uv pip compile pyproject.toml -o requirements.lock

# Install from lock file
uv pip install -r requirements.lock
```

---

## Development Workflow Scripts

Create convenience scripts:

### `dev-setup.sh`
```bash
#!/bin/bash
# Set up development environment

set -e

echo "Setting up gs-convert development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate and install
echo "Installing dependencies..."
source .venv/bin/activate
uv pip install -e ".[dev]"

echo ""
echo "✓ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
```

### `dev-test.sh`
```bash
#!/bin/bash
# Run tests and quality checks

source .venv/bin/activate

echo "Running tests..."
pytest

echo "Checking code formatting..."
black --check src/ tests/

echo "Running type checks..."
mypy src/

echo "✓ All checks passed!"
```

---

## FAQ

### Q: If I use `uv` for development, do users need `uv`?
**A:** No! Users can install with pip, pipx, or any Python package manager.

### Q: Can I publish to PyPI if I develop with `uv`?
**A:** Yes! PyPI doesn't care what tools you used during development.

### Q: Will Homebrew work with my package?
**A:** Yes! Homebrew reads `pyproject.toml` and builds independently.

### Q: Should I commit `.venv/` to git?
**A:** No! Virtual environments should never be committed. Add to `.gitignore`.

### Q: Should I commit `uv.lock`?
**A:** Maybe. It helps reproducibility but isn't necessary for libraries.

### Q: What's the difference between `pip install -e .` and `uv pip install -e .`?
**A:** Both do the same thing (editable install), but `uv` is much faster.

### Q: Can contributors use regular pip/venv instead of uv?
**A:** Yes! Include both options in README:
```bash
# Option 1: Using uv (faster)
uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"

# Option 2: Using standard tools
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

---

## Distribution Checklist

When you're ready to publish:

### PyPI (pip installable)
- [ ] Version bump in `pyproject.toml`
- [ ] Build: `python -m build`
- [ ] Upload: `twine upload dist/*`
- [ ] Test: `pip install gs-convert`

### Homebrew (brew installable)
- [ ] Publish to PyPI first
- [ ] Create Homebrew formula
- [ ] Submit to homebrew-core or create tap
- [ ] Test: `brew install gs-convert`

### GitHub Releases
- [ ] Tag version: `git tag v0.1.0`
- [ ] Push tags: `git push --tags`
- [ ] Create GitHub release
- [ ] Attach built distributions

---

## Current State of Your Project

Right now, `gs-convert` is installed globally in Homebrew's Python:
```bash
/opt/homebrew/bin/gs-convert
```

This works but pollutes the system. To switch to clean development:

```bash
# 1. Uninstall global version
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip uninstall gs-convert

# 2. Install uv
brew install uv

# 3. Set up dev environment
cd /Users/christopherbrown/Projects/gs_convert
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 4. Now gs-convert runs from .venv
which gs-convert  # Should show .venv/bin/gs-convert
```

---

## Summary

**Key Takeaway**: Your development environment (uv + venv) is **completely separate** from how users install your package.

- ✅ **You**: Use `uv venv` for clean, fast development
- ✅ **Users**: Install with `pip`, `pipx`, or `brew` (their choice)
- ✅ **PyPI**: Publishes from `pyproject.toml` (doesn't care about uv)
- ✅ **Homebrew**: Builds from PyPI (doesn't care about uv)

Your `pyproject.toml` is the source of truth for dependencies and metadata. Everything else builds from that.

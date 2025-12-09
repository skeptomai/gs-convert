# Quick Start: Development Setup

## Clean Development Setup (Recommended)

### Step 1: Uninstall Global Installation

First, clean up the current global installation:

```bash
# Check current installation
which gs-convert
# Should show: /opt/homebrew/bin/gs-convert

# Uninstall
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip uninstall gs-convert
```

### Step 2: Install uv

```bash
# Option 1: Homebrew (easiest)
brew install uv

# Option 2: Official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Step 3: Set Up Development Environment

```bash
cd /Users/christopherbrown/Projects/gs_convert

# Run setup script
./dev-setup.sh

# Or manually:
uv venv                          # Create virtual environment
source .venv/bin/activate        # Activate it
uv pip install -e ".[dev]"       # Install package in editable mode
```

### Step 4: Verify Everything Works

```bash
# Ensure venv is activated
source .venv/bin/activate

# Check gs-convert is installed from venv
which gs-convert
# Should show: /Users/christopherbrown/Projects/gs_convert/.venv/bin/gs-convert

# Test it works
gs-convert --version
gs-convert convert examples/test_gradient.png test.3200
```

---

## Daily Development Workflow

### Starting Work

```bash
cd /Users/christopherbrown/Projects/gs_convert
source .venv/bin/activate
```

Your prompt should change to show `(.venv)`.

### Making Changes

```bash
# Edit code in src/gs_convert/

# Test immediately (editable install means changes take effect)
gs-convert convert test.jpg output.3200

# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/
```

### Finishing Work

```bash
deactivate
```

---

## Understanding the Setup

### Before (Global Install)
```
System Python (Homebrew)
└── gs-convert installed globally ❌ 
    (pollutes system, hard to manage versions)
```

### After (uv + venv)
```
System Python (clean) ✓
Project Directory
├── .venv/                  ← Isolated environment
│   └── gs-convert          ← Installed here
├── src/gs_convert/         ← Your source code
└── pyproject.toml          ← Package definition
```

**Benefits:**
- System Python stays clean
- Easy to delete/recreate environment
- Different projects can have different dependencies
- Faster installations with uv
- Matches professional Python development practices

---

## How This Works with Distribution

### Your Development (uv)
```bash
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### User Installation (any method works)
```bash
# Option 1: pip (traditional)
pip install gs-convert

# Option 2: pipx (isolated)
pipx install gs-convert

# Option 3: uv (if they prefer)
uv pip install gs-convert

# Option 4: Homebrew (once you publish)
brew install gs-convert
```

**Key Point:** Your choice of development tools (uv) doesn't affect how users install your package!

---

## Publishing Workflow

### 1. Prepare Release

```bash
# Ensure venv is activated
source .venv/bin/activate

# Update version in pyproject.toml
# version = "0.1.0" → "0.2.0"

# Install build tools
uv pip install build twine

# Run tests
pytest

# Format code
black src/
```

### 2. Build Distribution

```bash
# Clean old builds
rm -rf dist/ build/

# Build source and wheel distributions
python -m build

# This creates:
# dist/gs-convert-0.2.0.tar.gz       (source)
# dist/gs_convert-0.2.0-py3-none-any.whl  (wheel)
```

### 3. Test Locally

```bash
# Test in clean environment
uv venv test-env
source test-env/bin/activate
pip install dist/gs_convert-0.2.0-py3-none-any.whl
gs-convert --version
deactivate
rm -rf test-env
```

### 4. Publish to PyPI

```bash
# Test PyPI first (recommended)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ gs-convert

# If all good, publish to real PyPI
twine upload dist/*
```

### 5. Create GitHub Release

```bash
git tag v0.2.0
git push origin v0.2.0

# Create release on GitHub with notes
# Attach dist/gs-convert-0.2.0.tar.gz
```

### 6. Homebrew Formula (Optional)

Once on PyPI, you can create a Homebrew formula. Either:

**Option A: Submit to homebrew-core**
- Create formula in homebrew-core repo
- Submit PR

**Option B: Create your own tap**
```bash
# Create tap repository
brew tap-new yourusername/tap

# Create formula
brew create https://files.pythonhosted.org/packages/.../gs-convert-0.2.0.tar.gz

# Users install with:
brew tap yourusername/tap
brew install gs-convert
```

---

## Common Commands Reference

### Development
```bash
source .venv/bin/activate        # Activate venv
uv pip install -e ".[dev]"       # Install editable with dev deps
uv pip install package-name      # Add new dependency
uv pip list                      # List installed packages
pytest                           # Run tests
black src/                       # Format code
mypy src/                        # Type check
deactivate                       # Exit venv
```

### Dependency Management
```bash
# Add to pyproject.toml, then:
uv pip install -e ".[dev]"

# Generate lock file (optional but recommended)
uv pip compile pyproject.toml -o requirements.lock

# Install from lock file
uv pip install -r requirements.lock
```

### Cleanup
```bash
# Remove venv and start fresh
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## Troubleshooting

### "gs-convert not found" after activation

```bash
# Make sure you're activated
source .venv/bin/activate

# Reinstall
uv pip install -e .

# Check installation
which gs-convert
# Should show path in .venv/bin/
```

### "Module not found" errors

```bash
# Reinstall dependencies
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Want to use regular pip instead of uv?

```bash
# Create venv with standard tools
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Everything else works the same!
```

### Switching between global and local

```bash
# Use local (venv) version
source .venv/bin/activate
which gs-convert  # Shows .venv/bin/gs-convert

# Use global version (if installed)
deactivate
which gs-convert  # Shows system path
```

---

## Best Practices

### ✅ Do:
- Use virtual environments (uv or standard venv)
- Install package in editable mode (`-e`)
- Keep dependencies in pyproject.toml
- Add .venv to .gitignore
- Activate venv before working
- Deactivate when done

### ❌ Don't:
- Install packages globally (except with pipx)
- Commit .venv directory
- Mix system and venv packages
- Forget to activate venv

---

## Next Steps

1. **Set up clean environment**: Run `./dev-setup.sh`
2. **Test it works**: Try converting some images
3. **Make changes**: Edit code, test immediately
4. **Add tests**: Create tests/ directory with pytest tests
5. **Share with others**: Publish to PyPI and/or create Homebrew formula

---

## Questions?

- **Development**: Use uv + venv for isolation and speed
- **Distribution**: pyproject.toml defines what users get
- **Publishing**: Same process regardless of dev tools
- **Users**: Can install with pip, pipx, brew, or uv (their choice)

Your development environment is **completely independent** from how you publish and how users install!

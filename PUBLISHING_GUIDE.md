# Publishing Guide: PyPI and Homebrew

## Overview

This guide shows how to publish `gs-convert` to both PyPI and Homebrew.

**Important**: Your development environment (uv) doesn't affect this at all!

## Prerequisites

### 1. PyPI Account
- Create account at https://pypi.org
- Create account at https://test.pypi.org (for testing)
- Set up 2FA
- Create API tokens

### 2. Install Publishing Tools

```bash
# Activate your dev environment
source .venv/bin/activate

# Install build and publish tools
uv pip install build twine
```

---

## Publishing to PyPI - Quick Reference

```bash
# 1. Update version in pyproject.toml
# 2. Build
python -m build

# 3. Upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# 4. Upload to PyPI
twine upload dist/*

# 5. Tag release
git tag v0.1.0 && git push --tags
```

---

## Detailed PyPI Publishing Steps

See full guide in the file for complete step-by-step instructions.

---

## Publishing to Homebrew

Once on PyPI, create Homebrew formula:

```bash
# Create tap: homebrew-tap repository
# Add Formula/gs-convert.rb
# Users install: brew tap yourusername/tap && brew install gs-convert
```

---

## Summary

**The key point**: Your development setup (uv venv) is completely separate from publishing!

- Development: `uv venv` (your choice)
- Publishing: `python -m build && twine upload`
- Users: Can use pip, pipx, brew, or uv (their choice)

All three are independent!

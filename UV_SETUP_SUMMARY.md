# UV Setup Summary - TL;DR

## Quick Answer to Your Question

**Q: Can I use `uv venv` for development and still publish to PyPI/Homebrew?**

**A: YES!** They are completely independent.

```
uv venv (development)  ≠  PyPI/Homebrew (distribution)
      ↓                           ↓
  Your choice               Users' choice
```

## Three Simple Facts

1. **Development** (you): Use `uv venv` for clean, fast isolation ✅
2. **Definition** (package): Lives in `pyproject.toml` ✅  
3. **Distribution** (users): Can use pip, pipx, brew, or uv ✅

**All three are independent!**

## What to Do Right Now

### Option 1: Keep Current Setup (Simple)

Just keep using the global installation. It works fine for solo development.

```bash
# Already installed globally - just use it
gs-convert convert image.jpg output.3200
```

### Option 2: Switch to Clean uv Setup (Recommended)

```bash
# 1. Install uv
brew install uv

# 2. Clean up global install
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip uninstall gs-convert

# 3. Set up dev environment
cd /Users/christopherbrown/Projects/gs_convert
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 4. Done! Now use it:
gs-convert convert image.jpg output.3200
```

### Option 3: Use Setup Script (Easiest)

```bash
cd /Users/christopherbrown/Projects/gs_convert
./dev-setup.sh
source .venv/bin/activate
```

## Publishing Still Works Exactly the Same

```bash
# Regardless of whether you used uv or pip for development:

# Build
python -m build

# Publish to PyPI
twine upload dist/*

# Users install with WHATEVER they want:
pip install gs-convert        # Works
pipx install gs-convert       # Works
uv pip install gs-convert     # Works
brew install gs-convert       # Works (once you create formula)
```

## Key Files

### For Development (your tools)
- `.venv/` - Virtual environment (never commit!)
- `uv.lock` - Optional lock file (can commit)
- `.gitignore` - Excludes .venv

### For Distribution (what users get)
- `pyproject.toml` - Package definition (**commit this!**)
- `src/gs_convert/` - Source code (**commit this!**)
- `README.md` - Documentation (**commit this!**)

## How Homebrew Works with This

**Homebrew doesn't care about your dev setup:**

```ruby
# Homebrew formula just uses pyproject.toml
class GsConvert < Formula
  # Downloads from PyPI
  # Reads dependencies from pyproject.toml
  # Creates its own virtualenv
  # Installs everything
end
```

Users run:
```bash
brew install gs-convert
```

They never know you used `uv`!

## Visual Summary

```
┌─────────────────────────────────────┐
│ YOUR MACHINE                        │
│                                     │
│ uv venv                             │
│ uv pip install -e ".[dev]"          │
│                                     │
│ Edit code → Test → Commit → Push   │
└─────────────────────────────────────┘
              ↓
        (git push)
              ↓
┌─────────────────────────────────────┐
│ GITHUB / PYPI                       │
│                                     │
│ pyproject.toml (source of truth)    │
│ Python source code                  │
│                                     │
│ Built distributions (.tar.gz, .whl)│
└─────────────────────────────────────┘
              ↓
    (user installs)
              ↓
┌─────────────────────────────────────┐
│ USER'S MACHINE                      │
│                                     │
│ pip install gs-convert              │
│ OR pipx install gs-convert          │
│ OR brew install gs-convert          │
│ OR uv pip install gs-convert        │
│                                     │
│ (All work the same!)                │
└─────────────────────────────────────┘
```

## Common Questions

**Q: Should I commit `.venv/`?**  
A: No! Never. Add to `.gitignore`.

**Q: Should I commit `pyproject.toml`?**  
A: Yes! Always. This defines your package.

**Q: Can contributors use pip instead of uv?**  
A: Yes! Both work:
```bash
# Option A: uv (faster)
uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"

# Option B: pip (traditional)
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

**Q: Will this work on Linux/Windows?**  
A: Yes! `uv` is cross-platform. Users can use pip/pipx on any platform.

**Q: How do I switch projects?**  
A: Just deactivate and activate the other project's venv:
```bash
deactivate                    # Exit current venv
cd /other/project
source .venv/bin/activate     # Enter other venv
```

## Recommendation

**For your project**: Use `uv venv` for development.

**Benefits:**
- ✅ Keeps system Python clean
- ✅ Fast installation (10-100x faster than pip)
- ✅ Matches professional Python practices
- ✅ Easy to delete and recreate
- ✅ Won't affect distribution or users AT ALL

**Cost:**
- One extra command: `source .venv/bin/activate`
- Need to run `./dev-setup.sh` once

**Worth it?** Absolutely yes if you plan to continue development.

## Next Steps

1. Read: `QUICK_START_DEV.md` for detailed setup
2. Read: `DEVELOPMENT.md` for full documentation
3. Read: `docs/development_vs_distribution.md` for the complete picture

Or just run:
```bash
./dev-setup.sh
source .venv/bin/activate
gs-convert convert test.jpg output.3200
```

And you're done! 🎉

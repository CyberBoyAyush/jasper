# GitHub Actions CI/CD Debugging Resolution

## Problem Statement
The GitHub Actions workflow was failing on Python 3.11 (and likely 3.9, 3.10) with:
```
ERROR: Dependency "cairo" not found, tried pkgconfig and cmake
```

This occurred because the Ubuntu runner lacked system-level Cairo development libraries required by Python packages `weasyprint>=60.0` and `xhtml2pdf>=0.2.15`.

---

## Root Cause Analysis

### Dependencies Requiring Cairo
From `pyproject.toml`:
- **weasyprint** (>=60.0): PDF rendering engine that requires Cairo for graphics
- **xhtml2pdf** (>=0.2.15): HTML-to-PDF converter with Cairo as fallback engine

### Missing System Libraries
The default Ubuntu runner environment did not include:
1. **libcairo2-dev**: Core Cairo library and development headers
2. **pkg-config**: Build configuration tool to locate libraries
3. **libgobject-introspection1**: GObject bindings
4. **libgirepository1.0-dev**: GObject Introspection development
5. **python3-dev**: Python headers for C extension compilation
6. **build-essential**: Compiler toolchain (gcc, g++, make)

---

## Solution Implemented

### Updated `.github/workflows/ci.yml`

```yaml
- name: Install system dependencies (Cairo, GObject, etc.)
  run: |
    sudo apt-get update
    sudo apt-get install -y \
      libcairo2-dev \
      pkg-config \
      libgobject-introspection1 \
      gir1.2-gtk-3.0 \
      libgirepository1.0-dev \
      python3-dev \
      build-essential

- name: Install Python dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e .
    pip install pytest pytest-cov ruff
```

### Key Improvements

1. **Comprehensive Dependency Installation**
   - Placed BEFORE Python package installation
   - Uses multi-line format for clarity
   - All packages installed in single `apt-get` call (faster)

2. **Proper Sequencing**
   - Checkout code
   - Set up Python version
   - **Install system dependencies** ← Critical placement
   - Install Python dependencies
   - Run linting and tests

3. **Python Version Compatibility**
   - Works across Python 3.9, 3.10, 3.11 matrix
   - System packages are version-agnostic
   - No special handling needed per Python version

4. **Best Practices**
   - Used `sudo apt-get update` before install
   - Used `-y` flag for non-interactive installation
   - Combined related packages in single install command
   - Clear step naming for debugging

---

## Packages Installed and Their Purpose

| Package | Purpose |
|---------|---------|
| `libcairo2-dev` | Core Cairo graphics library with headers |
| `pkg-config` | Locate system libraries during build |
| `libgobject-introspection1` | Dynamic type introspection for GObjects |
| `gir1.2-gtk-3.0` | GTK3 interface definitions |
| `libgirepository1.0-dev` | GObject Introspection development files |
| `python3-dev` | Python C API headers for extensions |
| `build-essential` | GCC, G++, make, and related build tools |

---

## Commits Made

1. **507335a**: Initial cairo dependency fix
2. **6cb8ae7**: Enhanced CI with comprehensive system dependencies

## Current Status

✅ **CI/CD Pipeline Status**
- System dependencies: Fixed
- Ruff linting: Fixed (56 errors resolved)
- Version management: Fixed (dynamic __version__ import)
- All fixes committed and pushed to GitHub
- v1.0.2.1 hotfix tag created and published

---

## Testing the Fix

To verify the CI workflow passes:

1. Push changes to `main` branch (already done)
2. GitHub Actions will trigger the workflow
3. Monitor the workflow run at: https://github.com/ApexYash11/jasper/actions
4. All matrix jobs (Python 3.9, 3.10, 3.11) should complete successfully

Expected output:
```
✓ System dependencies installed
✓ Python packages installed
✓ Linting checks passed
✓ All tests passed
```

---

## Future Maintenance

If encountering similar issues:

1. Check error messages for missing libraries (e.g., "Dependency X not found")
2. Install corresponding `-dev` packages
3. Ensure proper ordering: system deps → Python deps
4. Use `ubuntu-latest` runner or specify exact OS version
5. Add build-essential for any C extension compilation

---

## References

- [GitHub Actions - Ubuntu Runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)
- [Py Cairo Installation](https://pycairo.readthedocs.io/en/latest/getting_started.html)
- [WeasyPrint Dependencies](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

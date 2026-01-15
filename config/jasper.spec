# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Jasper Finance standalone executable.

This creates a single-file executable that includes:
- All Python dependencies (langchain, pydantic, typer, etc.)
- WeasyPrint + GTK+ runtime (for PDF generation)
- All templates and style files
- Ready to run without Python installation

Usage:
    pyinstaller jasper.spec
    dist/jasper.exe interactive
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project root
project_root = Path(__file__).parent.resolve()
jasper_dir = project_root / "jasper"

# Data files to bundle (templates, styles, etc.)
datas = [
    (str(jasper_dir / "templates"), "jasper/templates"),
    (str(jasper_dir / "styles"), "jasper/styles"),
]

# Collect WeasyPrint data files (fonts, etc.) if they exist
try:
    import weasyprint
    wp_path = Path(weasyprint.__file__).parent
    datas.append((str(wp_path), "weasyprint"))
except ImportError:
    pass

a = Analysis(
    [str(project_root / "jasper" / "__main__.py")],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'weasyprint',
        'xhtml2pdf',
        'cairocffi',
        'ctypes',
        'jinja2',
        'langchain_core',
        'langchain_openai',
        'openai',
        'pydantic',
        'markdown_it',
        'yfinance',
        'rich',
        'typer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='jasper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

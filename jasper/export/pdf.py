"""
PDF Export Module for Jasper Finance

Renders audit-ready PDF reports using Jinja2 + xhtml2pdf.
Ensures deterministic, offline-capable output without network access.
Windows-compatible (no GTK+ dependencies).

Architecture:
  - FinalReport (state.py) is the single source of truth
  - Jinja2 template (templates/report.html.jinja) handles semantic HTML
  - CSS (styles/report_v1.css) controls all layout and styling
  - xhtml2pdf compiles HTML+CSS → PDF deterministically
"""

import hashlib
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

from ..core.state import FinalReport


def get_report_template_dir() -> Path:
    """Get the templates directory path."""
    # Relative to this module (jasper/export/pdf.py)
    module_dir = Path(__file__).parent.parent
    templates_dir = module_dir / "templates"
    return templates_dir


def get_styles_dir() -> Path:
    """Get the styles directory path."""
    # Relative to this module
    module_dir = Path(__file__).parent.parent
    styles_dir = module_dir / "styles"
    return styles_dir


def load_css_content() -> str:
    """
    Load CSS content from report_v1.css.
    
    Returns:
        CSS content as string, safe to embed in HTML
    
    Raises:
        FileNotFoundError: If CSS file not found
    """
    css_path = get_styles_dir() / "report_v1.css"
    if not css_path.exists():
        raise FileNotFoundError(f"CSS stylesheet not found: {css_path}")
    
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()


def setup_jinja_environment() -> Environment:
    """
    Configure Jinja2 environment for report rendering.
    
    Returns:
        Configured Jinja2 Environment
    """
    template_dir = get_report_template_dir()
    
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(enabled_extensions=('html', 'jinja')),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    
    # Register custom filters for deterministic rendering
    env.filters['hash'] = lambda x: hashlib.sha256(x.encode()).hexdigest()[:16]
    env.filters['safe_html'] = lambda x: x.replace('<', '&lt;').replace('>', '&gt;') if x else ''
    
    return env


def render_report_html(report: FinalReport) -> str:
    """
    Render FinalReport to semantic HTML using Jinja2.
    
    Args:
        report: FinalReport object containing all report data
    
    Returns:
        HTML string (UTF-8 encoded)
    
    Raises:
        FileNotFoundError: If template or CSS not found
        Exception: If rendering fails
    """
    env = setup_jinja_environment()
    
    # Load CSS content once
    css_content = load_css_content()
    
    # Get template
    template = env.get_template("report.html.jinja")
    
    # Render with context
    html = template.render(
        report=report,
        css_content=css_content,
    )
    
    return html


def compile_html_to_pdf(html_content: str, output_path: str) -> str:
    """
    Compile semantic HTML + CSS to PDF using xhtml2pdf.
    
    Ensures:
      - Deterministic output (no network access, no external resources)
      - Consistent pagination and layout
      - Windows-compatible (no GTK+ dependencies)
    
    Args:
        html_content: Complete HTML string to render
        output_path: Path where PDF should be written
    
    Returns:
        Absolute path to generated PDF
    
    Raises:
        IOError: If PDF write fails
        Exception: If compilation fails
    """
    pdf_path = Path(output_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Convert HTML string to PDF using xhtml2pdf
        result_file = BytesIO()
        pisa.CreatePDF(
            html_content,
            dest=result_file,
            link_callback=_offline_link_callback,
        )
        
        # Write to file
        with open(pdf_path, "wb") as f:
            result_file.seek(0)
            f.write(result_file.getvalue())
        return str(pdf_path.resolve())
    
    except Exception as e:
        raise RuntimeError(f"PDF compilation failed: {str(e)}") from e


def _offline_link_callback(uri: str, rel: str):
    """
    Custom link callback that prevents network access during PDF generation.
    
    Args:
        uri: URL/path to resource
        rel: Relationship type
    
    Returns:
        None (prevents external requests)
    """
    # Return None to prevent fetching external resources
    # xhtml2pdf will skip unavailable resources
    return None


def export_report_to_pdf(
    report: FinalReport,
    output_path: str,
    validate: bool = True,
) -> str:
    """
    Export a FinalReport to audit-ready PDF.
    
    High-level entry point that validates state, renders HTML, and compiles PDF.
    
    Args:
        report: FinalReport object to export
        output_path: Path where PDF should be written
        validate: If True, verify report is valid before export
    
    Returns:
        Absolute path to generated PDF file
    
    Raises:
        ValueError: If report is invalid and validate=True
        FileNotFoundError: If templates/styles not found
        RuntimeError: If PDF generation fails
    """
    # Validation gate: fail loudly if report is incomplete
    if validate and not report.is_valid:
        issues_str = "\n  - ".join(report.validation_issues or ["Unknown issue"])
        raise ValueError(
            f"Cannot export invalid report. Validation failed with issues:\n"
            f"  - {issues_str}\n"
            f"Confidence: {report.confidence_score:.1%}\n"
            f"Please review data completeness and retry synthesis."
        )
    
    # Render HTML from report
    html = render_report_html(report)
    
    # Compile to PDF
    pdf_path = compile_html_to_pdf(html, output_path)
    
    return pdf_path


def export_report_html(
    report: FinalReport,
    output_path: str,
) -> str:
    """
    Export a FinalReport to HTML (for debugging/preview).
    
    Useful for inspecting rendered output before PDF generation.
    
    Args:
        report: FinalReport object to export
        output_path: Path where HTML should be written
    
    Returns:
        Absolute path to generated HTML file
    """
    html = render_report_html(report)
    
    html_path = Path(output_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return str(html_path.resolve())

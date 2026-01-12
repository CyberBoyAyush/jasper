"""
PDF Export Module for Jasper Finance

Renders audit-ready PDF reports using Jinja2 + WeasyPrint.
Ensures deterministic, offline-capable output without network access.
Supports modern CSS features (Grid, Flexbox) for professional layouts.

Architecture:
  - FinalReport (state.py) is the single source of truth
  - Jinja2 template (templates/report.html.jinja) handles semantic HTML
  - CSS (styles/report_v1.css) controls all layout and styling
  - WeasyPrint compiles HTML+CSS → PDF deterministically
"""

import hashlib
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt

from ..core.state import FinalReport


def render_markdown(text: str) -> str:
    """Convert Markdown to semantic HTML."""
    md = MarkdownIt("commonmark", {
        "html": True,
        "typographer": True,
    })
    return md.render(text)


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
    env.filters['markdown'] = render_markdown
    
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
    
    # Pre-render the synthesis text to HTML
    synthesis_html = render_markdown(report.synthesis_text)
    
    # Render with context
    html = template.render(
        report=report,
        css_content=css_content,
        synthesis_html=synthesis_html,
    )
    
    return html


def compile_html_to_pdf(html_content: str, output_path: str) -> str:
    """
    Compile semantic HTML + CSS to PDF.
    
    Tries WeasyPrint first for professional layouts. 
    Falls back to xhtml2pdf if system dependencies (GTK+) are missing.
    
    Args:
        html_content: Complete HTML string to render
        output_path: Path where PDF should be written
    
    Returns:
        Absolute path to generated PDF
    """
    pdf_path = Path(output_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    # --- Try WeasyPrint (Preferred) ---
    try:
        import contextlib
        import sys
        import logging
        
        # Suppress WeasyPrint loggers and standard error streams (GTK+ missing on Windows)
        logging.getLogger("weasyprint").setLevel(logging.CRITICAL)
        with contextlib.redirect_stdout(open(os.devnull, "w")), contextlib.redirect_stderr(open(os.devnull, "w")):
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(target=str(pdf_path))
        return str(pdf_path.resolve())
    except (ImportError, Exception):
        # Gracefully handle missing GTK+ or WeasyPrint
        pass

    # --- Fallback to xhtml2pdf (Compatible) ---
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        
        result_file = BytesIO()
        # Providing a base_url prevents 'NoneType' + 'str' errors when resolving paths
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=result_file,
            encoding='utf-8',
            base_url=str(Path.cwd())
        )
        
        if getattr(pisa_status, 'err', 0) != 0:
            # Try once more without explicit encoding if it failed
            result_file = BytesIO()
            pisa_status = pisa.CreatePDF(
                html_content, 
                dest=result_file,
                base_url=str(Path.cwd())
            )
            
        if getattr(pisa_status, 'err', 0) != 0:
            raise RuntimeError(f"xhtml2pdf fallback failed with status {getattr(pisa_status, 'err', 'unknown')}")
            
        with open(pdf_path, "wb") as f:
            result_file.seek(0)
            f.write(result_file.getvalue())
            
        return str(pdf_path.resolve())
        
    except Exception as e:
        raise RuntimeError(f"PDF compilation failed (all engines): {str(e)}") from e


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

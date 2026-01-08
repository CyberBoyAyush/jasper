from pathlib import Path
from dotenv import load_dotenv
import os
from .errors import ConfigError

load_dotenv()

def get_llm_api_key() -> str:
    """Get LLM API key from environment."""
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ConfigError(
            message="OPENROUTER_API_KEY not set",
            suggestion="1. Get a free key at https://openrouter.ai/keys\n"
                      "2. Create .env file in your working directory\n"
                      "3. Add: OPENROUTER_API_KEY=<your-key>",
            debug_details="Environment variable OPENROUTER_API_KEY not found in .env or OS"
        )
    return key

def get_financial_api_key() -> str:
    """Get financial data provider API key from environment."""
    key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    if key == "demo":
        import warnings
        warnings.warn(
            "Using Alpha Vantage demo API key (rate-limited and may return dummy data). "
            "For production, set ALPHA_VANTAGE_API_KEY in .env or as env var.",
            UserWarning
        )
    return key

def get_config():
    """Get configuration, raising ConfigError if any required key is missing."""
    return {
        "LLM_API_KEY": get_llm_api_key(),  # Raises ConfigError if not set
        "FINANCIAL_API_KEY": get_financial_api_key(),
        "ENV": os.getenv("ENV", "dev"),
    }

# --- JASPER UI CONFIGURATION ---

THEME = {
    "Background": "#000000",
    "Primary Text": "#E0E0E0",
    "Accent": "#00EA78",  # Phosphor Green
    "Brand": "#00EA78",   # Phosphor Green
    "Success": "#00EA78", # Phosphor Green
    "Warning": "#FFB302",
    "Error": "#FF007F",
}

BANNER_ART = """
      ██╗   ██████╗  ███████╗ ██████╗  ███████╗ ██████╗ 
      ██║  ██╔═══██╗ ██╔════╝ ██╔══██╗ ██╔════╝ ██╔══██╗
      ██║  ████████║ ███████╗ ██████╔╝ █████╗   ██████╔╝
 ██   ██║  ██╔═══██║ ╚════██║ ██╔═══╝  ██╔══╝   ██╔══██╗
 ╚█████╔╝  ██║   ██║ ███████║ ██║      ███████╗ ██║  ██║
  ╚════╝   ╚═╝   ╚═╝ ╚══════╝ ╚═╝      ╚══════╝ ╚═╝  ╚═╝
"""

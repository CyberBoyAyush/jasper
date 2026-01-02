from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

def get_config():
    return {
        "API_KEY": os.getenv("API_KEY", ""),
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

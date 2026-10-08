"""Streamlit Cloud root entry point for LangGraph Multi-Agent OCR Platform."""
import os
import sys
import runpy
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Run the core streamlit app
app_path = os.path.join(str(PROJECT_ROOT), "ocr_agentic_system", "app.py")
runpy.run_path(app_path, run_name="__main__")

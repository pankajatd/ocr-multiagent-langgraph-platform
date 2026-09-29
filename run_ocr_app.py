"""
Launcher script for LangGraph Multi-Agent OCR Platform.
"""
import sys
import subprocess
import os

def launch_cli():
    python_exe = os.path.join(os.getcwd(), "venv_ocr", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable
    cmd = [python_exe, "-m", "ocr_agentic_system.cli"] + sys.argv[1:]
    subprocess.run(cmd)

def launch_ui():
    python_exe = os.path.join(os.getcwd(), "venv_ocr", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable
    app_path = os.path.join(os.getcwd(), "ocr_agentic_system", "app.py")
    cmd = [python_exe, "-m", "streamlit", "run", app_path]
    subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ui":
        launch_ui()
    else:
        launch_cli()

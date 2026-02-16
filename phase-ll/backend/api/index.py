"""
Vercel serverless entry point for FastAPI application.
This file exports the FastAPI app for Vercel's Python runtime.
"""

import sys
from pathlib import Path

# Add parent directory to Python path so we can import from app
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.main import app

# Vercel expects the app to be exported
handler = app

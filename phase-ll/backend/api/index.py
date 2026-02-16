"""
Vercel serverless entry point for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) for serverless environments.
"""

import sys
from pathlib import Path

# Add parent directory to Python path so we can import from app
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.main import app
from mangum import Mangum

# Wrap FastAPI app with Mangum for serverless compatibility
handler = Mangum(app, lifespan="off")

"""
Vercel serverless entry point for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) for serverless environments.
"""

import sys
import os
from pathlib import Path

# Add parent directory to Python path so we can import from app
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Verify critical environment variables are set
required_vars = ["DATABASE_URL", "BETTER_AUTH_SECRET"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

from app.main import app
from mangum import Mangum

# Wrap FastAPI app with Mangum for serverless compatibility
handler = Mangum(app, lifespan="off")

"""Vercel Serverless Function entrypoint for CineMind FastAPI backend."""
import sys
from pathlib import Path

# Add project root to sys.path so 'backend' can be imported anywhere
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.main import app

# Vercel looks for the 'app' ASGI instance
__all__ = ["app"]


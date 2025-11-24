"""FastAPI application entrypoint package."""

from .bootstrap import create_api_app
from .main import app

__all__ = ["app", "create_api_app"]


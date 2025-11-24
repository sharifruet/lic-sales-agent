"""FastAPI entrypoint aligned with the new LangGraph-oriented layout."""

from __future__ import annotations

from .bootstrap import create_api_app

app = create_api_app()

__all__ = ["app", "create_api_app"]


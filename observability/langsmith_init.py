"""LangSmith project helpers."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def init_langsmith(project_name: str) -> bool:
    """Initialise LangSmith tracing if environment variables are configured."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        logger.info("LangSmith disabled: LANGSMITH_API_KEY not set.")
        return False

    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", project_name)
    logger.info("LangSmith tracing enabled for project '%s'.", project_name)
    return True


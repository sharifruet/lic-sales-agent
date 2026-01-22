from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path
import sys

import pytest
from httpx import ASGITransport, AsyncClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(PROJECT_ROOT / 'test.db').as_posix()}")
os.environ.setdefault("ENCRYPTION_KEY", "development-encryption-key-32-bytes!!")
os.environ.setdefault("JWT_SECRET_KEY", "development-jwt-secret-key-32-bytes!!")
os.environ.setdefault("ENVIRONMENT", "test")

from apps.api.main import app  # noqa: E402  # pylint: disable=wrong-import-position


@pytest.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


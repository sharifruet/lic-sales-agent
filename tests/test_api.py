"""Integration tests for FastAPI conversation endpoints."""

import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.main import app  # type: ignore  # pylint: disable=import-error
from tools import register_default_tools


@pytest.mark.asyncio()
async def test_conversation_flow() -> None:
    register_default_tools()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/conversations/demo/messages",
            json={"content": "Tell me about term life policies."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "demo"
        assert data["messages"], "Expected messages in response"

        get_response = await client.get("/api/conversations/demo")
        assert get_response.status_code == 200
        snapshot = get_response.json()
        assert snapshot["messages"][-1]["message_type"] in {"assistant", "system", "tool"}


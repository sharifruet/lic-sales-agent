import pytest
from httpx import AsyncClient


@pytest.mark.asyncio()
async def test_root_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "AI Life Insurance Sales Agent API"
    assert "version" in payload


@pytest.mark.asyncio()
async def test_health_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["environment"] == "test"


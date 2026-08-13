import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_redirect(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "SmartMES"
    assert "docs" in data


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["app_name"] == "SmartMES"


@pytest.mark.asyncio
async def test_health_db_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health/db")
    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert "status" in payload["data"]


@pytest.mark.asyncio
async def test_health_redis_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health/redis")
    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert "status" in payload["data"]

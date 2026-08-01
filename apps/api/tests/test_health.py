"""The liveness probe is the one route that must never depend on anything."""

from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient, api_prefix: str) -> None:
    response = await client.get(f"{api_prefix}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

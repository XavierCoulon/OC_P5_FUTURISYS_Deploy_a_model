import pytest


@pytest.mark.asyncio
async def test_root_router(async_client):
    """
    Test de l'endpoint racine '/' de l'API.
    Vérifie que le code HTTP est 200 et que le message attendu est retourné.
    """
    resp = await async_client.get("/")

    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to Futurisys ML API"}

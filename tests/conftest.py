import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.endpoints import api_router


@pytest_asyncio.fixture
async def async_client():
    """
    Async httpx client that mounts the FastAPI app via ASGITransport so tests
    can call routes defined on `api_router` (included without prefix).
    """
    app = FastAPI()
    app.include_router(api_router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:  # type: ignore
        yield client

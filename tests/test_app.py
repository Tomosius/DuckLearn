import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient, ASGITransport

# Import your actual FastAPI app
from app import app


@pytest.mark.asyncio
async def test_app_instance_type():
    """Ensure the imported object is a FastAPI instance."""
    assert isinstance(app, FastAPI)
    assert app.title == "DuckLearn"
    assert app.version == "1.0"


@pytest.mark.asyncio
async def test_hello_route_returns_correct_response():
    """Test /api/hello endpoint returns expected JSON and status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Tomosius FastAPI!"}


@pytest.mark.asyncio
async def test_hello_route_invalid_method_returns_405():
    """Ensure unsupported methods (like POST) are rejected on /api/hello."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/hello")

    assert response.status_code == 405
    assert response.json()["detail"] == "Method Not Allowed"


def test_cors_middleware_is_present():
    """Confirm CORSMiddleware is attached to the FastAPI app."""
    middleware_names = [mw.cls.__name__ for mw in app.user_middleware]
    assert "CORSMiddleware" in middleware_names


def test_cors_configuration_allows_localhost_origin():
    """Check that localhost:5173 is included in allowed origins."""
    cors = next((mw for mw in app.user_middleware if mw.cls == CORSMiddleware), None)
    assert cors is not None
    assert "http://localhost:5173" in cors.kwargs["allow_origins"]
    assert cors.kwargs["allow_credentials"] is True
    assert "*" in cors.kwargs["allow_methods"]
    assert "*" in cors.kwargs["allow_headers"]


@pytest.mark.asyncio
async def test_undefined_route_returns_404():
    """Requesting a non-existent route should return 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


@pytest.mark.asyncio
async def test_cors_preflight_options_request():
    """Verify CORS preflight (OPTIONS) request is allowed for localhost."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        }
        response = await ac.options("/api/hello", headers=headers)

    # CORS preflight should be handled
    assert response.status_code in (200, 204)
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
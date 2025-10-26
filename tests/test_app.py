import pytest
from httpx import ASGITransport, AsyncClient

# Import your actual FastAPI app
from app import app




@pytest.mark.asyncio
async def test_hello_route_returns_correct_response():
    """Test /api/hello endpoint returns expected JSON and status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.get('/api/hello')

    assert response.status_code == 200
    assert response.json() == {'message': 'Hello from Tomosius FastAPI!'}


@pytest.mark.asyncio
async def test_hello_route_invalid_method_returns_405():
    """Ensure unsupported methods (like POST) are rejected on /api/hello."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.post('/api/hello')

    assert response.status_code == 405
    assert response.json()['detail'] == 'Method Not Allowed'





@pytest.mark.asyncio
async def test_undefined_route_returns_404():
    """Requesting a non-existent route should return 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.get('/api/does-not-exist')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Not Found'


@pytest.mark.asyncio
async def test_cors_preflight_options_request():
    """Verify CORS preflight (OPTIONS) request is allowed for localhost."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        headers = {
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET',
        }
        response = await ac.options('/api/hello', headers=headers)

    # CORS preflight should be handled
    assert response.status_code in (200, 204)
    assert 'access-control-allow-origin' in response.headers
    assert (
        response.headers['access-control-allow-origin']
        == 'http://localhost:5173'
    )

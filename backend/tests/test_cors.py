from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_cors_allowed_origin():
    # settings.CORS_ORIGINS contains default like ["http://localhost:5173"]
    if not settings.CORS_ORIGINS:
        return # Skip if none configured

    allowed_origin = settings.CORS_ORIGINS[0]
    headers = {
        "Origin": allowed_origin,
        "Access-Control-Request-Method": "GET"
    }
    response = client.options("/api/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == allowed_origin

def test_cors_disallowed_origin():
    disallowed_origin = "http://evil-attacker.example.com"
    headers = {
        "Origin": disallowed_origin,
        "Access-Control-Request-Method": "GET"
    }
    response = client.options("/api/health", headers=headers)
    # The preflight response might be 400 or just return 200 without the CORS headers
    assert response.headers.get("access-control-allow-origin") is None

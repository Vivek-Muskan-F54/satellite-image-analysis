from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_readiness_check(mocker):
    # Mock the ML model ready function to simulate readiness
    mocker.patch('app.api.routes.health.check_model_ready', return_value=True)
    response = client.get("/api/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

def test_readiness_check_fails_on_ml(mocker):
    mocker.patch('app.api.routes.health.check_model_ready', return_value=False)
    response = client.get("/api/ready")
    assert response.status_code == 503
    assert "not ready" in response.json()["detail"].lower()

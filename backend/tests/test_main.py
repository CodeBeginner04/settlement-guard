from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "api-gateway"
    # Note: Status might be "no_model" in CI environment if artifacts aren't present

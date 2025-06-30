from fastapi.testclient import TestClient
from app.core.config import settings

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Custom GPT Adapter Service"}

def test_read_health(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 
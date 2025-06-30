import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.api.deps import get_current_application
from app.models.custom_gpt import CustomGPTApplication
from app.core.config import settings
from app.core.security import create_access_token
import uuid

def get_mock_current_application():
    return MagicMock(id='test_app_id')

app.dependency_overrides[get_current_application] = get_mock_current_application

@pytest.fixture
def client():
    return TestClient(app)

@patch('app.api.v1.endpoints.search.memory_bank_client.search_memories', new_callable=AsyncMock)
@patch('app.api.v1.endpoints.search.log_search_activity.delay')
def test_search_memories_success(mock_log_delay, mock_memory_search, client: TestClient):
    app_id = uuid.uuid4()
    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}
    
    mock_app = CustomGPTApplication(id=app_id)

    mock_memory_search.return_value = [{"memory_id": "mem-123", "content": "test content", "relevance_score": 0.9, "metadata": {}}]
    search_payload = {"query": "test query"}

    with patch("app.api.deps.get_current_application", return_value=mock_app):
        response = client.post(f"{settings.API_V1_STR}/search/", json=search_payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_log_delay.assert_called_once()

@patch('app.api.v1.endpoints.search.memory_bank_client.search_memories', new_callable=AsyncMock)
@patch('app.api.v1.endpoints.search.log_search_activity.delay')
def test_search_memories_service_unavailable(mock_log_delay, mock_memory_search, client: TestClient):
    app_id = uuid.uuid4()
    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}
    
    mock_app = CustomGPTApplication(id=app_id)
    
    mock_memory_search.side_effect = Exception("Service Down")
    search_payload = {"query": "test query"}

    with patch("app.api.deps.get_current_application", return_value=mock_app):
        response = client.post(f"{settings.API_V1_STR}/search/", json=search_payload, headers=headers)

    assert response.status_code == 500
    mock_log_delay.assert_called_once() 
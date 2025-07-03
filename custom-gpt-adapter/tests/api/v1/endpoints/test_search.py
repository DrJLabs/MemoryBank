import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.api.deps import get_current_application
from app.models.custom_gpt import CustomGPTApplication
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
import uuid
from sqlalchemy.orm import Session

def get_mock_current_application():
    return MagicMock(id='test_app_id')

app.dependency_overrides[get_current_application] = get_mock_current_application

@pytest.fixture
def client():
    return TestClient(app)

@patch('app.api.v1.endpoints.search.memory_bank_client.search_memories', new_callable=AsyncMock)
@patch('app.api.v1.endpoints.search.log_search_activity.delay')
def test_search_memories_success(mock_log_delay, mock_memory_search, client: TestClient, db_session: Session):
    app_id = uuid.uuid4()
    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}
    
    app = CustomGPTApplication(
        id=app_id,
        name="Test Search App",
        client_id="test-search-client",
        client_secret=get_password_hash("test-secret"),
        permissions=["read", "write"]
    )
    db_session.add(app)
    db_session.commit()

    mock_memory_search.return_value = [
        {
            "memory_id": "mem_123",
            "content": "Test memory content",
            "relevance_score": 0.95,
            "metadata": {"source": "test"}
        }
    ]

    payload = {"query": "test search", "limit": 10}
    response = client.post(f"{settings.API_V1_STR}/search/", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["results"]) == 1
    assert data["results"][0]["memory_id"] == "mem_123"
    
    mock_memory_search.assert_called_once_with(query="test search", limit=10)
    
    mock_log_delay.assert_called_once()

@patch('app.api.v1.endpoints.search.memory_bank_client.search_memories', new_callable=AsyncMock)
@patch('app.api.v1.endpoints.search.log_search_activity.delay')
def test_search_memories_error(mock_log_delay, mock_memory_search, client: TestClient, db_session: Session):
    app_id = uuid.uuid4()
    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}
    
    app = CustomGPTApplication(
        id=app_id,
        name="Test Search Error App",
        client_id="test-search-error-client",
        client_secret=get_password_hash("test-secret"),
        permissions=["read", "write"]
    )
    db_session.add(app)
    db_session.commit()

    mock_memory_search.side_effect = Exception("Search service unavailable")

    payload = {"query": "test search", "limit": 10}
    response = client.post(f"{settings.API_V1_STR}/search/", json=payload, headers=headers)

    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]

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
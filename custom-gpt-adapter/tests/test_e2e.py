"""
End-to-end tests for Custom GPT Adapter Service
Tests the complete user flows: authentication, search, and memory creation
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.custom_gpt import CustomGPTApplication

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_app():
    """Create a test Custom GPT application"""
    db = TestingSessionLocal()
    app = CustomGPTApplication(
        name="Test GPT",
        client_id="test-client-id",
        client_secret="test-client-secret",
        permissions=["read", "write"]
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    yield app
    db.delete(app)
    db.commit()
    db.close()

class TestE2EWorkflows:
    """Test complete end-to-end workflows"""

    def test_complete_authentication_flow(self, test_app):
        """Test OAuth authentication flow"""
        # Request token
        response = client.post(
            "/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": test_app.client_id,
                "client_secret": "test-client-secret"
            }
        )
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "Bearer"

        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/api/v1/me", headers=headers)
        assert response.status_code == 200

    def test_complete_search_flow(self, test_app):
        """Test memory search flow"""
        # Get authentication token
        token_response = client.post(
            "/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": test_app.client_id,
                "client_secret": "test-client-secret"
            }
        )
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Perform search
        search_data = {
            "query": "test search query",
            "limit": 5,
            "context": {
                "custom_gpt_id": "gpt-test",
                "conversation_id": "conv-123"
            }
        }
        response = client.post("/api/v1/search", json=search_data, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "request_id" in result
        assert "results" in result

    def test_complete_memory_creation_flow(self, test_app):
        """Test memory creation flow"""
        # Get authentication token
        token_response = client.post(
            "/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": test_app.client_id,
                "client_secret": "test-client-secret"
            }
        )
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create memory
        memory_data = {
            "content": "This is a test memory",
            "metadata": {
                "category": "TECHNICAL",
                "tags": ["test", "e2e"]
            },
            "context": {
                "custom_gpt_id": "gpt-test",
                "conversation_id": "conv-456"
            }
        }
        response = client.post("/api/v1/memories", json=memory_data, headers=headers)
        assert response.status_code == 202  # Accepted for async processing
        result = response.json()
        assert result["status"] == "accepted"
        assert "request_id" in result

    def test_rate_limiting_enforcement(self, test_app):
        """Test that rate limiting is properly enforced"""
        # Update app with strict rate limit
        db = TestingSessionLocal()
        db_app = db.query(CustomGPTApplication).filter_by(id=test_app.id).first()
        db_app.rate_limit = "2/minute"  # Very low limit for testing
        db.commit()
        db.close()

        # Get token
        token_response = client.post(
            "/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": test_app.client_id,
                "client_secret": "test-client-secret"
            }
        )
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Make requests until rate limited
        responses = []
        for i in range(5):
            response = client.post(
                "/api/v1/search",
                json={"query": f"test {i}"},
                headers=headers
            )
            responses.append(response.status_code)

        # Should have some successful and some rate limited
        assert 200 in responses
        assert 429 in responses  # Too Many Requests

    def test_error_handling_flow(self):
        """Test error handling for various scenarios"""
        # Invalid credentials
        response = client.post(
            "/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "invalid-id",
                "client_secret": "invalid-secret"
            }
        )
        assert response.status_code == 401

        # Missing authentication
        response = client.post("/api/v1/search", json={"query": "test"})
        assert response.status_code == 403

        # Invalid request data
        token_response = client.post(
            "/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "test-client-id",
                "client_secret": "test-client-secret"
            }
        )
        if token_response.status_code == 200:
            token = token_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Missing required field
            response = client.post("/api/v1/search", json={}, headers=headers)
            assert response.status_code == 422  # Validation error
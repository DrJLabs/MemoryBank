import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, Base
from app.database import get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the in-memory database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    # Set up the database tables
    Base.metadata.create_all(bind=engine)
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    # Mock the MCP server setup as it's not needed for this test
    with patch("app.main.setup_mcp_server", return_value=None):
        yield TestClient(app)
    # Tear down the database tables
    Base.metadata.drop_all(bind=engine)
    # Clear the dependency override
    app.dependency_overrides = {}


def test_read_main(client: TestClient):
    """
    Test that the root endpoint or a known endpoint returns a successful response.
    Here we test the main endpoint of the memories router.
    """
    # Mock the list method on the service used by the router
    with patch("app.services.memory_service.MemoryService.list") as mock_list:
        mock_list.return_value = [] # Return an empty list for simplicity
        response = client.get("/memories/")
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0, "page": 1, "size": 50, "pages": 0}
        mock_list.assert_called_once() 
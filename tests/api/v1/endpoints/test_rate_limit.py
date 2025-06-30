import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import time
import uuid

from app.models.custom_gpt import CustomGPTApplication
from app.core.security import create_access_token
from app.core.config import settings
from sqlalchemy.orm import Session

def test_rate_limit_exceeded(db_session: Session, client: TestClient):
    app_id = uuid.uuid4()
    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}
    
    app = CustomGPTApplication(id=app_id, name="Test App", client_id="test-client", client_secret="secret", rate_limit="5/minute")
    db_session.add(app)
    db_session.commit()
    
    with patch("app.api.deps.get_current_application", return_value=app):
        for i in range(5):
            response = client.post(f"{settings.API_V1_STR}/search/", json={"query": f"test {i}"}, headers=headers)
            assert response.status_code == 200

        response = client.post(f"{settings.API_V1_STR}/search/", json={"query": "test 6"}, headers=headers)
        assert response.status_code == 429

def test_rate_limit_resets(db_session: Session, client: TestClient):
    app_id = uuid.uuid4()
    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}

    app = CustomGPTApplication(id=app_id, name="Test App 2", client_id="test-client-2", client_secret="secret", rate_limit="5/second")
    db_session.add(app)
    db_session.commit()

    with patch("app.api.deps.get_current_application", return_value=app):
        for i in range(5):
            response = client.post(f"{settings.API_V1_STR}/search/", json={"query": f"test {i}"}, headers=headers)
            assert response.status_code == 200

        response = client.post(f"{settings.API_V1_STR}/search/", json={"query": "test 6"}, headers=headers)
        assert response.status_code == 429

        time.sleep(1)

        response = client.post(f"{settings.API_V1_STR}/search/", json={"query": "test 7"}, headers=headers)
        assert response.status_code == 200 
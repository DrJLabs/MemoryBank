from unittest.mock import patch
from fastapi.testclient import TestClient
import uuid

from app.models.custom_gpt import CustomGPTApplication
from app.core.security import create_access_token
from app.core.config import settings
from sqlalchemy.orm import Session

def test_create_memory_success(db_session: Session, client: TestClient):
    app_id = uuid.uuid4()
    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}

    app = CustomGPTApplication(id=app_id)
    db_session.add(app)
    db_session.commit()
    
    with patch("app.api.v1.endpoints.memories.log_memory_creation_activity.delay") as mock_delay:
        payload = {"content": "This is a new memory."}
        response = client.post(f"{settings.API_V1_STR}/memories/", json=payload, headers=headers)

        assert response.status_code == 202
        assert "message" in response.json()
        mock_delay.assert_called_once()
        call_kwargs = mock_delay.call_args.kwargs
        assert call_kwargs["application_id"] == str(app_id) 
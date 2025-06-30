import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash, create_access_token, create_refresh_token
from app.models.custom_gpt import CustomGPTApplication

def test_get_access_token(db_session: Session, client: TestClient) -> None:
    client_id = "test_client"
    client_secret = "test_secret"
    app_name = "Test App"
    hashed_secret = get_password_hash(client_secret)
    db_app = CustomGPTApplication(id=uuid.uuid4(), name=app_name, client_id=client_id, client_secret=hashed_secret)
    db_session.add(db_app)
    db_session.commit()

    response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": client_id, "password": client_secret},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_use_access_token(db_session: Session, client: TestClient) -> None:
    client_id = "test_client_2"
    client_secret = "test_secret_2"
    app_name = "Test App 2"
    
    hashed_secret = get_password_hash(client_secret)
    app_id = uuid.uuid4()
    db_app = CustomGPTApplication(id=app_id, name=app_name, client_id=client_id, client_secret=hashed_secret)
    db_session.add(db_app)
    db_session.commit()

    access_token = create_access_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(app_id)
    assert data["name"] == app_name
    assert data["client_id"] == client_id

def test_refresh_token(db_session: Session, client: TestClient) -> None:
    client_id = "test_client_3"
    client_secret = "test_secret_3"
    app_name = "Test App 3"
    
    hashed_secret = get_password_hash(client_secret)
    app_id = uuid.uuid4()
    db_app = CustomGPTApplication(id=app_id, name=app_name, client_id=client_id, client_secret=hashed_secret)
    db_session.add(db_app)
    db_session.commit()
    
    refresh_token = create_refresh_token(subject=str(app_id))
    headers = {"Authorization": f"Bearer {refresh_token}"}
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        headers=headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer" 
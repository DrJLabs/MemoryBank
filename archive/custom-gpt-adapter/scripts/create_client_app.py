import uuid
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.custom_gpt import CustomGPTApplication
from app.core.security import get_password_hash

def create_tables():
    Base.metadata.create_all(bind=engine)

def create_client_application(db: Session, name: str, client_id: str, client_secret: str):
    hashed_secret = get_password_hash(client_secret)
    db_app = CustomGPTApplication(
        id=uuid.uuid4(),
        name=name,
        client_id=client_id,
        client_secret=hashed_secret
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    print(f"Application '{name}' created with client_id '{client_id}'.")
    return db_app

def main():
    create_tables()
    db = SessionLocal()
    try:
        create_client_application(
            db,
            name="Test Application",
            client_id="test_client",
            client_secret="test_secret"
        )
    finally:
        db.close()

if __name__ == "__main__":
    main() 
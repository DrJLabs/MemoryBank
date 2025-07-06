from sqlalchemy.orm import Session
import uuid
from . import models

def get_application_by_client_id(db: Session, *, client_id: str):
    return db.query(models.CustomGPTApplication).filter(models.CustomGPTApplication.client_id == client_id).first()

def get_application(db: Session, id: uuid.UUID):
    return db.query(models.CustomGPTApplication).filter(models.CustomGPTApplication.id == id).first() 
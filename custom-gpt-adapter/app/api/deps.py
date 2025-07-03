from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError
import uuid

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.core.database import get_db

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)

def get_current_application(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.CustomGPTApplication:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Convert string UUID back to UUID object
    try:
        app_id = uuid.UUID(str(token_data.sub))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token format",
        )
    
    application = crud.get_application(db, id=app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

def get_current_application_from_refresh_token(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.CustomGPTApplication:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        if token_data.token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Convert string UUID back to UUID object
    try:
        app_id = uuid.UUID(str(token_data.sub))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token format",
        )
    
    application = crud.get_application(db, id=app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application 
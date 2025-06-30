from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.api import deps

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 access token login, get an access token for future requests
    """
    application = crud.get_application_by_client_id(db, client_id=form_data.username)
    if not application or not security.verify_password(
        form_data.password, application.client_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect client_id or client_secret",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        subject=application.id,
    )
    refresh_token = security.create_refresh_token(
        subject=application.id
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }

@router.post("/refresh", response_model=schemas.AccessToken)
async def refresh_token(
    current_application: models.CustomGPTApplication = Depends(deps.get_current_application_from_refresh_token),
):
    """
    OAuth2 refresh token, get a new access token
    """
    access_token = security.create_access_token(
        subject=current_application.id
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    } 
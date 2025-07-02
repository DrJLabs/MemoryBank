from fastapi import APIRouter, Depends

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=schemas.Application)
def read_users_me(
    current_application: models.CustomGPTApplication = Depends(deps.get_current_application),
):
    """
    Get current application.
    """
    return current_application 
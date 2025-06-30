import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api import deps
from app import models
from app.workers.memory_processor import log_memory_creation_activity
from app.core.limiter import limiter

router = APIRouter()

class MemoryCreateRequest(BaseModel):
    content: str
    context: Optional[Dict[str, Any]] = None

class MemoryCreateResponse(BaseModel):
    status: str = "pending"
    request_id: str
    message: str = "Memory creation request received and is being processed."

@router.post("/", response_model=MemoryCreateResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10/minute")
async def create_memory(
    memory_request: MemoryCreateRequest,
    request: Request,
    current_app: models.CustomGPTApplication = Depends(deps.get_current_application)
):
    """
    Receives a request to create a new memory and queues it for asynchronous processing.
    """
    request_id = str(uuid.uuid4())

    try:
        # Dispatch the memory creation and audit logging task to the background worker
        log_memory_creation_activity.delay(
            application_id=str(current_app.id),
            request_data=memory_request.model_dump(),
            request_id=request_id
        )

        return MemoryCreateResponse(request_id=request_id)

    except Exception as e:
        # This part would be executed if the message queue (e.g., Redis) is down
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to queue memory creation request: {e}"
        ) 
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.api import deps
from app import models, schemas
from app.clients.memory_bank_client import memory_bank_client
from app.workers.memory_processor import log_search_activity
from app.core.limiter import limiter
import httpx

router = APIRouter()

# Pydantic Models from Story 1.3
class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    memory_id: str
    content: str
    relevance_score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    status: str
    request_id: str
    results: List[SearchResult]

@router.post("/", response_model=schemas.SearchResponse)
@limiter.limit("10/minute")
async def search_memories(
    request: schemas.SearchRequest,
    req: Request,
    db: deps.Session = Depends(deps.get_db),
    current_application: models.CustomGPTApplication = Depends(
        deps.get_current_application
    ),
):
    """
    Search for memories in the Memory Bank.
    """
    try:
        search_results = await memory_bank_client.search_memories(
            query=request.query, limit=request.limit
        )

        # Assuming search_results is a list of dicts that match SearchResult
        response_data = {
            "status": "success",
            "results": search_results,
        }
        
        # Asynchronously log the search activity
        log_search_activity.delay(
            application_id=str(current_application.id),
            request_data=request.model_dump(),
            response_status=200,
        )
        return schemas.SearchResponse(**response_data)
    except httpx.HTTPStatusError as e:
        log_search_activity.delay(
            application_id=str(current_application.id),
            request_data=request.model_dump(),
            response_status=e.response.status_code,
        )
        raise HTTPException(
            status_code=e.response.status_code, detail="Error searching memories"
        )
    except Exception:
        log_search_activity.delay(
            application_id=str(current_application.id),
            request_data=request.model_dump(),
            response_status=500,
        )
        raise HTTPException(status_code=500, detail="Internal server error") 
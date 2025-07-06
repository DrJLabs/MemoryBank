from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid

class SearchFilter(BaseModel):
    categories: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None

class SearchContext(BaseModel):
    custom_gpt_id: str
    conversation_id: str

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
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    results: List[SearchResult] 
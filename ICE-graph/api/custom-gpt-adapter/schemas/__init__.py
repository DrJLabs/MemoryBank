from pydantic import BaseModel
import uuid
from .search import SearchRequest, SearchResult, SearchResponse
from .token import Token, AccessToken, TokenPayload

class ApplicationBase(BaseModel):
    name: str
    client_id: str

class ApplicationCreate(ApplicationBase):
    client_secret: str

class ApplicationUpdate(ApplicationBase):
    pass

class ApplicationInDBBase(ApplicationBase):
    id: uuid.UUID
    client_id: str

    class Config:
        orm_mode = True

class Application(ApplicationBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class ApplicationInDB(Application):
    client_secret: str

__all__ = [
    "SearchRequest",
    "SearchResult",
    "SearchResponse",
    "Token",
    "AccessToken",
    "TokenPayload",
] 
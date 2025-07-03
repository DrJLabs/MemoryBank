from pydantic import BaseModel
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
    token_type: str | None = None 
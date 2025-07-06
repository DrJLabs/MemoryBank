from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.deps import get_current_application

class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            token = request.headers.get("Authorization")
            if token:
                app = await get_current_application(token=token.split(" ")[1])
                request.state.current_app = app
        except Exception:
            request.state.current_app = None
        
        response = await call_next(request)
        return response 
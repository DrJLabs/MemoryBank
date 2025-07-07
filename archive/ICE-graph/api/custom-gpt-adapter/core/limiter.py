from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from app.api.deps import get_current_application
from app.models.custom_gpt import CustomGPTApplication

def get_rate_limit(request: Request):
    app: CustomGPTApplication = request.state.current_app
    return app.rate_limit if app else "10/minute"

limiter = Limiter(key_func=get_rate_limit) 
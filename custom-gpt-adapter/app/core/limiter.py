from slowapi import Limiter
from fastapi import Request

from app.models.custom_gpt import CustomGPTApplication

def get_rate_limit(request: Request):
    app: CustomGPTApplication = request.state.current_app
    return app.rate_limit if app else "10/minute"

limiter = Limiter(key_func=get_rate_limit) 
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1.endpoints import health, auth, users, memories, search
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.limiter import limiter
from app.middleware import RateLimiterMiddleware
from prometheus_fastapi_instrumentator.metrics import Info

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for the application.
    This is called on startup and shutdown.
    """
    print("Starting up...")
    # Add any startup logic here
    app.state.limiter = limiter
    yield
    print("Shutting down...")
    # Add any shutdown logic here

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RateLimiterMiddleware)

# 1. Add Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def client_id_label(info: Info):
    if hasattr(info.request.state, "current_app") and info.request.state.current_app:
        return {"client_id": info.request.state.current_app.client_id}
    return {"client_id": "unknown"}

# 2. Instrument for Prometheus
Instrumentator().instrument(app).expose(app)

# 3. Add Routers
@app.get("/")
def read_root():
    return {"message": "Welcome to the Custom GPT Adapter Service"}

app.include_router(health.router, prefix=f"{settings.API_V1_STR}", tags=["Health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(memories.router, prefix=f"{settings.API_V1_STR}/memories", tags=["Memories"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["Search"])
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "a-secret-key"
    PROJECT_NAME: str = "Custom GPT Adapter"
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    
    REDIS_HOST: str
    
    MEMORY_BANK_API_URL: str = "http://localhost:8080"
    MEMORY_BANK_API_KEY: str = "super-secret-key"

    class Config:
        case_sensitive = True
        if os.getenv("TESTING"):
            env_file = "tests/.env.test"
        else:
            env_file = ".env"

settings = Settings() 
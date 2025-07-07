from pydantic import computed_field
from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "Custom GPT Adapter Service"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    # Security settings
    SECRET_KEY: str = "dacec417e406d67652e0ed30a69dc3cfd72b63465d0802c6aaba029d12255582"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Memory Bank Service settings
    MEMORY_BANK_API_URL: str = "http://localhost:8001" # Default for local dev
    MEMORY_BANK_API_KEY: str = "super-secret-key"

    # Database settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "app"
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings() 
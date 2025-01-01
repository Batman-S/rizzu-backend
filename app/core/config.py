from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    openai_api_key: str
    max_workers: int = int(os.getenv("MAX_WORKERS", 4))
    rate_limit: str = os.getenv("RATE_LIMIT", "10/minute")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    cache_ttl: int = 3600
    timeout: float = 30.0
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_timeout: int = 2
    redis_connect_timeout: int = 2
    redis_password: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()

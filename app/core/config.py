from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: str
    max_workers: int = 4
    rate_limit: str = "10/minute"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    cache_ttl: int = 3600
    timeout: float = 30.0
    
    # Redis settings for caching
    redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()

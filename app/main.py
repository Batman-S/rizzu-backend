from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.v1.endpoints import process_image
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import uvicorn
from app.core.config import settings
import os

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Rizzu Backend",
    description="Backend service for Rizzu.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include OCR router
app.include_router(process_image.router, prefix="/api/v1", tags=["OCR"])

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

@app.on_event("shutdown")
async def shutdown():
    await FastAPICache.clear()

# Health check for DigitalOcean
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=settings.max_workers,
        loop="uvloop",
        http="httptools",
    )

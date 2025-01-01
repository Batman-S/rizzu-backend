from fastapi import FastAPI
from app.api.v1.endpoints import process_image

app = FastAPI(
    title="Rizzu Backend",
    description="Backend service for Rizzu.",
    version="1.0.0",
)

# Include OCR router
app.include_router(process_image.router, prefix="/api/v1", tags=["OCR"])

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from app.services.openai import OpenAIService, get_openai_service
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
import asyncio

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/process-image/")
@limiter.limit("10/minute")  # Adjust rate limit as needed
async def process_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Endpoint to process an image with rate limiting and optimized handling
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        # Read the image file with a size limit
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        image_bytes = await file.read(MAX_SIZE)
        
        if len(image_bytes) >= MAX_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        # Process the image
        response = await openai_service.process_image(image_bytes)
        
        # Clean up
        background_tasks.add_task(file.file.close)
        
        return {"status": "success", "response": response}

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Body
from app.services.openai import OpenAIService, get_openai_service

router = APIRouter()


@router.post("/process-image/")
async def process_image(
    file: UploadFile = File(...),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Endpoint to process an image and generate a response using GPT-4 Vision.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        # Read the image file
        image_bytes = await file.read()

        # Process the image and prompt
        response = await openai_service.process_image(image_bytes)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


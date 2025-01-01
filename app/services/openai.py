import base64
from openai import AsyncOpenAI
from app.core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import aiohttp
import hashlib


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=30.0,  # Adjust timeout
            max_retries=3,  # Add retries
        )
        self.session = None

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    @cache(expire=3600)  # Cache responses for 1 hour
    async def process_image(self, image_bytes: bytes) -> str:
        """
        Process image with caching and error handling
        """
        # Generate cache key based on image content
        cache_key = hashlib.md5(image_bytes).hexdigest()

        try:
            # Your existing code...
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            response = await self.client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                },
                            },
                        ],
                    },
                ],
                timeout=25.0,  # Specific timeout for this request
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {str(e)}")

    async def cleanup(self):
        if self.session:
            await self.session.close()


def get_openai_service() -> OpenAIService:
    return OpenAIService()

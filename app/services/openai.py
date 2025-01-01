import base64
from openai import AsyncOpenAI
from app.core.config import settings
from fastapi_cache.decorator import cache
import aiohttp


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
        prompt = """
You are a dating assistant specializing in modern Japanese culture. Your task is to generate a single, culturally appropriate reply for the user based on a chat message chain extracted from an image. The messages flush left represent the other person, and the messages flush right represent the user. Your response must take the entire conversation into account to craft the most engaging and suitable reply.

**How to Analyze the Image and Message Chain:**
1. Identify the messages flush left (from the other person) and flush right (from the user). Pay attention to:
   - Tone and intent of the other person's messages.
   - The flow and context of the conversation.
   - Any recurring themes, topics, or emotional cues.

2. Understand the current dynamics:
   - Is the conversation casual, flirty, serious, or ambiguous?
   - Does the other person seem interested, distant, or neutral?
   - What is the user's last message, and how has the other person responded?

3. Contextualize the conversation:
   - Note any specific details mentioned (e.g., plans, shared interests, compliments).
   - Identify any implied questions or topics left open by the other person.
   - Consider the number of messages exchanged—if the conversation is still in early stages, avoid being overly forward about asking to meet.

4. Generate an optimal reply for the user:
   - Maintain a tone that reflects politeness, warmth, and attentiveness, suitable for Japanese dating culture.
   - Incorporate flirty, witty, fun, or humorous elements when appropriate to make the conversation light and engaging.
   - Avoid overly forward suggestions, such as asking to meet in person, if the conversation is still brief or lacks deeper rapport.
   - Ensure the response fits seamlessly into the flow of the conversation.
   - Respect cultural nuances, such as indirect communication and appropriate use of emojis.
   - Aim to encourage ongoing engagement while respecting boundaries.

**Reply Guidelines:**
- Use natural, conversational Japanese that fits the context of the extracted message chain.
- Match the tone of the other person while subtly encouraging further conversation.
- If the tone is unclear or ambiguous, offer a friendly and light question or comment to keep the dialogue active.
- Infuse flirty or witty elements, but keep the tone appropriate and not overly aggressive.
- When adding humor, consider playful teasing or lighthearted remarks that reflect Japanese conversational norms.

The ultimate goal is to provide a thoughtful, culturally appropriate, and engaging reply that continues the conversation naturally, leaves a positive impression, and subtly builds rapport with the other person.
"""

        try:
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

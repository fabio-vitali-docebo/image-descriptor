from abc import ABC, abstractmethod
from openai import OpenAI

class VisionService(ABC):
    """Abstract base class for vision services."""
    
    @abstractmethod
    async def describe_image(self, image_url: str) -> str:
        """
        Generate a description for the given image.
        
        Args:
            image_url: URL of the image to describe
            
        Returns:
            str: A detailed description of the image
        """
        pass

class OpenAIVisionService(VisionService):
    """OpenAI Vision API implementation."""
    
    def __init__(self, api_key: str):
        """Initialize the OpenAI Vision service."""
        self.client = OpenAI(api_key=api_key)

    async def describe_image(self, image_url: str) -> str:
        """Generate a description using OpenAI Vision API."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please describe this image in detail."},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't process this image: {str(e)}" 
from abc import ABC, abstractmethod
import logging
import requests
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)

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
        logger.debug("Initializing OpenAI Vision service")
        self.client = OpenAI(api_key=api_key)
    
    async def describe_image(self, image_url: str) -> str:
        """
        Describe an image using OpenAI's GPT-4o model.
        
        Args:
            image_url: The URL of the image to describe
            
        Returns:
            str: A detailed description of the image
        """
        try:
            logger.debug(f"Describing image: {image_url}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please provide a detailed description of this image."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            description = response.choices[0].message.content
            logger.debug(f"Generated description: {description}")
            return description
            
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            raise 
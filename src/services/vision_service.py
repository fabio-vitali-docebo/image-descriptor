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
                            {
                                "type": "text", 
                                "text": """Analizza questa immagine e rispondi in italiano. 

PRIMO: Determina se si tratta di un annuncio di evento (concerto, conferenza, festival, spettacolo, mostra, etc.).

SE È UN ANNUNCIO DI EVENTO, estrai e presenta queste informazioni in questo formato:
🎫 INFORMAZIONI EVENTO
• Nome evento: [nome dell'evento]
• Descrizione: [breve descrizione dell'evento]
• Data: [data/e dell'evento]
• Orario: [orario di inizio e fine se disponibile]
• Luogo: [nome del luogo/venue e indirizzo se disponibile]
• Organizzatore: [se indicato]
• Prezzo/Biglietti: [informazioni sui biglietti se disponibili]
• Contatti: [siti web, telefoni, email se disponibili]

SECONDO: Fornisci sempre una descrizione dettagliata dell'immagine, includendo tutti gli elementi visibili, i colori, lo stile grafico, il layout, le persone (se presenti), gli oggetti e l'atmosfera generale."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            description = response.choices[0].message.content
            logger.debug(f"Generated description: {description}")
            return description
            
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            raise 
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, Chat, User, PhotoSize
from telegram.ext import ContextTypes
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.vision_service import OpenAIVisionService
from src.bot.telegram_bot import ImageDescriptionBot

@pytest.fixture
def mock_openai_api_key():
    """Mock OpenAI API key for testing"""
    return "test_openai_api_key"

@pytest.fixture  
def mock_telegram_token():
    """Mock Telegram token for testing"""
    return "test_telegram_token"

@pytest.fixture
def mock_vision_service(mock_openai_api_key):
    """Mock vision service for testing"""
    with patch('src.services.vision_service.OpenAI'):
        service = OpenAIVisionService(mock_openai_api_key)
        return service

@pytest.fixture
def mock_telegram_bot(mock_telegram_token, mock_vision_service):
    """Mock telegram bot for testing"""
    with patch('telegram.ext.Application.builder'):
        bot = ImageDescriptionBot(mock_telegram_token, mock_vision_service)
        return bot

@pytest.fixture
def sample_update():
    """Create a sample Telegram update with photo"""
    # Create mock objects
    user = User(id=123, is_bot=False, first_name="Test", username="testuser")
    chat = Chat(id=456, type="private")
    photo = PhotoSize(file_id="test_photo_id", file_unique_id="unique_id", width=800, height=600)
    
    message = Message(
        message_id=789,
        from_user=user,
        date=None,
        chat=chat,
        photo=[photo]
    )
    
    update = Update(update_id=1, message=message)
    return update

@pytest.fixture
def sample_context():
    """Create a sample context for testing"""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    context.bot.get_file = AsyncMock()
    return context

@pytest.fixture
def sample_image_url():
    """Sample image URL for testing"""
    return "https://api.telegram.org/file/botTEST_TOKEN/photos/test_image.jpg"

@pytest.fixture
def sample_regular_image_response():
    """Sample AI response for regular image description"""
    return """Questa è un'immagine che mostra un paesaggio montano durante il tramonto. 
    I colori dominanti sono il dorato e l'arancione del cielo, con silhouette scure delle montagne. 
    Si possono vedere alcune nuvole sparse e la luce calda del sole che crea un'atmosfera serena e rilassante."""

@pytest.fixture
def sample_event_image_response():
    """Sample AI response for event announcement image"""
    return """🎫 **INFORMAZIONI EVENTO**
• **Nome evento:** Festival Jazz Estivo 2024
• **Descrizione:** Tre giorni di musica jazz con artisti internazionali
• **Data:** 15-17 Luglio 2024
• **Orario:** 20:00 - 24:00
• **Luogo:** Parco della Musica, Via Roma 123, Milano
• **Organizzatore:** Associazione Jazz Milano
• **Prezzo/Biglietti:** €25 giornaliero, €60 abbonamento 3 giorni
• **Contatti:** www.jazzfestival.it, info@jazzfestival.it

L'immagine mostra un poster colorato con design moderno in tonalità blu e oro. 
Al centro è presente il titolo dell'evento in caratteri grandi e eleganti. 
Sono visibili silhouette di musicisti con strumenti jazz e note musicali stilizzate."""

@pytest.fixture
def mock_openai_response_regular(sample_regular_image_response):
    """Mock OpenAI response for regular image"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = sample_regular_image_response
    return mock_response

@pytest.fixture  
def mock_openai_response_event(sample_event_image_response):
    """Mock OpenAI response for event image"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = sample_event_image_response
    return mock_response

@pytest.fixture
def mock_telegram_file():
    """Mock Telegram file response"""
    mock_file = Mock()
    mock_file.file_path = "photos/test_image.jpg"
    return mock_file 
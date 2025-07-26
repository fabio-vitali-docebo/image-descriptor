import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.vision_service import VisionService

class TestBasicFunctionality:
    """Basic functionality tests that work without async complications"""
    
    def test_vision_service_is_abstract(self):
        """Test that VisionService cannot be instantiated directly"""
        with pytest.raises(TypeError):
            VisionService()
    
    def test_basic_imports(self):
        """Test that we can import our modules"""
        from src.services.vision_service import OpenAIVisionService
        from src.bot.telegram_bot import ImageDescriptionBot
        
        # Test that classes exist
        assert OpenAIVisionService is not None
        assert ImageDescriptionBot is not None
    
    def test_openai_vision_service_init(self):
        """Test OpenAI Vision Service initialization"""
        from src.services.vision_service import OpenAIVisionService
        
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            service = OpenAIVisionService("test_api_key")
            
            # Verify OpenAI client was created with correct API key
            mock_openai.assert_called_once_with(api_key="test_api_key")
            assert service.client == mock_client
    
    def test_telegram_bot_init(self):
        """Test Telegram Bot initialization"""
        from src.bot.telegram_bot import ImageDescriptionBot
        from src.services.vision_service import VisionService
        
        # Create a mock vision service
        mock_vision_service = Mock(spec=VisionService)
        
        with patch('telegram.ext.Application.builder') as mock_builder:
            mock_app = Mock()
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            
            bot = ImageDescriptionBot("test_token", mock_vision_service)
            
            assert bot.token == "test_token"
            assert bot.vision_service == mock_vision_service
            assert bot.application == mock_app
    
    def test_vision_service_describe_image_sync_wrapper(self):
        """Test vision service describe_image method with sync wrapper"""
        from src.services.vision_service import OpenAIVisionService
        
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            # Setup OpenAI mock
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test description in Italian"
            mock_client.chat.completions.create.return_value = mock_response
            
            # Create service
            service = OpenAIVisionService("test_api_key")
            
            # Test the async method using asyncio.run
            async def test_async():
                return await service.describe_image("https://example.com/image.jpg")
            
            result = asyncio.run(test_async())
            
            # Verify result
            assert result == "Test description in Italian"
            mock_client.chat.completions.create.assert_called_once()
            
            # Verify the call includes Italian instructions
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == 'gpt-4o'
            assert call_args[1]['max_tokens'] == 500
            
            messages = call_args[1]['messages']
            assert len(messages) == 1
            assert messages[0]['role'] == 'user'
            
            # Check that prompt includes event detection instructions
            text_content = messages[0]['content'][0]['text']
            assert 'INFORMAZIONI EVENTO' in text_content
            assert 'italiano' in text_content
    
    def test_telegram_bot_start_command_sync_wrapper(self):
        """Test telegram bot start command with sync wrapper"""
        from src.bot.telegram_bot import ImageDescriptionBot
        from src.services.vision_service import VisionService
        
        # Create mocks
        mock_vision_service = Mock(spec=VisionService)
        
        with patch('telegram.ext.Application.builder') as mock_builder:
            mock_app = Mock()
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            
            bot = ImageDescriptionBot("test_token", mock_vision_service)
            
            # Create fully mocked update and context (like in other tests)
            update = Mock()
            update.effective_user = Mock()
            update.message = Mock()
            update.message.reply_text = AsyncMock()
            
            context = Mock()
            
            # Test start command using asyncio.run
            async def test_async():
                await bot.start_command(update, context)
            
            asyncio.run(test_async())
            
            # Verify Italian welcome message was sent
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args[0][0]
            assert "Ciao!" in call_args
            assert "Image Descriptor Bot" in call_args
            assert "descrizione dettagliata" in call_args 
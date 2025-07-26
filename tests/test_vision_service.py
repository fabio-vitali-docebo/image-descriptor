import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.vision_service import OpenAIVisionService, VisionService

class TestVisionService:
    """Test the abstract VisionService interface"""
    
    def test_vision_service_is_abstract(self):
        """Test that VisionService cannot be instantiated directly"""
        with pytest.raises(TypeError):
            VisionService()

class TestOpenAIVisionService:
    """Test the OpenAI Vision Service implementation"""
    
    def test_describe_regular_image(self, mock_openai_api_key, mock_openai_response_regular, sample_image_url):
        """Test describing a regular image (non-event)"""
        async def _test():
            with patch('src.services.vision_service.OpenAI') as mock_openai:
                # Setup mock
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_client.chat.completions.create.return_value = mock_openai_response_regular
                
                # Create service and test
                service = OpenAIVisionService(mock_openai_api_key)
                result = await service.describe_image(sample_image_url)
                return result, mock_client
        
        result, mock_client = asyncio.run(_test())
        
        # Verify
        assert "paesaggio montano" in result
        assert "tramonto" in result
        assert "dorato e l'arancione" in result
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that the call includes Italian instructions
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        prompt_text = messages[0]['content'][0]['text']
        assert "italiano" in prompt_text
        assert "INFORMAZIONI EVENTO" in prompt_text

    @pytest.mark.asyncio
    async def test_describe_event_image(self, mock_openai_api_key, mock_openai_response_event, sample_image_url):
        """Test describing an event announcement image"""
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            # Setup mock
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_openai_response_event
            
            # Create service and test
            service = OpenAIVisionService(mock_openai_api_key)
            result = await service.describe_image(sample_image_url)
            
            # Verify event information extraction
            assert "🎫 **INFORMAZIONI EVENTO**" in result
            assert "Festival Jazz Estivo 2024" in result
            assert "15-17 Luglio 2024" in result
            assert "20:00 - 24:00" in result
            assert "Parco della Musica" in result
            assert "€25 giornaliero" in result
            assert "www.jazzfestival.it" in result
            
            # Verify description is also included
            assert "poster colorato" in result
            assert "design moderno" in result

    @pytest.mark.asyncio 
    async def test_openai_api_parameters(self, mock_openai_api_key, mock_openai_response_regular, sample_image_url):
        """Test that correct parameters are sent to OpenAI API"""
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            # Setup mock
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_openai_response_regular
            
            # Create service and test
            service = OpenAIVisionService(mock_openai_api_key)
            await service.describe_image(sample_image_url)
            
            # Verify API call parameters
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == 'gpt-4o'
            assert call_args[1]['max_tokens'] == 500
            
            # Verify message structure
            messages = call_args[1]['messages']
            assert len(messages) == 1
            assert messages[0]['role'] == 'user'
            assert len(messages[0]['content']) == 2
            
            # Verify text prompt
            text_content = messages[0]['content'][0]
            assert text_content['type'] == 'text'
            assert 'PRIMO: Determina se si tratta di un annuncio di evento' in text_content['text']
            
            # Verify image URL
            image_content = messages[0]['content'][1]
            assert image_content['type'] == 'image_url'
            assert image_content['image_url']['url'] == sample_image_url

    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_openai_api_key, sample_image_url):
        """Test handling of OpenAI API errors"""
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            # Setup mock to raise exception
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            # Create service and test
            service = OpenAIVisionService(mock_openai_api_key)
            
            # Verify exception is re-raised
            with pytest.raises(Exception, match="API Error"):
                await service.describe_image(sample_image_url)

    def test_service_initialization(self, mock_openai_api_key):
        """Test proper initialization of OpenAIVisionService"""
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            service = OpenAIVisionService(mock_openai_api_key)
            
            # Verify OpenAI client was created with correct API key
            mock_openai.assert_called_once_with(api_key=mock_openai_api_key)
            assert service.client == mock_client

    @pytest.mark.asyncio
    async def test_different_image_formats(self, mock_openai_api_key, mock_openai_response_regular):
        """Test with different image URL formats"""
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_openai_response_regular
            
            service = OpenAIVisionService(mock_openai_api_key)
            
            # Test different URL formats
            test_urls = [
                "https://api.telegram.org/file/botTOKEN/photos/image.jpg",
                "https://example.com/image.png",
                "https://cdn.example.com/uploads/photo_123.jpeg"
            ]
            
            for url in test_urls:
                result = await service.describe_image(url)
                assert result is not None
                assert len(result) > 0 
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.bot.telegram_bot import ImageDescriptionBot
from src.services.vision_service import VisionService

class TestImageDescriptionBot:
    """Test the ImageDescriptionBot class"""

    def test_bot_initialization(self, mock_telegram_token, mock_vision_service):
        """Test proper initialization of ImageDescriptionBot"""
        with patch('telegram.ext.Application.builder') as mock_builder:
            mock_app = Mock()
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            
            bot = ImageDescriptionBot(mock_telegram_token, mock_vision_service)
            
            assert bot.token == mock_telegram_token
            assert bot.vision_service == mock_vision_service
            assert bot.application == mock_app

    @pytest.mark.asyncio
    async def test_start_command_handler(self, mock_telegram_bot, sample_update, sample_context):
        """Test /start command handler with Italian response"""
        # Setup update for /start command
        sample_update.message.text = "/start"
        sample_update.message.photo = None
        sample_update.message.reply_text = AsyncMock()
        
        # Test start command
        await mock_telegram_bot.start_command(sample_update, sample_context)
        
        # Verify Italian welcome message
        sample_update.message.reply_text.assert_called_once()
        call_args = sample_update.message.reply_text.call_args[0][0]
        assert "Ciao!" in call_args
        assert "Image Descriptor Bot" in call_args
        assert "descrizione dettagliata" in call_args

    @pytest.mark.asyncio
    async def test_handle_image_regular(self, mock_telegram_bot, sample_update, sample_context, 
                                      mock_telegram_file, sample_regular_image_response):
        """Test handling regular image with description"""
        # Setup mocks
        sample_context.bot.get_file.return_value = mock_telegram_file
        sample_update.message.chat.send_action = AsyncMock()
        sample_update.message.reply_text = AsyncMock()
        
        # Mock vision service response
        mock_telegram_bot.vision_service.describe_image = AsyncMock(
            return_value=sample_regular_image_response
        )
        
        # Test image handling
        await mock_telegram_bot.handle_image(sample_update, sample_context)
        
        # Verify file was retrieved
        sample_context.bot.get_file.assert_called_once_with("test_photo_id")
        
        # Verify typing action
        sample_update.message.chat.send_action.assert_called_once_with('typing')
        
        # Verify vision service was called with correct URL
        expected_url = f"https://api.telegram.org/file/bot{mock_telegram_bot.token}/{mock_telegram_file.file_path}"
        mock_telegram_bot.vision_service.describe_image.assert_called_once_with(expected_url)
        
        # Verify Italian intro and citation
        sample_update.message.reply_text.assert_called_once()
        call_args = sample_update.message.reply_text.call_args
        response_text = call_args[0][0]
        
        assert "Ecco la descrizione dell'immagine:" in response_text
        assert sample_regular_image_response in response_text
        
        # Verify citation (reply_to_message_id)
        assert call_args[1]['reply_to_message_id'] == sample_update.message.message_id

    @pytest.mark.asyncio
    async def test_handle_image_event(self, mock_telegram_bot, sample_update, sample_context,
                                    mock_telegram_file, sample_event_image_response):
        """Test handling event announcement image"""
        # Setup mocks
        sample_context.bot.get_file.return_value = mock_telegram_file
        sample_update.message.chat.send_action = AsyncMock()
        sample_update.message.reply_text = AsyncMock()
        
        # Mock vision service response for event
        mock_telegram_bot.vision_service.describe_image = AsyncMock(
            return_value=sample_event_image_response
        )
        
        # Test image handling
        await mock_telegram_bot.handle_image(sample_update, sample_context)
        
        # Verify response contains event information
        call_args = sample_update.message.reply_text.call_args
        response_text = call_args[0][0]
        
        assert "Ecco la descrizione dell'immagine:" in response_text
        assert "🎫 **INFORMAZIONI EVENTO**" in response_text
        assert "Festival Jazz Estivo 2024" in response_text
        assert "15-17 Luglio 2024" in response_text

    @pytest.mark.asyncio
    async def test_handle_image_no_photo(self, mock_telegram_bot, sample_update, sample_context):
        """Test handling update with no photo"""
        # Remove photo from update
        sample_update.message.photo = None
        
        # Mock reply_text to track calls
        sample_update.message.reply_text = AsyncMock()
        
        # Test image handling
        await mock_telegram_bot.handle_image(sample_update, sample_context)
        
        # Verify no processing occurred
        sample_update.message.reply_text.assert_not_called()
        sample_context.bot.get_file.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_image_no_user(self, mock_telegram_bot, sample_update, sample_context):
        """Test handling update with no effective user"""
        # Remove user from update
        sample_update._effective_user = None
        
        # Mock reply_text to track calls
        sample_update.message.reply_text = AsyncMock()
        
        # Test image handling
        await mock_telegram_bot.handle_image(sample_update, sample_context)
        
        # Verify no processing occurred
        sample_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_image_vision_service_error(self, mock_telegram_bot, sample_update, 
                                                   sample_context, mock_telegram_file):
        """Test error handling when vision service fails"""
        # Setup mocks
        sample_context.bot.get_file.return_value = mock_telegram_file
        sample_update.message.chat.send_action = AsyncMock()
        sample_update.message.reply_text = AsyncMock()
        
        # Mock vision service to raise exception
        mock_telegram_bot.vision_service.describe_image = AsyncMock(
            side_effect=Exception("Vision service error")
        )
        
        # Test image handling
        await mock_telegram_bot.handle_image(sample_update, sample_context)
        
        # Verify error message in Italian with citation
        sample_update.message.reply_text.assert_called_once()
        call_args = sample_update.message.reply_text.call_args
        
        error_message = call_args[0][0]
        assert "Mi dispiace" in error_message
        assert "non sono riuscito a elaborare" in error_message
        assert "Riprova più tardi" in error_message
        
        # Verify citation
        assert call_args[1]['reply_to_message_id'] == sample_update.message.message_id

    @pytest.mark.asyncio
    async def test_handle_image_telegram_api_error(self, mock_telegram_bot, sample_update, sample_context):
        """Test error handling when Telegram API fails"""
        # Setup mocks - get_file fails
        sample_context.bot.get_file.side_effect = Exception("Telegram API error")
        sample_update.message.chat.send_action = AsyncMock()
        sample_update.message.reply_text = AsyncMock()
        
        # Test image handling
        await mock_telegram_bot.handle_image(sample_update, sample_context)
        
        # Verify error message
        sample_update.message.reply_text.assert_called_once()
        call_args = sample_update.message.reply_text.call_args
        error_message = call_args[0][0]
        assert "Mi dispiace" in error_message

    def test_setup_handlers(self, mock_telegram_bot):
        """Test that handlers are properly set up"""
        # Mock the application methods
        mock_telegram_bot.application.add_handler = Mock()
        mock_telegram_bot.application.add_error_handler = Mock()
        
        # Setup handlers
        mock_telegram_bot.setup_handlers()
        
        # Verify handlers were added
        assert mock_telegram_bot.application.add_handler.call_count == 2
        mock_telegram_bot.application.add_error_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handler_network_error(self, mock_telegram_bot):
        """Test error handler for NetworkError"""
        from telegram.error import NetworkError
        
        # Create mock context with NetworkError
        mock_context = Mock()
        mock_context.error = NetworkError("Network error")
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            await mock_telegram_bot.error_handler(None, mock_context)
            mock_print.assert_called_with("Network error occurred")

    @pytest.mark.asyncio
    async def test_error_handler_timeout_error(self, mock_telegram_bot):
        """Test error handler for TimedOut error"""
        from telegram.error import TimedOut
        
        # Create mock context with TimedOut error
        mock_context = Mock()
        mock_context.error = TimedOut()
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            await mock_telegram_bot.error_handler(None, mock_context)
            mock_print.assert_called_with("Request timed out")

    @pytest.mark.asyncio
    async def test_error_handler_generic_error(self, mock_telegram_bot):
        """Test error handler for generic errors"""
        # Create mock context with generic error
        mock_context = Mock()
        mock_context.error = Exception("Generic error")
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            await mock_telegram_bot.error_handler(None, mock_context)
            mock_print.assert_called_with("Exception while handling an update: Generic error")

    def test_start_method_setup(self, mock_telegram_bot):
        """Test start method calls proper setup"""
        # Mock the application and its methods
        mock_telegram_bot.application.run_polling = Mock()
        
        with patch.object(mock_telegram_bot, 'setup_handlers') as mock_setup:
            with patch('builtins.print'):
                # Test start method
                mock_telegram_bot.start()
                
                # Verify setup was called
                mock_setup.assert_called_once()
                
                # Verify polling was started with correct parameters
                mock_telegram_bot.application.run_polling.assert_called_once()
                call_kwargs = mock_telegram_bot.application.run_polling.call_args[1]
                assert call_kwargs['drop_pending_updates'] == True
                assert call_kwargs['read_timeout'] == 30 
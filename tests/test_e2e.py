import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.bot.telegram_bot import ImageDescriptionBot
from src.services.vision_service import OpenAIVisionService
from src.handlers.lambda_handler import process_update, lambda_handler

class TestEndToEndBot:
    """End-to-end integration tests for the complete bot workflow"""

    @pytest.mark.asyncio
    async def test_complete_image_processing_flow_regular(self, mock_openai_api_key, 
                                                        mock_telegram_token, sample_regular_image_response):
        """Test complete flow: Telegram update -> Bot -> Vision Service -> Response"""
        
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            with patch('telegram.ext.Application.builder') as mock_builder:
                # Setup OpenAI mock
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = sample_regular_image_response
                mock_client.chat.completions.create.return_value = mock_response
                
                # Setup Telegram bot mock
                mock_app = Mock()
                mock_builder.return_value.token.return_value.build.return_value = mock_app
                
                # Create services
                vision_service = OpenAIVisionService(mock_openai_api_key)
                bot = ImageDescriptionBot(mock_telegram_token, vision_service)
                
                # Create mock update and context
                update = Mock()
                update.effective_user = Mock()
                update.message = Mock()
                update.message.photo = [Mock()]
                update.message.photo[-1].file_id = "test_file_id"
                update.message.message_id = 123
                update.message.chat.send_action = AsyncMock()
                update.message.reply_text = AsyncMock()
                
                context = Mock()
                mock_file = Mock()
                mock_file.file_path = "photos/test.jpg"
                context.bot.get_file = AsyncMock(return_value=mock_file)
                
                # Execute the complete flow
                await bot.handle_image(update, context)
                
                # Verify the complete chain
                # 1. Telegram file was retrieved
                context.bot.get_file.assert_called_once_with("test_file_id")
                
                # 2. OpenAI was called with correct parameters
                mock_client.chat.completions.create.assert_called_once()
                call_args = mock_client.chat.completions.create.call_args
                assert call_args[1]['model'] == 'gpt-4o'
                assert call_args[1]['max_tokens'] == 500
                
                # 3. Response was sent with Italian intro and citation
                update.message.reply_text.assert_called_once()
                response_args = update.message.reply_text.call_args
                response_text = response_args[0][0]
                
                assert "Ecco la descrizione dell'immagine:" in response_text
                assert sample_regular_image_response in response_text
                assert response_args[1]['reply_to_message_id'] == 123

    @pytest.mark.asyncio
    async def test_complete_image_processing_flow_event(self, mock_openai_api_key, 
                                                      mock_telegram_token, sample_event_image_response):
        """Test complete flow for event announcement image"""
        
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            with patch('telegram.ext.Application.builder') as mock_builder:
                # Setup OpenAI mock for event response
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = sample_event_image_response
                mock_client.chat.completions.create.return_value = mock_response
                
                # Setup Telegram bot mock
                mock_app = Mock()
                mock_builder.return_value.token.return_value.build.return_value = mock_app
                
                # Create services
                vision_service = OpenAIVisionService(mock_openai_api_key)
                bot = ImageDescriptionBot(mock_telegram_token, vision_service)
                
                # Create mock update and context
                update = Mock()
                update.effective_user = Mock()
                update.message = Mock()
                update.message.photo = [Mock()]
                update.message.photo[-1].file_id = "event_file_id"
                update.message.message_id = 456
                update.message.chat.send_action = AsyncMock()
                update.message.reply_text = AsyncMock()
                
                context = Mock()
                mock_file = Mock()
                mock_file.file_path = "photos/event.jpg"
                context.bot.get_file = AsyncMock(return_value=mock_file)
                
                # Execute the complete flow
                await bot.handle_image(update, context)
                
                # Verify event-specific response
                update.message.reply_text.assert_called_once()
                response_args = update.message.reply_text.call_args
                response_text = response_args[0][0]
                
                # Check Italian intro
                assert "Ecco la descrizione dell'immagine:" in response_text
                
                # Check event information extraction
                assert "🎫 **INFORMAZIONI EVENTO**" in response_text
                assert "Festival Jazz Estivo 2024" in response_text
                assert "15-17 Luglio 2024" in response_text
                assert "Parco della Musica" in response_text
                
                # Check citation
                assert response_args[1]['reply_to_message_id'] == 456

class TestLambdaHandlerE2E:
    """End-to-end tests for AWS Lambda handler"""

    @pytest.mark.asyncio 
    async def test_lambda_handler_start_command(self, mock_telegram_token, mock_openai_api_key):
        """Test lambda handler processing /start command"""
        
        # Mock SSM parameter store
        with patch('src.handlers.lambda_handler.get_ssm_parameter') as mock_ssm:
            mock_ssm.side_effect = lambda param: {
                "/image-descriptor/telegram-token": mock_telegram_token,
                "/image-descriptor/openai-api-key": mock_openai_api_key
            }[param]
            
            # Mock requests for Telegram API
            with patch('requests.post') as mock_post:
                mock_post.return_value = Mock()
                
                # Create lambda event for /start command
                event = {
                    'body': json.dumps({
                        'message': {
                            'message_id': 1,
                            'chat': {'id': 123},
                            'text': '/start'
                        }
                    })
                }
                
                # Process the event
                result = await process_update(
                    json.loads(event['body']), 
                    mock_telegram_token, 
                    mock_openai_api_key
                )
                
                # Verify response
                assert result['statusCode'] == 200
                assert result['body'] == "Start message sent"
                
                # Verify Telegram API was called with Italian message
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                payload = call_args[1]['json']
                
                assert payload['chat_id'] == 123
                assert "Ciao!" in payload['text']
                assert "Image Descriptor Bot" in payload['text']

    @pytest.mark.asyncio
    async def test_lambda_handler_image_processing(self, mock_telegram_token, mock_openai_api_key,
                                                 sample_regular_image_response):
        """Test lambda handler processing image"""
        
        # Mock SSM parameter store
        with patch('src.handlers.lambda_handler.get_ssm_parameter') as mock_ssm:
            mock_ssm.side_effect = lambda param: {
                "/image-descriptor/telegram-token": mock_telegram_token,
                "/image-descriptor/openai-api-key": mock_openai_api_key
            }[param]
            
            # Mock OpenAI vision service
            with patch('src.services.vision_service.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = sample_regular_image_response
                mock_client.chat.completions.create.return_value = mock_response
                
                # Mock requests for Telegram API
                with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
                    # Mock Telegram getFile API
                    mock_get.return_value = Mock()
                    mock_get.return_value.json.return_value = {
                        'ok': True,
                        'result': {'file_path': 'photos/test.jpg'}
                    }
                    
                    mock_post.return_value = Mock()
                    
                    # Create lambda event for image
                    event = {
                        'body': json.dumps({
                            'message': {
                                'message_id': 789,
                                'chat': {'id': 456},
                                'photo': [{'file_id': 'test_file_id'}]
                            }
                        })
                    }
                    
                    # Process the event
                    result = await process_update(
                        json.loads(event['body']), 
                        mock_telegram_token, 
                        mock_openai_api_key
                    )
                    
                    # Verify response
                    assert result['statusCode'] == 200
                    assert result['body'] == "Description sent"
                    
                    # Verify Telegram APIs were called
                    assert mock_get.call_count == 1  # getFile
                    assert mock_post.call_count == 1  # sendMessage
                    
                    # Verify sendMessage payload
                    send_call_args = mock_post.call_args
                    payload = send_call_args[1]['json']
                    
                    assert payload['chat_id'] == 456
                    assert "Ecco la descrizione dell'immagine:" in payload['text']
                    assert sample_regular_image_response in payload['text']
                    assert payload['reply_to_message_id'] == 789

    def test_lambda_handler_complete_flow(self, mock_telegram_token, mock_openai_api_key):
        """Test complete lambda handler flow from event to response"""
        
        with patch('src.handlers.lambda_handler.get_ssm_parameter') as mock_ssm:
            with patch('asyncio.run') as mock_asyncio_run:
                mock_ssm.side_effect = lambda param: {
                    "/image-descriptor/telegram-token": mock_telegram_token,
                    "/image-descriptor/openai-api-key": mock_openai_api_key
                }[param]
                
                mock_asyncio_run.return_value = {"statusCode": 200, "body": "Success"}
                
                # Create lambda event
                event = {
                    'body': json.dumps({'message': {'text': '/start', 'chat': {'id': 123}}})
                }
                context = {}
                
                # Call lambda handler
                from src.handlers.lambda_handler import lambda_handler
                result = lambda_handler(event, context)
                
                # Verify flow
                assert result['statusCode'] == 200
                mock_asyncio_run.assert_called_once()

class TestBotResilience:
    """Test bot resilience and error recovery"""

    @pytest.mark.asyncio
    async def test_bot_handles_multiple_rapid_requests(self, mock_telegram_token, mock_openai_api_key,
                                                     sample_regular_image_response):
        """Test bot can handle multiple rapid image requests"""
        
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            with patch('telegram.ext.Application.builder') as mock_builder:
                # Setup mocks
                mock_client = Mock()
                mock_openai.return_value = mock_client
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = sample_regular_image_response
                mock_client.chat.completions.create.return_value = mock_response
                
                mock_app = Mock()
                mock_builder.return_value.token.return_value.build.return_value = mock_app
                
                # Create bot
                vision_service = OpenAIVisionService(mock_openai_api_key)
                bot = ImageDescriptionBot(mock_telegram_token, vision_service)
                
                # Create multiple updates
                updates = []
                contexts = []
                for i in range(5):
                    update = Mock()
                    update.effective_user = Mock()
                    update.message = Mock()
                    update.message.photo = [Mock()]
                    update.message.photo[-1].file_id = f"file_{i}"
                    update.message.message_id = i
                    update.message.chat.send_action = AsyncMock()
                    update.message.reply_text = AsyncMock()
                    
                    context = Mock()
                    mock_file = Mock()
                    mock_file.file_path = f"photos/test_{i}.jpg"
                    context.bot.get_file = AsyncMock(return_value=mock_file)
                    
                    updates.append(update)
                    contexts.append(context)
                
                # Process all updates concurrently
                tasks = [bot.handle_image(update, context) 
                        for update, context in zip(updates, contexts)]
                await asyncio.gather(*tasks)
                
                # Verify all were processed
                assert mock_client.chat.completions.create.call_count == 5
                for update in updates:
                    update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_bot_graceful_degradation_on_partial_failures(self, mock_telegram_token, 
                                                              mock_openai_api_key):
        """Test bot continues working even if some requests fail"""
        
        with patch('src.services.vision_service.OpenAI') as mock_openai:
            with patch('telegram.ext.Application.builder') as mock_builder:
                # Setup mocks - some calls succeed, some fail
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                def side_effect(*args, **kwargs):
                    # Simulate intermittent failures
                    if 'fail' in kwargs.get('messages', [{}])[0].get('content', [{}])[1].get('image_url', {}).get('url', ''):
                        raise Exception("OpenAI API Error")
                    else:
                        mock_response = Mock()
                        mock_response.choices = [Mock()]
                        mock_response.choices[0].message.content = "Success response"
                        return mock_response
                
                mock_client.chat.completions.create.side_effect = side_effect
                
                mock_app = Mock()
                mock_builder.return_value.token.return_value.build.return_value = mock_app
                
                # Create bot
                vision_service = OpenAIVisionService(mock_openai_api_key)
                bot = ImageDescriptionBot(mock_telegram_token, vision_service)
                
                # Create updates - some will fail, some succeed
                updates_and_contexts = []
                for i, should_fail in enumerate([False, True, False, True, False]):
                    update = Mock()
                    update.effective_user = Mock()
                    update.message = Mock()
                    update.message.photo = [Mock()]
                    update.message.photo[-1].file_id = f"file_{i}"
                    update.message.message_id = i
                    update.message.chat.send_action = AsyncMock()
                    update.message.reply_text = AsyncMock()
                    
                    context = Mock()
                    mock_file = Mock()
                    fail_suffix = "_fail" if should_fail else ""
                    mock_file.file_path = f"photos/test_{i}{fail_suffix}.jpg"
                    context.bot.get_file = AsyncMock(return_value=mock_file)
                    
                    updates_and_contexts.append((update, context, should_fail))
                
                # Process all updates
                for update, context, should_fail in updates_and_contexts:
                    await bot.handle_image(update, context)
                    
                    # All should get responses (success or error message)
                    update.message.reply_text.assert_called_once()
                    
                    call_args = update.message.reply_text.call_args
                    response_text = call_args[0][0]
                    
                    if should_fail:
                        # Should get error message in Italian
                        assert "Mi dispiace" in response_text
                    else:
                        # Should get success response
                        assert "Ecco la descrizione dell'immagine:" in response_text
                        assert "Success response" in response_text 
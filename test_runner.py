#!/usr/bin/env python3
"""
Simple test runner for Image Descriptor Bot that bypasses pytest configuration issues
"""
import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class TestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def run_test(self, test_func, test_name):
        """Run a single test function"""
        try:
            print(f"🧪 Running: {test_name}")
            test_func()
            print(f"✅ PASSED: {test_name}")
            self.tests_passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {str(e)}")
            self.tests_failed += 1
            self.failures.append((test_name, str(e)))

    def run_async_test(self, test_func, test_name):
        """Run an async test function"""
        try:
            print(f"🧪 Running: {test_name}")
            asyncio.run(test_func())
            print(f"✅ PASSED: {test_name}")
            self.tests_passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {str(e)}")
            self.tests_failed += 1
            self.failures.append((test_name, str(e)))

    def run_test_method(self, test_class, method_name, test_name, **fixtures):
        """Run a test method from a test class"""
        try:
            print(f"🧪 Running: {test_name}")
            instance = test_class()
            method = getattr(instance, method_name)
            
            # Get method signature to filter fixtures
            import inspect
            sig = inspect.signature(method)
            
            # Filter fixtures to only include those expected by the method
            filtered_fixtures = {}
            for param_name in sig.parameters:
                if param_name != 'self' and param_name in fixtures:
                    filtered_fixtures[param_name] = fixtures[param_name]
            
            # Check if it's an async method
            if asyncio.iscoroutinefunction(method):
                asyncio.run(method(**filtered_fixtures))
            else:
                method(**filtered_fixtures)
                
            print(f"✅ PASSED: {test_name}")
            self.tests_passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {str(e)}")
            self.tests_failed += 1
            self.failures.append((test_name, str(e)))

    def print_summary(self):
        """Print test summary"""
        total = self.tests_passed + self.tests_failed
        print("\n" + "="*50)
        print(f"📊 Test Summary: {self.tests_passed}/{total} passed")
        
        if self.tests_failed > 0:
            print(f"\n❌ Failed tests:")
            for name, error in self.failures:
                print(f"  - {name}: {error}")
        else:
            print("🎉 All tests passed!")

# Fixtures for tests
def get_mock_fixtures():
    """Get mock fixtures for tests"""
    return {
        'mock_openai_api_key': 'test_openai_key',
        'mock_telegram_token': 'test_telegram_token',
        'sample_regular_image_response': 'Questa è una descrizione di un\'immagine regolare.',
        'sample_event_image_response': '''Questa è un'immagine di un evento musicale.

🎫 **INFORMAZIONI EVENTO**
**Nome:** Festival Jazz Estivo 2024
**Date:** 15-17 Luglio 2024
**Luogo:** Parco della Musica
**Prezzo:** €25-€60'''
    }

# Basic standalone tests (from original simple runner)
def test_vision_service_abstract():
    """Test VisionService is abstract"""
    from src.services.vision_service import VisionService
    try:
        VisionService()
        raise AssertionError("VisionService should not be instantiable")
    except TypeError:
        pass  # Expected

def test_openai_service_init():
    """Test OpenAI service initialization"""
    from src.services.vision_service import OpenAIVisionService
    
    with patch('src.services.vision_service.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        service = OpenAIVisionService("test_key")
        
        assert service.client == mock_client
        mock_openai.assert_called_once_with(api_key="test_key")

async def test_vision_service_describe_image():
    """Test vision service describe image functionality"""
    from src.services.vision_service import OpenAIVisionService
    
    with patch('src.services.vision_service.OpenAI') as mock_openai:
        # Setup mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Descrizione italiana dell'immagine"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        service = OpenAIVisionService("test_key")
        result = await service.describe_image("https://example.com/image.jpg")
        
        # Verify
        assert result == "Descrizione italiana dell'immagine"
        mock_client.chat.completions.create.assert_called_once()
        
        # Check API call parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'gpt-4o'
        assert call_args[1]['max_tokens'] == 500
        
        # Check Italian and event detection in prompt
        messages = call_args[1]['messages']
        text_content = messages[0]['content'][0]['text']
        assert 'italiano' in text_content
        assert 'INFORMAZIONI EVENTO' in text_content

def test_bot_initialization():
    """Test bot initialization"""
    from src.bot.telegram_bot import ImageDescriptionBot
    from src.services.vision_service import VisionService
    
    mock_vision_service = Mock(spec=VisionService)
    
    with patch('telegram.ext.Application.builder') as mock_builder:
        mock_app = Mock()
        mock_builder.return_value.token.return_value.build.return_value = mock_app
        
        bot = ImageDescriptionBot("test_token", mock_vision_service)
        
        assert bot.token == "test_token"
        assert bot.vision_service == mock_vision_service
        assert bot.application == mock_app

async def test_bot_start_command():
    """Test bot start command"""
    from src.bot.telegram_bot import ImageDescriptionBot
    from src.services.vision_service import VisionService
    
    mock_vision_service = Mock(spec=VisionService)
    
    with patch('telegram.ext.Application.builder') as mock_builder:
        mock_app = Mock()
        mock_builder.return_value.token.return_value.build.return_value = mock_app
        
        bot = ImageDescriptionBot("test_token", mock_vision_service)
        
        # Create fully mocked update and context
        update = Mock()
        update.effective_user = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        
        context = Mock()
        
        # Test
        await bot.start_command(update, context)
        
        # Verify Italian welcome message
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Ciao!" in call_args
        assert "Image Descriptor Bot" in call_args

def test_imports():
    """Test that all modules can be imported"""
    from src.services.vision_service import OpenAIVisionService, VisionService
    from src.bot.telegram_bot import ImageDescriptionBot
    from src.handlers.lambda_handler import lambda_handler, process_update
    
    # All should import without error
    assert OpenAIVisionService is not None
    assert VisionService is not None
    assert ImageDescriptionBot is not None
    assert lambda_handler is not None
    assert process_update is not None

def run_unit_tests(runner):
    """Run unit tests from test_unit.py"""
    print("\n🔬 UNIT TESTS")
    print("-" * 30)
    
    try:
        # Import test classes from test_unit.py
        from tests.test_unit import TestBasicFunctionality
        
        test_class = TestBasicFunctionality()
        
        # Run each test method
        runner.run_test(test_class.test_vision_service_is_abstract, "test_unit: vision_service_is_abstract")
        runner.run_test(test_class.test_basic_imports, "test_unit: basic_imports")
        runner.run_test(test_class.test_openai_vision_service_init, "test_unit: openai_vision_service_init")
        runner.run_test(test_class.test_telegram_bot_init, "test_unit: telegram_bot_init")
        runner.run_test(test_class.test_vision_service_describe_image_sync_wrapper, "test_unit: vision_service_describe_image")
        runner.run_test(test_class.test_telegram_bot_start_command_sync_wrapper, "test_unit: telegram_bot_start_command")
        
    except ImportError as e:
        print(f"⚠️  Could not import test_unit.py tests: {e}")

def run_e2e_tests(runner):
    """Run end-to-end tests from test_e2e.py"""
    print("\n🌐 END-TO-END TESTS")
    print("-" * 30)
    
    try:
        # Import test classes from test_e2e.py
        from tests.test_e2e import TestEndToEndBot, TestLambdaHandlerE2E, TestBotResilience
        
        fixtures = get_mock_fixtures()
        
        # Run TestEndToEndBot tests
        runner.run_test_method(TestEndToEndBot, 'test_complete_image_processing_flow_regular', 
                             "test_e2e: complete_image_processing_flow_regular", **fixtures)
        runner.run_test_method(TestEndToEndBot, 'test_complete_image_processing_flow_event',
                             "test_e2e: complete_image_processing_flow_event", **fixtures)
        
        # Run TestLambdaHandlerE2E tests
        runner.run_test_method(TestLambdaHandlerE2E, 'test_lambda_handler_start_command',
                             "test_e2e: lambda_handler_start_command", **fixtures)
        runner.run_test_method(TestLambdaHandlerE2E, 'test_lambda_handler_image_processing',
                             "test_e2e: lambda_handler_image_processing", **fixtures)
        runner.run_test_method(TestLambdaHandlerE2E, 'test_lambda_handler_complete_flow',
                             "test_e2e: lambda_handler_complete_flow", **fixtures)
        
        # Run TestBotResilience tests
        runner.run_test_method(TestBotResilience, 'test_bot_handles_multiple_rapid_requests',
                             "test_e2e: bot_handles_multiple_rapid_requests", **fixtures)
        runner.run_test_method(TestBotResilience, 'test_bot_graceful_degradation_on_partial_failures',
                             "test_e2e: bot_graceful_degradation_on_partial_failures", **fixtures)
        
    except ImportError as e:
        print(f"⚠️  Could not import test_e2e.py tests: {e}")

def main(test_type="all"):
    """Main test runner"""
    print("🤖 Image Descriptor Bot - Simple Test Runner")
    print("=" * 50)
    
    runner = TestRunner()
    
    if test_type in ["all", "unit"]:
        # Run original standalone tests
        print("\n⚡ STANDALONE TESTS")
        print("-" * 30)
        runner.run_test(test_vision_service_abstract, "VisionService Abstract")
        runner.run_test(test_openai_service_init, "OpenAI Service Init")
        runner.run_test(test_bot_initialization, "Bot Initialization")
        runner.run_test(test_imports, "Module Imports")
        runner.run_async_test(test_vision_service_describe_image, "Vision Service Describe Image")
        runner.run_async_test(test_bot_start_command, "Bot Start Command")
        
        # Run unit tests from test_unit.py
        run_unit_tests(runner)
    
    if test_type in ["all", "e2e", "integration"]:
        # Run E2E tests from test_e2e.py
        run_e2e_tests(runner)
    
    runner.print_summary()
    
    # Return appropriate exit code
    return 0 if runner.tests_failed == 0 else 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Image Descriptor Bot tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "e2e", "integration", "all"], 
        default="all",
        help="Type of tests to run"
    )
    
    args = parser.parse_args()
    exit_code = main(args.type)
    sys.exit(exit_code) 
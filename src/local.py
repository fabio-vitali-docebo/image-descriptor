import os
from dotenv import load_dotenv
from src.bot.telegram_bot import ImageDescriptionBot
from src.services.vision_service import OpenAIVisionService

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not telegram_token or not openai_api_key:
        raise ValueError(
            "Please set TELEGRAM_TOKEN and OPENAI_API_KEY environment variables"
        )
    
    # Initialize services
    vision_service = OpenAIVisionService(openai_api_key)
    bot = ImageDescriptionBot(telegram_token, vision_service)
    
    # Start the bot
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        await bot.stop()
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 
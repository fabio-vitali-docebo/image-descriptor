import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from telegram.error import NetworkError, TimedOut
from src.services.vision_service import VisionService

class ImageDescriptionBot:
    def __init__(self, token: str, vision_service: VisionService):
        """Initialize the bot with token and vision service."""
        self.token = token
        self.vision_service = vision_service
        self.application = Application.builder().token(token).build()

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors."""
        if isinstance(context.error, NetworkError):
            print("Network error occurred")
        elif isinstance(context.error, TimedOut):
            print("Request timed out")
        else:
            print(f"Exception while handling an update: {context.error}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        if update.effective_user:
            await update.message.reply_text(
                "Ciao! Sono Image Descriptor Bot. Inviami un'immagine e ti fornirò una descrizione dettagliata!"
            )

    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming images."""
        try:
            if not update.effective_user:
                return
                
            if not update.message or not update.message.photo:
                return
            
            # Get the photo with the highest resolution
            photo = update.message.photo[-1]
            
            # Send typing action
            await update.message.chat.send_action('typing')
            
            # Get the file from Telegram
            file = await context.bot.get_file(photo.file_id)
            
            # Get the file URL
            file_url = file.file_path
            
            # Get image description from vision service
            description = await self.vision_service.describe_image(file_url)
            
            # Format the response with Italian intro sentence
            response_text = f"Ecco la descrizione dell'immagine:\n\n{description}"
            
            # Reply to the original message with the description (this creates a citation)
            await update.message.reply_text(response_text, reply_to_message_id=update.message.message_id)
            
        except Exception as e:
            if update.message:
                await update.message.reply_text(
                    "Mi dispiace, non sono riuscito a elaborare questa immagine. Riprova più tardi.",
                    reply_to_message_id=update.message.message_id
                )

    def setup_handlers(self) -> None:
        """Set up message handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(
            MessageHandler(filters.PHOTO, self.handle_image)
        )
        self.application.add_error_handler(self.error_handler)

    def start(self) -> None:
        """Start the bot."""
        print("Starting Image Descriptor Bot...")
        self.setup_handlers()
        print("Image Descriptor Bot started, polling for updates...")
        
        try:
            # Use run_polling() which manages its own event loop
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
                pool_timeout=30
            )
        except Exception as e:
            print(f"Error in polling: {e}")
            raise

    async def stop(self) -> None:
        """Stop the bot."""
        print("Stopping Image Descriptor Bot...")
        await self.application.stop()
        print("Image Descriptor Bot stopped") 
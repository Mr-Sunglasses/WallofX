"""Telegram bot handler for wallofx."""
import re
import os
import logging
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from ..twitter.extractor import TweetExtractor
from ..image.generator import ImageGenerator

logger = logging.getLogger(__name__)


class WallOfXBot:
    """Main bot class for handling Telegram interactions."""

    def __init__(self):
        """Initialize the bot with required dependencies."""
        self.extractor = TweetExtractor()
        self.image_generator = ImageGenerator()
        self.tweet_url_pattern = re.compile(
            r'https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+/status/\d+'
        )
        logger.info("WallOfXBot initialized")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        welcome_message = (
            "Welcome to WallOfX!\n\n"
            "Turn any tweet into a beautiful, high-quality image ready for sharing or printing.\n\n"
            "Just send me a tweet URL and I'll do the rest.\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/help - How to use this bot"
        )
        await update.message.reply_text(welcome_message)
        logger.info(f"User {update.effective_user.id} sent /start")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        help_message = (
            "How to use WallOfX:\n\n"
            "1. Find a tweet on Twitter/X\n"
            "2. Copy the tweet URL\n"
            "3. Paste and send it here\n"
            "4. Get your image!\n\n"
            "Supported URLs:\n"
            "twitter.com/user/status/...\n"
            "x.com/user/status/...\n\n"
            "The images are high resolution (300 DPI) - perfect for printing or sharing."
        )
        await update.message.reply_text(help_message)
        logger.info(f"User {update.effective_user.id} sent /help")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming messages and extract tweet URLs."""
        if not update.message or not update.message.text:
            return

        text = update.message.text
        logger.info(f"Received message from user {update.effective_user.id}: {text[:100]}")

        urls = self.tweet_url_pattern.findall(text)

        if not urls:
            await update.message.reply_text(
                "Please send a valid tweet URL.\n"
                "Example: https://x.com/user/status/123456"
            )
            logger.warning(f"No tweet URL found in message: {text[:100]}")
            return

        # Process the first valid URL
        tweet_url = urls[0]
        logger.info(f"Found tweet URL: {tweet_url}")
        await self.process_tweet(update, tweet_url)

    async def process_tweet(self, update: Update, tweet_url: str) -> None:
        """Process a tweet and generate an image."""
        status_message = await update.message.reply_text("Fetching tweet...")
        logger.info(f"Processing tweet: {tweet_url}")

        try:
            # Extract tweet data
            logger.info("Calling TweetExtractor...")
            tweet_data = await self.extractor.extract(tweet_url)
            if not tweet_data:
                await status_message.edit_text("Could not fetch this tweet. Please check the URL and try again.")
                logger.error(f"Failed to extract tweet data from: {tweet_url}")
                return

            logger.info(f"Tweet data extracted: author={tweet_data.author_name}, text_length={len(tweet_data.text)}")

            await status_message.edit_text("Creating image...")

            # Generate image
            logger.info("Calling ImageGenerator...")
            image_path = await self.image_generator.generate(tweet_data)
            logger.info(f"Image generated at: {image_path}")

            # Delete status message
            await status_message.delete()

            # Send the generated image
            caption_text = tweet_data.text[:150]
            if len(tweet_data.text) > 150:
                caption_text += "..."
            
            with open(image_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"@{tweet_data.author_username.lstrip('@')}: {caption_text}"
                )
            logger.info(f"Image sent successfully to user {update.effective_user.id}")

        except Exception as e:
            logger.exception(f"Error processing tweet: {e}")
            await status_message.edit_text("Something went wrong. Please try again later.")

    def run(self):
        """Start the bot."""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        application = Application.builder().token(token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info("Starting bot polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

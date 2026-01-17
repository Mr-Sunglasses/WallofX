#!/usr/bin/env python3
"""Main entry point for WallOfX Telegram bot."""
import os
import sys
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('wallofx.log')
    ]
)

from wallofx.src.bot import WallOfXBot


def main():
    """Start the WallOfX bot."""
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        print("Please create a .env file with your bot token.")
        sys.exit(1)

    logging.info("🎨 Starting WallOfX bot...")
    print("🎨 Starting WallOfX bot...")
    print("Send /start to your bot to begin!")

    bot = WallOfXBot()
    bot.run()


if __name__ == '__main__':
    main()

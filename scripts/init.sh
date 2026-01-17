#!/bin/bash
set -e

echo "🎨 Initializing WallOfX..."

# Check if .env already exists
if [ -f .env ]; then
    read -p ".env file already exists. Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Copy .env.example to .env
cp .env.example .env

echo "✅ Created .env file"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env and add your TELEGRAM_BOT_TOKEN"
echo "2. Get your token from @BotFather on Telegram"
echo "3. Run: uv sync"
echo "4. Run: uv run run.py"
echo ""
echo "To get a bot token:"
echo "  1. Open Telegram and search for @BotFather"
echo "  2. Send /newbot and follow the instructions"
echo "  3. Copy the token and paste it in .env"

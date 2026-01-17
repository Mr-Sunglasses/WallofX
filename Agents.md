# WallOfX

A Telegram bot that converts tweets into beautiful, printable images.

## Overview

WallOfX is a Telegram bot that extracts tweet data and generates high-resolution, print-ready images. Users simply send a tweet URL to the bot, and it creates a beautifully formatted image that can be printed and displayed.

## Features

- **Tweet Extraction**: Uses the [FixTweet/FixupX API](https://fxtwitter.com) to extract tweet data without requiring API keys
- **Beautiful Image Generation**: Creates high-resolution (300 DPI) images with:
  - Circular avatar with author info
  - Verified badge
  - Formatted tweet text (mentions, hashtags, URLs highlighted in blue)
  - Image attachments (single, side-by-side, or 2x2 grid)
  - Metrics (retweets, likes)
  - "Posted on X" branding
- **Multiple Themes**: Dark, dim, and light color schemes
- **Text Format Preservation**: Maintains original tweet line breaks and formatting

## Architecture

```
wallofx/
├── wallofx/
│   ├── src/
│   │   ├── bot/
│   │   │   └── handler.py      # Telegram bot handler
│   │   ├── twitter/
│   │   │   └── extractor.py    # Tweet data extractor
│   │   └── image/
│   │       └── generator.py    # Image generator
│   └── static/
│       └── output/             # Generated images
├── run.py                      # Entry point
├── pyproject.toml              # UV project config
├── Dockerfile                  # Docker container
├── docker-compose.yml          # Docker Compose config
└── Makefile                    # Build/run commands
```

## Components

### Bot Handler (`src/bot/handler.py`)
- Handles Telegram bot interactions
- Processes incoming messages for tweet URLs
- Coordinates tweet extraction and image generation
- Sends generated images back to users

### Tweet Extractor (`src/twitter/extractor.py`)
- Uses FixTweet API to extract tweet data
- Returns structured `TweetData` with:
  - Author info (name, username, avatar)
  - Tweet text and creation date
  - Images
  - Metrics (replies, retweets, likes, views)

### Image Generator (`src/image/generator.py`)
- Generates 2000×2400px images at 300 DPI
- Supports dark, dim, and light themes
- Renders formatted text with colored entities
- Draws custom icons (verified badge, retweet, like, X logo)

## Usage

### Running Locally

```bash
# Install dependencies with UV
uv sync

# Set up environment
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN

# Run the bot
make run
# or
python run.py
```

### Running with Docker

```bash
# Build and run with Docker Compose
make run-docker

# View logs
make logs-docker

# Stop
make stop-docker
```

### Bot Commands

- `/start` - Welcome message
- `/help` - Help information
- Send a tweet URL to generate an image

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from [@BotFather](https://t.me/botfather) |

## Dependencies

- `python-telegram-bot` - Telegram Bot API wrapper
- `Pillow` - Image generation
- `aiohttp` - Async HTTP client
- `python-dotenv` - Environment variable management

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make init` | Initialize .env file |
| `make install` | Install dependencies |
| `make run` | Run the bot locally |
| `make run-docker` | Run with Docker |
| `make stop-docker` | Stop Docker containers |
| `make logs-docker` | View Docker logs |

## API Used

**FixTweet API** (`https://api.fxtwitter.com`)
- Free to use
- No authentication required
- Returns tweet data in JSON format

## License

MIT

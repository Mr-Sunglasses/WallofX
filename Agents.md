# WallOfX

A Telegram bot that converts tweets into beautiful, high-quality images.

## Overview

WallOfX is a Telegram bot that extracts tweet data and generates print-ready images. Users send a tweet URL to the bot, and it creates a beautifully formatted image that matches Twitter/X's native card design.

## Features

- **Tweet Extraction**: Uses the [FixTweet/FxTwitter API](https://github.com/FixTweet/FxTwitter) to extract tweet data without requiring Twitter API keys
- **High-Quality Image Generation**: Creates 1200×1600px images at 300 DPI with:
  - Circular profile avatar
  - Verified badge (blue checkmark)
  - Author name and @username
  - Tweet text with proper line breaks preserved
  - Colored entities (mentions, hashtags, URLs in Twitter blue)
  - Image attachments (single, 2-up, or 2×2 grid layouts)
  - Engagement metrics (replies, reposts, likes)
  - Date and view count
- **Multiple Themes**: Dark (default), dim, and light color schemes
- **Text Format Preservation**: Maintains original tweet formatting and line breaks

## Architecture

```
wallofx/
├── wallofx/
│   ├── src/
│   │   ├── bot/
│   │   │   └── handler.py      # Telegram bot - handles commands and messages
│   │   ├── twitter/
│   │   │   └── extractor.py    # Tweet data extraction via FxTwitter API
│   │   └── image/
│   │       └── generator.py    # PIL-based image generation
│   └── static/
│       └── output/             # Generated images (temporary storage)
├── run.py                      # Application entry point
├── pyproject.toml              # UV/pip project configuration
├── Dockerfile                  # Container build configuration
├── docker-compose.yml          # Container orchestration
├── Makefile                    # Development commands
└── Agents.md                   # This file - project context for AI agents
```

## Components

### Bot Handler (`wallofx/src/bot/handler.py`)

The Telegram bot interface. Responsibilities:
- `/start` command - Welcome message and basic info
- `/help` command - Usage instructions
- Message handling - Detects tweet URLs in messages
- Orchestrates the extract → generate → send pipeline
- Error handling - Logs errors internally, shows friendly messages to users

Key patterns:
- Uses `python-telegram-bot` async API
- URL detection via regex for twitter.com and x.com domains
- Status messages updated during processing, then deleted on success

### Tweet Extractor (`wallofx/src/twitter/extractor.py`)

Extracts tweet data using the FxTwitter API. Responsibilities:
- Parse tweet ID from various URL formats
- Call FxTwitter API (`https://api.fxtwitter.com/status/{id}`)
- Parse response into `TweetData` dataclass
- Preserve original text formatting (line breaks)

`TweetData` fields:
- `url`, `author_name`, `author_username`, `author_avatar`
- `text`, `created_at`, `images` (list of URLs)
- `likes`, `retweets`, `replies`, `views`

### Image Generator (`wallofx/src/image/generator.py`)

Generates tweet card images using PIL/Pillow. Responsibilities:
- Render tweet in Twitter-like card format
- Support multiple color themes
- Handle text wrapping and entity coloring
- Process and layout attached images
- Output high-resolution PNG at 300 DPI

Key implementation details:
- Uses 2× scale factor for crisp output (1200×1600 canvas)
- Font loading with fallbacks for different OS environments
- Circular avatar masking
- Verified badge drawn as blue circle with white checkmark
- Dynamic height - crops to content
- Image grid layouts for 1, 2, 3, or 4 images

## Development

### Prerequisites
- Python 3.11+
- UV package manager (recommended) or pip
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Local Development

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Add TELEGRAM_BOT_TOKEN to .env

# Run the bot
make run
# or: python run.py
```

### Docker Deployment

```bash
# Build and start
make run-docker

# View logs
make logs-docker

# Stop
make stop-docker
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |

## API Reference

### FxTwitter API

**Endpoint**: `GET https://api.fxtwitter.com/status/{tweet_id}`

**Response** (simplified):
```json
{
  "code": 200,
  "message": "OK",
  "tweet": {
    "id": "123456789",
    "text": "Tweet content...",
    "author": {
      "name": "Display Name",
      "screen_name": "username",
      "avatar_url": "https://..."
    },
    "created_at": "Thu Oct 13 20:47:08 +0000 2022",
    "likes": 100,
    "retweets": 50,
    "replies": 10,
    "views": 1000,
    "media": {
      "photos": [{"url": "https://..."}]
    }
  }
}
```

## Design Decisions

1. **FxTwitter over Twitter API**: No authentication required, free, reliable
2. **PIL over other image libs**: Widely available, sufficient for this use case
3. **Async throughout**: Bot and HTTP calls are async for better concurrency
4. **2× scale rendering**: Ensures crisp images on high-DPI displays
5. **No error details to users**: Security best practice, errors logged server-side
6. **Dynamic image height**: Crops to content rather than fixed dimensions

## Troubleshooting

**Bot not responding**
- Check `TELEGRAM_BOT_TOKEN` is set correctly
- Verify bot is running (check logs)

**Tweet extraction fails**
- Tweet may be from a private/suspended account
- FxTwitter API may be temporarily unavailable

**Image quality issues**
- Ensure fonts are installed (DejaVu Sans on Linux)
- Check source images are accessible

**Font not found**
- Install DejaVu fonts: `apt install fonts-dejavu` (Debian/Ubuntu)
- On macOS, falls back to Helvetica

## License

MIT

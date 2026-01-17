# WallOfX

A Telegram bot that transforms tweets into beautiful, high-resolution images perfect for printing and framing.

## Features

- Extract tweets from Twitter/X URLs using [FixTweet API](https://docs.fxtwitter.com/)
- Generate beautiful print-worthy images (300 DPI)
- Multiple color themes (dark, light, sepia, midnight)
- Handle tweets with images
- Display engagement metrics
- No API keys required - uses free FixTweet service

## Project Structure

```
wallofx/
├── run.py                          # Main entry point
├── pyproject.toml                  # UV project configuration
├── Dockerfile                      # Docker image
├── docker-compose.yml              # Docker compose config
├── Makefile                        # Make commands
├── .env.example                    # Environment variables template
├── wallofx/
│   ├── __init__.py
│   └── src/
│       ├── bot/
│       │   ├── __init__.py
│       │   └── handler.py          # Telegram bot handler
│       ├── twitter/
│       │   ├── __init__.py
│       │   └── extractor.py        # Tweet data extraction (FixTweet API)
│       └── image/
│           ├── __init__.py
│           └── generator.py        # Image generation
└── static/
    ├── fonts/                      # Custom fonts (optional)
    ├── templates/                  # Image templates (optional)
    └── output/                     # Generated images
```

## Quick Start (Local)

### Prerequisites

- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Setup

```bash
# Initialize .env file
make init

# Install dependencies
make install

# Run the bot
make run
```

## Quick Start (Docker)

```bash
# Initialize .env file
make init

# Build and run with Docker
make run-docker

# View logs
make logs-docker
```

## Available Commands

```bash
make help              # Show all available commands
make init              # Initialize .env file
make install           # Install dependencies
make run               # Run locally with uv
make build-docker      # Build Docker image
make run-docker        # Run with Docker
make stop-docker       # Stop Docker containers
make restart-docker    # Restart Docker containers
make logs-docker       # View Docker logs
make clean             # Clean generated files
```

## Manual Setup

### 1. Get a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your bot token:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. Install System Dependencies (Optional)

For better font rendering, install DejaVu fonts:

```bash
# Debian/Ubuntu
sudo apt-get install fonts-dejavu-core

# Fedora/RHEL
sudo dnf install dejavu-sans-fonts
```

### 4. Run the Bot

**With uv:**
```bash
uv sync
uv run run.py
```

**With Docker:**
```bash
docker-compose up -d
```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to see the welcome message
3. Paste any tweet URL (e.g., `https://x.com/user/status/123456789`)
4. Receive a beautiful image ready for printing!

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Help information |

## How It Works

WallOfX uses the [FixTweet API](https://docs.fxtwitter.com/) to fetch tweet data without requiring Twitter API credentials. This means:

- No API keys needed
- No rate limits (within reason)
- Works with public tweets only
- Free to use

## Customization

### Themes

You can customize the color theme by editing `wallofx/src/image/generator.py`:

```python
THEMES = {
    'dark': {...},
    'light': {...},
    'sepia': {...},
    'midnight': {...},
}
```

### Image Quality

Images are generated at 300 DPI for printing. To adjust:

```python
width = 2400  # Image width in pixels
```

## Output

Generated images are saved in `wallofx/static/output/` with the format:
```
tweet_YYYYMMDD_HHMMSS_theme.png
```

## License

MIT

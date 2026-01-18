"""Tweet extractor using FixTweet/FixupX API."""
import re
import logging
from dataclasses import dataclass
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class TweetData:
    """Data class for tweet information."""

    url: str
    author_name: str
    author_username: str
    author_avatar: Optional[str]
    text: str
    created_at: str
    images: list[str]
    likes: int
    retweets: int
    replies: int
    views: Optional[int]


class TweetExtractor:
    """Extract tweet data using FixTweet/FixupX API."""

    # FixTweet API endpoint
    API_BASE = "https://api.fxtwitter.com"

    def __init__(self):
        """Initialize the extractor."""
        self.user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
        logger.info("TweetExtractor initialized")

    def _extract_tweet_id(self, url: str) -> Optional[str]:
        """Extract tweet ID from URL."""
        match = re.search(r'/status/(\d+)', url)
        return match.group(1) if match else None

    def _clean_text(self, text: str) -> str:
        """Clean tweet text while preserving line breaks."""
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Clean each line individually, preserving line breaks
        lines = text.split('\n')
        cleaned_lines = [' '.join(line.split()) for line in lines]
        return '\n'.join(cleaned_lines)

    def _format_date(self, date_str: str) -> str:
        """Format date from FixTweet API response."""
        # FixTweet returns format: "Thu Oct 13 20:47:08 +0000 2022"
        # Keep it as is for display
        return date_str

    async def extract(self, url: str) -> Optional[TweetData]:
        """Extract tweet data using FixTweet API.

        Args:
            url: Tweet URL (e.g., https://x.com/user/status/123456789)

        Returns:
            TweetData object or None if extraction fails
        """
        logger.info(f"Extracting tweet from URL: {url}")

        tweet_id = self._extract_tweet_id(url)
        if not tweet_id:
            logger.error(f"Could not extract tweet ID from URL: {url}")
            return None

        logger.info(f"Extracted tweet ID: {tweet_id}")

        # Use FixTweet API - no auth required, free to use
        api_url = f"{self.API_BASE}/status/{tweet_id}"
        logger.info(f"Calling FixTweet API: {api_url}")

        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    logger.info(f"FixTweet API responded with status: {response.status}")

                    if response.status != 200:
                        logger.error(f"FixTweet API returned non-200 status: {response.status}")
                        return None

                    data = await response.json()
                    logger.debug(f"FixTweet API response: {data}")
                    return self._parse_fxtweet_response(data, url)

        except Exception as e:
            logger.exception(f"Error calling FixTweet API: {e}")
            return None

    def _parse_fxtweet_response(self, data: dict, original_url: str) -> Optional[TweetData]:
        """Parse FixTweet API response into TweetData.

        Response format:
        {
            "code": 200,
            "message": "OK",
            "tweet": {
                "url": "https://twitter.com/...",
                "id": "...",
                "text": "...",
                "author": {
                    "name": "...",
                    "screen_name": "...",
                    "avatar_url": "..."
                },
                "created_at": "...",
                "likes": 0,
                "retweets": 0,
                "replies": 0,
                "views": 0,
                "media": {
                    "photos": [...],
                    "videos": [...]
                }
            }
        }
        """
        logger.debug(f"Parsing FixTweet response, code={data.get('code')}, message={data.get('message')}")

        if data.get('code') != 200 or data.get('message') != 'OK':
            logger.error(f"FixTweet API returned error: code={data.get('code')}, message={data.get('message')}")
            return None

        tweet = data.get('tweet', {})
        if not tweet:
            logger.error("FixTweet API response missing 'tweet' field")
            return None

        author = tweet.get('author', {})
        media = tweet.get('media', {})
        photos = media.get('photos', [])

        # Extract image URLs from photos
        images = [photo.get('url', '') for photo in photos if photo.get('url')]
        logger.info(f"Extracted {len(images)} images from tweet")

        tweet_data = TweetData(
            url=tweet.get('url', original_url),
            author_name=author.get('name', 'Unknown'),
            author_username=f"@{author.get('screen_name', 'unknown')}",
            author_avatar=author.get('avatar_url'),
            text=self._clean_text(tweet.get('text', '')),
            created_at=self._format_date(tweet.get('created_at', '')),
            images=images,
            likes=tweet.get('likes', 0),
            retweets=tweet.get('retweets', 0),
            replies=tweet.get('replies', 0),
            views=tweet.get('views'),
        )

        logger.info(f"Successfully parsed tweet data: author={tweet_data.author_name}, likes={tweet_data.likes}")
        return tweet_data

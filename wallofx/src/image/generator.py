"""Image generator for creating beautiful tweet images."""
import os
import re
import logging
from io import BytesIO
from datetime import datetime
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
import aiohttp

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generate beautiful images from tweet data."""

    # Color themes
    THEMES = {
        'dark': {
            'background': (0, 0, 0),
            'text': (231, 233, 234),
            'secondary_text': (113, 118, 123),
            'link': (29, 155, 240),
            'accent': (29, 155, 240),
            'divider': (56, 68, 77),
            'icon': (113, 118, 123),
        },
        'dim': {
            'background': (21, 24, 28),
            'text': (247, 249, 249),
            'secondary_text': (139, 152, 165),
            'link': (29, 155, 240),
            'accent': (29, 155, 240),
            'divider': (56, 68, 77),
            'icon': (139, 152, 165),
        },
        'light': {
            'background': (255, 255, 255),
            'text': (15, 20, 25),
            'secondary_text': (83, 100, 113),
            'link': (29, 155, 240),
            'accent': (29, 155, 240),
            'divider': (180, 185, 190),
            'icon': (83, 100, 113),
        },
    }

    def __init__(self, theme: str = 'dark'):
        """Initialize the image generator."""
        self.theme = self.THEMES.get(theme, self.THEMES['dark'])
        self.theme_name = theme
        self.output_dir = 'wallofx/static/output'
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"ImageGenerator initialized with theme '{theme}'")

    def _draw_x_logo(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
        """Draw an X logo."""
        color = self.theme['text']
        lw = max(3, size // 8)
        # Draw X
        draw.line([(x, y), (x + size, y + size)], fill=color, width=lw)
        draw.line([(x + size, y), (x, y + size)], fill=color, width=lw)

    def _draw_verified_badge(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
        """Draw a verified badge."""
        badge_color = (29, 155, 240)
        draw.ellipse([(x, y), (x + size, y + size)], fill=badge_color)
        lw = max(2, size // 10)
        # Checkmark
        draw.line([(x + size * 0.25, y + size * 0.5), (x + size * 0.4, y + size * 0.7)],
                  fill=(255, 255, 255), width=lw)
        draw.line([(x + size * 0.4, y + size * 0.7), (x + size * 0.75, y + size * 0.3)],
                  fill=(255, 255, 255), width=lw)

    def _draw_retweet_icon(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
        """Draw retweet icon."""
        color = self.theme['icon']
        lw = max(2, size // 6)

        # Two arrows
        # Left arrow pointing up
        cx1, cy1 = x + size * 0.25, y + size * 0.2
        draw.polygon([(cx1, cy1), (cx1 - size*0.1, cy1 + size*0.15), (cx1 + size*0.1, cy1 + size*0.15)], fill=color)
        draw.line([(cx1, cy1 + size*0.15), (cx1, cy1 + size*0.6)], fill=color, width=lw)

        # Right arrow pointing down
        cx2, cy2 = x + size * 0.75, y + size * 0.8
        draw.polygon([(cx2, cy2), (cx2 - size*0.1, cy2 - size*0.15), (cx2 + size*0.1, cy2 - size*0.15)], fill=color)
        draw.line([(cx2, cy2 - size*0.15), (cx2, cy2 - size*0.6)], fill=color, width=lw)

    def _draw_like_icon(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
        """Draw like icon (heart)."""
        color = self.theme['icon']
        lw = max(2, size // 6)

        # Simple heart shape
        cx, cy = x + size / 2, y + size * 0.35

        # Draw heart using lines for simplicity
        # Left curve
        draw.arc([(x, y), (x + size * 0.5, y + size * 0.5)], start=0, end=180, fill=color, width=lw)
        # Right curve
        draw.arc([(x + size * 0.5, y), (x + size, y + size * 0.5)], start=0, end=180, fill=color, width=lw)
        # Bottom point
        tip_y = y + size
        draw.line([(x, y + size * 0.25), (cx, tip_y)], fill=color, width=lw)
        draw.line([(x + size, y + size * 0.25), (cx, tip_y)], fill=color, width=lw)

    async def generate(self, tweet_data) -> str:
        """Generate an image from tweet data."""
        logger.info(f"Generating image for tweet by {tweet_data.author_name}")

        # Dimensions
        width = 2000
        height = 2400

        img = Image.new('RGB', (width, height), self.theme['background'])
        draw = ImageDraw.Draw(img)

        # Load fonts
        try:
            font_name = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 68)
            font_text = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 78)
            font_meta = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 42)
            font_metrics = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
            logger.info("Loaded fonts successfully")
        except OSError as e:
            logger.warning(f"Could not load fonts: {e}")
            font_name = ImageFont.load_default()
            font_text = font_name
            font_meta = font_name
            font_metrics = font_name
            font_small = font_name

        # Layout
        padding_side = 110
        padding_top = 110
        content_width = width - (2 * padding_side)
        current_y = padding_top

        # ========== HEADER ==========
        avatar_size = 110

        # Avatar
        avatar_x = padding_side
        avatar_y = current_y

        logger.debug(f"Loading avatar from: {tweet_data.author_avatar}")
        avatar_image = await self._load_image(tweet_data.author_avatar, avatar_size)
        if avatar_image:
            avatar_image = avatar_image.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([(0, 0), (avatar_size, avatar_size)], fill=255)
            avatar_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            avatar_layer.paste(avatar_image, (avatar_x, avatar_y), mask)
            img.paste(avatar_layer, (0, 0), avatar_layer.convert('L'))
        else:
            initials = self._get_initials(tweet_data.author_name)
            draw.ellipse([avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size],
                        fill=self.theme['accent'])
            bbox = draw.textbbox((0, 0), initials, font=font_name)
            text_x = avatar_x + (avatar_size - (bbox[2] - bbox[0])) // 2
            text_y = avatar_y + (avatar_size - (bbox[3] - bbox[1])) // 2
            draw.text((text_x, text_y), initials, fill=(255, 255, 255), font=font_name)

        # Author info
        text_x = avatar_x + avatar_size + 20
        text_y = current_y + 10

        # Name
        draw.text((text_x, text_y), tweet_data.author_name, fill=self.theme['text'], font=font_name)
        name_bbox = draw.textbbox((text_x, text_y), tweet_data.author_name, font=font_name)
        name_width = name_bbox[2] - name_bbox[0]

        # Verified badge
        self._draw_verified_badge(draw, text_x + name_width + 10, text_y + 8, 30)

        # Username + date
        meta_y = text_y + 82
        date_str = self._format_date(tweet_data.created_at)
        meta_text = f"{tweet_data.author_username} · {date_str}"
        draw.text((text_x, meta_y), meta_text, fill=self.theme['secondary_text'], font=font_meta)

        current_y += avatar_size + 65

        # ========== TWEET TEXT ==========
        logger.debug(f"Processing tweet text (length: {len(tweet_data.text)})")
        current_y = self._render_text(draw, tweet_data.text, padding_side, current_y, content_width, font_text)

        # ========== IMAGES ==========
        if tweet_data.images:
            logger.info(f"Processing {len(tweet_data.images)} images")
            current_y += 30

            num_images = min(len(tweet_data.images), 4)

            if num_images == 1:
                tweet_image = await self._load_image(tweet_data.images[0], 1200)
                if tweet_image:
                    img_width = content_width
                    img_height = min(1500, int(img_width * (tweet_image.height / tweet_image.width)))
                    tweet_image = tweet_image.resize((img_width, img_height), Image.Resampling.LANCZOS)
                    tweet_image = self._add_rounded_corners(tweet_image, 20)
                    img.paste(tweet_image, (padding_side, current_y), tweet_image)
                    current_y += img_height + 35

            elif num_images == 2:
                img_w = (content_width - 16) // 2
                max_h = 850
                for i, url in enumerate(tweet_data.images[:2]):
                    tweet_image = await self._load_image(url, 900)
                    if tweet_image:
                        img_h = min(max_h, int(img_w * (tweet_image.height / tweet_image.width)))
                        tweet_image = tweet_image.resize((img_w, img_h), Image.Resampling.LANCZOS)
                        tweet_image = self._add_rounded_corners(tweet_image, 18)
                        img.paste(tweet_image, (padding_side + i * (img_w + 16), current_y), tweet_image)
                current_y += max_h + 35

            else:
                img_w = (content_width - 16) // 2
                max_h = 700
                for i, url in enumerate(tweet_data.images[:4]):
                    tweet_image = await self._load_image(url, 900)
                    if tweet_image:
                        img_h = min(max_h, int(img_w * (tweet_image.height / tweet_image.width)))
                        tweet_image = tweet_image.resize((img_w, img_h), Image.Resampling.LANCZOS)
                        tweet_image = self._add_rounded_corners(tweet_image, 18)
                        row = i // 2
                        col = i % 2
                        img.paste(tweet_image,
                                (padding_side + col * (img_w + 16), current_y + row * (max_h + 16)),
                                tweet_image)
                current_y += (max_h * 2) + 50

        # ========== METRICS BAR ==========
        current_y += 45

        # Divider line
        draw.line([padding_side, current_y, width - padding_side, current_y],
                 fill=self.theme['divider'], width=1)
        current_y += 55

        # Format numbers
        retweets = self._format_number(tweet_data.retweets)
        likes = self._format_number(tweet_data.likes)

        # Draw retweet
        icon_size = 28
        self._draw_retweet_icon(draw, padding_side + 20, current_y, icon_size)
        draw.text((padding_side + 20 + icon_size + 10, current_y + 4), retweets,
                 fill=self.theme['secondary_text'], font=font_metrics)

        # Draw like
        like_x = padding_side + content_width // 2 + 20
        self._draw_like_icon(draw, like_x, current_y, icon_size)
        draw.text((like_x + icon_size + 10, current_y + 4), likes,
                 fill=self.theme['secondary_text'], font=font_metrics)

        current_y += 75

        # ========== BOTTOM BRANDING ==========
        logo_size = 26
        self._draw_x_logo(draw, padding_side, current_y, logo_size)

        branding_text = "Posted on X"
        draw.text((padding_side + logo_size + 10, current_y + 4), branding_text,
                 fill=self.theme['secondary_text'], font=font_small)

        # Date on right
        date_final = self._format_date_full(tweet_data.created_at)
        date_bbox = draw.textbbox((0, 0), date_final, font=font_small)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text((width - padding_side - date_width, current_y + 4), date_final,
                 fill=self.theme['secondary_text'], font=font_small)

        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"tweet_{timestamp}_{self.theme_name}.png"
        filepath = os.path.join(self.output_dir, filename)
        logger.info(f"Saving image to: {filepath}")
        img.save(filepath, 'PNG', dpi=(300, 300))
        logger.info("Image saved successfully")

        return filepath

    def _render_text(self, draw: ImageDraw.ImageDraw, text: str, x: int, y: int,
                     max_width: int, font) -> int:
        """Render tweet text preserving original formatting."""
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Split by explicit line breaks
        lines = text.split('\n')
        line_height = 105

        for line in lines:
            if not line.strip():
                # Empty line
                y += line_height * 0.5
                continue

            # Parse entities in this line
            parts = self._parse_text_entities(line)

            # Render parts with color
            current_x = x
            current_line_parts = []
            line_width = 0

            for part_text, part_type in parts:
                color = self.theme['link'] if part_type in ('mention', 'hashtag', 'url') else self.theme['text']
                bbox = draw.textbbox((0, 0), part_text, font=font)
                part_width = bbox[2] - bbox[0]

                if line_width + part_width <= max_width:
                    current_line_parts.append((part_text, current_x, color))
                    line_width += part_width
                    current_x += part_width
                else:
                    # Line too long - render current and start new line
                    for p_text, p_x, p_color in current_line_parts:
                        draw.text((p_x, y), p_text, fill=p_color, font=font)
                    y += line_height
                    current_x = x
                    line_width = 0
                    current_line_parts = []

                    # Check if part alone is too long
                    if part_width > max_width:
                        # Split long word/URL
                        words = part_text.split(' ')
                        for word in words:
                            w_bbox = draw.textbbox((0, 0), word, font=font)
                            w_width = w_bbox[2] - w_bbox[0]
                            if line_width + w_width > max_width:
                                y += line_height
                                current_x = x
                                line_width = 0
                            draw.text((current_x, y), word, fill=color, font=font)
                            current_x += w_width
                            line_width += w_width
                    else:
                        current_line_parts.append((part_text, current_x, color))
                        line_width = part_width
                        current_x = part_width

            # Render remaining parts
            for p_text, p_x, p_color in current_line_parts:
                draw.text((p_x, y), p_text, fill=p_color, font=font)
            y += line_height

        return y

    def _parse_text_entities(self, text: str) -> list[tuple[str, str]]:
        """Parse text into (text, type) tuples."""
        parts = []
        remaining = text

        patterns = [
            (r'https?://\S+', 'url'),
            (r'@\w+', 'mention'),
            (r'#\w+', 'hashtag'),
        ]

        while remaining:
            earliest_match = None
            earliest_pos = len(remaining)
            match_type = None

            for pattern, entity_type in patterns:
                match = re.search(pattern, remaining)
                if match and match.start() < earliest_pos:
                    earliest_match = match
                    earliest_pos = match.start()
                    match_type = entity_type

            if earliest_match:
                if earliest_pos > 0:
                    parts.append((remaining[:earliest_pos], 'text'))
                parts.append((earliest_match.group(0), match_type))
                remaining = remaining[earliest_match.end():]
            else:
                if remaining:
                    parts.append((remaining, 'text'))
                break

        return parts

    def _add_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Add rounded corners."""
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        return output

    def _get_initials(self, name: str) -> str:
        """Get initials from name."""
        parts = name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0].upper()}{parts[1][0].upper()}"
        return name[:2].upper() if len(name) >= 2 else name[:1].upper()

    def _format_date(self, date_str: str) -> str:
        """Format date short."""
        if not date_str:
            return ''
        try:
            from datetime import datetime as dt
            parsed = dt.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
            return parsed.strftime("%b %d, %Y")
        except (ValueError, AttributeError):
            return date_str[:12] if len(date_str) > 12 else date_str

    def _format_date_full(self, date_str: str) -> str:
        """Format date full."""
        if not date_str:
            return ''
        try:
            from datetime import datetime as dt
            parsed = dt.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
            return parsed.strftime("%B %d, %Y at %I:%M %p")
        except (ValueError, AttributeError):
            return date_str

    def _format_number(self, num: int) -> str:
        """Format number."""
        if num >= 1000000:
            return f'{num / 1000000:.1f}M'
        elif num >= 1000:
            return f'{num / 1000:.1f}K'
        return str(num)

    async def _load_image(self, url: Optional[str], size: int) -> Optional[Image.Image]:
        """Load image from URL."""
        if not url:
            return None

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        img = Image.open(BytesIO(image_data))
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        return img
        except Exception as e:
            logger.debug(f"Error loading image: {e}")

        return None

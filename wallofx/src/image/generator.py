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

    THEMES = {
        'dark': {
            'background': (0, 0, 0),
            'text': (231, 233, 234),
            'secondary': (113, 118, 123),
            'link': (29, 155, 240),
            'divider': (47, 51, 54),
        },
        'dim': {
            'background': (21, 32, 43),
            'text': (255, 255, 255),
            'secondary': (136, 153, 166),
            'link': (29, 155, 240),
            'divider': (56, 68, 77),
        },
        'light': {
            'background': (255, 255, 255),
            'text': (15, 20, 25),
            'secondary': (83, 100, 113),
            'link': (29, 155, 240),
            'divider': (207, 217, 222),
        },
    }

    def __init__(self, theme: str = 'dark'):
        self.theme = self.THEMES.get(theme, self.THEMES['dark'])
        self.theme_name = theme
        self.output_dir = 'wallofx/static/output'
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate(self, tweet_data) -> str:
        """Generate an image from tweet data."""
        # High resolution for quality
        scale = 2  # 2x for retina/high quality
        width = 600 * scale
        height = 800 * scale
        
        img = Image.new('RGB', (width, height), self.theme['background'])
        draw = ImageDraw.Draw(img)

        # Load fonts (scaled)
        font_name = self._load_font(17 * scale, bold=True)
        font_handle = self._load_font(15 * scale)
        font_text = self._load_font(23 * scale)
        font_small = self._load_font(14 * scale)

        pad = 16 * scale
        y = pad

        # === HEADER ===
        avatar_size = 40 * scale
        avatar = await self._load_image(tweet_data.author_avatar, avatar_size * 2)
        
        if avatar:
            avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, avatar_size-1, avatar_size-1), fill=255)
            img.paste(avatar, (pad, y), mask)
        else:
            draw.ellipse((pad, y, pad + avatar_size, y + avatar_size), fill=self.theme['link'])

        # Name + badge
        name_x = pad + avatar_size + 10 * scale
        draw.text((name_x, y), tweet_data.author_name, fill=self.theme['text'], font=font_name)
        name_w = draw.textbbox((0, 0), tweet_data.author_name, font=font_name)[2]
        
        # Verified badge right after name
        badge_x = name_x + name_w + 4 * scale
        badge_y = y + 4 * scale
        badge_r = 9 * scale
        draw.ellipse((badge_x, badge_y, badge_x + badge_r*2, badge_y + badge_r*2), fill=(29, 155, 240))
        # Checkmark
        cx, cy = badge_x + badge_r, badge_y + badge_r
        draw.line([(cx - 5*scale, cy), (cx - 1*scale, cy + 4*scale), (cx + 5*scale, cy - 4*scale)], fill=(255,255,255), width=2*scale)

        # Username
        draw.text((name_x, y + 24 * scale), tweet_data.author_username, fill=self.theme['secondary'], font=font_handle)

        y += avatar_size + 16 * scale

        # === TWEET TEXT ===
        y = self._draw_text(draw, tweet_data.text, pad, y, width - pad*2, font_text, scale)
        y += 16 * scale

        # === DATE + VIEWS ===
        date_str = self._format_date(tweet_data.created_at)
        views = self._fmt_num(tweet_data.views) if tweet_data.views else None
        meta = f"{date_str} · {views} Views" if views else date_str
        draw.text((pad, y), meta, fill=self.theme['secondary'], font=font_small)
        y += 28 * scale

        # === DIVIDER ===
        draw.line((pad, y, width - pad, y), fill=self.theme['divider'], width=scale)
        y += 16 * scale

        # === METRICS ===
        parts = []
        if tweet_data.replies: parts.append(f"{self._fmt_num(tweet_data.replies)} Replies")
        if tweet_data.retweets: parts.append(f"{self._fmt_num(tweet_data.retweets)} Reposts")
        if tweet_data.likes: parts.append(f"{self._fmt_num(tweet_data.likes)} Likes")
        if parts:
            draw.text((pad, y), " · ".join(parts), fill=self.theme['secondary'], font=font_small)
            y += 28 * scale
            draw.line((pad, y, width - pad, y), fill=self.theme['divider'], width=scale)
            y += 16 * scale

        # === IMAGES ===
        if tweet_data.images:
            y = await self._draw_images(img, tweet_data.images, pad, y, width - pad*2, scale)

        # Crop to content
        final_h = min(y + pad, height)
        img = img.crop((0, 0, width, final_h))

        # Save at high quality
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(self.output_dir, f"tweet_{ts}.png")
        img.save(path, 'PNG', dpi=(300, 300), optimize=False)
        return path

    def _load_font(self, size, bold=False):
        """Load font with fallbacks."""
        paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
        ]
        for p in paths:
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
        return ImageFont.load_default()

    def _draw_text(self, draw, text, x, y, max_w, font, scale=1):
        """Draw tweet text with minimal line spacing."""
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Get font metrics for line height
        bbox = draw.textbbox((0, 0), "Ay", font=font)
        line_h = int((bbox[3] - bbox[1]) * 1.4)  # Proper line spacing
        para_gap = 8 * scale  # Gap between paragraphs
        
        for para in text.split('\n'):
            if not para.strip():
                y += para_gap  # Small gap for empty lines
                continue
            
            # Word wrap
            words = para.split()
            line = ""
            for word in words:
                test = f"{line} {word}".strip()
                if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
                    line = test
                else:
                    if line:
                        self._draw_line_with_entities(draw, line, x, y, font)
                        y += line_h
                    line = word
            
            if line:
                self._draw_line_with_entities(draw, line, x, y, font)
                y += line_h
        
        return y

    def _draw_line_with_entities(self, draw, line, x, y, font):
        """Draw a line with colored @mentions, #hashtags, URLs."""
        pattern = r'(@\w+|#\w+|https?://\S+)'
        parts = re.split(pattern, line)
        
        for part in parts:
            if not part:
                continue
            color = self.theme['link'] if re.match(pattern, part) else self.theme['text']
            draw.text((x, y), part, fill=color, font=font)
            x += draw.textbbox((0, 0), part, font=font)[2]

    async def _draw_images(self, img, urls, x, y, max_w, scale=1):
        """Draw tweet images."""
        n = min(len(urls), 4)
        gap = 4 * scale
        r = 12 * scale
        
        if n == 1:
            tweet_img = await self._load_image(urls[0], 1200)
            if tweet_img:
                # Fit width, cap height
                max_h = 300 * scale
                img_scale = min(max_w / tweet_img.width, max_h / tweet_img.height, 1.0)
                w, h = int(tweet_img.width * img_scale), int(tweet_img.height * img_scale)
                tweet_img = tweet_img.resize((w, h), Image.Resampling.LANCZOS)
                tweet_img = self._round_corners(tweet_img, r)
                img.paste(tweet_img, (x, y), tweet_img)
                y += h + 12 * scale
        elif n == 2:
            iw = (max_w - gap) // 2
            ih = 150 * scale
            for i, url in enumerate(urls[:2]):
                tweet_img = await self._load_image(url, 600)
                if tweet_img:
                    tweet_img = self._crop_fit(tweet_img, iw, ih)
                    tweet_img = self._round_corners(tweet_img, r)
                    img.paste(tweet_img, (x + i * (iw + gap), y), tweet_img)
            y += ih + 12 * scale
        else:
            iw = (max_w - gap) // 2
            ih = 120 * scale
            for i, url in enumerate(urls[:4]):
                tweet_img = await self._load_image(url, 500)
                if tweet_img:
                    tweet_img = self._crop_fit(tweet_img, iw, ih)
                    tweet_img = self._round_corners(tweet_img, r)
                    row, col = divmod(i, 2)
                    img.paste(tweet_img, (x + col * (iw + gap), y + row * (ih + gap)), tweet_img)
            rows = (min(n, 4) + 1) // 2
            y += rows * ih + (rows - 1) * gap + 12 * scale
        
        return y

    def _crop_fit(self, img, w, h):
        """Center crop to fit dimensions."""
        scale = max(w / img.width, h / img.height)
        nw, nh = int(img.width * scale), int(img.height * scale)
        img = img.resize((nw, nh), Image.Resampling.LANCZOS)
        left, top = (nw - w) // 2, (nh - h) // 2
        return img.crop((left, top, left + w, top + h))

    def _round_corners(self, img, r):
        """Add rounded corners."""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        mask = Image.new('L', img.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width-1, img.height-1), r, fill=255)
        out = Image.new('RGBA', img.size, (0, 0, 0, 0))
        out.paste(img, (0, 0))
        out.putalpha(mask)
        return out

    def _format_date(self, s):
        """Format date string."""
        if not s:
            return ''
        try:
            d = datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
            return d.strftime("%I:%M %p · %b %d, %Y").lstrip('0')
        except:
            return s[:20]

    def _fmt_num(self, n):
        """Format number."""
        if not n:
            return '0'
        n = int(n)
        if n >= 1_000_000:
            return f'{n/1_000_000:.1f}M'
        if n >= 1_000:
            return f'{n/1_000:.1f}K'
        return str(n)

    async def _load_image(self, url, size):
        """Load image from URL."""
        if not url:
            return None
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status == 200:
                        return Image.open(BytesIO(await r.read())).convert('RGBA')
        except:
            pass
        return None

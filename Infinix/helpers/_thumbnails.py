# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of InfinixMusic
#ALONE-CODER

import os
import aiohttp
import traceback
from PIL import (Image, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont, ImageOps)

from Infinix import logger, config
from Infinix.helpers import Track


class Thumbnail:
    def __init__(self):
        self.rect = (914, 514)
        self.fill = (255, 255, 255)
        self.font1 = ImageFont.truetype("Infinix/helpers/Raleway-Bold.ttf", 30)
        self.font2 = ImageFont.truetype("Infinix/helpers/Inter-Light.ttf", 30)

        # Ensure cache directory exists
        os.makedirs("cache", exist_ok=True)

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(await resp.read())
            return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            thumb = Image.open(temp).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
            blur = thumb.filter(ImageFilter.GaussianBlur(25))
            image = ImageEnhance.Brightness(blur).enhance(.40)

            _rect = ImageOps.fit(thumb, self.rect, method=Image.LANCZOS, centering=(0.5, 0.5))
            
            # Create new mask each time to avoid issues
            mask = Image.new("L", self.rect, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, self.rect[0], self.rect[1]), radius=15, fill=255)
            _rect.putalpha(mask)
            image.paste(_rect, (183, 30), _rect)

            draw = ImageDraw.Draw(image)
            channel_text = f"{song.channel_name[:25]} | {song.view_count}" if song.view_count else song.channel_name[:25]
            draw.text((50, 560), channel_text, font=self.font2, fill=self.fill)
            draw.text((50, 600), song.title[:50], font=self.font1, fill=self.fill)
            draw.text((40, 650), "0:01", font=self.font1)
            draw.line([(140, 670), (1160, 670)], fill=self.fill, width=5, joint="curve")
            draw.text((1185, 650), song.duration or "0:00", font=self.font1, fill=self.fill)

            image.save(output)
            if os.path.exists(temp):
                os.remove(temp)
            return output
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
            logger.error(traceback.format_exc())
            return config.DEFAULT_THUMB

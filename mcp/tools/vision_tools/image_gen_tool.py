from __future__ import annotations

import io
import time
from pathlib import Path
from typing import Any, Dict
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageFont

from mcp.base_tool import BaseTool
from shared.constants import IMAGE_BG_SIZE, IMAGE_CHAR_SIZE


class HFImageGenTool(BaseTool):
    name = "hf_image_gen"
    description = "Generate images using free Pollinations API (formerly Hugging Face)."

    def _call_pollinations(self, prompt: str, kind: str) -> Image.Image:
        if kind == "background":
            width, height = IMAGE_BG_SIZE
        else:
            width, height = IMAGE_CHAR_SIZE
        
        # We append some style tags for better visual novel consistency
        style_suffix = ", high quality anime visual novel style, masterpiece"
        full_prompt = prompt + style_suffix
        encoded_prompt = quote(full_prompt)
        
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
        
        # Keep retries short so the pipeline can fall back quickly instead of stalling.
        max_retries = 3
        base_wait = 1  # Start at 1 second
        
        last_error = None
        for attempt in range(max_retries):
            try:
                # 30 seconds timeout is enough for a quick check before falling back.
                response = requests.get(url, timeout=30)
                
                # Handle rate limiting (429) with very aggressive backoff
                if response.status_code == 429:
                    wait_time = base_wait * (2 ** attempt)
                    if attempt < max_retries - 1:
                        print(f"[Attempt {attempt + 1}/{max_retries}] Rate limited (429). Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        last_error = f"Rate limited after {max_retries} attempts"
                        break
                
                # Handle server errors (5xx) with backoff
                if 500 <= response.status_code < 600:
                    wait_time = base_wait * (2 ** attempt)
                    if attempt < max_retries - 1:
                        print(f"[Attempt {attempt + 1}/{max_retries}] Server error ({response.status_code}). Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        last_error = f"Server error {response.status_code} after {max_retries} attempts"
                        break
                
                # Success: return image
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    return image.convert("RGBA")
                
                # Other errors: give up immediately
                response.raise_for_status()
                
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                wait_time = base_wait * (2 ** attempt)
                if attempt < max_retries - 1:
                    print(f"[Attempt {attempt + 1}/{max_retries}] Connection error: {e}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    last_error = str(e)
                    break
            except Exception as e:
                last_error = str(e)
                break
        
        # All retries exhausted. Return a deterministic placeholder so the
        # pipeline can still complete instead of failing the whole job.
        width, height = IMAGE_BG_SIZE if kind == "background" else IMAGE_CHAR_SIZE
        placeholder = Image.new("RGBA", (width, height), (20, 24, 38, 255))
        draw = ImageDraw.Draw(placeholder)
        title = "Image generation unavailable"
        subtitle = (last_error or "rate limited").strip()
        try:
            font_title = ImageFont.truetype("arial.ttf", 36)
            font_subtitle = ImageFont.truetype("arial.ttf", 22)
        except Exception:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()

        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

        center_x = width // 2
        center_y = height // 2
        draw.rounded_rectangle((40, 40, width - 40, height - 40), radius=24, outline=(255, 255, 255, 60), width=3)
        draw.text((center_x - title_width // 2, center_y - title_height - 8), title, fill=(240, 245, 255, 255), font=font_title)
        draw.text((center_x - subtitle_width // 2, center_y + 8), subtitle[:120], fill=(180, 190, 210, 255), font=font_subtitle)
        return placeholder

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        prompt = kwargs["prompt"]
        kind = kwargs.get("kind", "background")
        output_path = Path(kwargs["output_path"])
        
        image = self._call_pollinations(prompt, kind)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        return {"image_path": str(output_path)}

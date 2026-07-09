from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
from PIL import Image
from rembg import new_session, remove

from mcp.base_tool import BaseTool
from shared.utils.cloud import is_cloud_mode
from shared.utils import setup_logger

logger = setup_logger("bg-removal")
_rembg_session = None


def _get_rembg_session():
    global _rembg_session
    if _rembg_session is None:
        import os

        model = os.getenv("REMBG_MODEL", "u2netp")
        logger.info("Initialising rembg session with model=%s", model)
        _rembg_session = new_session(model)
    return _rembg_session


class ImageBackgroundRemovalTool(BaseTool):
    name = "image_bg_removal"
    description = "Remove background from character images."

    def _remove_white_background(self, input_path: Path, output_path: Path) -> None:
        """Fast PIL-based removal for white-background character sprites (cloud mode)."""
        img = Image.open(input_path).convert("RGBA")
        arr = np.array(img)
        rgb = arr[:, :, :3].astype(np.int16)
        # Characters are generated on pure white — treat near-white as transparent.
        white_mask = np.all(rgb >= 235, axis=2)
        arr[white_mask, 3] = 0
        Image.fromarray(arr, mode="RGBA").save(output_path)

    def _remove_with_rembg(self, input_path: Path, output_path: Path) -> None:
        src = input_path.read_bytes()
        out = remove(src, session=_get_rembg_session())
        output_path.write_bytes(out)
        Image.open(output_path).convert("RGBA").save(output_path)

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        input_path = Path(kwargs["input_path"])
        output_path = Path(kwargs["output_path"])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if is_cloud_mode():
            logger.info("Using lightweight white-background removal (cloud mode)")
            self._remove_white_background(input_path, output_path)
        else:
            self._remove_with_rembg(input_path, output_path)

        return {"image_path": str(output_path)}

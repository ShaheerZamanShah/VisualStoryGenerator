from __future__ import annotations

from pathlib import Path
import tempfile

import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont


W, H = 1280, 720

def _font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def _slide(title: str, lines: list[str], output_path: Path) -> None:
    img = Image.new("RGB", (W, H), color=(8, 14, 36))
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, W, 90), fill=(20, 35, 78))
    draw.text((40, 30), title, fill=(232, 241, 255), font=_font(38))

    y = 150
    for line in lines:
        draw.text((60, y), f"- {line}", fill=(214, 226, 255), font=_font(30))
        y += 64

    draw.text((60, H - 70), "Agentic AI Video Pipeline Demo", fill=(140, 164, 224), font=_font(24))
    img.save(output_path)


def main() -> None:
    slides = [
        ("Initial Generation", ["Prompt submitted in UI", "Story, audio, and video phases complete", "Final video artifact created"]),
        ("Edit 1", ["Query: Change Alice hair to red", "Intent: character_visuals", "Execution: state + snapshot updated"]),
        ("Edit 2", ["Query: Make scene 2 background rainy", "Intent: background_visuals", "Execution: overrides stored"]),
        ("Edit 3", ["Query: Add dramatic music", "Intent: music", "Execution: audio override stored"]),
        ("Revert 1", ["Action: Undo", "Restored previous JSON state", "Assets restored from snapshot"]),
        ("Revert 2", ["Action: Undo", "Restored earlier JSON state", "Assets restored from snapshot"]),
        ("Deliverable Complete", ["Flow shown: initial -> 3 edits -> 2 reverts", "Includes classification + execution + undo", "Ready for report appendix"]),
    ]

    out_path = Path("docs/demo/edit_agent_demo.mp4")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        clips = []
        for idx, (title, lines) in enumerate(slides):
            img_path = td_path / f"slide_{idx:02d}.png"
            _slide(title, lines, img_path)
            arr = np.array(Image.open(img_path).convert("RGB"))
            clips.append(ImageClip(arr).set_duration(2.8))

        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(out_path),
            fps=24,
            codec="libx264",
            audio=False,
            preset="fast",
            logger=None,
        )

    print(f"Demo video written to: {out_path}")


if __name__ == "__main__":
    main()

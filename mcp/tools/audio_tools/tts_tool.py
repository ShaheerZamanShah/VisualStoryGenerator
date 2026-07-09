from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any, Dict

from mcp.base_tool import BaseTool
from shared.utils import setup_logger

# edge-tts voices (cross-platform, used in Docker/Linux)
_EDGE_VOICES = {
    "female": "en-US-JennyNeural",
    "male": "en-US-GuyNeural",
}


class CoquiTTSTool(BaseTool):
    name = "coqui_tts"
    description = "Generate speech audio with gender-aware voice selection."

    def __init__(self) -> None:
        self.logger = setup_logger("tts-tool")
        self._engine = os.getenv("TTS_ENGINE", "edge_tts").lower()

    def _wpm_to_edge_rate(self, wpm: int) -> str:
        pct = round((wpm - 165) / 165 * 100)
        pct = max(-50, min(50, pct))
        return f"{pct:+d}%"

    async def _edge_tts_async(self, text: str, voice: str, rate: str, output_path: Path) -> None:
        import edge_tts

        mp3_path = output_path.with_suffix(".mp3")
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(str(mp3_path))
        self._mp3_to_wav(mp3_path, output_path)
        if mp3_path.exists():
            mp3_path.unlink()

    def _mp3_to_wav(self, mp3_path: Path, wav_path: Path) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(mp3_path),
                "-ar",
                "22050",
                "-ac",
                "1",
                "-sample_fmt",
                "s16",
                str(wav_path),
            ],
            check=True,
            capture_output=True,
        )

    def _run_edge_tts(self, text: str, gender: str, rate: int, output_path: Path) -> None:
        voice = _EDGE_VOICES.get(gender, _EDGE_VOICES["male"])
        edge_rate = self._wpm_to_edge_rate(rate)
        asyncio.run(self._edge_tts_async(text, voice, edge_rate, output_path))

    def _get_female_voice_id(self) -> str | None:
        try:
            import pyttsx3

            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            engine.stop()
            for v in voices:
                name_lower = v.name.lower()
                if any(kw in name_lower for kw in ("zira", "female", "woman", "helen", "hazel")):
                    return v.id
            if len(voices) > 1:
                return voices[1].id
        except Exception:
            pass
        return None

    def _run_pyttsx3(self, text: str, gender: str, rate: int, output_path: Path) -> None:
        import pyttsx3

        voice_id_line = ""
        if gender == "female":
            female_id = self._get_female_voice_id()
            if female_id:
                safe_id = female_id.replace("\\", "\\\\")
                voice_id_line = f"engine.setProperty('voice', r'{safe_id}')"

        script = textwrap.dedent(
            f"""
            import pyttsx3
            import time
            engine = pyttsx3.init()
            engine.setProperty('rate', {rate})
            {voice_id_line}
            engine.save_to_file({repr(text)}, {repr(str(output_path))})
            engine.runAndWait()
            time.sleep(0.5)
        """
        ).strip()

        subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            timeout=30,
            text=True,
        )

    def _create_fallback_silence(self, output_path: Path) -> None:
        import numpy as np
        from scipy.io import wavfile as sp_wavfile

        sr = 22050
        silence = np.zeros(sr, dtype=np.int16)
        sp_wavfile.write(str(output_path), sr, silence)

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        text = kwargs["text"]
        output_path = Path(kwargs["output_path"])
        gender = kwargs.get("gender", "male").lower()
        rate = int(kwargs.get("rate", 165))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        engines = [self._engine]
        if self._engine == "edge_tts":
            engines.append("pyttsx3")
        elif self._engine == "pyttsx3":
            engines.append("edge_tts")
        else:
            engines = ["edge_tts", "pyttsx3"]

        for engine_name in dict.fromkeys(engines):
            for attempt in range(2):
                try:
                    if engine_name == "edge_tts":
                        self._run_edge_tts(text, gender, rate, output_path)
                    else:
                        self._run_pyttsx3(text, gender, rate, output_path)

                    if output_path.exists() and output_path.stat().st_size > 100:
                        self.logger.info(
                            "Generated TTS at %s (engine=%s, gender=%s)",
                            output_path,
                            engine_name,
                            gender,
                        )
                        return {"audio_path": str(output_path)}
                except Exception as exc:
                    self.logger.warning(
                        "TTS attempt failed (engine=%s, attempt=%d): %s",
                        engine_name,
                        attempt + 1,
                        exc,
                    )
                time.sleep(0.5)

        self.logger.warning("TTS failed for all engines. Creating fallback silence.")
        self._create_fallback_silence(output_path)
        return {"audio_path": str(output_path)}

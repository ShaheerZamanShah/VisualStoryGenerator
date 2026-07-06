from __future__ import annotations

import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any, Dict

import pyttsx3

from mcp.base_tool import BaseTool
from shared.utils import setup_logger


class CoquiTTSTool(BaseTool):
    name = "coqui_tts"
    description = "Generate speech audio with local TTS, with gender-aware voice selection."

    def __init__(self) -> None:
        self.logger = setup_logger("tts-tool")

    def _get_female_voice_id(self) -> str | None:
        """Return the COM voice token for a female SAPI5 voice, or None."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            engine.stop()
            for v in voices:
                name_lower = v.name.lower()
                # Windows SAPI5: Zira is female, David is male
                if any(kw in name_lower for kw in ("zira", "female", "woman", "helen", "hazel")):
                    return v.id
            # Fallback: voice index 1 is commonly female on Windows
            if len(voices) > 1:
                return voices[1].id
        except Exception:
            pass
        return None

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        text = kwargs["text"]
        output_path = Path(kwargs["output_path"])
        gender = kwargs.get("gender", "male").lower()  # "male" or "female"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        voice_id_line = ""
        if gender == "female":
            female_id = self._get_female_voice_id()
            if female_id:
                # Escape backslashes for embedding in the script string
                safe_id = female_id.replace("\\", "\\\\")
                voice_id_line = f"engine.setProperty('voice', r'{safe_id}')"

        # Run pyttsx3 in a subprocess to avoid SAPI5 COM deadlocks in thread pools
        rate = int(kwargs.get("rate", 165))
        
        # Use textwrap.dedent to properly format the script
        script = textwrap.dedent(f"""
            import pyttsx3
            import time
            engine = pyttsx3.init()
            engine.setProperty('rate', {rate})
            {voice_id_line}
            engine.save_to_file({repr(text)}, {repr(str(output_path))})
            engine.runAndWait()
            time.sleep(0.5)
        """).strip()
        max_retries = 2
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    [sys.executable, "-c", script], 
                    check=True, 
                    capture_output=True, 
                    timeout=30,
                    text=True
                )
                
                # Validate file was created
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    if file_size > 100:  # Valid WAV file
                        self.logger.info("Generated TTS line at %s (gender=%s, size=%d bytes)", output_path, gender, file_size)
                        return {"audio_path": str(output_path)}
                    else:
                        self.logger.warning("TTS created empty file (%d bytes), retrying...", file_size)
                else:
                    self.logger.warning("TTS file not created, retrying...")
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("TTS subprocess timed out on attempt %d", attempt + 1)
            except Exception as e:
                self.logger.warning("TTS generation error on attempt %d: %s", attempt + 1, e)
            
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
        
        # Fallback: create minimal valid WAV file to prevent pipeline break
        self.logger.warning("TTS failed after %d attempts. Creating fallback silence file.", max_retries)
        try:
            import numpy as np
            from scipy.io import wavfile as sp_wavfile
            # Generate 1 second of silence at 22050 Hz
            sr = 22050
            silence = np.zeros(sr, dtype=np.int16)
            sp_wavfile.write(str(output_path), sr, silence)
            self.logger.info("Created fallback silence audio: %s", output_path)
        except Exception as e:
            self.logger.error("Failed to create fallback audio: %s", e)
            raise RuntimeError(f"TTS failed and could not create fallback: {e}")
        
        return {"audio_path": str(output_path)}

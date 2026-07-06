from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from mcp.tools.llm_tools import GroqJsonStructurerTool
from shared.schemas import StorySpec
from shared.utils import setup_logger, write_json

from .planner import build_story_prompt


class StoryAgent:
    def __init__(self) -> None:
        self.logger = setup_logger("story-agent")
        self.generator = GroqJsonStructurerTool()

    def run(self, job_id: str, user_prompt: str) -> Dict:
        self.logger.info("Generating story for job %s", job_id)
        prompt = build_story_prompt(user_prompt)
        data = self.generator.run(prompt=prompt, schema_model=StorySpec, attempts=5)["json"]
        story_spec = StorySpec.model_validate(data)

        out_dir = Path("data/outputs") / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "story_spec.json"
        write_json(out_path, story_spec.model_dump())
        self.logger.info("Story written: %s", out_path)
        return {"story_spec": story_spec.model_dump(), "story_spec_path": str(out_path)}

    def revise(
        self,
        job_id: str,
        original_prompt: str,
        current_story: Dict,
        edit_request: str,
        intent: str,
        params: Dict | None = None,
    ) -> Dict:
        """Revise an existing story spec using the user's edit request."""
        self.logger.info("Revising story for job %s with intent %s", job_id, intent)
        params = params or {}
        prompt = (
            "Revise the following existing story spec according to the user's edit request. "
            "Preserve the overall quality and keep it valid for the pipeline. "
            "If the edit asks for a longer or richer script, expand the dialogue rather than shortening it. "
            "If the edit changes characters, settings, mood, or script, apply all requested changes consistently. "
            "Maintain exactly two characters, 3-5 scenes, and total runtime around 50-70 seconds. "
            "Return strict JSON matching the StorySpec schema only.\n\n"
            f"Original user prompt:\n{original_prompt}\n\n"
            f"Current story JSON:\n{json.dumps(current_story, ensure_ascii=False, indent=2)}\n\n"
            f"Edit request:\n{edit_request}\n\n"
            f"Classified intent: {intent}\n"
            f"Extracted params: {json.dumps(params, ensure_ascii=False, indent=2)}\n"
        )
        data = self.generator.run(prompt=prompt, schema_model=StorySpec, attempts=3)["json"]
        story_spec = StorySpec.model_validate(data)
        out_dir = Path("data/outputs") / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "story_spec_edited.json"
        write_json(out_path, story_spec.model_dump())
        self.logger.info("Revised story written: %s", out_path)
        return {"story_spec": story_spec.model_dump(), "story_spec_path": str(out_path)}

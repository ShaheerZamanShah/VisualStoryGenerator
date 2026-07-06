from __future__ import annotations

import json
import re
from typing import Any, Dict, Type

from pydantic import BaseModel, ValidationError

from mcp.base_tool import BaseTool
from mcp.tools.llm_tools.text_generator import GroqTextGeneratorTool
from shared.utils import setup_logger


class GroqJsonStructurerTool(BaseTool):
    name = "groq_json_structurer"
    description = "Generate and validate JSON with Groq."

    def __init__(self):
        self.logger = setup_logger("json-structurer")

    def _extract_json(self, text: str) -> str:
        """Extract JSON from various formats."""
        text = text.strip()
        
        # Try direct JSON if starts with {
        if text.startswith('{'):
            return text
        
        # Extract from markdown code blocks
        markdown_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
        if markdown_match:
            return markdown_match.group(1).strip()
        
        # Extract from triple backticks without newlines
        backtick_match = re.search(r'```([\s\S]+?)```', text)
        if backtick_match:
            return backtick_match.group(1).strip()
        
        # Find JSON object by matching braces
        brace_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', text, re.DOTALL)
        if brace_match:
            return brace_match.group(0)
        
        return text

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        prompt = kwargs["prompt"]
        schema_model: Type[BaseModel] = kwargs["schema_model"]
        attempts = kwargs.get("attempts", 5)
        generator = GroqTextGeneratorTool()
        error_context = ""

        for attempt in range(attempts):
            final_prompt = (
                f"{prompt}\n\n"
                f"CRITICAL: Return ONLY valid JSON (no markdown, no explanation, no code blocks).\n"
                f"Schema: {json.dumps(schema_model.model_json_schema(), indent=2)}\n"
                f"{error_context}"
            )
            
            system_prompt = (
                "You are a JSON generation expert. "
                "Return ONLY valid, properly formatted JSON with NO markdown, NO code blocks, NO explanations. "
                "Start with { and end with }. Every field must be present."
            )
            
            out = generator.run(
                prompt=final_prompt,
                system=system_prompt,
                temperature=0.05
            )["text"].strip()
            
            self.logger.debug(f"Attempt {attempt + 1} LLM output length: {len(out)}")
            
            # Try multiple extraction strategies
            extracted_json = self._extract_json(out)
            
            if extracted_json:
                try:
                    payload = json.loads(extracted_json)
                    parsed = schema_model.model_validate(payload)
                    self.logger.info(f"JSON generation succeeded on attempt {attempt + 1}")
                    return {"json": parsed.model_dump()}
                except (json.JSONDecodeError, ValidationError) as exc:
                    error_context = f"\nPrevious error: {str(exc)[:150]}"
                    self.logger.debug(f"Attempt {attempt + 1} failed: {exc}")
        
        self.logger.error("Could not produce valid JSON after retries")
        raise ValueError("Could not produce valid JSON after retries.")

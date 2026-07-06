from __future__ import annotations

from textwrap import dedent


def build_story_prompt(user_prompt: str) -> str:
    return dedent(
        f"""
        Generate a cinematic short-film plan from this user prompt:
        "{user_prompt}"

        HARD RULES:
        1) Exactly two characters.
        2) Total runtime approximately 1 minute (50-70s).
        3) 3-5 scenes with clear progression and enough dialogue to feel complete.
        4) Dialogues only spoken by the two characters.
        5) Visual descriptions must be suitable for visual-novel-style image generation.
        6) The story must not feel clipped or rushed. Give each scene multiple dialogue beats when possible.

        Return only strict JSON matching schema.
        """
    ).strip()

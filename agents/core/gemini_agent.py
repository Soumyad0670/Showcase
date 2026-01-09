from agno.agent import Agent
from agno.run import RunContext
from agno.models.google import Gemini
import json
import re


class GeminiAgent(Agent):
    name = "gemini_agent"

    def __init__(self):
        # Initialize Agent with Gemini model
        super().__init__(
            model=Gemini(id="gemini-2.5-flash"),
            markdown=False,
        )

    def run(self, ctx: RunContext):
        """
        Calls Gemini LLM using Agent.run(), extracts structured JSON,
        validates it, and stores profile in workflow state.
        """
        prompt = ctx.state.get("prompt")
        if not prompt:
            raise ValueError("Prompt missing in workflow state")

        # IMPORTANT:
        # We intentionally call Agent.run() to execute the LLM
        run_output = super().run(prompt)

        # Agno version compatibility
        response_text = (
            getattr(run_output, "content", None)
            or getattr(run_output, "text", None)
        )

        if not response_text:
            raise ValueError("Empty response from Gemini model")

        profile = self._extract_json(response_text)

        # Defaults for optional fields
        profile.setdefault("experience_years", 0)
        profile.setdefault("projects", [])

        # Required field validation
        if not profile.get("name") or not profile.get("role"):
            raise ValueError("Missing required fields: name or role")

        ctx.state["profile"] = profile

    # -------------------------
    # Helpers
    # -------------------------

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM output safely"""

        # 1️⃣ Try direct JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2️⃣ Try fenced JSON block
        match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            text,
            re.DOTALL,
        )
        if match:
            return json.loads(match.group(1))

        # 3️⃣ Try first JSON object in text
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        raise ValueError("Failed to extract JSON from Gemini response")

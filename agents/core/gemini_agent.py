from agno import Agent, Context
from agno.llms import Gemini


class GeminiAgent(Agent):
    name = "gemini_agent"

    def __init__(self):
        super().__init__()
        self.llm = Gemini(model="gemini-1.5-pro")

    def run(self, ctx: Context):
        prompt = ctx.state.get("prompt")
        if not prompt:
            raise ValueError("Prompt missing for GeminiAgent")

        response = self.llm.generate(prompt)
        ctx.state["llm_output"] = response.text

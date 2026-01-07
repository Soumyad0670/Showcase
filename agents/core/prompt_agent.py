from agno import Agent, Context


class PromptAgent(Agent):
    name = "prompt_agent"

    def run(self, ctx: Context):
        raw_text = ctx.state.get("raw_text")
        if not raw_text:
            raise ValueError("raw_text missing in PromptAgent")

        prompt = f"""
        Extract the following into structured JSON:
        - name
        - role
        - skills
        - experience_years
        - projects

        Resume:
        {raw_text}
        """

        ctx.state["prompt"] = prompt.strip()

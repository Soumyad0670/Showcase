import json
import asyncio
import inspect
import uuid
import sys
import os
from dotenv import load_dotenv  # <--- NEW: Import dotenv

# 1. Load environment variables from .env file immediately
load_dotenv()

# --- PATH FIX: Ensure 'core' modules can be found ---
# If running from 'Showcase/agents', this adds the current dir to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Framework Imports
from agno.workflow import Workflow
from agno.run import RunContext

# Agent Imports
from core.data_agent import DataAgent
from core.prompt_agent import PromptAgent
from core.gemini_agent import GeminiAgent
from core.schema_builder import SchemaBuilderAgent
from core.template_selector_agent import TemplateSelectorAgent

class PortfolioBuilderWorkflow(Workflow):
    """
    Custom Workflow to orchestrate the Portfolio Builder pipeline.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_agent = DataAgent()
        self.prompt_agent = PromptAgent()
        self.gemini_agent = GeminiAgent()
        self.schema_agent = SchemaBuilderAgent()
        self.selector_agent = TemplateSelectorAgent()

    async def run(self, input_data: str):
        print(f"🚀 Starting Workflow: {self.name}")

        # --- Context Setup ---
        ctx = RunContext(
            run_id=str(uuid.uuid4()), 
            session_id=str(uuid.uuid4())
        )
        ctx.state = {"input": input_data}
        ctx.workflow = self

        # --- Step 1: Input Normalization (Sync) ---
        print("\n🔄 [1/5] Running DataAgent (Normalizing Input)...")
        # DataAgent is typically synchronous
        self.data_agent.run(ctx)
        
        if "raw_text" not in ctx.state:
            raise ValueError("❌ DataAgent failed to produce 'raw_text'")

        # --- Step 2: Prompt Engineering (Async) ---
        print("🔄 [2/5] Running PromptAgent (Building Prompt)...")
        # ✅ FIX: Added 'await' because PromptAgent.run is async
        await self.prompt_agent.run(ctx)

        # --- Step 3: LLM Generation (Sync/Async Check) ---
        print("🔄 [3/5] Running GeminiAgent (Calling LLM)...")
        
        # Defensive check: handles both sync and async implementations of GeminiAgent
        if inspect.iscoroutinefunction(self.gemini_agent.run):
            await self.gemini_agent.run(ctx)
        else:
            self.gemini_agent.run(ctx)

        # --- Step 4: Schema Building (Async) ---
        print("🔄 [4/5] Running SchemaBuilderAgent (Structuring Data)...")
        # ✅ FIX: Added 'await' for SchemaBuilderAgent
        await self.schema_agent.run(ctx)

        # --- Step 5: Template Selection (Async) ---
        print("🔄 [5/5] Running TemplateSelectorAgent (Choosing Layout)...")
        # ✅ FIX: Added 'await' for TemplateSelectorAgent
        await self.selector_agent.run(ctx)

        return ctx

def create_app():
    return PortfolioBuilderWorkflow(name="Portfolio-Builder")

app = create_app()

async def main():
    # Sample input representing a raw resume or user form data
    sample_input = {
        "name": "Arjun Sharma",
        "role": "Full Stack Developer",
        "skills": "Python, React, Docker, AWS",
        "experience_years": 5,
        "projects": "E-commerce platform, Chat app",
        "education": "B.Tech in CS"
    }

    input_text = json.dumps(sample_input, indent=2)

    try:
        # Run the workflow
        result_context = await app.run(input_text)

        print("\n✅ Workflow Complete!")
        print("-" * 50)
        print("Final State Keys:", list(result_context.state.keys()))
        
        # Print success details
        if "template" in result_context.state:
             print(f"Selected Template: {result_context.state['template'].get('name', 'Unknown')}")
        
        if "profile" in result_context.state:
             name = result_context.state['profile'].get('name', 'User')
             print(f"Profile Generated for: {name}")

    except Exception as e:
        print(f"\n❌ Workflow Failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
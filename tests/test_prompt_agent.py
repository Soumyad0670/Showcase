import pytest
import sys
import os
from unittest.mock import MagicMock

# ------------------- PATH FIX -------------------
# Ensures 'core' can be imported from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_path = os.path.join(current_dir, "../agents")
sys.path.insert(0, agents_path)
# ------------------------------------------------

from agno.run import RunContext
from agents.core.prompt_agent import PromptAgent

class TestPromptAgent:
    
    @pytest.fixture
    def agent(self):
        return PromptAgent()

    @pytest.mark.asyncio
    async def test_run_success(self, agent):
        """
        Scenario: 'raw_text' exists.
        Expected: Generates correct prompt and saves to state.
        """
        # Setup Context
        ctx = MagicMock(spec=RunContext)
        ctx.state = {"raw_text": "John Doe, Python Developer"}

        # Run (await because the agent is async)
        result = await agent.run(ctx)

        # Assertion 1: Check return value
        assert "prompt" in result
        assert "Extract profile information" in result["prompt"]
        assert "John Doe, Python Developer" in result["prompt"]

        # Assertion 2: Check state update
        assert ctx.state["prompt"] == result["prompt"]

    @pytest.mark.asyncio
    async def test_run_missing_raw_text(self, agent):
        """
        Scenario: 'raw_text' is missing from state.
        Expected: Raises ValueError.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {}  # Empty state

        with pytest.raises(ValueError, match="raw_text` is missing"):
            await agent.run(ctx)

    @pytest.mark.asyncio
    async def test_run_invalid_input_type(self, agent):
        """
        Scenario: 'raw_text' is not a string (e.g., None or int).
        Expected: Raises ValueError.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {"raw_text": 12345}  # Invalid type

        with pytest.raises(ValueError, match="raw_text` is missing or invalid"):
            await agent.run(ctx)
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# ------------------- PATH FIX -------------------
# Add the 'agents' folder to Python's search path.
# This ensures 'from core.gemini_agent import ...' works 
# regardless of where you run the test from.
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_path = os.path.join(current_dir, "../agents")
sys.path.insert(0, agents_path)
# ------------------------------------------------

from agno.run import RunContext
# Now this import will work successfully
from agents.core.gemini_agent import GeminiAgent

class TestGeminiAgent:

    @pytest.fixture
    def mock_context(self):
        """Creates a fake context with a prompt ready."""
        ctx = MagicMock(spec=RunContext)
        ctx.state = {"prompt": "Generate a profile for Arjun"}
        return ctx

    @pytest.fixture
    def agent(self):
        """Initializes the agent but prevents real API connection during init."""
        # Patching 'core.gemini_agent.Gemini' prevents the real API call
        with patch("core.gemini_agent.Gemini"):
            return GeminiAgent()

    def test_run_success_clean_json(self, agent, mock_context):
        """Scenario: LLM returns perfect JSON."""
        fake_response = MagicMock()
        
        # Simulate the object structure your agent expects
        # MUST include 'name' and 'role' to pass validation
        fake_response.content = '{"name": "Arjun", "role": "Dev"}'
        fake_response.text = fake_response.content
        
        with patch("agno.agent.Agent.run", return_value=fake_response) as mock_super_run:
            try:
                # Execute
                agent.run(mock_context)
                
                # Assertions
                mock_super_run.assert_called_once()
                # Verify that it didn't crash
            except Exception as e:
                pytest.fail(f"Agent crashed with valid input: {e}")

    def test_run_success_markdown_json(self, agent, mock_context):
        """Scenario: LLM wraps JSON in markdown."""
        fake_response = MagicMock()
        
        # --- FIX: Added "role" field so validation passes ---
        fake_response.content = '```json\n{"name": "Sarah", "role": "Data Scientist"}\n```'
        fake_response.text = fake_response.content
        
        with patch("agno.agent.Agent.run", return_value=fake_response):
            try:
                agent.run(mock_context)
            except Exception as e:
                pytest.fail(f"Agent failed to parse markdown JSON: {e}")

    def test_missing_prompt_raises_error(self, agent):
        """Scenario: Context has no prompt."""
        ctx = MagicMock(spec=RunContext)
        ctx.state = {}  # Empty state
        
        with pytest.raises(ValueError, match="Prompt missing"):
            agent.run(ctx)

    def test_empty_llm_response(self, agent, mock_context):
        """Scenario: LLM returns None or empty string."""
        fake_response = MagicMock()
        fake_response.content = None
        fake_response.text = ""

        with patch("agno.agent.Agent.run", return_value=fake_response):
            with pytest.raises(ValueError, match="Empty response"):
                agent.run(mock_context)
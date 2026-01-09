import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch
from pathlib import Path

# ------------------- PATH FIX -------------------
# Ensures 'core' can be imported from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_path = os.path.join(current_dir, "../agents")
sys.path.insert(0, agents_path)
# ------------------------------------------------

from agno.run import RunContext
# Adjust import path as necessary
from agents.core.template_selector_agent import TemplateSelectorAgent

class TestTemplateSelectorAgent:

    # --- Fixture 1: Fake Registry Data ---
    @pytest.fixture
    def mock_registry_json(self):
        """Returns a valid JSON string simulating registry.json"""
        return json.dumps({
            "minimalist": {
                "id": "minimalist",
                "name": "Clean & Simple",
                "tags": ["writer", "simple"]
            },
            "tech_modern": {
                "id": "tech_modern",
                "name": "Tech Modern",
                "tags": ["developer", "data"]
            },
            "creative_bold": {
                "id": "creative_bold",
                "name": "Bold Creative",
                "tags": ["designer", "artist"]
            }
        })

    # --- Fixture 2: Initialized Agent with Fake File ---
    @pytest.fixture
    def agent(self, mock_registry_json):
        """
        Initializes agent but tricks it into reading our fake JSON string
        instead of a real file on disk.
        """
        # We mock Path.exists to return True
        # We mock Path.read_text to return our JSON string
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=mock_registry_json):
            
            # Initialize with a dummy path; the mock handles the rest
            return TemplateSelectorAgent(registry_path="dummy_registry.json")

    @pytest.mark.asyncio
    async def test_run_flow_success(self, agent):
        """
        Scenario: 'profile' exists in state.
        Expected: Calls selection logic and updates state.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "profile": {
                "role": "Backend Dev",
                "skills": ["Python", "Docker"]
            }
        }

        # Since we don't have the full _select_template logic in your snippet,
        # we assume it returns a valid dict based on the registry.
        # We mock the internal _select_template method to test the `run` flow specifically.
        fake_template = {"id": "tech_modern", "name": "Tech Modern"}
        
        with patch.object(agent, '_select_template', return_value=fake_template) as mock_select:
            result = await agent.run(ctx)
            
            # Assertions
            assert result == fake_template
            assert ctx.state["template"] == fake_template
            mock_select.assert_called_once_with(ctx.state["profile"])

    @pytest.mark.asyncio
    async def test_run_missing_profile_raises_error(self, agent):
        """
        Scenario: 'profile' key is missing from context.
        Expected: ValueError.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {} # Empty state

        with pytest.raises(ValueError, match="profile` missing"):
            await agent.run(ctx)

    def test_init_raises_error_if_file_missing(self):
        """
        Scenario: Registry file does not exist.
        Expected: FileNotFoundError.
        """
        # Patch exists() to return False
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Template registry not found"):
                TemplateSelectorAgent(registry_path="missing_file.json")

    def test_init_raises_error_on_bad_json(self):
        """
        Scenario: Registry file exists but contains broken JSON.
        Expected: ValueError (wrapping the JSONDecodeError).
        """
        bad_json_content = "{ 'broken': " # Missing closing brace
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=bad_json_content):
             
            with pytest.raises(ValueError, match="Invalid JSON"):
                TemplateSelectorAgent(registry_path="bad_file.json")
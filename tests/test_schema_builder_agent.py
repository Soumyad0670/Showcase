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
# Adjust import if your file name is different (e.g., schema_builder.py)
from agents.core.schema_builder import SchemaBuilderAgent

class TestSchemaBuilderAgent:

    @pytest.fixture
    def agent(self):
        return SchemaBuilderAgent()

    @pytest.mark.asyncio
    async def test_run_success_full_profile(self, agent):
        """
        Scenario: Complete profile with all fields.
        Expected: Full schema with all sections populated.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "profile": {
                "name": "Arjun",
                "role": "DevOps Engineer",
                "skills": ["Python", "Docker", "AWS"],
                "experience_years": 5,
                "projects": [{"title": "Cloud Migration", "description": "Moved to AWS"}]
            }
        }

        # Run agent
        schema = await agent.run(ctx)

        # Assertions
        assert ctx.state["schema"] == schema
        assert schema["hero"]["name"] == "Arjun"
        assert schema["hero"]["tagline"] == "DevOps Engineer with 5+ years experience"
        assert schema["generation_flags"]["hero"] is True
        assert len(schema["projects"]) == 1
        assert schema["projects"][0]["title"] == "Cloud Migration"

    @pytest.mark.asyncio
    async def test_run_missing_profile_raises_error(self, agent):
        """
        Scenario: 'profile' key is missing in state.
        Expected: ValueError.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {} # Empty state

        with pytest.raises(ValueError, match="profile` missing"):
            await agent.run(ctx)

    @pytest.mark.asyncio
    async def test_skill_categorization_logic(self, agent):
        """
        Scenario: Profile has mixed skills.
        Expected: Skills sorted into correct categories (languages, tools, etc).
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "profile": {
                "name": "Test User",
                "skills": ["Python", "React", "Docker", "UnknownTool"]
            }
        }

        schema = await agent.run(ctx)
        cats = schema["skills"]["categories"]

        assert "Python" in cats["languages"]
        assert "React" in cats["frameworks"]
        assert "Docker" in cats["tools"]
        assert "UnknownTool" in cats["other"]

    @pytest.mark.asyncio
    async def test_projects_string_conversion(self, agent):
        """
        Scenario: Projects are strings (not dicts).
        Expected: Converted to dicts with 'title' set to the string.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "profile": {
                "name": "Test User",
                "projects": ["Simple Project A", "Simple Project B"]
            }
        }

        schema = await agent.run(ctx)
        projects = schema["projects"]

        assert len(projects) == 2
        assert projects[0]["title"] == "Simple Project A"
        assert projects[0]["id"] == "project_0"
        # Ensure description is empty string, not None or missing
        assert projects[0]["description"] == ""

    @pytest.mark.asyncio
    async def test_hero_tagline_no_experience(self, agent):
        """
        Scenario: Experience is 0 or missing.
        Expected: Tagline contains ONLY role, no 'years experience' text.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "profile": {
                "name": "Junior",
                "role": "Intern",
                "experience_years": 0
            }
        }

        schema = await agent.run(ctx)
        
        # Should NOT say "with 0+ years experience"
        assert schema["hero"]["tagline"] == "Intern"
import pytest
from unittest.mock import MagicMock
# Assuming your agent is in a file named data_agent.py
from agents.core.data_agent import DataAgent

class TestDataAgent:
    
    @pytest.fixture
    def agent(self):
        """Initialize the agent."""
        return DataAgent()

    @pytest.fixture
    def mock_context(self):
        """Mock the Agno RunContext."""
        ctx = MagicMock()
        # State is usually a dict in these frameworks
        ctx.state = {} 
        return ctx

    def test_missing_input_raises_error(self, agent, mock_context):
        """Test that missing 'input' key raises ValueError."""
        # state is empty
        with pytest.raises(ValueError, match="Missing 'input'"):
            agent.run(mock_context)

    def test_dictionary_normalization_and_sorting(self, agent, mock_context):
        """Test that dicts are formatted 'k: v' and keys are sorted."""
        mock_context.state["input"] = {"zulu": "last", "alpha": "first"}
        
        agent.run(mock_context)
        
        expected = "alpha: first\nzulu: last"
        assert mock_context.state["raw_text"] == expected

    def test_string_stripping(self, agent, mock_context):
        """Test that whitespace is stripped from string inputs."""
        mock_context.state["input"] = "   dirty input   "
        
        agent.run(mock_context)
        
        assert mock_context.state["raw_text"] == "dirty input"

    def test_non_dict_types(self, agent, mock_context):
        """Test integers, floats, and lists."""
        inputs = [
            (123, "123"),
            (45.67, "45.67"),
            (["a", "b"], "['a', 'b']")
        ]
        
        for input_val, expected_str in inputs:
            mock_context.state["input"] = input_val
            agent.run(mock_context)
            assert mock_context.state["raw_text"] == expected_str

    def test_nested_dictionary_handling(self, agent, mock_context):
        """
        CRITICAL: Verifying behavior for nested dicts.
        The current code does NOT recursively format, it just stringifies the sub-dict.
        """
        mock_context.state["input"] = {"meta": {"id": 1, "status": "ok"}}
        
        agent.run(mock_context)
        
        # This asserts the current behavior (shallow stringify)
        # If the requirement changes to deep cleaning, this test will fail (which is good).
        expected = "meta: {'id': 1, 'status': 'ok'}"
        assert mock_context.state["raw_text"] == expected
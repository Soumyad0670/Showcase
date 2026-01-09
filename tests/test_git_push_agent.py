import pytest
import sys
import os
import subprocess
from unittest.mock import MagicMock, patch
from pathlib import Path

# ------------------- PATH FIX -------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_path = os.path.join(current_dir, "../agents")
sys.path.insert(0, agents_path)
# ------------------------------------------------

from agno.run import RunContext
# Adjust import to match your file name
from agents.core.git_push_agent import GitPushAgent, GitPushAgentAdvanced

class TestGitPushAgent:
    
    @pytest.fixture
    def mock_subprocess(self):
        """Mocks subprocess.run globally for the test execution."""
        with patch("subprocess.run") as mock:
            # Default behavior: Success with empty output
            mock.return_value.stdout = ""
            mock.return_value.returncode = 0
            yield mock

    @pytest.fixture
    def mock_path_exists(self):
        """Mocks Path.exists to always return True."""
        with patch("pathlib.Path.exists", return_value=True) as mock:
            yield mock

    @pytest.fixture
    def agent(self):
        return GitPushAgent()

    def test_ensure_git_repo_success(self, agent, mock_subprocess):
        """Scenario: We are inside a git repo."""
        agent._ensure_git_repo()
        mock_subprocess.assert_called_with(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True, capture_output=True, text=True
        )

    def test_ensure_git_repo_fails(self, agent, mock_subprocess):
        """Scenario: Not a git repo."""
        # Simulate git command failure
        mock_subprocess.side_effect = subprocess.CalledProcessError(128, "cmd")
        
        with pytest.raises(RuntimeError, match="Not inside a git repository"):
            agent._ensure_git_repo()

    def test_run_success_flow(self, agent, mock_subprocess, mock_path_exists):
        """
        Scenario: File exists, changes detected, commit & push succeed.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "final_output": "portfolio.html",
            "profile": {"name": "Arjun"}
        }

        # Setup mock for 'git status' to return changes (so it proceeds to commit)
        # We need side_effect to return different things for different calls if needed
        # But simple way: make sure 'git status' returns something stringy
        mock_subprocess.return_value.stdout = "M portfolio.html"

        agent.run(ctx)

        # Verify key commands
        # 1. Add
        mock_subprocess.assert_any_call(
            ["git", "add", "portfolio.html"], 
            check=True, capture_output=True, text=True
        )
        # 2. Commit
        mock_subprocess.assert_any_call(
            ["git", "commit", "-m", "Add portfolio for Arjun"], 
            check=True, capture_output=True, text=True
        )
        # 3. Push
        mock_subprocess.assert_any_call(
            ["git", "push"], 
            check=True, capture_output=True, text=True
        )
        
        assert ctx.state["git_status"] == "✅ Pushed to GitHub"

    def test_run_no_changes_to_commit(self, agent, mock_subprocess, mock_path_exists):
        """
        Scenario: git status returns empty (no changes).
        Expected: Skip commit/push, update status to info.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "final_output": "portfolio.html",
            "profile": {"name": "Arjun"}
        }

        # Simulate empty status output
        mock_subprocess.return_value.stdout = "" 

        agent.run(ctx)

        # Ensure commit was NOT called
        # We check that 'git commit' was never in the call args list
        for call in mock_subprocess.call_args_list:
            args = call[0][0] # extract the command list
            assert "commit" not in args
            assert "push" not in args

        assert ctx.state["git_status"] == "ℹ️ No changes to commit"

    def test_missing_output_file_raises_error(self, agent, mock_subprocess):
        """Scenario: final_output missing in state."""
        ctx = MagicMock(spec=RunContext)
        ctx.state = {} 

        with pytest.raises(ValueError, match="No output file"):
            agent.run(ctx)

    def test_file_not_found_on_disk(self, agent, mock_subprocess):
        """Scenario: File is in state, but not on disk."""
        ctx = MagicMock(spec=RunContext)
        ctx.state = {"final_output": "ghost.html"}

        # Force Path.exists to return False
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                agent.run(ctx)

class TestGitPushAgentAdvanced:

    @pytest.fixture
    def agent(self):
        return GitPushAgentAdvanced(branch_name="test-portfolio", enable_gh_pages=False)

    def test_advanced_branch_creation(self, agent):
        """
        Scenario: Run advanced agent.
        Expected: Creates branch formatted as 'branch-name-username'.
        """
        ctx = MagicMock(spec=RunContext)
        ctx.state = {
            "final_output": "index.html",
            "profile": {"name": "John Doe"}
        }

        with patch("subprocess.run") as mock_run, \
             patch("pathlib.Path.exists", return_value=True):
            
            # Simulate 'git status' having changes
            mock_run.return_value.stdout = "M index.html"
            
            agent.run(ctx)

            expected_branch = "test-portfolio-john-doe"

            # Check checkout/branch creation
            # We look for the call: ['git', 'checkout', '-b', 'test-portfolio-john-doe']
            # OR ['git', 'checkout', 'test-portfolio-john-doe'] (if it exists)
            # Since we didn't mock 'git branch --list' specifically, we can just check if
            # checkout was called with the correct branch name.
            
            checkout_calls = [
                call[0][0] for call in mock_run.call_args_list 
                if "checkout" in call[0][0] and expected_branch in call[0][0]
            ]
            assert len(checkout_calls) > 0

            # Verify Push upstream
            mock_run.assert_any_call(
                ["git", "push", "-u", "origin", expected_branch],
                check=True, capture_output=True, text=True
            )
            
            assert ctx.state["git_branch"] == expected_branch
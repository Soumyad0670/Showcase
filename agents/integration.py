"""
Main integration layer between backend services and the agent system.

Responsibilities:
- Validate inputs
- Invoke orchestrator pipeline
- Handle errors cleanly
- Provide async + sync APIs
- Act as the single entry point for agent usage
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional, Tuple

from agents.orchestrator import get_orchestrator, PortfolioOrchestrator

# Logging

logger = logging.getLogger("agents.integration")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Domain Exceptions

class PortfolioError(Exception):
    """Base exception for portfolio-related failures."""


class ValidationError(PortfolioError):
    """Raised when input validation fails."""


class GenerationError(PortfolioError):
    """Raised when portfolio generation fails."""


class ConfigurationError(PortfolioError):
    """Raised when configuration is invalid."""


# Validation

def validate_input(parsed_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Lightweight validation before running the pipeline.
    """

    if not isinstance(parsed_data, dict):
        return False, "parsed_data must be a dictionary"

    if not parsed_data.get("name") and not parsed_data.get("email"):
        return False, "At least one of 'name' or 'email' is required"

    has_core_content = any(
        parsed_data.get(key)
        for key in ("skills", "projects", "experience")
    )

    if not has_core_content:
        return False, (
            "At least one of 'skills', 'projects', or 'experience' must be provided"
        )

    return True, None


# Core Async APIs

async def generate_portfolio(
    parsed_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a complete portfolio configuration from parsed resume data.
    """

    is_valid, error = validate_input(parsed_data)
    if not is_valid:
        logger.warning("Input validation failed: %s", error)
        raise ValidationError(error)

    try:
        logger.info("Starting portfolio generation")

        orchestrator: PortfolioOrchestrator = get_orchestrator(config)
        portfolio = await orchestrator.process_resume(parsed_data)

        logger.info("Portfolio generation completed successfully")
        return portfolio

    except ValidationError:
        raise

    except Exception as exc:
        logger.exception("Portfolio generation failed")
        raise GenerationError(str(exc)) from exc


async def regenerate_section(
    current_portfolio: Dict[str, Any],
    section: str,
    preferences: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Regenerate a specific section of an existing portfolio.
    """

    if not isinstance(current_portfolio, dict):
        raise ValidationError("current_portfolio must be a dictionary")

    if not section:
        raise ValidationError("section must be provided")

    try:
        logger.info("Regenerating section: %s", section)

        orchestrator: PortfolioOrchestrator = get_orchestrator(config)
        updated_portfolio = await orchestrator.regenerate_section(
            current_portfolio=current_portfolio,
            section=section,
            preferences=preferences or {},
        )

        logger.info("Section '%s' regenerated successfully", section)
        return updated_portfolio

    except ValidationError:
        raise

    except Exception as exc:
        logger.exception("Section regeneration failed")
        raise GenerationError(str(exc)) from exc


async def export_portfolio(
    portfolio: Dict[str, Any],
    format: str = "json",
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Export a portfolio to a supported format.
    """

    if not isinstance(portfolio, dict):
        raise ValidationError("portfolio must be a dictionary")

    if format not in {"json", "yaml", "html_preview"}:
        raise ValidationError(f"Unsupported export format: {format}")

    try:
        orchestrator: PortfolioOrchestrator = get_orchestrator(config)
        output = await orchestrator.export_portfolio(portfolio, format)

        logger.info("Portfolio exported as %s", format)
        return output

    except Exception as exc:
        logger.exception("Portfolio export failed")
        raise GenerationError(str(exc)) from exc


# Sync Wrappers 
def _run_async(coro):
    """
    Safe asyncio runner for sync contexts.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()

    return asyncio.run(coro)


def generate_portfolio_sync(
    parsed_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _run_async(generate_portfolio(parsed_data, config))


def regenerate_section_sync(
    current_portfolio: Dict[str, Any],
    section: str,
    preferences: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _run_async(
        regenerate_section(current_portfolio, section, preferences, config)
    )


def export_portfolio_sync(
    portfolio: Dict[str, Any],
    format: str = "json",
    config: Optional[Dict[str, Any]] = None,
) -> str:
    return _run_async(export_portfolio(portfolio, format, config))

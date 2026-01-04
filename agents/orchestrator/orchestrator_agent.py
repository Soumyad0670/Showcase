"""
ORCHESTRATOR.PY
===============

Central coordinator for the Showcase AI agent pipeline.

Pipeline:
1. Data preprocessing
2. Schema building
3. Content generation
4. Validation & enhancement

This module owns:
- Execution order
- Error boundaries
- Agent composition
- Regeneration logic
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from agents.middleware.data_preprocessor import DataPreprocessor
from agents.core.schema_builder import SchemaBuilder
from agents.generation.content_generator import ContentGenerator
from agents.validation.validator import PortfolioValidator

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logger = logging.getLogger("agents.orchestrator")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class OrchestratorError(Exception):
    """Base orchestrator error."""


class PipelineStageError(OrchestratorError):
    """Raised when a pipeline stage fails."""


class ValidationError(OrchestratorError):
    """Raised when validation fails."""


# ---------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------

class PortfolioOrchestrator:
    """
    Coordinates all agents to produce a final portfolio.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

        self.preprocessor = DataPreprocessor(
            self.config.get("preprocessing", {})
        )
        self.schema_builder = SchemaBuilder(
            self.config.get("schema", {})
        )
        self.content_generator = ContentGenerator(
            self.config.get("generation", {})
        )
        self.validator = PortfolioValidator(
            self.config.get("validation", {})
        )

        logger.info("PortfolioOrchestrator initialized")

    # -----------------------------------------------------------------
    # Main Pipeline
    # -----------------------------------------------------------------

    async def process_resume(
        self,
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the full portfolio generation pipeline.
        """

        started_at = datetime.utcnow()

        try:
            logger.info("Pipeline started")

            # 1. Preprocess
            preprocessed = await self.preprocessor.preprocess(parsed_data)

            # 2. Schema
            schema = await self.schema_builder.build_schema(preprocessed)

            # 3. Generation
            generated = await self.content_generator.generate(
                schema=schema,
                user_data=preprocessed,
                preferences=user_preferences,
            )

            # 4. Validation
            validated = await self.validator.validate_and_enhance(
                generated,
                original_data=preprocessed,
            )

            validated["metadata"] = {
                "generated_at": started_at.isoformat() + "Z",
                "pipeline": "showcase-ai",
                "version": "1.0.0",
            }

            logger.info("Pipeline completed successfully")
            return validated

        except ValidationError:
            raise

        except Exception as exc:
            logger.exception("Pipeline failed")
            raise PipelineStageError(str(exc)) from exc

    # -----------------------------------------------------------------
    # Section Regeneration
    # -----------------------------------------------------------------

    async def regenerate_section(
        self,
        portfolio: Dict[str, Any],
        section: str,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Regenerate a specific section (hero, bio, project index, etc).
        """

        if not section:
            raise ValidationError("section must be provided")

        logger.info("Regenerating section: %s", section)

        context = self._extract_context(portfolio, section)

        new_content = await self.content_generator.regenerate_section(
            section=section,
            context=context,
            preferences=preferences,
        )

        updated = self._update_section(portfolio, section, new_content)

        validated = await self.validator.validate_section(
            updated,
            section,
        )

        validated.setdefault("metadata", {})
        validated["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"

        return validated

    # -----------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------

    async def export_portfolio(
        self,
        portfolio: Dict[str, Any],
        format: str = "json",
    ) -> str:
        """
        Export portfolio to supported formats.
        """

        if format == "json":
            return json.dumps(portfolio, indent=2, ensure_ascii=False)

        if format == "yaml":
            try:
                import yaml
            except ImportError as exc:
                raise OrchestratorError("PyYAML not installed") from exc

            return yaml.dump(
                portfolio,
                allow_unicode=True,
                sort_keys=False,
            )

        if format == "html_preview":
            return self._generate_html_preview(portfolio)

        raise ValidationError(f"Unsupported export format: {format}")

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _extract_context(
        self,
        portfolio: Dict[str, Any],
        section: str,
    ) -> Dict[str, Any]:
        return {
            "section": section,
            "current_content": portfolio.get(section),
            "profile": {
                "name": portfolio.get("hero", {}).get("name"),
                "skills": portfolio.get("skills", []),
            },
        }

    def _update_section(
        self,
        portfolio: Dict[str, Any],
        section: str,
        content: Any,
    ) -> Dict[str, Any]:
        updated = dict(portfolio)
        updated[section] = content
        return updated

    def _generate_html_preview(self, portfolio: Dict[str, Any]) -> str:
        hero = portfolio.get("hero", {})
        bio = portfolio.get("bio", "")
        projects = portfolio.get("projects", [])

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{hero.get("name", "Portfolio")}</title>
</head>
<body>
  <h1>{hero.get("name", "")}</h1>
  <p>{hero.get("tagline", "")}</p>

  <h2>About</h2>
  <p>{bio}</p>

  <h2>Projects</h2>
  {"".join(f"<h3>{p.get('title')}</h3><p>{p.get('description')}</p>" for p in projects)}
</body>
</html>
"""


# ---------------------------------------------------------------------
# Singleton Access
# ---------------------------------------------------------------------

_orchestrator: Optional[PortfolioOrchestrator] = None
_lock = asyncio.Lock()


async def get_orchestrator(
    config: Optional[Dict[str, Any]] = None,
    force_new: bool = False,
) -> PortfolioOrchestrator:
    global _orchestrator

    async with _lock:
        if _orchestrator is None or force_new:
            _orchestrator = PortfolioOrchestrator(config)
            logger.info("Created orchestrator instance")

        return _orchestrator

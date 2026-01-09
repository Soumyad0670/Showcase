from agno.agent import Agent
from agno.run import RunContext
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class TemplateSelectorAgent(Agent):
    name = "template_selector_agent"

    def __init__(self, registry_path: str | Path | None = None):
        super().__init__()

        # --- FIX 1: DYNAMIC PATH RESOLUTION (Server Safe) ---
        if registry_path is None:
            # Go up 3 levels to find the root folder
            base_dir = Path(__file__).resolve().parent.parent.parent
            registry_path = base_dir / "templates" / "registry.json"

        registry_path = Path(registry_path).resolve()

        if not registry_path.exists():
            raise FileNotFoundError(f"Template registry not found at: {registry_path}")

        try:
            # Load the entire JSON object
            self.full_registry = json.loads(
                registry_path.read_text(encoding="utf-8")
            )
            # Create a quick lookup dictionary for templates by ID
            self.templates_map = {t['id']: t for t in self.full_registry.get('templates', [])}
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in registry file: {registry_path}") from e

    async def run(self, ctx: RunContext):
        profile = ctx.state.get("profile")

        if not profile or not isinstance(profile, dict):
            # Log warning but don't crash, create a dummy profile to force fallback
            logger.warning("Profile missing. Using empty profile.")
            profile = {}

        template = self._select_template(profile)
        
        # Save to state
        ctx.state["template"] = template
        return template

    def _select_template(self, profile: dict) -> dict:
        """
        Selects a template using the logic defined in registry.json
        """
        # 1. Extract User Data
        user_role = profile.get("role", "").lower()
        user_industry = profile.get("industry", "").lower()
        user_skills = set(s.lower() for s in profile.get("skills", []))

        # 2. Get Selection Criteria from JSON
        criteria = self.full_registry.get("selectionCriteria", {})
        
        # --- STRATEGY A: Check by ROLE ---
        by_role = criteria.get("byRole", {})
        for role_key, recommended_ids in by_role.items():
            if role_key in user_role:
                # Found a match! (e.g., 'developer' in 'Software Developer')
                logger.info(f"Matched Role '{role_key}'. Suggesting: {recommended_ids[0]}")
                return self._get_template_by_id(recommended_ids[0])

        # --- STRATEGY B: Check by INDUSTRY ---
        by_industry = criteria.get("byIndustry", {})
        for ind_key, recommended_ids in by_industry.items():
            if ind_key in user_industry:
                logger.info(f"Matched Industry '{ind_key}'. Suggesting: {recommended_ids[0]}")
                return self._get_template_by_id(recommended_ids[0])

        # --- STRATEGY C: Simple Skill Keyword Matching ---
        # If they have "research" or "publications" -> Academic
        if "research" in user_skills or "publications" in user_skills:
            return self._get_template_by_id("academic-researcher")
        
        # If they have "figma" or "photoshop" -> Creative
        if "figma" in user_skills or "design" in user_skills:
             return self._get_template_by_id("creative-bold")

        # --- STRATEGY D: FALLBACK ---
        # Get fallback from JSON or hardcode safety net
        fallback_id = self.full_registry.get("aiSelectionGuidelines", {}).get("fallback", "modern-minimal")
        logger.info(f"No specific match found. Using fallback: {fallback_id}")
        
        return self._get_template_by_id(fallback_id)

    def _get_template_by_id(self, template_id: str) -> dict:
        """Helper to safely retrieve a template object"""
        template = self.templates_map.get(template_id)
        if template:
            return template
        
        # Absolute safety net: If the ID in the rules doesn't exist, return the first available template
        logger.warning(f"Template ID '{template_id}' not found in templates list. Returning first available.")
        return list(self.templates_map.values())[0]
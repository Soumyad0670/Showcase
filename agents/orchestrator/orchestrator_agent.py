


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  VISIT AGENTS_README.md in main agents folder before going to the code 

"""
ORCHESTRATOR.PY - Main Agent Orchestration System
==================================================

PURPOSE:
This file is the brain of the Showcase application's agent system. It coordinates
all the different AI agents to transform a parsed resume into a complete portfolio.

DATA FLOW:
1. Receives: Parsed resume data (JSON) containing name, skills, projects, etc.
2. Coordinates: Multiple specialized agents (schema builder, content generator, validator)
3. Outputs: Complete portfolio configuration ready for frontend rendering

HOW IT WORKS:
- Acts as a conductor, calling different agents in sequence
- Manages state between agent calls
- Handles errors and retries
- Ensures data consistency across the pipeline

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""

import logging
from typing import Dict, Any, Optional
import json
from datetime import datetime

from agents.core.schema_builder import SchemaBuilder
from agents.generation.content_generator import ContentGenerator
from agents.validation.validator import PortfolioValidator
from agents.middleware.data_preprocessor import DataPreprocessor

logger = logging.getLogger(__name__)


class PortfolioOrchestrator:
    """
    Main orchestrator that coordinates all agents to build a portfolio.
    
    This class manages the entire pipeline from parsed resume to final portfolio:
    - Preprocesses and validates input data
    - Builds structured schema
    - Generates content using LLMs
    - Validates output quality
    - Handles errors and logging
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with all required agents.
        
        Args:
            config: Configuration dictionary for agent behaviors
        """
        self.config = config or {}
        
        # Initialize all specialized agents
        self.preprocessor = DataPreprocessor(self.config.get('preprocessing', {}))
        self.schema_builder = SchemaBuilder(self.config.get('schema', {}))
        self.content_generator = ContentGenerator(self.config.get('generation', {}))
        self.validator = PortfolioValidator(self.config.get('validation', {}))
        
        logger.info("PortfolioOrchestrator initialized successfully")
    
    async def process_resume(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main pipeline execution method.
        
        This method orchestrates the entire transformation:
        1. Preprocess and normalize data
        2. Build structured schema
        3. Generate content using LLMs
        4. Validate and enhance output
        5. Return complete portfolio configuration
        
        Args:
            parsed_data: Dictionary containing:
                - name: User's full name
                - email: Contact email
                - skills: List of skills
                - projects: List of project descriptions
                - experience: Work experience entries
                - education: Educational background
        
        Returns:
            Complete portfolio configuration ready for frontend:
                - hero: Hero section content
                - bio: Generated biography
                - projects: Enhanced project entries
                - skills: Categorized skills
                - layout: Layout recommendations
                - theme: Visual theme suggestions
        """
        try:
            logger.info(f"Starting portfolio generation for: {parsed_data.get('name', 'Unknown')}")
            
            # STEP 1: Preprocess input data
            # Clean, normalize, and enrich the parsed resume data
            preprocessed_data = await self.preprocessor.preprocess(parsed_data)
            logger.info("✓ Data preprocessing complete")
            
            # STEP 2: Build portfolio schema
            # Create structured schema with hero line, bio template, project structure
            schema = await self.schema_builder.build_schema(preprocessed_data)
            logger.info("✓ Schema building complete")
            
            # STEP 3: Generate content using Gemini
            # Use constrained generation to fill in creative content
            generated_content = await self.content_generator.generate(
                schema=schema,
                user_data=preprocessed_data
            )
            logger.info("✓ Content generation complete")
            
            # STEP 4: Validate and enhance
            # Check quality, consistency, and enhance if needed
            validated_portfolio = await self.validator.validate_and_enhance(
                generated_content,
                original_data=preprocessed_data
            )
            logger.info("✓ Validation and enhancement complete")
            
            # Add metadata
            validated_portfolio['metadata'] = {
                'generated_at': datetime.utcnow().isoformat(),
                'version': '1.0',
                'pipeline': 'showcase-ai'
            }
            
            logger.info("Portfolio generation completed successfully")
            return validated_portfolio
            
        except Exception as e:
            logger.error(f"Error in portfolio generation pipeline: {str(e)}")
            raise
    
    async def regenerate_section(
        self, 
        portfolio: Dict[str, Any], 
        section: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Regenerate a specific section of the portfolio.
        
        Useful for iterative refinement when user wants to change:
        - Hero line
        - Bio
        - Specific project descriptions
        
        Args:
            portfolio: Current portfolio configuration
            section: Section name to regenerate ('hero', 'bio', 'project_0', etc.)
            preferences: User preferences for regeneration
        
        Returns:
            Updated portfolio with regenerated section
        """
        try:
            logger.info(f"Regenerating section: {section}")
            
            # Extract relevant context
            context = self._extract_section_context(portfolio, section)
            
            # Regenerate using content generator
            new_content = await self.content_generator.regenerate_section(
                section=section,
                context=context,
                preferences=preferences
            )
            
            # Update portfolio
            updated_portfolio = self._update_portfolio_section(
                portfolio, 
                section, 
                new_content
            )
            
            # Validate updated section
            validated = await self.validator.validate_section(
                updated_portfolio,
                section
            )
            
            logger.info(f"✓ Section '{section}' regenerated successfully")
            return validated
            
        except Exception as e:
            logger.error(f"Error regenerating section '{section}': {str(e)}")
            raise
    
    def _extract_section_context(
        self, 
        portfolio: Dict[str, Any], 
        section: str
    ) -> Dict[str, Any]:
        """Extract relevant context for section regeneration."""
        context = {
            'section': section,
            'current_content': portfolio.get(section),
            'user_profile': {
                'name': portfolio.get('hero', {}).get('name'),
                'skills': portfolio.get('skills', []),
                'style': portfolio.get('metadata', {}).get('style_preferences')
            }
        }
        return context
    
    def _update_portfolio_section(
        self,
        portfolio: Dict[str, Any],
        section: str,
        new_content: Any
    ) -> Dict[str, Any]:
        """Update a specific section in the portfolio."""
        updated = portfolio.copy()
        
        # Handle nested sections (e.g., 'project_0')
        if '_' in section:
            parent, index = section.rsplit('_', 1)
            if parent in updated and isinstance(updated[parent], list):
                updated[parent][int(index)] = new_content
        else:
            updated[section] = new_content
        
        return updated
    
    async def export_portfolio(
        self, 
        portfolio: Dict[str, Any],
        format: str = 'json'
    ) -> str:
        """
        Export portfolio in different formats.
        
        Args:
            portfolio: Complete portfolio configuration
            format: Export format ('json', 'yaml', 'html_preview')
        
        Returns:
            Serialized portfolio data
        """
        try:
            if format == 'json':
                return json.dumps(portfolio, indent=2)
            elif format == 'yaml':
                import yaml
                return yaml.dump(portfolio, default_flow_style=False)
            elif format == 'html_preview':
                # Generate simple HTML preview
                return self._generate_html_preview(portfolio)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            logger.error(f"Error exporting portfolio: {str(e)}")
            raise
    
    def _generate_html_preview(self, portfolio: Dict[str, Any]) -> str:
        """Generate simple HTML preview of portfolio."""
        hero = portfolio.get('hero', {})
        bio = portfolio.get('bio', '')
        projects = portfolio.get('projects', [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{hero.get('name', 'Portfolio')} - Preview</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }}
                .hero {{ text-align: center; margin-bottom: 40px; }}
                .bio {{ line-height: 1.6; margin-bottom: 40px; }}
                .project {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="hero">
                <h1>{hero.get('name', 'Portfolio')}</h1>
                <p>{hero.get('tagline', '')}</p>
            </div>
            <div class="bio">
                <h2>About</h2>
                <p>{bio}</p>
            </div>
            <div class="projects">
                <h2>Projects</h2>
                {''.join(f'<div class="project"><h3>{p.get("title")}</h3><p>{p.get("description")}</p></div>' for p in projects)}
            </div>
        </body>
        </html>
        """
        return html


# Singleton instance for the application
_orchestrator_instance = None

def get_orchestrator(config: Optional[Dict[str, Any]] = None) -> PortfolioOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = PortfolioOrchestrator(config)
    return _orchestrator_instance
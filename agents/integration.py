

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  VISIT AGENTS_README.md in main agents folder before going to the code 


"""
INTEGRATION.PY - Main API Integration Point
============================================

PURPOSE:
This is the main entry point that the backend calls to use the agent system.
It provides a clean API for the rest of the application to interact with agents.

DATA FLOW:
1. Backend receives resume upload (PDF/PNG/DOCX)
2. OCR + NLP parsing extracts data
3. Backend calls this integration module
4. Agent orchestrator processes data through pipeline
5. Returns complete portfolio configuration
6. Frontend receives and renders

HOW IT WORKS:
- Provides async API functions
- Handles error cases gracefully
- Manages agent lifecycle
- Logs all operations
- Returns structured responses

USAGE:
    from agents.integration import generate_portfolio
    
    portfolio = await generate_portfolio(parsed_resume_data)

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""

import logging
from typing import Dict, Any, Optional
import asyncio

from agents.orchestrator import get_orchestrator, PortfolioOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def generate_portfolio(
    parsed_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main function to generate portfolio from parsed resume data.
    
    This is the primary API function that the backend should call.
    
    Args:
        parsed_data: Dictionary containing parsed resume data:
            - name: str
            - email: str (optional)
            - skills: List[str]
            - projects: List[Dict]
            - experience: List[Dict] (optional)
            - education: List[Dict] (optional)
            - links: Dict[str, str] (optional)
        
        config: Optional configuration dictionary:
            - gemini_api_key: str (if not in env)
            - strict_validation: bool (default: False)
            - preprocessing: Dict
            - generation: Dict
    
    Returns:
        Complete portfolio configuration:
            - hero: Dict (name, tagline, email, links)
            - bio: str (generated biography)
            - projects: List[Dict] (enhanced project descriptions)
            - skills: Dict (categorized skills)
            - layout: Dict (layout hints)
            - theme: Dict (theme suggestions)
            - metadata: Dict (generation info)
            - validation: Dict (quality scores)
    
    Raises:
        ValueError: If input data is invalid
        Exception: If generation fails
    
    Example:
        >>> parsed_data = {
        ...     'name': 'John Doe',
        ...     'email': 'john@example.com',
        ...     'skills': ['Python', 'React', 'Machine Learning'],
        ...     'projects': [
        ...         {
        ...             'title': 'AI Chatbot',
        ...             'description': 'Built a chatbot using NLP',
        ...             'technologies': ['Python', 'TensorFlow']
        ...         }
        ...     ]
        ... }
        >>> portfolio = await generate_portfolio(parsed_data)
        >>> print(portfolio['hero']['tagline'])
        'Building intelligent systems with Machine Learning'
    """
    try:
        logger.info("=" * 60)
        logger.info("STARTING PORTFOLIO GENERATION")
        logger.info("=" * 60)
        
        # Get or create orchestrator
        orchestrator = get_orchestrator(config)
        
        # Run the pipeline
        portfolio = await orchestrator.process_resume(parsed_data)
        
        logger.info("=" * 60)
        logger.info("PORTFOLIO GENERATION COMPLETE")
        logger.info("=" * 60)
        
        return portfolio
        
    except Exception as e:
        logger.error(f"Failed to generate portfolio: {str(e)}")
        raise


async def regenerate_section(
    current_portfolio: Dict[str, Any],
    section: str,
    preferences: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Regenerate a specific section of the portfolio.
    
    Useful for iterative refinement when user wants different content.
    
    Args:
        current_portfolio: Current complete portfolio
        section: Section to regenerate ('hero', 'bio', 'project_0', etc.)
        preferences: User preferences for regeneration:
            - tone: str ('professional', 'casual', 'creative')
            - style: str ('action-oriented', 'descriptive', 'technical')
            - emphasis: str ('technical', 'impact', 'creative')
            - length: str ('short', 'medium', 'long')
        config: Optional configuration
    
    Returns:
        Updated portfolio with regenerated section
    
    Example:
        >>> preferences = {'tone': 'creative', 'style': 'bold'}
        >>> updated = await regenerate_section(
        ...     portfolio, 
        ...     'hero', 
        ...     preferences
        ... )
    """
    try:
        logger.info(f"Regenerating section: {section}")
        
        orchestrator = get_orchestrator(config)
        updated_portfolio = await orchestrator.regenerate_section(
            current_portfolio,
            section,
            preferences
        )
        
        logger.info(f"Section '{section}' regenerated successfully")
        return updated_portfolio
        
    except Exception as e:
        logger.error(f"Failed to regenerate section '{section}': {str(e)}")
        raise


async def export_portfolio(
    portfolio: Dict[str, Any],
    format: str = 'json',
    config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Export portfolio in different formats.
    
    Args:
        portfolio: Complete portfolio configuration
        format: Export format ('json', 'yaml', 'html_preview')
        config: Optional configuration
    
    Returns:
        Serialized portfolio data
    
    Example:
        >>> json_str = await export_portfolio(portfolio, 'json')
        >>> with open('portfolio.json', 'w') as f:
        ...     f.write(json_str)
    """
    try:
        orchestrator = get_orchestrator(config)
        exported = await orchestrator.export_portfolio(portfolio, format)
        
        logger.info(f"Portfolio exported to {format}")
        return exported
        
    except Exception as e:
        logger.error(f"Failed to export portfolio: {str(e)}")
        raise


def validate_input(parsed_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate input data before processing.
    
    Quick validation to catch obvious issues before starting pipeline.
    
    Args:
        parsed_data: Data to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Example:
        >>> valid, error = validate_input(parsed_data)
        >>> if not valid:
        ...     return {"error": error}
    """
    # Check for required fields
    if not isinstance(parsed_data, dict):
        return False, "Input must be a dictionary"
    
    if not parsed_data.get('name') and not parsed_data.get('email'):
        return False, "Either 'name' or 'email' is required"
    
    has_content = any([
        parsed_data.get('skills'),
        parsed_data.get('projects'),
        parsed_data.get('experience')
    ])
    
    if not has_content:
        return False, "At least one of 'skills', 'projects', or 'experience' is required"
    
    return True, None


# Synchronous wrapper for non-async contexts
def generate_portfolio_sync(
    parsed_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Synchronous version of generate_portfolio.
    
    Use this if calling from synchronous code.
    
    Example:
        >>> portfolio = generate_portfolio_sync(parsed_data)
    """
    return asyncio.run(generate_portfolio(parsed_data, config))


def regenerate_section_sync(
    current_portfolio: Dict[str, Any],
    section: str,
    preferences: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Synchronous version of regenerate_section.
    
    Example:
        >>> updated = regenerate_section_sync(portfolio, 'hero', {'tone': 'creative'})
    """
    return asyncio.run(regenerate_section(current_portfolio, section, preferences, config))


# Error handling utilities
class PortfolioGenerationError(Exception):
    """Base exception for portfolio generation errors."""
    pass


class ValidationError(PortfolioGenerationError):
    """Raised when input validation fails."""
    pass


class GenerationError(PortfolioGenerationError):
    """Raised when content generation fails."""
    pass


class ConfigurationError(PortfolioGenerationError):
    """Raised when configuration is invalid."""
    pass


# Example usage and testing
async def _example_usage():
    """Example of how to use the integration API."""
    
    # Example input data
    sample_data = {
        'name': 'Alice Johnson',
        'email': 'alice.j@example.com',
        'skills': [
            'Python', 'React', 'Machine Learning', 
            'Deep Learning', 'NLP', 'TensorFlow',
            'PyTorch', 'Docker', 'AWS'
        ],
        'projects': [
            {
                'title': 'Smart Resume Parser',
                'description': 'Built an AI-powered resume parser using NLP and OCR',
                'technologies': ['Python', 'TensorFlow', 'Tesseract', 'FastAPI'],
                'links': {'github': 'https://github.com/alice/resume-parser'}
            },
            {
                'title': 'Real-time Chat App',
                'description': 'Developed a real-time chat application with WebSockets',
                'technologies': ['React', 'Node.js', 'Socket.io', 'MongoDB']
            }
        ],
        'experience': [
            {
                'company': 'Tech Startup Inc',
                'position': 'ML Engineer',
                'duration': '2022-Present',
                'description': 'Leading ML initiatives'
            }
        ],
        'education': [
            {
                'institution': 'University of Technology',
                'degree': 'B.Tech in Computer Science',
                'year': '2022'
            }
        ],
        'links': {
            'github': 'https://github.com/alice',
            'linkedin': 'https://linkedin.com/in/alice'
        }
    }
    
    # Validate input first
    is_valid, error = validate_input(sample_data)
    if not is_valid:
        print(f"Validation error: {error}")
        return
    
    # Generate portfolio
    print("Generating portfolio...")
    portfolio = await generate_portfolio(sample_data)
    
    print("\n" + "=" * 60)
    print("GENERATED PORTFOLIO")
    print("=" * 60)
    print(f"\nHero: {portfolio['hero']['name']}")
    print(f"Tagline: {portfolio['hero']['tagline']}")
    print(f"\nBio: {portfolio['bio'][:150]}...")
    print(f"\nProjects: {len(portfolio['projects'])} projects")
    print(f"Quality Score: {portfolio['validation']['overall']['score']:.2f}")
    
    # Example: Regenerate hero with different style
    print("\n" + "=" * 60)
    print("REGENERATING HERO WITH CREATIVE STYLE")
    print("=" * 60)
    
    updated = await regenerate_section(
        portfolio,
        'hero',
        preferences={'tone': 'creative', 'style': 'bold'}
    )
    
    print(f"New tagline: {updated['hero']['tagline']}")
    
    # Export to JSON
    json_export = await export_portfolio(portfolio, 'json')
    print(f"\nExported portfolio size: {len(json_export)} characters")


if __name__ == '__main__':
    # Run example
    asyncio.run(_example_usage())
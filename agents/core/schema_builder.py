

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  VISIT AGENTS_README.md in main agents folder before going to the code 

"""
SCHEMA_BUILDER.PY - Portfolio Schema Construction Agent
========================================================

PURPOSE:
This agent transforms raw parsed resume data into a structured portfolio schema.
It analyzes the user's profile and creates a blueprint for content generation.

DATA FLOW IN:
- Preprocessed resume data (name, skills, projects, experience, education)

DATA FLOW OUT:
- Structured schema with:
  * Hero line template
  * Bio structure
  * Project entries with categorization
  * Skill groupings
  * Layout hints (what to emphasize)

HOW IT WORKS:
- Analyzes user's domain (developer, designer, data scientist, etc.)
- Determines best portfolio structure for their profile
- Creates templates that the content generator will fill
- Suggests visual hierarchy and emphasis points

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""

import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)


class SchemaBuilder:
    """
    Builds structured portfolio schema from preprocessed data.
    
    This agent is responsible for:
    - Determining portfolio structure
    - Categorizing skills and projects
    - Creating content templates
    - Suggesting layout priorities
    """
    
    # Skill category mappings
    SKILL_CATEGORIES = {
        'languages': ['python', 'javascript', 'java', 'c++', 'c', 'rust', 'go', 'typescript', 'ruby', 'php', 'swift', 'kotlin'],
        'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'spring', 'nextjs', 'tensorflow', 'pytorch'],
        'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'firebase', 'dynamodb', 'cassandra'],
        'tools': ['git', 'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'jenkins', 'github actions', 'terraform'],
        'ml_ai': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'reinforcement learning', 'llm', 'transformers']
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize schema builder with configuration."""
        self.config = config
        logger.info("SchemaBuilder initialized")
    
    async def build_schema(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to build portfolio schema.
        
        Takes preprocessed resume data and creates a structured blueprint
        that guides content generation.
        
        Args:
            preprocessed_data: Clean, normalized resume data
        
        Returns:
            Schema dictionary with structure and templates
        """
        try:
            logger.info("Building portfolio schema...")
            
            # Determine user's primary domain
            domain = self._detect_domain(preprocessed_data)
            logger.info(f"Detected domain: {domain}")
            
            # Build schema components
            schema = {
                'domain': domain,
                'hero': self._build_hero_schema(preprocessed_data, domain),
                'bio': self._build_bio_schema(preprocessed_data, domain),
                'projects': self._build_projects_schema(preprocessed_data),
                'skills': self._build_skills_schema(preprocessed_data),
                'layout_hints': self._generate_layout_hints(preprocessed_data, domain),
                'theme_suggestions': self._suggest_theme(domain)
            }
            
            logger.info("Schema built successfully")
            return schema
            
        except Exception as e:
            logger.error(f"Error building schema: {str(e)}")
            raise
    
    def _detect_domain(self, data: Dict[str, Any]) -> str:
        """
        Detect user's primary professional domain.
        
        Analyzes skills, projects, and experience to categorize:
        - software_engineer
        - ml_engineer
        - data_scientist
        - frontend_developer
        - backend_developer
        - fullstack_developer
        - designer
        - researcher
        """
        skills = [s.lower() for s in data.get('skills', [])]
        projects = [p.get('description', '').lower() for p in data.get('projects', [])]
        
        # ML/AI detection
        ml_keywords = ['machine learning', 'deep learning', 'neural network', 'tensorflow', 'pytorch', 'nlp', 'computer vision']
        ml_score = sum(1 for kw in ml_keywords if any(kw in s for s in skills + projects))
        
        # Frontend detection
        frontend_keywords = ['react', 'vue', 'angular', 'css', 'html', 'ui', 'frontend']
        frontend_score = sum(1 for kw in frontend_keywords if any(kw in s for s in skills + projects))
        
        # Backend detection
        backend_keywords = ['api', 'backend', 'server', 'database', 'django', 'flask', 'express']
        backend_score = sum(1 for kw in backend_keywords if any(kw in s for s in skills + projects))
        
        # Data science detection
        data_keywords = ['data analysis', 'pandas', 'numpy', 'visualization', 'statistics']
        data_score = sum(1 for kw in data_keywords if any(kw in s for s in skills + projects))
        
        # Determine primary domain
        scores = {
            'ml_engineer': ml_score,
            'data_scientist': data_score,
            'frontend_developer': frontend_score,
            'backend_developer': backend_score
        }
        
        # Check for fullstack
        if frontend_score >= 2 and backend_score >= 2:
            return 'fullstack_developer'
        
        # Return highest scoring domain
        primary_domain = max(scores, key=scores.get)
        return primary_domain if scores[primary_domain] > 0 else 'software_engineer'
    
    def _build_hero_schema(self, data: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """
        Build hero section schema.
        
        The hero section is the first thing visitors see.
        Creates a template for the tagline/hero line.
        """
        name = data.get('name', 'Portfolio')
        
        # Hero line templates based on domain
        templates = {
            'ml_engineer': "Building intelligent systems with {primary_tech}",
            'data_scientist': "Turning data into insights and impact",
            'frontend_developer': "Crafting beautiful, responsive web experiences",
            'backend_developer': "Engineering scalable, robust server solutions",
            'fullstack_developer': "Full-stack developer bringing ideas to life",
            'software_engineer': "Software engineer passionate about {focus_area}"
        }
        
        return {
            'name': name,
            'template': templates.get(domain, templates['software_engineer']),
            'email': data.get('email'),
            'links': data.get('links', {}),
            'needs_generation': True  # Signal that LLM should generate actual tagline
        }
    
    def _build_bio_schema(self, data: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """
        Build bio/about section schema.
        
        Creates structure for a compelling bio that:
        - Introduces the person professionally
        - Highlights key achievements
        - Shows personality
        - Includes call-to-action
        """
        return {
            'structure': [
                'opening_hook',  # Engaging first sentence
                'background',    # Professional background
                'expertise',     # What they're good at
                'passion',       # What drives them
                'current_focus', # What they're working on now
                'call_to_action' # How to connect
            ],
            'tone': 'professional_friendly',
            'length_target': '150-200 words',
            'key_points': self._extract_bio_key_points(data),
            'needs_generation': True
        }
    
    def _extract_bio_key_points(self, data: Dict[str, Any]) -> List[str]:
        """Extract key points that should be in the bio."""
        points = []
        
        # Add education if present
        education = data.get('education', [])
        if education:
            latest_edu = education[0]
            points.append(f"Education: {latest_edu.get('degree', '')} {latest_edu.get('institution', '')}")
        
        # Add years of experience if calculable
        experience = data.get('experience', [])
        if experience:
            points.append(f"Experience: {len(experience)} positions")
        
        # Add project count
        projects = data.get('projects', [])
        if projects:
            points.append(f"Projects: {len(projects)} notable projects")
        
        # Add top skills
        skills = data.get('skills', [])[:5]
        if skills:
            points.append(f"Top skills: {', '.join(skills)}")
        
        return points
    
    def _build_projects_schema(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build schema for projects section.
        
        Each project gets:
        - Title
        - Enhanced description (will be generated)
        - Tech stack
        - Impact metrics (if available)
        - Links
        - Visual prominence (featured or not)
        """
        projects = data.get('projects', [])
        schema_projects = []
        
        for idx, project in enumerate(projects):
            schema_project = {
                'id': f"project_{idx}",
                'title': project.get('title', f'Project {idx + 1}'),
                'raw_description': project.get('description', ''),
                'tech_stack': project.get('technologies', []),
                'links': project.get('links', {}),
                'featured': idx < 3,  # First 3 projects are featured
                'needs_enhancement': True,  # LLM will enhance description
                'target_length': '100-150 words' if idx < 3 else '50-75 words'
            }
            schema_projects.append(schema_project)
        
        # Sort by featured status
        schema_projects.sort(key=lambda x: (not x['featured'], x['id']))
        
        return schema_projects
    
    def _build_skills_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build skills section schema.
        
        Categorizes skills into groups for better presentation:
        - Languages
        - Frameworks & Libraries
        - Tools & Platforms
        - Domains (ML/AI, etc.)
        """
        skills = data.get('skills', [])
        categorized = {category: [] for category in self.SKILL_CATEGORIES.keys()}
        categorized['other'] = []
        
        # Categorize each skill
        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False
            
            for category, keywords in self.SKILL_CATEGORIES.items():
                if any(keyword in skill_lower for keyword in keywords):
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'].append(skill)
        
        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}
        
        return {
            'categorized': categorized,
            'total_count': len(skills),
            'display_format': 'grouped_tags'  # or 'skill_bars', 'simple_list'
        }
    
    def _generate_layout_hints(self, data: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """
        Generate hints for the frontend about layout priorities.
        
        Tells the build engine what to emphasize based on profile.
        """
        hints = {
            'primary_sections': ['hero', 'projects', 'skills'],  # Always show these
            'optional_sections': [],
            'emphasis': {}
        }
        
        # Add experience section if significant
        if len(data.get('experience', [])) >= 2:
            hints['primary_sections'].insert(2, 'experience')
        else:
            hints['optional_sections'].append('experience')
        
        # Emphasis hints
        if len(data.get('projects', [])) >= 4:
            hints['emphasis']['projects'] = 'high'
        
        if domain in ['ml_engineer', 'data_scientist']:
            hints['emphasis']['technical_depth'] = 'high'
            hints['optional_sections'].append('publications')
        
        if domain in ['frontend_developer', 'designer']:
            hints['emphasis']['visual_appeal'] = 'high'
            hints['layout_style'] = 'creative'
        
        return hints
    
    def _suggest_theme(self, domain: str) -> Dict[str, Any]:
        """
        Suggest visual theme based on domain.
        
        Provides color palette and style recommendations.
        """
        themes = {
            'ml_engineer': {
                'primary_color': '#4A90E2',  # Blue
                'style': 'modern_tech',
                'font_pair': 'Inter + JetBrains Mono'
            },
            'frontend_developer': {
                'primary_color': '#F39C12',  # Orange
                'style': 'creative_bold',
                'font_pair': 'Poppins + Roboto'
            },
            'data_scientist': {
                'primary_color': '#27AE60',  # Green
                'style': 'clean_analytical',
                'font_pair': 'Roboto + Source Code Pro'
            },
            'default': {
                'primary_color': '#2C3E50',  # Dark blue-gray
                'style': 'professional_minimal',
                'font_pair': 'Open Sans + Fira Code'
            }
        }
        
        return themes.get(domain, themes['default'])
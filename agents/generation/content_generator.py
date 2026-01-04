

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  VISIT AGENTS_README.md in main agents folder before going to the code 

"""
CONTENT_GENERATOR.PY - AI Content Generation Agent (Gemini Integration)
========================================================================

PURPOSE:
This is the creative brain of the pipeline. It uses Google's Gemini LLM to generate
compelling portfolio content from the structured schema.

DATA FLOW IN:
- Portfolio schema (from schema_builder)
- User data (original preprocessed data for context)

DATA FLOW OUT:
- Complete portfolio with AI-generated content:
  * Hero tagline
  * Professional bio
  * Enhanced project descriptions
  * Section content

HOW IT WORKS:
- Uses constrained generation (not plain prompts!)
- Sends schema + strict formatting rules to Gemini
- Generates React components, Tailwind styles, config files
- Maintains consistency across all generated content
- Uses temperature control for creativity vs. accuracy balance

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""

import logging
from typing import Dict, Any, List, Optional
import json
import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    AI-powered content generator using Google Gemini.
    
    This agent is responsible for:
    - Generating compelling hero taglines
    - Writing professional bios
    - Enhancing project descriptions
    - Creating section content
    - Maintaining consistent tone and style
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize content generator with Gemini configuration."""
        self.config = config
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY') or config.get('gemini_api_key')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or config")
        
        genai.configure(api_key=api_key)
        
        # Initialize model with optimized settings
        self.model = genai.GenerativeModel(
            model_name='gemini-pro',
            generation_config={
                'temperature': 0.7,  # Balance creativity and consistency
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        logger.info("ContentGenerator initialized with Gemini")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate(
        self, 
        schema: Dict[str, Any], 
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main generation method - creates complete portfolio content.
        
        Uses constrained generation to ensure output matches schema exactly.
        
        Args:
            schema: Portfolio schema from SchemaBuilder
            user_data: Original preprocessed user data for context
        
        Returns:
            Complete portfolio with all generated content
        """
        try:
            logger.info("Starting content generation with Gemini...")
            
            portfolio = {}
            
            # Generate hero section
            portfolio['hero'] = await self._generate_hero(
                schema['hero'], 
                user_data,
                schema['domain']
            )
            logger.info("✓ Hero section generated")
            
            # Generate bio
            portfolio['bio'] = await self._generate_bio(
                schema['bio'],
                user_data,
                schema['domain']
            )
            logger.info("✓ Bio generated")
            
            # Generate/enhance projects
            portfolio['projects'] = await self._generate_projects(
                schema['projects'],
                user_data
            )
            logger.info("✓ Projects enhanced")
            
            # Include skills as-is (already structured)
            portfolio['skills'] = schema['skills']
            
            # Include layout hints and theme
            portfolio['layout'] = schema['layout_hints']
            portfolio['theme'] = schema['theme_suggestions']
            
            logger.info("Content generation completed successfully")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            raise
    
    async def _generate_hero(
        self,
        hero_schema: Dict[str, Any],
        user_data: Dict[str, Any],
        domain: str
    ) -> Dict[str, Any]:
        """
        Generate hero section with compelling tagline.
        
        The tagline should be:
        - Concise (8-15 words)
        - Impactful and memorable
        - Specific to user's domain
        - Action-oriented
        """
        skills = user_data.get('skills', [])[:5]
        projects = user_data.get('projects', [])
        
        prompt = f"""
Generate a compelling hero tagline for a {domain.replace('_', ' ')}'s portfolio.

Context:
- Name: {hero_schema.get('name')}
- Top Skills: {', '.join(skills)}
- Number of projects: {len(projects)}

Requirements:
- 8-15 words maximum
- Impactful and memorable
- Specific to their expertise
- No clichés or generic phrases
- Action-oriented language

Template inspiration: {hero_schema.get('template')}

Return ONLY the tagline, no explanation.
"""
        
        response = self.model.generate_content(prompt)
        tagline = response.text.strip().strip('"\'')
        
        return {
            'name': hero_schema.get('name'),
            'tagline': tagline,
            'email': hero_schema.get('email'),
            'links': hero_schema.get('links', {})
        }
    
    async def _generate_bio(
        self,
        bio_schema: Dict[str, Any],
        user_data: Dict[str, Any],
        domain: str
    ) -> str:
        """
        Generate professional bio following the schema structure.
        
        The bio should:
        - Be 150-200 words
        - Follow the structure: hook → background → expertise → passion → current focus
        - Sound natural and engaging
        - Include key facts from user data
        """
        key_points = bio_schema.get('key_points', [])
        
        prompt = f"""
Write a professional bio for a {domain.replace('_', ' ')}'s portfolio.

Context:
{chr(10).join(f'- {point}' for point in key_points)}

Structure to follow:
1. Opening hook (1 sentence - engaging introduction)
2. Background (1-2 sentences - professional journey)
3. Expertise (2 sentences - what they excel at)
4. Passion (1 sentence - what drives them)
5. Current focus (1 sentence - what they're working on)

Requirements:
- 150-200 words total
- Professional but friendly tone
- Natural, conversational flow
- No buzzwords or clichés
- First person voice ("I" not "they")

Return ONLY the bio text, no formatting or sections headers.
"""
        
        response = self.model.generate_content(prompt)
        bio = response.text.strip()
        
        return bio
    
    async def _generate_projects(
        self,
        projects_schema: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance project descriptions using AI.
        
        For each project:
        - Takes raw description
        - Enhances with impact language
        - Highlights technical achievements
        - Makes it more engaging
        """
        enhanced_projects = []
        
        for project in projects_schema:
            if project.get('needs_enhancement'):
                enhanced_desc = await self._enhance_project_description(
                    project['title'],
                    project['raw_description'],
                    project['tech_stack'],
                    project['target_length']
                )
            else:
                enhanced_desc = project['raw_description']
            
            enhanced_projects.append({
                'id': project['id'],
                'title': project['title'],
                'description': enhanced_desc,
                'tech_stack': project['tech_stack'],
                'links': project.get('links', {}),
                'featured': project['featured']
            })
        
        return enhanced_projects
    
    async def _enhance_project_description(
        self,
        title: str,
        raw_description: str,
        tech_stack: List[str],
        target_length: str
    ) -> str:
        """
        Enhance a single project description.
        
        Makes it more compelling while staying truthful.
        """
        prompt = f"""
Enhance this project description for a portfolio.

Project: {title}
Original description: {raw_description}
Technologies used: {', '.join(tech_stack) if tech_stack else 'Not specified'}

Requirements:
- Target length: {target_length}
- Make it more engaging and impactful
- Highlight technical achievements
- Include what problem it solved
- Mention technologies naturally
- Stay truthful to original description
- Use active, strong verbs

Return ONLY the enhanced description, no additional commentary.
"""
        
        response = self.model.generate_content(prompt)
        enhanced = response.text.strip()
        
        return enhanced
    
    async def regenerate_section(
        self,
        section: str,
        context: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Regenerate a specific section with new preferences.
        
        Used when user wants to:
        - Try a different hero tagline
        - Rewrite bio in different tone
        - Enhance project description differently
        """
        preferences = preferences or {}
        
        if section == 'hero':
            return await self._regenerate_hero(context, preferences)
        elif section == 'bio':
            return await self._regenerate_bio(context, preferences)
        elif section.startswith('project_'):
            return await self._regenerate_project(context, preferences)
        else:
            raise ValueError(f"Unknown section: {section}")
    
    async def _regenerate_hero(
        self,
        context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate hero tagline with preferences."""
        tone = preferences.get('tone', 'professional')
        style = preferences.get('style', 'action-oriented')
        
        user_profile = context.get('user_profile', {})
        
        prompt = f"""
Generate an alternative hero tagline.

Context:
- Name: {user_profile.get('name')}
- Skills: {', '.join(user_profile.get('skills', [])[:5])}

Preferences:
- Tone: {tone}
- Style: {style}

Requirements:
- 8-15 words
- Different from typical taglines
- Match the requested tone and style

Return ONLY the tagline.
"""
        
        response = self.model.generate_content(prompt)
        new_tagline = response.text.strip().strip('"\'')
        
        return {
            'name': user_profile.get('name'),
            'tagline': new_tagline
        }
    
    async def _regenerate_bio(
        self,
        context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> str:
        """Regenerate bio with different emphasis."""
        emphasis = preferences.get('emphasis', 'balanced')
        length = preferences.get('length', 'medium')
        
        current_bio = context.get('current_content', '')
        user_profile = context.get('user_profile', {})
        
        length_map = {
            'short': '100-120 words',
            'medium': '150-200 words',
            'long': '220-280 words'
        }
        
        prompt = f"""
Rewrite this bio with different emphasis.

Current bio: {current_bio}

Preferences:
- Emphasis: {emphasis} (e.g., 'technical', 'leadership', 'creative', 'impact')
- Length: {length_map.get(length, '150-200 words')}

Requirements:
- Keep core facts the same
- Adjust tone and emphasis as requested
- First person voice
- Natural flow

Return ONLY the new bio.
"""
        
        response = self.model.generate_content(prompt)
        new_bio = response.text.strip()
        
        return new_bio
    
    async def _regenerate_project(
        self,
        context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate project description with preferences."""
        emphasis = preferences.get('emphasis', 'technical')
        
        current_project = context.get('current_content', {})
        
        prompt = f"""
Rewrite this project description with different emphasis.

Project: {current_project.get('title')}
Current description: {current_project.get('description')}

Preferences:
- Emphasis: {emphasis}

Requirements:
- Adjust focus based on emphasis
- Keep core facts the same
- 100-150 words

Return ONLY the new description.
"""
        
        response = self.model.generate_content(prompt)
        new_description = response.text.strip()
        
        return {
            **current_project,
            'description': new_description
        }
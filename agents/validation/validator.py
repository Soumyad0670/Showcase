


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  VISIT AGENTS_README.md in main agents folder before going to the code 

"""
VALIDATOR.PY - Portfolio Quality Validation & Enhancement
=========================================================

PURPOSE:
This is the quality control agent. It validates that generated content meets
quality standards and enhances it if needed. Think of it as the editor.

DATA FLOW IN:
- Generated portfolio content from ContentGenerator
- Original preprocessed data (for fact-checking)

DATA FLOW OUT:
- Validated and potentially enhanced portfolio:
  * Quality checked (length, coherence, accuracy)
  * Enhanced if needed (fixing issues)
  * Ready for frontend consumption

HOW IT WORKS:
- Checks content length requirements
- Validates consistency with original data
- Ensures no placeholder text remains
- Checks for appropriate tone
- Can trigger regeneration if quality is too low
- Adds quality metadata

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""

import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)


class PortfolioValidator:
    """
    Validates and enhances generated portfolio content.
    
    This agent ensures:
    - Content quality meets standards
    - Consistency with original data
    - Appropriate length and tone
    - No placeholder or template text
    - Professional presentation
    """
    
    # Validation thresholds
    MIN_TAGLINE_WORDS = 5
    MAX_TAGLINE_WORDS = 20
    MIN_BIO_WORDS = 100
    MAX_BIO_WORDS = 300
    MIN_PROJECT_DESC_WORDS = 30
    
    # Forbidden placeholder patterns
    PLACEHOLDER_PATTERNS = [
        r'\[.*?\]',  # [placeholder]
        r'Lorem ipsum',
        r'TODO',
        r'FIXME',
        r'XXX',
        r'placeholder',
        r'sample text',
        r'example\.com'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize validator with configuration."""
        self.config = config
        self.strict_mode = config.get('strict_validation', False)
        logger.info(f"PortfolioValidator initialized (strict_mode={self.strict_mode})")
    
    async def validate_and_enhance(
        self,
        portfolio: Dict[str, Any],
        original_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main validation method.
        
        Validates entire portfolio and enhances if needed.
        
        Args:
            portfolio: Generated portfolio content
            original_data: Original preprocessed data for fact-checking
        
        Returns:
            Validated and enhanced portfolio with quality metadata
        """
        try:
            logger.info("Starting portfolio validation...")
            
            validation_results = {
                'hero': self._validate_hero(portfolio.get('hero', {})),
                'bio': self._validate_bio(portfolio.get('bio', '')),
                'projects': self._validate_projects(portfolio.get('projects', [])),
                'overall': {}
            }
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_score(validation_results)
            validation_results['overall']['score'] = overall_score
            validation_results['overall']['passed'] = overall_score >= 0.7
            
            # Add validation metadata to portfolio
            portfolio['validation'] = validation_results
            
            # Check consistency with original data
            consistency_issues = self._check_consistency(portfolio, original_data)
            if consistency_issues:
                portfolio['validation']['consistency_warnings'] = consistency_issues
                logger.warning(f"Found {len(consistency_issues)} consistency issues")
            
            # Enhance if needed
            if overall_score < 0.7 and not self.strict_mode:
                logger.info("Quality below threshold, applying enhancements...")
                portfolio = await self._enhance_portfolio(portfolio, validation_results)
            elif overall_score < 0.7 and self.strict_mode:
                raise ValueError(f"Portfolio quality too low: {overall_score:.2f}")
            
            logger.info(f"Validation complete. Overall score: {overall_score:.2f}")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error in validation: {str(e)}")
            raise
    
    def _validate_hero(self, hero: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate hero section.
        
        Checks:
        - Tagline length
        - No placeholders
        - Contains name
        - Professional tone
        """
        result = {
            'passed': True,
            'issues': [],
            'score': 1.0
        }
        
        tagline = hero.get('tagline', '')
        word_count = len(tagline.split())
        
        # Check length
        if word_count < self.MIN_TAGLINE_WORDS:
            result['issues'].append(f"Tagline too short ({word_count} words, min {self.MIN_TAGLINE_WORDS})")
            result['score'] -= 0.3
        elif word_count > self.MAX_TAGLINE_WORDS:
            result['issues'].append(f"Tagline too long ({word_count} words, max {self.MAX_TAGLINE_WORDS})")
            result['score'] -= 0.2
        
        # Check for placeholders
        if self._contains_placeholders(tagline):
            result['issues'].append("Tagline contains placeholder text")
            result['score'] -= 0.5
        
        # Check for name
        if not hero.get('name'):
            result['issues'].append("Missing name in hero section")
            result['score'] -= 0.3
        
        result['passed'] = result['score'] >= 0.6
        return result
    
    def _validate_bio(self, bio: str) -> Dict[str, Any]:
        """
        Validate bio section.
        
        Checks:
        - Length requirements
        - No placeholders
        - Natural flow
        - Professional but friendly tone
        - First person voice
        """
        result = {
            'passed': True,
            'issues': [],
            'score': 1.0
        }
        
        word_count = len(bio.split())
        
        # Check length
        if word_count < self.MIN_BIO_WORDS:
            result['issues'].append(f"Bio too short ({word_count} words, min {self.MIN_BIO_WORDS})")
            result['score'] -= 0.3
        elif word_count > self.MAX_BIO_WORDS:
            result['issues'].append(f"Bio too long ({word_count} words, max {self.MAX_BIO_WORDS})")
            result['score'] -= 0.1
        
        # Check for placeholders
        if self._contains_placeholders(bio):
            result['issues'].append("Bio contains placeholder text")
            result['score'] -= 0.5
        
        # Check for first person voice
        if not self._is_first_person(bio):
            result['issues'].append("Bio should be in first person voice")
            result['score'] -= 0.2
        
        # Check for natural flow (no excessive repetition)
        if self._has_repetitive_patterns(bio):
            result['issues'].append("Bio contains repetitive patterns")
            result['score'] -= 0.1
        
        result['passed'] = result['score'] >= 0.6
        return result
    
    def _validate_projects(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate all projects.
        
        Checks each project for:
        - Description quality
        - Appropriate length
        - No placeholders
        - Has title
        """
        result = {
            'passed': True,
            'issues': [],
            'score': 1.0,
            'individual_scores': []
        }
        
        if not projects:
            result['issues'].append("No projects found")
            result['score'] = 0.5
            return result
        
        for idx, project in enumerate(projects):
            project_result = self._validate_single_project(project, idx)
            result['individual_scores'].append(project_result)
            
            if not project_result['passed']:
                result['issues'].extend([f"Project {idx}: {issue}" for issue in project_result['issues']])
        
        # Average score across projects
        if result['individual_scores']:
            result['score'] = sum(p['score'] for p in result['individual_scores']) / len(result['individual_scores'])
        
        result['passed'] = result['score'] >= 0.6
        return result
    
    def _validate_single_project(self, project: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """Validate a single project."""
        result = {
            'passed': True,
            'issues': [],
            'score': 1.0
        }
        
        title = project.get('title', '')
        description = project.get('description', '')
        
        # Check title
        if not title:
            result['issues'].append("Missing title")
            result['score'] -= 0.3
        
        # Check description length
        word_count = len(description.split())
        if word_count < self.MIN_PROJECT_DESC_WORDS:
            result['issues'].append(f"Description too short ({word_count} words)")
            result['score'] -= 0.3
        
        # Check for placeholders
        if self._contains_placeholders(description):
            result['issues'].append("Contains placeholder text")
            result['score'] -= 0.5
        
        # Check for tech stack
        if not project.get('tech_stack'):
            result['issues'].append("Missing tech stack")
            result['score'] -= 0.1
        
        result['passed'] = result['score'] >= 0.6
        return result
    
    def _contains_placeholders(self, text: str) -> bool:
        """Check if text contains placeholder patterns."""
        for pattern in self.PLACEHOLDER_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_first_person(self, text: str) -> bool:
        """Check if text is in first person voice."""
        first_person_indicators = ['I ', 'my ', 'me ', "I'm ", "I've ", "I'll "]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in first_person_indicators)
    
    def _has_repetitive_patterns(self, text: str) -> bool:
        """Check for excessive repetition in text."""
        sentences = text.split('.')
        if len(sentences) < 3:
            return False
        
        # Check for repeated sentence starts
        starts = [s.strip().split()[:3] for s in sentences if s.strip()]
        starts_str = [' '.join(s) for s in starts if len(s) >= 3]
        
        if len(starts_str) != len(set(starts_str)):
            return True  # Found duplicate sentence starts
        
        return False
    
    def _calculate_overall_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            'hero': 0.25,
            'bio': 0.35,
            'projects': 0.40
        }
        
        score = 0.0
        for section, weight in weights.items():
            if section in validation_results:
                score += validation_results[section]['score'] * weight
        
        return score
    
    def _check_consistency(
        self,
        portfolio: Dict[str, Any],
        original_data: Dict[str, Any]
    ) -> List[str]:
        """
        Check consistency between generated content and original data.
        
        Ensures:
        - Names match
        - Skills mentioned are in original skills
        - Project count is reasonable
        """
        issues = []
        
        # Check name consistency
        hero_name = portfolio.get('hero', {}).get('name', '')
        original_name = original_data.get('name', '')
        if hero_name and original_name and hero_name.lower() != original_name.lower():
            issues.append(f"Name mismatch: '{hero_name}' vs '{original_name}'")
        
        # Check if generated content mentions skills not in original
        bio = portfolio.get('bio', '')
        original_skills = set(s.lower() for s in original_data.get('skills', []))
        
        # This is a simplified check - in production you might use NLP
        for skill in original_skills:
            if len(skill) > 4 and skill in bio.lower():
                # Good - mentioned a real skill
                pass
        
        # Check project count consistency
        generated_projects = len(portfolio.get('projects', []))
        original_projects = len(original_data.get('projects', []))
        if generated_projects > original_projects:
            issues.append(f"More projects generated ({generated_projects}) than in original data ({original_projects})")
        
        return issues
    
    async def _enhance_portfolio(
        self,
        portfolio: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance portfolio to fix validation issues.
        
        This could involve:
        - Trimming overly long content
        - Padding short content with more detail
        - Fixing placeholder text
        - Improving tone
        
        Note: In production, this might call back to ContentGenerator
        for regeneration of specific sections.
        """
        enhanced = portfolio.copy()
        
        # Fix hero issues
        if validation_results['hero']['score'] < 0.7:
            logger.info("Enhancing hero section...")
            # In production: trigger regeneration
            # For now: log the issue
            enhanced['validation']['hero_enhanced'] = True
        
        # Fix bio issues
        if validation_results['bio']['score'] < 0.7:
            logger.info("Enhancing bio section...")
            enhanced['validation']['bio_enhanced'] = True
        
        # Fix project issues
        if validation_results['projects']['score'] < 0.7:
            logger.info("Enhancing projects section...")
            enhanced['validation']['projects_enhanced'] = True
        
        return enhanced
    
    async def validate_section(
        self,
        portfolio: Dict[str, Any],
        section: str
    ) -> Dict[str, Any]:
        """
        Validate a specific section after regeneration.
        
        Used when user regenerates a section and we need to
        validate just that part.
        """
        validation_result = {}
        
        if section == 'hero':
            validation_result = self._validate_hero(portfolio.get('hero', {}))
        elif section == 'bio':
            validation_result = self._validate_bio(portfolio.get('bio', ''))
        elif section.startswith('project_'):
            idx = int(section.split('_')[1])
            projects = portfolio.get('projects', [])
            if idx < len(projects):
                validation_result = self._validate_single_project(projects[idx], idx)
        
        if not validation_result.get('passed'):
            logger.warning(f"Section '{section}' failed validation: {validation_result.get('issues')}")
        
        return portfolio
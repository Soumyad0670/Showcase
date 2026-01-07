"""
Template Selector Agent
Intelligently selects the most appropriate portfolio template based on resume content
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Try to import AI provider for intelligent selection
try:
    from app.ai_providers.gemini_provider import GeminiProvider
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


@dataclass
class TemplateScore:
    """Represents a template with its selection score"""
    template_id: str
    template_name: str
    score: float
    reasons: List[str]


class TemplateRegistry:
    """Manages template registry and provides query methods"""
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize the template registry
        
        Args:
            registry_path: Path to registry.json file. If None, auto-detects.
        """
        if registry_path is None:
            # Auto-detect registry path
            registry_path = self._find_registry_path()
        
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
    
    def _find_registry_path(self) -> str:
        """Auto-detect registry.json location"""
        possible_paths = [
            Path(__file__).parent.parent / "templates" / "registry.json",
            Path("templates") / "registry.json",
            Path("../templates/registry.json"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            "Could not find registry.json. Please specify registry_path or "
            "ensure registry.json exists in the templates/ folder"
        )
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load and parse the registry JSON file"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load registry from {self.registry_path}: {e}")
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID"""
        for template in self.registry['templates']:
            if template['id'] == template_id:
                return template
        return None
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates"""
        return self.registry['templates']
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all templates in a specific category"""
        return [t for t in self.registry['templates'] if t['category'] == category]
    
    def get_featured_templates(self) -> List[Dict[str, Any]]:
        """Get all featured templates"""
        return [t for t in self.registry['templates'] if t.get('featured', False)]
    
    def get_templates_by_industry(self, industry: str) -> List[str]:
        """Get template IDs suitable for a specific industry"""
        criteria = self.registry.get('selectionCriteria', {})
        by_industry = criteria.get('byIndustry', {})
        return by_industry.get(industry.lower(), [])
    
    def get_templates_by_role(self, role: str) -> List[str]:
        """Get template IDs suitable for a specific role"""
        criteria = self.registry.get('selectionCriteria', {})
        by_role = criteria.get('byRole', {})
        return by_role.get(role.lower(), [])
    
    def get_templates_by_experience(self, experience_level: str) -> List[str]:
        """Get template IDs suitable for an experience level"""
        criteria = self.registry.get('selectionCriteria', {})
        by_experience = criteria.get('byExperienceLevel', {})
        return by_experience.get(experience_level.lower(), [])


class TemplateSelectorAgent:
    """
    Intelligent agent for selecting the most appropriate portfolio template
    based on resume content and user preferences
    """
    
    def __init__(self, registry_path: Optional[str] = None, use_ai: bool = True):
        """
        Initialize the template selector agent
        
        Args:
            registry_path: Path to registry.json file
            use_ai: Whether to use AI for enhanced selection (requires Gemini API)
        """
        self.registry = TemplateRegistry(registry_path)
        self.use_ai = use_ai and AI_AVAILABLE
        
        if self.use_ai:
            try:
                self.ai_provider = GeminiProvider()
            except Exception as e:
                print(f"Warning: AI provider unavailable: {e}")
                self.use_ai = False
    
    def select_template(
        self,
        resume_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select the best template based on resume data and preferences
        
        Args:
            resume_data: Structured resume data (from OCR/parsing)
            preferences: Optional user preferences (industry, style, etc.)
        
        Returns:
            Dictionary containing selected template and reasoning
        """
        if self.use_ai:
            return self._ai_powered_selection(resume_data, preferences)
        else:
            return self._rule_based_selection(resume_data, preferences)
    
    def _rule_based_selection(
        self,
        resume_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Rule-based template selection using registry guidelines
        """
        scores = []
        
        for template in self.registry.get_all_templates():
            score_obj = self._calculate_template_score(template, resume_data, preferences)
            scores.append(score_obj)
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x.score, reverse=True)
        
        best_match = scores[0]
        template_data = self.registry.get_template(best_match.template_id)
        
        return {
            'template_id': best_match.template_id,
            'template_name': best_match.template_name,
            'template_data': template_data,
            'confidence_score': best_match.score,
            'selection_reasons': best_match.reasons,
            'alternatives': [
                {
                    'template_id': s.template_id,
                    'template_name': s.template_name,
                    'score': s.score
                }
                for s in scores[1:4]  # Top 3 alternatives
            ]
        }
    
    def _calculate_template_score(
        self,
        template: Dict[str, Any],
        resume_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> TemplateScore:
        """
        Calculate how well a template matches the resume data
        """
        score = 0.0
        reasons = []
        
        # Base score from popularity
        score += template.get('popularity', 50) * 0.3
        
        # Check technical skills (for tech templates)
        skills = resume_data.get('skills', {})
        technical_skills = skills.get('technical', [])
        
        if len(technical_skills) > 5 and template['id'] in ['tech-developer', 'modern-minimal']:
            score += 25
            reasons.append(f"Strong technical skill set ({len(technical_skills)} skills)")
        
        # Check for publications (academic)
        publications = resume_data.get('publications', [])
        if len(publications) > 0 and template['id'] == 'academic-researcher':
            score += 30
            reasons.append(f"Has {len(publications)} publications")
        
        # Check for executive positions
        experience = resume_data.get('experience', [])
        executive_keywords = ['ceo', 'cto', 'cfo', 'vp', 'director', 'chief']
        
        for exp in experience:
            title = exp.get('title', '').lower()
            if any(keyword in title for keyword in executive_keywords):
                if template['id'] == 'business-executive':
                    score += 30
                    reasons.append(f"Executive role: {exp.get('title')}")
                break
        
        # Check for creative/design work
        creative_keywords = ['design', 'creative', 'artist', 'ui', 'ux', 'graphic']
        projects = resume_data.get('projects', [])
        
        has_creative = any(
            any(keyword in str(proj.get('description', '')).lower() for keyword in creative_keywords)
            for proj in projects
        )
        
        if has_creative and template['id'] in ['creative-bold', 'freelancer-versatile']:
            score += 25
            reasons.append("Creative/design-focused work")
        
        # Check industry match
        if preferences:
            preferred_industry = preferences.get('industry', '').lower()
            if preferred_industry:
                suitable_industries = template.get('suitableFor', {}).get('industries', [])
                if preferred_industry in suitable_industries:
                    score += 20
                    reasons.append(f"Matches preferred industry: {preferred_industry}")
        
        # Check experience level
        experience_level = self._determine_experience_level(resume_data)
        suitable_levels = template.get('suitableFor', {}).get('experienceLevel', [])
        
        if experience_level in suitable_levels:
            score += 15
            reasons.append(f"Suitable for {experience_level} level")
        
        # Diversity of skills (freelancer)
        skill_categories = len([k for k, v in skills.items() if v])
        if skill_categories >= 3 and template['id'] == 'freelancer-versatile':
            score += 20
            reasons.append(f"Diverse skill set ({skill_categories} categories)")
        
        # Featured templates get small boost
        if template.get('featured', False):
            score += 5
        
        return TemplateScore(
            template_id=template['id'],
            template_name=template['name'],
            score=score,
            reasons=reasons
        )
    
    def _determine_experience_level(self, resume_data: Dict[str, Any]) -> str:
        """
        Determine experience level from resume data
        """
        experience = resume_data.get('experience', [])
        total_years = 0
        
        for exp in experience:
            # Try to calculate years from dates
            start = exp.get('start_date', '')
            end = exp.get('end_date', '')
            
            # Simple heuristic: count number of positions
            total_years += 1
        
        if total_years < 2:
            return 'junior'
        elif total_years < 5:
            return 'mid'
        elif total_years < 10:
            return 'senior'
        else:
            return 'executive'
    
    def _ai_powered_selection(
        self,
        resume_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        AI-powered template selection using LLM
        """
        # Get rule-based recommendation as baseline
        rule_based = self._rule_based_selection(resume_data, preferences)
        
        # Prepare prompt for AI
        templates_info = [
            {
                'id': t['id'],
                'name': t['name'],
                'description': t['description'],
                'suitableFor': t.get('suitableFor', {}),
                'features': t.get('features', {}).get('sections', [])
            }
            for t in self.registry.get_all_templates()
        ]
        
        prompt = f"""
Based on the following resume data, select the most appropriate portfolio template.

Resume Summary:
- Skills: {list(resume_data.get('skills', {}).keys())}
- Experience: {len(resume_data.get('experience', []))} positions
- Projects: {len(resume_data.get('projects', []))} projects
- Publications: {len(resume_data.get('publications', []))} publications
- Education: {len(resume_data.get('education', []))} degrees

Available Templates:
{json.dumps(templates_info, indent=2)}

Rule-Based Recommendation: {rule_based['template_id']} ({rule_based['template_name']})
Reasons: {', '.join(rule_based['selection_reasons'])}

Please analyze and either:
1. Confirm the rule-based selection, or
2. Recommend a different template with strong justification

Respond in JSON format:
{{
    "template_id": "selected-template-id",
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation",
    "key_factors": ["factor1", "factor2"]
}}
"""
        
        try:
            response = self.ai_provider.generate_content(prompt)
            ai_selection = json.loads(response)
            
            # Merge AI insights with rule-based data
            selected_template = self.registry.get_template(ai_selection['template_id'])
            
            return {
                'template_id': ai_selection['template_id'],
                'template_name': selected_template['name'],
                'template_data': selected_template,
                'confidence_score': ai_selection.get('confidence', 0.8) * 100,
                'selection_reasons': ai_selection.get('key_factors', []),
                'ai_reasoning': ai_selection.get('reasoning', ''),
                'rule_based_alternative': rule_based,
                'selection_method': 'ai_powered'
            }
        
        except Exception as e:
            print(f"AI selection failed, falling back to rule-based: {e}")
            rule_based['selection_method'] = 'rule_based_fallback'
            return rule_based
    
    def get_recommendations(
        self,
        resume_data: Dict[str, Any],
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get top N template recommendations with scores
        """
        scores = []
        
        for template in self.registry.get_all_templates():
            score_obj = self._calculate_template_score(template, resume_data)
            scores.append(score_obj)
        
        # Sort by score
        scores.sort(key=lambda x: x.score, reverse=True)
        
        recommendations = []
        for score_obj in scores[:top_n]:
            template_data = self.registry.get_template(score_obj.template_id)
            recommendations.append({
                'template_id': score_obj.template_id,
                'template_name': score_obj.template_name,
                'score': score_obj.score,
                'reasons': score_obj.reasons,
                'template_data': template_data
            })
        
        return recommendations


def main():
    """Example usage of the Template Selector Agent"""
    
    # Example resume data
    example_resume = {
        'skills': {
            'technical': ['Python', 'JavaScript', 'React', 'Node.js', 'Docker', 'AWS'],
            'soft': ['Leadership', 'Communication']
        },
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'Tech Corp',
                'start_date': '2020-01',
                'end_date': 'Present'
            },
            {
                'title': 'Software Developer',
                'company': 'Startup Inc',
                'start_date': '2018-01',
                'end_date': '2020-01'
            }
        ],
        'projects': [
            {
                'name': 'E-commerce Platform',
                'description': 'Built scalable microservices architecture'
            }
        ],
        'education': [
            {
                'degree': 'B.S. Computer Science',
                'institution': 'University'
            }
        ],
        'publications': []
    }
    
    # Initialize agent
    print("Initializing Template Selector Agent...")
    agent = TemplateSelectorAgent(use_ai=False)
    
    # Select template
    print("\nAnalyzing resume and selecting template...")
    result = agent.select_template(example_resume)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"SELECTED TEMPLATE: {result['template_name']}")
    print(f"{'='*60}")
    print(f"Template ID: {result['template_id']}")
    print(f"Confidence Score: {result['confidence_score']:.1f}%")
    print(f"\nSelection Reasons:")
    for reason in result['selection_reasons']:
        print(f"  • {reason}")
    
    print(f"\nAlternative Templates:")
    for alt in result['alternatives']:
        print(f"  • {alt['template_name']} (Score: {alt['score']:.1f})")
    
    # Get all recommendations
    print(f"\n{'='*60}")
    print("TOP RECOMMENDATIONS")
    print(f"{'='*60}")
    recommendations = agent.get_recommendations(example_resume, top_n=3)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['template_name']} (Score: {rec['score']:.1f})")
        print(f"   Reasons: {', '.join(rec['reasons'][:2])}")


if __name__ == "__main__":
    main()
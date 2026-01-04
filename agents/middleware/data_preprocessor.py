


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  VISIT AGENTS_README.md in main agents folder before going to the code 

"""
DATA_PREPROCESSOR.PY - Input Data Preprocessing Middleware
===========================================================

PURPOSE:
This middleware cleans and normalizes the parsed resume data before it enters
the main agent pipeline. It's the data janitor that ensures quality input.

DATA FLOW IN:
- Raw parsed data from OCR + NLP parsing (potentially messy)
- May have:
  * Inconsistent formatting
  * Missing fields
  * Duplicate entries
  * Invalid email/links
  * Unstructured text

DATA FLOW OUT:
- Clean, normalized, validated data ready for schema building:
  * Standardized field names
  * Valid email and URLs
  * Deduplicated skills
  * Properly structured nested objects
  * Enriched with metadata

HOW IT WORKS:
- Validates required fields
- Cleans and normalizes text
- Extracts and validates URLs/emails
- Deduplicates and categorizes data
- Fills in missing optional fields with defaults

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""

import logging
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import string

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Preprocesses and validates parsed resume data.
    
    This middleware ensures:
    - Data quality and consistency
    - Required fields are present
    - Text is cleaned and normalized
    - URLs and emails are valid
    - No duplicate entries
    """
    
    # Email validation regex
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Common skill variations to normalize
    SKILL_NORMALIZATIONS = {
        'js': 'JavaScript',
        'ts': 'TypeScript',
        'py': 'Python',
        'reactjs': 'React',
        'nodejs': 'Node.js',
        'vuejs': 'Vue.js',
        'ml': 'Machine Learning',
        'ai': 'Artificial Intelligence',
        'dl': 'Deep Learning',
        'nlp': 'Natural Language Processing',
        'cv': 'Computer Vision',
        'aws': 'Amazon Web Services',
        'gcp': 'Google Cloud Platform',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize preprocessor with configuration."""
        self.config = config
        logger.info("DataPreprocessor initialized")
    
    async def preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main preprocessing method.
        
        Takes raw parsed data and returns cleaned, validated data.
        
        Args:
            raw_data: Raw data from OCR + NLP parsing
        
        Returns:
            Clean, validated, normalized data
        """
        try:
            logger.info("Starting data preprocessing...")
            
            # Validate required fields
            self._validate_required_fields(raw_data)
            
            # Build preprocessed data structure
            preprocessed = {
                'name': self._clean_name(raw_data.get('name', '')),
                'email': self._validate_email(raw_data.get('email', '')),
                'skills': self._process_skills(raw_data.get('skills', [])),
                'projects': self._process_projects(raw_data.get('projects', [])),
                'experience': self._process_experience(raw_data.get('experience', [])),
                'education': self._process_education(raw_data.get('education', [])),
                'links': self._process_links(raw_data.get('links', {})),
                'metadata': {
                    'processed_at': self._get_timestamp(),
                    'source': raw_data.get('source', 'unknown'),
                    'data_quality_score': 0.0  # Will be calculated
                }
            }
            
            # Calculate data quality score
            preprocessed['metadata']['data_quality_score'] = self._calculate_quality_score(preprocessed)
            
            logger.info(f"Preprocessing complete. Quality score: {preprocessed['metadata']['data_quality_score']:.2f}")
            return preprocessed
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {str(e)}")
            raise
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """
        Validate that required fields are present.
        
        Required fields:
        - name (or at least some identifying info)
        - At least one of: skills, projects, experience
        """
        if not data.get('name') and not data.get('email'):
            raise ValueError("Missing required field: name or email must be provided")
        
        has_content = any([
            data.get('skills'),
            data.get('projects'),
            data.get('experience')
        ])
        
        if not has_content:
            raise ValueError("Resume must contain at least skills, projects, or experience")
    
    def _clean_name(self, name: str) -> str:
        """
        Clean and normalize name.
        
        - Remove extra whitespace
        - Capitalize properly
        - Remove special characters (except spaces, hyphens, apostrophes)
        """
        if not name:
            return "Portfolio"
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove unwanted characters
        allowed = string.ascii_letters + string.whitespace + "-'."
        name = ''.join(c for c in name if c in allowed)
        
        # Title case
        name = name.title()
        
        return name.strip()
    
    def _validate_email(self, email: str) -> Optional[str]:
        """
        Validate and clean email address.
        
        Returns None if invalid.
        """
        if not email:
            return None
        
        email = email.strip().lower()
        
        if self.EMAIL_PATTERN.match(email):
            return email
        
        logger.warning(f"Invalid email format: {email}")
        return None
    
    def _process_skills(self, skills: List[Any]) -> List[str]:
        """
        Process and normalize skills list.
        
        - Convert to strings
        - Normalize common abbreviations
        - Remove duplicates
        - Sort by relevance/frequency
        """
        if not skills:
            return []
        
        processed_skills = []
        seen = set()
        
        for skill in skills:
            # Convert to string and clean
            skill_str = str(skill).strip()
            
            if not skill_str or len(skill_str) < 2:
                continue
            
            # Normalize known abbreviations
            skill_lower = skill_str.lower()
            normalized = self.SKILL_NORMALIZATIONS.get(skill_lower, skill_str)
            
            # Title case for consistency
            normalized = normalized.title()
            
            # Check for duplicates (case-insensitive)
            normalized_lower = normalized.lower()
            if normalized_lower not in seen:
                processed_skills.append(normalized)
                seen.add(normalized_lower)
        
        return processed_skills
    
    def _process_projects(self, projects: List[Any]) -> List[Dict[str, Any]]:
        """
        Process and structure projects list.
        
        Each project should have:
        - title
        - description
        - technologies (optional)
        - links (optional)
        """
        if not projects:
            return []
        
        processed_projects = []
        
        for idx, project in enumerate(projects):
            # Handle different input formats
            if isinstance(project, str):
                # Simple string project
                processed_project = {
                    'title': f'Project {idx + 1}',
                    'description': project,
                    'technologies': [],
                    'links': {}
                }
            elif isinstance(project, dict):
                processed_project = {
                    'title': project.get('title', project.get('name', f'Project {idx + 1}')),
                    'description': self._clean_text(project.get('description', '')),
                    'technologies': self._extract_technologies(project),
                    'links': self._process_project_links(project.get('links', {}))
                }
            else:
                logger.warning(f"Skipping invalid project format: {type(project)}")
                continue
            
            # Only include if has meaningful content
            if processed_project['description'] or processed_project['technologies']:
                processed_projects.append(processed_project)
        
        return processed_projects
    
    def _process_experience(self, experience: List[Any]) -> List[Dict[str, Any]]:
        """
        Process work experience entries.
        
        Each entry should have:
        - company
        - position/role
        - duration
        - description (optional)
        """
        if not experience:
            return []
        
        processed_experience = []
        
        for exp in experience:
            if not isinstance(exp, dict):
                continue
            
            processed_exp = {
                'company': exp.get('company', exp.get('organization', '')),
                'position': exp.get('position', exp.get('role', exp.get('title', ''))),
                'duration': self._normalize_duration(exp.get('duration', exp.get('period', ''))),
                'description': self._clean_text(exp.get('description', '')),
                'location': exp.get('location', '')
            }
            
            # Only include if has company and position
            if processed_exp['company'] or processed_exp['position']:
                processed_experience.append(processed_exp)
        
        return processed_experience
    
    def _process_education(self, education: List[Any]) -> List[Dict[str, Any]]:
        """
        Process education entries.
        
        Each entry should have:
        - institution/school
        - degree
        - field of study (optional)
        - graduation year (optional)
        """
        if not education:
            return []
        
        processed_education = []
        
        for edu in education:
            if not isinstance(edu, dict):
                continue
            
            processed_edu = {
                'institution': edu.get('institution', edu.get('school', edu.get('university', ''))),
                'degree': edu.get('degree', ''),
                'field': edu.get('field', edu.get('major', '')),
                'year': self._extract_year(edu.get('year', edu.get('graduation', '')))
            }
            
            # Only include if has institution
            if processed_edu['institution']:
                processed_education.append(processed_edu)
        
        return processed_education
    
    def _process_links(self, links: Dict[str, Any]) -> Dict[str, str]:
        """
        Process and validate social/portfolio links.
        
        Common links:
        - github
        - linkedin
        - portfolio/website
        - twitter
        """
        if not links:
            return {}
        
        processed_links = {}
        
        for key, url in links.items():
            if not url:
                continue
            
            # Clean and validate URL
            cleaned_url = self._validate_url(str(url))
            if cleaned_url:
                processed_links[key.lower()] = cleaned_url
        
        return processed_links
    
    def _process_project_links(self, links: Any) -> Dict[str, str]:
        """Process links specific to projects."""
        if isinstance(links, str):
            # Single URL provided
            return {'demo': self._validate_url(links)} if self._validate_url(links) else {}
        elif isinstance(links, dict):
            return self._process_links(links)
        else:
            return {}
    
    def _validate_url(self, url: str) -> Optional[str]:
        """
        Validate and normalize URL.
        
        Returns None if invalid.
        """
        url = url.strip()
        
        # Add https:// if no scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            result = urlparse(url)
            if result.scheme and result.netloc:
                return url
        except Exception:
            pass
        
        logger.warning(f"Invalid URL: {url}")
        return None
    
    def _extract_technologies(self, project: Dict[str, Any]) -> List[str]:
        """Extract technology list from project."""
        tech = project.get('technologies', project.get('tech_stack', project.get('tools', [])))
        
        if isinstance(tech, str):
            # Split comma-separated string
            tech = [t.strip() for t in tech.split(',')]
        
        return [t for t in tech if t] if isinstance(tech, list) else []
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text content.
        
        - Remove extra whitespace
        - Remove special characters
        - Normalize line breaks
        """
        if not text:
            return ''
        
        # Replace multiple whitespace with single space
        text = ' '.join(text.split())
        
        # Remove weird characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text.strip()
    
    def _normalize_duration(self, duration: str) -> str:
        """Normalize duration strings (e.g., '2020-2022', 'Jan 2020 - Present')."""
        if not duration:
            return ''
        return ' '.join(str(duration).split())
    
    def _extract_year(self, year_str: Any) -> Optional[int]:
        """Extract year from various formats."""
        if not year_str:
            return None
        
        # Try to extract 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', str(year_str))
        if year_match:
            return int(year_match.group())
        
        return None
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0.0 to 1.0).
        
        Factors:
        - Presence of key fields
        - Amount of content
        - Validity of data
        """
        score = 0.0
        max_score = 100.0
        
        # Name (10 points)
        if data['name'] and data['name'] != 'Portfolio':
            score += 10
        
        # Email (10 points)
        if data['email']:
            score += 10
        
        # Skills (20 points)
        if data['skills']:
            score += min(20, len(data['skills']) * 2)
        
        # Projects (30 points)
        if data['projects']:
            score += min(30, len(data['projects']) * 10)
        
        # Experience (15 points)
        if data['experience']:
            score += min(15, len(data['experience']) * 5)
        
        # Education (10 points)
        if data['education']:
            score += min(10, len(data['education']) * 5)
        
        # Links (5 points)
        if data['links']:
            score += min(5, len(data['links']) * 2)
        
        return min(1.0, score / max_score)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
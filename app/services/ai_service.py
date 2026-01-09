import logging
from pydantic import ValidationError
from agents.integration import generate_portfolio
from app.schemas.portfolio import PortfolioOutput
from app.adapters.gemini_adapter import gemini_adapter
import json

logger = logging.getLogger(__name__)

class AIService:
    async def generate_portfolio_content(self, raw_text: str) -> dict:
        try:
            logger.info("AI Generation pipeline started")
            
            # Parse raw text into structured data first
            parsed_data = await self._parse_resume(raw_text)
            
            portfolio_data = await generate_portfolio(parsed_data)

            if not isinstance(portfolio_data, dict):
                logger.error(f"AI pipeline returned type {type(portfolio_data)} instead of dict")
                raise RuntimeError("AI pipeline returned invalid portfolio payload")

            # Adapter: Transform Agent output to API Schema
            from datetime import datetime
            
            # 1. Hero
            hero_data = portfolio_data.get("hero", {})
            if "bio_short" not in hero_data:
                # Fallback: first sentence of bio or tagline
                bio = portfolio_data.get("bio", "")
                hero_data["bio_short"] = bio.split(".")[0] if bio else hero_data.get("tagline", "")
            
            # 2. Bio
            if "bio_long" not in portfolio_data:
                portfolio_data["bio_long"] = portfolio_data.get("bio", "")
                
            # 3. Theme
            if "theme" not in portfolio_data or not portfolio_data["theme"]:
                portfolio_data["theme"] = {"primary_color": "#4A90E2", "style": "modern_tech"}

            # 4. Metadata
            portfolio_data["quality_score"] = 0.85 # Mock score if missing
            portfolio_data["generated_at"] = datetime.utcnow().isoformat()
            
            # 5. Skills - Ensure structure matches SkillCategory
            # Agent output: {'raw': [], 'count': 0, 'categories': {'languages': ['Python']}}
            # Schema needs: List[SkillCategory] -> [{'category': 'languages', 'items': ['Python']}]
            skills_data = portfolio_data.get("skills", {})
            if isinstance(skills_data, dict) and "categories" in skills_data:
                formatted_skills = []
                for cat, items in skills_data["categories"].items():
                    formatted_skills.append({"category": cat.capitalize(), "items": items})
                portfolio_data["skills"] = formatted_skills

            logger.info(f"AI Generated Portfolio Data (pre-validation): {json.dumps(portfolio_data, default=str)[:500]}...")

            try:
                validated_data = PortfolioOutput(**portfolio_data)
                logger.info("AI output successfully validated against PortfolioOutput schema")
                
                return validated_data.model_dump()

            except ValidationError as e:
                logger.error(f"AI Schema validation failed: {str(e)}")
                raise RuntimeError("AI returned data that does not match the required portfolio structure")

        except Exception as e:
            if not isinstance(e, RuntimeError):
                logger.exception("Critical failure in the AI generation pipeline")
            raise

    async def _parse_resume(self, text: str) -> dict:
        prompt = f"""
        Extract the following information from the resume text below and return it as a JSON object:
        - name
        - email
        - phone
        - location
        - summary (or bio)
        - skills (list of strings)
        - experience (list of objects with company, role, duration, description)
        - projects (list of objects with title, description, technologies)
        - education (list of objects with institution, degree, year)
        - links (object with key-value pairs)

        Resume Text:
        {text[:10000]}
        
        Return ONLY valid JSON.
        """
        try:
             json_text = await gemini_adapter.generate_text(prompt)
             # Clean markdown code blocks if present
             if "```json" in json_text:
                 json_text = json_text.split("```json")[1].split("```")[0]
             elif "```" in json_text:
                 json_text = json_text.split("```")[1].split("```")[0]
                 
             return json.loads(json_text)
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            # Return minimal fallback to allow partial processing or failure
            return {"name": "Unknown Candidate", "raw_text": text}

ai_service = AIService()
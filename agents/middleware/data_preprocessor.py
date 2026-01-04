"""
DATA_PREPROCESSOR.PY
====================

Input normalization middleware for agent pipeline.

Responsibilities:
- Validate minimum viable resume data
- Normalize text fields
- Deduplicate and clean skills
- Sanitize URLs and emails
- Produce deterministic, schema-safe output

This module MUST NOT:
- Call LLMs
- Perform I/O
- Mutate incoming data
"""

from __future__ import annotations

import logging
import re
import string
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logger = logging.getLogger("agents.preprocessor")
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

class PreprocessingError(Exception):
    """Base exception for preprocessing failures."""


class InputValidationError(PreprocessingError):
    """Raised when resume input is invalid."""


# ---------------------------------------------------------------------
# Preprocessor
# ---------------------------------------------------------------------

class DataPreprocessor:
    """
    Normalizes parsed resume data before agent orchestration.
    """

    EMAIL_REGEX = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    SKILL_MAP = {
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "reactjs": "React",
        "nodejs": "Node.js",
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence",
        "nlp": "Natural Language Processing",
        "cv": "Computer Vision",
        "aws": "Amazon Web Services",
        "gcp": "Google Cloud Platform",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        logger.info("DataPreprocessor initialized")

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    async def preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point for preprocessing pipeline.
        """

        self._validate_minimum_input(raw_data)

        processed = {
            "name": self._clean_name(raw_data.get("name")),
            "email": self._validate_email(raw_data.get("email")),
            "skills": self._process_skills(raw_data.get("skills")),
            "projects": self._process_projects(raw_data.get("projects")),
            "experience": self._process_experience(raw_data.get("experience")),
            "education": self._process_education(raw_data.get("education")),
            "links": self._process_links(raw_data.get("links")),
            "metadata": {
                "processed_at": self._timestamp(),
                "source": raw_data.get("source", "unknown"),
                "quality_score": 0.0,
            },
        }

        processed["metadata"]["quality_score"] = self._quality_score(processed)

        logger.info(
            "Preprocessing complete | quality_score=%.2f",
            processed["metadata"]["quality_score"],
        )

        return processed

    # -----------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------

    def _validate_minimum_input(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise InputValidationError("Input must be a dictionary")

        if not data.get("name") and not data.get("email"):
            raise InputValidationError("Either name or email is required")

        if not any(data.get(k) for k in ("skills", "projects", "experience")):
            raise InputValidationError(
                "At least one of skills, projects, or experience is required"
            )

    # -----------------------------------------------------------------
    # Field processors
    # -----------------------------------------------------------------

    def _clean_name(self, name: Optional[str]) -> str:
        if not name:
            return "Portfolio"

        allowed = string.ascii_letters + " -'."
        cleaned = "".join(c for c in name if c in allowed)
        cleaned = " ".join(cleaned.split())

        return cleaned.title()

    def _validate_email(self, email: Optional[str]) -> Optional[str]:
        if not email:
            return None

        email = email.strip().lower()
        if self.EMAIL_REGEX.match(email):
            return email

        logger.warning("Invalid email dropped: %s", email)
        return None

    def _process_skills(self, skills: Any) -> List[str]:
        if not skills:
            return []

        if not isinstance(skills, list):
            skills = [skills]

        seen = set()
        output: List[str] = []

        for raw in skills:
            skill = str(raw).strip()
            if len(skill) < 2:
                continue

            key = skill.lower()
            normalized = self.SKILL_MAP.get(key, skill)

            norm_key = normalized.lower()
            if norm_key not in seen:
                seen.add(norm_key)
                output.append(normalized)

        return output

    def _process_projects(self, projects: Any) -> List[Dict[str, Any]]:
        if not projects:
            return []

        output = []

        for idx, proj in enumerate(projects if isinstance(projects, list) else []):
            if isinstance(proj, str):
                output.append({
                    "title": f"Project {idx + 1}",
                    "description": self._clean_text(proj),
                    "technologies": [],
                    "links": {},
                })
                continue

            if not isinstance(proj, dict):
                continue

            output.append({
                "title": proj.get("title") or proj.get("name") or f"Project {idx + 1}",
                "description": self._clean_text(proj.get("description")),
                "technologies": self._extract_tech(proj),
                "links": self._process_links(proj.get("links")),
            })

        return output

    def _process_experience(self, experience: Any) -> List[Dict[str, Any]]:
        if not experience:
            return []

        output = []

        for exp in experience if isinstance(experience, list) else []:
            if not isinstance(exp, dict):
                continue

            output.append({
                "company": exp.get("company") or exp.get("organization"),
                "position": exp.get("position") or exp.get("role"),
                "duration": self._normalize_duration(exp.get("duration")),
                "description": self._clean_text(exp.get("description")),
                "location": exp.get("location"),
            })

        return output

    def _process_education(self, education: Any) -> List[Dict[str, Any]]:
        if not education:
            return []

        output = []

        for edu in education if isinstance(education, list) else []:
            if not isinstance(edu, dict):
                continue

            output.append({
                "institution": edu.get("institution") or edu.get("school"),
                "degree": edu.get("degree"),
                "field": edu.get("field") or edu.get("major"),
                "year": self._extract_year(edu.get("year")),
            })

        return output

    def _process_links(self, links: Any) -> Dict[str, str]:
        if not isinstance(links, dict):
            return {}

        clean = {}
        for k, v in links.items():
            url = self._validate_url(v)
            if url:
                clean[k.lower()] = url

        return clean

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    def _validate_url(self, url: Any) -> Optional[str]:
        if not url:
            return None

        url = str(url).strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return url
        except Exception:
            pass

        logger.warning("Invalid URL dropped: %s", url)
        return None

    def _extract_tech(self, project: Dict[str, Any]) -> List[str]:
        tech = project.get("technologies") or project.get("tools") or []
        if isinstance(tech, str):
            tech = [t.strip() for t in tech.split(",")]
        return [t for t in tech if t]

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        text = " ".join(str(text).split())
        return text.encode("ascii", "ignore").decode()

    def _normalize_duration(self, duration: Any) -> Optional[str]:
        if not duration:
            return None
        return " ".join(str(duration).split())

    def _extract_year(self, value: Any) -> Optional[int]:
        if not value:
            return None
        match = re.search(r"\b(19|20)\d{2}\b", str(value))
        return int(match.group()) if match else None

    def _quality_score(self, data: Dict[str, Any]) -> float:
        score = 0.0

        if data["name"] != "Portfolio":
            score += 0.15
        if data["email"]:
            score += 0.15
        if data["skills"]:
            score += min(0.25, len(data["skills"]) * 0.05)
        if data["projects"]:
            score += min(0.25, len(data["projects"]) * 0.1)
        if data["experience"]:
            score += 0.2

        return round(min(score, 1.0), 2)

    def _timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

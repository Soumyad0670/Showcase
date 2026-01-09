import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


class ValidationAgent:
    """
    Production-grade validation agent.

    Responsibilities:
    - Validate generated portfolio content
    - Ensure consistency with original resume data
    - Compute deterministic quality scores
    - Decide pass / fail (NO silent fixing)
    """

    # Thresholds
    MIN_TAGLINE_WORDS = 6
    MAX_TAGLINE_WORDS = 18
    MIN_BIO_WORDS = 120
    MAX_BIO_WORDS = 280
    MIN_PROJECT_DESC_WORDS = 40

    PASS_SCORE = 0.70

    PLACEHOLDER_PATTERNS = [
        r"\[.*?\]",
        r"lorem ipsum",
        r"\b(todo|fixme|tbd)\b",
        r"sample text",
        r"example\.com",
        r"your (name|project|company)",
    ]

    def __init__(self, strict: bool = False):
        self.strict = strict

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        portfolio = state.get("generated_content")
        original = state.get("clean_data")

        if not portfolio or not original:
            raise ValidationError("Missing data for validation")

        results = {
            "hero": self._validate_hero(portfolio.get("hero", {})),
            "bio": self._validate_bio(portfolio.get("bio", "")),
            "projects": self._validate_projects(portfolio.get("projects", [])),
        }

        overall_score = self._overall_score(results)

        results["overall"] = {
            "score": round(overall_score, 3),
            "passed": overall_score >= self.PASS_SCORE,
        }

        consistency = self._check_consistency(portfolio, original)
        if consistency:
            results["consistency_warnings"] = consistency

        portfolio["validation"] = results

        if self.strict and not results["overall"]["passed"]:
            raise ValidationError(
                f"Portfolio validation failed (score={overall_score:.2f})"
            )

        state["validated"] = results["overall"]["passed"]
        return state

    # ---------------- HERO ---------------- #

    def _validate_hero(self, hero: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        score = 1.0

        tagline = hero.get("tagline", "").strip()
        wc = len(tagline.split())

        if wc < self.MIN_TAGLINE_WORDS:
            issues.append("Tagline too short")
            score -= 0.3
        elif wc > self.MAX_TAGLINE_WORDS:
            issues.append("Tagline too long")
            score -= 0.2

        if not hero.get("name"):
            issues.append("Missing name")
            score -= 0.3

        if self._has_placeholders(tagline):
            issues.append("Contains placeholder text")
            score -= 0.5

        return self._finalize(score, issues)

    # ---------------- BIO ---------------- #

    def _validate_bio(self, bio: str) -> Dict[str, Any]:
        issues = []
        score = 1.0

        wc = len(bio.split())

        if wc < self.MIN_BIO_WORDS:
            issues.append("Bio too short")
            score -= 0.3
        elif wc > self.MAX_BIO_WORDS:
            issues.append("Bio too long")
            score -= 0.1

        if self._has_placeholders(bio):
            issues.append("Contains placeholder text")
            score -= 0.5

        if not self._is_first_person(bio):
            issues.append("Not written in first person")
            score -= 0.2

        if self._is_repetitive(bio):
            issues.append("Repetitive phrasing detected")
            score -= 0.1

        return self._finalize(score, issues)

    # ---------------- PROJECTS ---------------- #

    def _validate_projects(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not projects:
            return self._finalize(0.4, ["No projects provided"])

        scores = []
        issues = []

        for i, project in enumerate(projects):
            res = self._validate_project(project)
            scores.append(res["score"])
            if not res["passed"]:
                issues.extend([f"Project {i}: {e}" for e in res["issues"]])

        avg_score = sum(scores) / len(scores)
        return self._finalize(avg_score, issues)

    def _validate_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        score = 1.0

        desc = project.get("description", "")
        wc = len(desc.split())

        if not project.get("title"):
            issues.append("Missing title")
            score -= 0.3

        if wc < self.MIN_PROJECT_DESC_WORDS:
            issues.append("Description too short")
            score -= 0.3

        if self._has_placeholders(desc):
            issues.append("Contains placeholder text")
            score -= 0.5

        if not project.get("technologies"):
            issues.append("Missing tech stack")
            score -= 0.1

        return self._finalize(score, issues)

    # ---------------- HELPERS ---------------- #

    def _finalize(self, score: float, issues: List[str]) -> Dict[str, Any]:
        score = max(0.0, min(score, 1.0))
        return {
            "score": round(score, 3),
            "passed": score >= 0.6,
            "issues": issues,
        }

    def _overall_score(self, results: Dict[str, Any]) -> float:
        weights = {"hero": 0.25, "bio": 0.35, "projects": 0.40}
        return sum(results[k]["score"] * w for k, w in weights.items())

    def _has_placeholders(self, text: str) -> bool:
        text = text.lower()
        return any(re.search(p, text) for p in self.PLACEHOLDER_PATTERNS)

    def _is_first_person(self, text: str) -> bool:
        return any(p in text.lower() for p in [" i ", " my ", " i'm ", " i've "])

    def _is_repetitive(self, text: str) -> bool:
        sentences = [s.strip().lower() for s in text.split(".") if s.strip()]
        return len(sentences) != len(set(sentences))

    def _check_consistency(
        self, portfolio: Dict[str, Any], original: Dict[str, Any]
    ) -> List[str]:
        warnings = []

        if portfolio.get("hero", {}).get("name") != original.get("name"):
            warnings.append("Hero name does not match original data")

        original_skills = set(s.lower() for s in original.get("skills", []))
        bio = portfolio.get("bio", "").lower()

        hallucinated = [
            word for word in re.findall(r"\b[a-zA-Z]{4,}\b", bio)
            if word not in original_skills
        ]

        if len(hallucinated) > 15:
            warnings.append("Possible skill hallucination in bio")

        if len(portfolio.get("projects", [])) > len(original.get("projects", [])):
            warnings.append("Generated more projects than provided")

        return warnings

    async def validate_and_enhance(
        self, generated_content: Dict[str, Any], original_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapter method for Orchestrator compatibility.
        """
        state = {
            "generated_content": generated_content,
            "clean_data": original_data,
        }
        
        # Reuse existing run logic
        try:
            await self.run(state)
        except ValidationError:
            if self.strict:
                raise
            # If not strict, we continue but mark valid=False inside run()
            
        return generated_content

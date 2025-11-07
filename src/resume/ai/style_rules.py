from __future__ import annotations

"""Style rules and validation for resume content generation.

This module provides configurable style guidelines and validation functions
to ensure resume content meets quality standards and ATS requirements.
"""

import re
from typing import Any

from pydantic import BaseModel
from pydantic import Field


class StyleRules(BaseModel):
    """Configurable style rules for resume content generation.

    These rules are enforced during content generation and validation
    to ensure consistent, professional, ATS-friendly resume content.
    """

    # Punctuation rules
    no_em_dashes: bool = Field(
        default=True,
        description="Reject em dashes (—) in content",
    )
    no_en_dashes: bool = Field(
        default=False,
        description="Reject en dashes (–) in content",
    )
    bullet_end_punctuation: str = Field(
        default="",
        description="Required punctuation at end of bullets ('', '.', or ';')",
    )

    # Formatting rules
    max_bullet_length: int = Field(
        default=120,
        description="Maximum character length for achievement bullets",
    )
    action_verb_start: bool = Field(
        default=True,
        description="Bullets must start with action verbs",
    )
    no_first_person: bool = Field(
        default=True,
        description="No first-person pronouns (I, my, we, our)",
    )

    # Content rules
    quantify_achievements: bool = Field(
        default=True,
        description="Prefer metrics and numbers in achievements",
    )
    no_buzzwords: list[str] = Field(
        default_factory=lambda: [
            "synergy",
            "rockstar",
            "ninja",
            "guru",
            "wizard",
            "unicorn",
        ],
        description="List of buzzwords to avoid",
    )

    def validate_bullet(self, bullet: str) -> list[str]:
        """Validate a single achievement bullet against style rules.

        Args:
            bullet: The achievement bullet text to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        violations = []

        # Check em dashes
        if self.no_em_dashes and "—" in bullet:
            violations.append(f"Em dash (—) found: {bullet[:50]}...")

        # Check en dashes
        if self.no_en_dashes and "–" in bullet:
            violations.append(f"En dash (–) found: {bullet[:50]}...")

        # Check bullet length
        if len(bullet) > self.max_bullet_length:
            violations.append(
                f"Bullet too long ({len(bullet)} chars, max {self.max_bullet_length}): "
                f"{bullet[:50]}..."
            )

        # Check action verb start
        if self.action_verb_start:
            if not bullet or not bullet[0].isupper():
                violations.append(
                    f"Bullet doesn't start with capital letter: {bullet[:50]}..."
                )
            # Check if starts with common weak words
            weak_starts = [
                "responsible for",
                "duties included",
                "worked on",
                "helped with",
            ]
            if any(bullet.lower().startswith(weak) for weak in weak_starts):
                violations.append(f"Weak action verb: {bullet[:50]}...")

        # Check first person
        if self.no_first_person:
            first_person_patterns = [
                r"\bI\b",
                r"\bmy\b",
                r"\bmine\b",
                r"\bwe\b",
                r"\bour\b",
                r"\bours\b",
            ]
            for pattern in first_person_patterns:
                if re.search(pattern, bullet, re.IGNORECASE):
                    violations.append(f"First person pronoun found: {bullet[:50]}...")
                    break

        # Check buzzwords
        for buzzword in self.no_buzzwords:
            if buzzword.lower() in bullet.lower():
                violations.append(
                    f"Buzzword '{buzzword}' found: {bullet[:50]}..."
                )

        # Check end punctuation
        if self.bullet_end_punctuation:
            if not bullet.endswith(self.bullet_end_punctuation):
                violations.append(
                    f"Bullet doesn't end with '{self.bullet_end_punctuation}': "
                    f"{bullet[:50]}..."
                )

        return violations

    def validate_content(self, content: dict[str, Any]) -> list[str]:
        """Validate resume content structure against style rules.

        Args:
            content: Resume content dictionary with 'experiences' key

        Returns:
            List of all validation errors found
        """
        all_violations = []

        # Extract all achievement bullets
        experiences = content.get("experiences", [])
        for exp in experiences:
            bullets = exp.get("achievements", [])
            for bullet in bullets:
                violations = self.validate_bullet(bullet)
                all_violations.extend(violations)

        return all_violations


# Common action verbs for resume bullets (for reference/future use)
STRONG_ACTION_VERBS = {
    "leadership": [
        "Led",
        "Directed",
        "Managed",
        "Orchestrated",
        "Coordinated",
        "Spearheaded",
        "Pioneered",
        "Championed",
    ],
    "technical": [
        "Architected",
        "Engineered",
        "Developed",
        "Implemented",
        "Built",
        "Designed",
        "Programmed",
        "Automated",
    ],
    "improvement": [
        "Optimized",
        "Enhanced",
        "Improved",
        "Streamlined",
        "Refined",
        "Upgraded",
        "Modernized",
        "Accelerated",
    ],
    "analysis": [
        "Analyzed",
        "Evaluated",
        "Assessed",
        "Investigated",
        "Diagnosed",
        "Researched",
        "Measured",
        "Monitored",
    ],
    "collaboration": [
        "Collaborated",
        "Partnered",
        "Facilitated",
        "Mentored",
        "Trained",
        "Coached",
        "Advised",
        "Consulted",
    ],
    "achievement": [
        "Achieved",
        "Delivered",
        "Reduced",
        "Increased",
        "Eliminated",
        "Generated",
        "Saved",
        "Exceeded",
    ],
}


def get_action_verbs_by_category(category: str) -> list[str]:
    """Get list of strong action verbs for a specific category.

    Args:
        category: One of 'leadership', 'technical', 'improvement',
                 'analysis', 'collaboration', 'achievement'

    Returns:
        List of action verbs for the category
    """
    return STRONG_ACTION_VERBS.get(category, [])


def get_all_action_verbs() -> list[str]:
    """Get all strong action verbs across all categories.

    Returns:
        Flat list of all action verbs
    """
    all_verbs = []
    for verbs in STRONG_ACTION_VERBS.values():
        all_verbs.extend(verbs)
    return all_verbs

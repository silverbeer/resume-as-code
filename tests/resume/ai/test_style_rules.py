from __future__ import annotations

"""Tests for style rules validation."""

import pytest

from resume.ai.style_rules import StyleRules


class TestStyleRules:
    """Test suite for StyleRules validation."""

    def test_validate_bullet_em_dash(self) -> None:
        """Test em dash detection."""
        rules = StyleRules(no_em_dashes=True)
        bullet = "Improved deployment speed — reduced time by 50%"

        violations = rules.validate_bullet(bullet)

        assert len(violations) == 1
        assert "Em dash" in violations[0]

    def test_validate_bullet_first_person(self) -> None:
        """Test first-person pronoun detection."""
        rules = StyleRules(no_first_person=True)
        bullets = [
            "I led a team of 5 engineers",
            "Managed my team effectively",
            "We delivered the project on time",
            "Coordinated with our stakeholders",
        ]

        for bullet in bullets:
            violations = rules.validate_bullet(bullet)
            assert any("First person" in v for v in violations), f"Failed for: {bullet}"

    def test_validate_bullet_length(self) -> None:
        """Test bullet length validation."""
        rules = StyleRules(max_bullet_length=50)
        bullet = "A" * 51

        violations = rules.validate_bullet(bullet)

        assert len(violations) == 1
        assert "too long" in violations[0]

    def test_validate_bullet_weak_start(self) -> None:
        """Test weak action verb detection."""
        rules = StyleRules(action_verb_start=True)
        bullets = [
            "Responsible for managing team",
            "Worked on improving performance",
            "Helped with deployment automation",
        ]

        for bullet in bullets:
            violations = rules.validate_bullet(bullet)
            assert any("Weak action verb" in v for v in violations), f"Failed for: {bullet}"

    def test_validate_bullet_buzzwords(self) -> None:
        """Test buzzword detection."""
        rules = StyleRules(no_buzzwords=["rockstar", "ninja"])
        bullet = "Rockstar engineer who delivered amazing results"

        violations = rules.validate_bullet(bullet)

        assert len(violations) == 1
        assert "rockstar" in violations[0].lower()

    def test_validate_bullet_no_violations(self) -> None:
        """Test valid bullet passes all rules."""
        rules = StyleRules(
            no_em_dashes=True,
            no_first_person=True,
            action_verb_start=True,
            max_bullet_length=120,
        )
        bullet = "Led team of 5 engineers, reducing deployment time by 60%"

        violations = rules.validate_bullet(bullet)

        assert len(violations) == 0

    def test_validate_content_structure(self) -> None:
        """Test content structure validation."""
        rules = StyleRules(no_em_dashes=True)
        content = {
            "experiences": [
                {
                    "achievements": [
                        "Good bullet without issues",
                        "Bad bullet with em dash — here",
                    ]
                }
            ]
        }

        violations = rules.validate_content(content)

        assert len(violations) == 1
        assert "Em dash" in violations[0]


class TestStyleRulesConfiguration:
    """Test StyleRules configuration options."""

    def test_default_configuration(self) -> None:
        """Test default rule configuration."""
        rules = StyleRules()

        assert rules.no_em_dashes is True
        assert rules.no_en_dashes is False
        assert rules.max_bullet_length == 120
        assert rules.action_verb_start is True
        assert rules.no_first_person is True
        assert rules.quantify_achievements is True
        assert "rockstar" in rules.no_buzzwords

    def test_custom_configuration(self) -> None:
        """Test custom rule configuration."""
        rules = StyleRules(
            no_em_dashes=False,
            max_bullet_length=100,
            no_buzzwords=["synergy"],
        )

        assert rules.no_em_dashes is False
        assert rules.max_bullet_length == 100
        assert rules.no_buzzwords == ["synergy"]

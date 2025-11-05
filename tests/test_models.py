"""Tests for resume data models."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from resume.models import (
    ContactInfo,
    Experience,
    Footer,
    Header,
    ProfessionalExperience,
    Resume,
    Skill,
    Skills,
    Summary,
)


class TestContactInfo:
    """Tests for ContactInfo model."""

    def test_valid_contact_info(self):
        """Test creating valid ContactInfo."""
        contact = ContactInfo(
            email="test@example.com",
            phone="+1-555-0100",
            linkedin="https://linkedin.com/in/test",
            github="https://github.com/test",
            website="https://test.dev",
            location="New York, NY",
        )

        assert contact.email == "test@example.com"
        assert contact.phone == "+1-555-0100"
        assert str(contact.linkedin) == "https://linkedin.com/in/test"
        assert str(contact.github) == "https://github.com/test"
        assert str(contact.website) == "https://test.dev/"
        assert contact.location == "New York, NY"

    def test_contact_info_optional_fields(self):
        """Test ContactInfo with only required fields."""
        contact = ContactInfo(email="test@example.com")

        assert contact.email == "test@example.com"
        assert contact.phone is None
        assert contact.linkedin is None
        assert contact.github is None
        assert contact.website is None
        assert contact.location is None

    def test_invalid_email(self):
        """Test ContactInfo with invalid email."""
        with pytest.raises(ValidationError):
            ContactInfo(email="not-an-email")

    def test_invalid_url(self):
        """Test ContactInfo with invalid URL."""
        with pytest.raises(ValidationError):
            ContactInfo(email="test@example.com", linkedin="not-a-url")


class TestHeader:
    """Tests for Header model."""

    def test_valid_header(self, sample_contact_info: ContactInfo):
        """Test creating valid Header."""
        header = Header(
            name="John Doe", title="Software Engineer", contact=sample_contact_info
        )

        assert header.name == "John Doe"
        assert header.title == "Software Engineer"
        assert header.contact == sample_contact_info

    def test_header_requires_all_fields(self):
        """Test Header requires all fields."""
        with pytest.raises(ValidationError):
            Header(name="John Doe", title="Engineer")  # Missing contact


class TestSummary:
    """Tests for Summary model."""

    def test_valid_summary(self):
        """Test creating valid Summary."""
        summary = Summary(content="Professional summary goes here.")

        assert summary.content == "Professional summary goes here."

    def test_summary_requires_content(self):
        """Test Summary requires content field."""
        with pytest.raises(ValidationError):
            Summary()  # Missing required content field


class TestExperience:
    """Tests for Experience model."""

    def test_valid_experience_current(self):
        """Test creating current Experience."""
        exp = Experience(
            company="Tech Corp",
            title="Senior Engineer",
            location="San Francisco, CA",
            start_date=date(2020, 1, 1),
            end_date=None,
            current=True,
            achievements=["Built microservices", "Led team"],
            technologies=["Python", "AWS"],
        )

        assert exp.company == "Tech Corp"
        assert exp.title == "Senior Engineer"
        assert exp.start_date == date(2020, 1, 1)
        assert exp.end_date is None
        assert exp.is_current is True
        assert len(exp.achievements) == 2
        assert len(exp.technologies) == 2

    def test_valid_experience_past(self):
        """Test creating past Experience."""
        exp = Experience(
            company="Old Corp",
            title="Engineer",
            start_date=date(2018, 1, 1),
            end_date=date(2020, 12, 31),
            current=False,
        )

        assert exp.is_current is False
        assert exp.end_date == date(2020, 12, 31)

    def test_experience_is_current_property(self):
        """Test is_current property logic."""
        # Current job
        exp1 = Experience(
            company="Test", title="Engineer", start_date=date(2020, 1, 1), current=True
        )
        assert exp1.is_current is True

        # Past job with end_date
        exp2 = Experience(
            company="Test",
            title="Engineer",
            start_date=date(2018, 1, 1),
            end_date=date(2020, 1, 1),
            current=False,
        )
        assert exp2.is_current is False

        # No end_date means current (returns True per is_current property logic: current OR end_date is None)
        exp3 = Experience(
            company="Test", title="Engineer", start_date=date(2020, 1, 1), current=False
        )
        assert exp3.is_current is True  # Because end_date is None


class TestProfessionalExperience:
    """Tests for ProfessionalExperience model."""

    def test_valid_professional_experience(self, sample_experience: ProfessionalExperience):
        """Test creating ProfessionalExperience."""
        assert len(sample_experience.experiences) == 2
        assert sample_experience.experiences[0].company == "Tech Corp"
        assert sample_experience.experiences[1].company == "Startup Inc"

    def test_empty_experiences(self):
        """Test ProfessionalExperience with no experiences."""
        prof_exp = ProfessionalExperience(experiences=[])
        assert len(prof_exp.experiences) == 0


class TestSkill:
    """Tests for Skill model."""

    def test_valid_skill(self):
        """Test creating valid Skill."""
        skill = Skill(name="Python", category="Programming", proficiency="Expert")

        assert skill.name == "Python"
        assert skill.category == "Programming"
        assert skill.proficiency == "Expert"

    def test_skill_optional_proficiency(self):
        """Test Skill with optional proficiency."""
        skill = Skill(name="Python", category="Programming")

        assert skill.proficiency is None


class TestSkills:
    """Tests for Skills model."""

    def test_valid_skills(self, sample_skills: Skills):
        """Test creating Skills."""
        assert len(sample_skills.skills) == 4

    def test_get_by_category(self, sample_skills: Skills):
        """Test get_by_category method."""
        programming = sample_skills.get_by_category("Programming")
        assert len(programming) == 1
        assert programming[0].name == "Python"

        infrastructure = sample_skills.get_by_category("Infrastructure")
        assert len(infrastructure) == 1
        assert infrastructure[0].name == "Kubernetes"

        # Non-existent category
        nonexistent = sample_skills.get_by_category("NonExistent")
        assert len(nonexistent) == 0

    def test_get_by_category_multiple(self):
        """Test get_by_category with multiple skills in same category."""
        skills = Skills(
            skills=[
                Skill(name="Python", category="Programming", proficiency="Expert"),
                Skill(name="JavaScript", category="Programming", proficiency="Advanced"),
                Skill(name="Go", category="Programming", proficiency="Intermediate"),
            ]
        )

        programming = skills.get_by_category("Programming")
        assert len(programming) == 3
        assert programming[0].name == "Python"
        assert programming[1].name == "JavaScript"
        assert programming[2].name == "Go"


class TestFooter:
    """Tests for Footer model."""

    def test_valid_footer_with_link(self):
        """Test creating Footer with link."""
        footer = Footer(
            text="Built with Resume as Code",
            link="https://github.com/test/resume",
            link_text="View Source",
        )

        assert footer.text == "Built with Resume as Code"
        assert str(footer.link) == "https://github.com/test/resume"
        assert footer.link_text == "View Source"

    def test_valid_footer_without_link(self):
        """Test creating Footer without link."""
        footer = Footer(text="Built with Resume as Code")

        assert footer.text == "Built with Resume as Code"
        assert footer.link is None
        assert footer.link_text is None

    def test_footer_with_emojis(self):
        """Test Footer with emojis."""
        footer = Footer(text="Built with Resume as Code 🚀 | Open source 💻")

        assert "🚀" in footer.text
        assert "💻" in footer.text


class TestResume:
    """Tests for Resume model."""

    def test_valid_resume_with_footer(self, sample_resume: Resume):
        """Test creating complete Resume with footer."""
        assert sample_resume.header.name == "John Doe"
        assert sample_resume.summary.content is not None
        assert len(sample_resume.experience.experiences) == 2
        assert len(sample_resume.skills.skills) == 4
        assert sample_resume.footer is not None
        assert sample_resume.footer.text == "Built with Resume as Code 🚀"

    def test_valid_resume_without_footer(
        self,
        sample_header: Header,
        sample_summary: Summary,
        sample_experience: ProfessionalExperience,
        sample_skills: Skills,
    ):
        """Test creating Resume without footer."""
        resume = Resume(
            header=sample_header,
            summary=sample_summary,
            experience=sample_experience,
            skills=sample_skills,
            footer=None,
        )

        assert resume.footer is None

    def test_resume_validation(
        self,
        sample_summary: Summary,
        sample_experience: ProfessionalExperience,
        sample_skills: Skills,
    ):
        """Test Resume requires all fields."""
        with pytest.raises(ValidationError):
            Resume(
                # Missing header
                summary=sample_summary,
                experience=sample_experience,
                skills=sample_skills,
            )

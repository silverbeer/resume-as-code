"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
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


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory structure."""
    data_dir = tmp_path / "data"
    common_dir = data_dir / "common"
    profiles_dir = data_dir / "profiles"

    common_dir.mkdir(parents=True)
    profiles_dir.mkdir(parents=True)

    return data_dir


@pytest.fixture
def sample_header_data() -> dict:
    """Sample header data for testing."""
    return {
        "name": "John Doe",
        "title": "Software Engineer",
        "contact": {
            "email": "john@example.com",
            "phone": "+1-555-0100",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "website": "https://johndoe.dev",
            "location": "San Francisco, CA",
        },
    }


@pytest.fixture
def sample_summary_data() -> dict:
    """Sample summary data for testing."""
    return {"content": "Experienced software engineer with 10+ years of experience."}


@pytest.fixture
def sample_experience_data() -> dict:
    """Sample experience data for testing."""
    return {
        "experiences": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "location": "San Francisco, CA",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "current": False,
                "achievements": [
                    "Built scalable microservices architecture",
                    "Led team of 5 engineers",
                ],
                "technologies": ["Python", "Kubernetes", "AWS"],
            },
            {
                "company": "Startup Inc",
                "title": "Software Engineer",
                "location": "Remote",
                "start_date": "2018-01-01",
                "current": True,
                "achievements": ["Developed REST APIs", "Improved test coverage"],
                "technologies": ["Python", "Django", "PostgreSQL"],
            },
        ]
    }


@pytest.fixture
def sample_skills_data() -> dict:
    """Sample skills data for testing."""
    return {
        "skills": [
            {"name": "Python", "category": "Programming", "proficiency": "Expert"},
            {"name": "Kubernetes", "category": "Infrastructure", "proficiency": "Advanced"},
            {"name": "pytest", "category": "Testing", "proficiency": "Expert"},
            {"name": "AWS", "category": "Cloud", "proficiency": "Advanced"},
        ]
    }


@pytest.fixture
def sample_footer_data() -> dict:
    """Sample footer data for testing."""
    return {
        "text": "Built with Resume as Code 🚀",
        "link": "https://github.com/example/resume-as-code",
        "link_text": "View on GitHub",
    }


@pytest.fixture
def sample_contact_info() -> ContactInfo:
    """Create sample ContactInfo model."""
    from resume.models import ContactInfo

    return ContactInfo(
        email="john@example.com",
        phone="+1-555-0100",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe",
        website="https://johndoe.dev",
        location="San Francisco, CA",
    )


@pytest.fixture
def sample_header(sample_contact_info: ContactInfo) -> Header:
    """Create sample Header model."""
    from resume.models import Header

    return Header(
        name="John Doe", title="Software Engineer", contact=sample_contact_info
    )


@pytest.fixture
def sample_summary() -> Summary:
    """Create sample Summary model."""
    from resume.models import Summary

    return Summary(content="Experienced software engineer with 10+ years of experience.")


@pytest.fixture
def sample_experience() -> ProfessionalExperience:
    """Create sample ProfessionalExperience model."""
    from resume.models import Experience, ProfessionalExperience

    experiences = [
        Experience(
            company="Tech Corp",
            title="Senior Engineer",
            location="San Francisco, CA",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            current=False,
            achievements=[
                "Built scalable microservices architecture",
                "Led team of 5 engineers",
            ],
            technologies=["Python", "Kubernetes", "AWS"],
        ),
        Experience(
            company="Startup Inc",
            title="Software Engineer",
            location="Remote",
            start_date=date(2018, 1, 1),
            end_date=None,
            current=True,
            achievements=["Developed REST APIs", "Improved test coverage"],
            technologies=["Python", "Django", "PostgreSQL"],
        ),
    ]

    return ProfessionalExperience(experiences=experiences)


@pytest.fixture
def sample_skills() -> Skills:
    """Create sample Skills model."""
    from resume.models import Skill, Skills

    skills = [
        Skill(name="Python", category="Programming", proficiency="Expert"),
        Skill(name="Kubernetes", category="Infrastructure", proficiency="Advanced"),
        Skill(name="pytest", category="Testing", proficiency="Expert"),
        Skill(name="AWS", category="Cloud", proficiency="Advanced"),
    ]

    return Skills(skills=skills)


@pytest.fixture
def sample_footer() -> Footer:
    """Create sample Footer model."""
    from resume.models import Footer

    return Footer(
        text="Built with Resume as Code 🚀",
        link="https://github.com/example/resume-as-code",
        link_text="View on GitHub",
    )


@pytest.fixture
def sample_resume(
    sample_header: Header,
    sample_summary: Summary,
    sample_experience: ProfessionalExperience,
    sample_skills: Skills,
    sample_footer: Footer,
) -> Resume:
    """Create complete sample Resume model."""
    from resume.models import Resume

    return Resume(
        header=sample_header,
        summary=sample_summary,
        experience=sample_experience,
        skills=sample_skills,
        footer=sample_footer,
    )

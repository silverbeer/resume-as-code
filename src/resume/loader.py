"""Data loader for resume components."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from resume.models import ContactInfo
from resume.models import Experience
from resume.models import Header
from resume.models import ProfessionalExperience
from resume.models import Resume
from resume.models import Skill
from resume.models import Skills
from resume.models import Summary
from resume.utils import get_data_dir
from resume.utils import load_yaml
from resume.utils import read_text_file


class ResumeLoader:
    """Loader for resume data from YAML files."""

    def __init__(self, profile: str) -> None:
        """Initialize loader with profile name.

        Args:
            profile: Profile name (e.g., 'sre-leadership')
        """
        self.profile = profile
        self.data_dir = get_data_dir()
        self.common_dir = self.data_dir / "common"
        self.profile_dir = self.data_dir / "profiles" / profile

        if not self.profile_dir.exists():
            raise ValueError(f"Profile not found: {profile}")

    def load_header(self) -> Header:
        """Load header data.

        Returns:
            Header model
        """
        data = load_yaml(self.common_dir / "header.yml")
        contact_data = data.pop("contact")
        return Header(
            name=data["name"],
            title=data["title"],
            contact=ContactInfo(**contact_data),
        )

    def load_summary(self) -> Summary:
        """Load profile-specific summary.

        Returns:
            Summary model
        """
        data = load_yaml(self.profile_dir / "summary.yml")
        return Summary(content=data["content"])

    def load_experience(self) -> ProfessionalExperience:
        """Load professional experience.

        Returns:
            ProfessionalExperience model with list of experiences
        """
        data = load_yaml(self.common_dir / "experience.yml")
        experiences = []

        for exp_data in data["experiences"]:
            # Convert date strings to date objects
            start_date = self._parse_date(exp_data["start_date"])
            end_date = None
            if "end_date" in exp_data and exp_data["end_date"]:
                end_date = self._parse_date(exp_data["end_date"])

            exp = Experience(
                company=exp_data["company"],
                title=exp_data["title"],
                location=exp_data.get("location"),
                start_date=start_date,
                end_date=end_date,
                current=exp_data.get("current", False),
                achievements=exp_data.get("achievements", []),
                technologies=exp_data.get("technologies", []),
            )
            experiences.append(exp)

        return ProfessionalExperience(experiences=experiences)

    def load_skills(self) -> Skills:
        """Load skills.

        Returns:
            Skills model with list of skills
        """
        data = load_yaml(self.common_dir / "skills.yml")
        skills = [Skill(**skill_data) for skill_data in data["skills"]]
        return Skills(skills=skills)

    def load_resume(self) -> Resume:
        """Load complete resume for profile.

        Returns:
            Complete Resume model
        """
        return Resume(
            header=self.load_header(),
            summary=self.load_summary(),
            experience=self.load_experience(),
            skills=self.load_skills(),
        )

    def load_job_description(self) -> str:
        """Load job description text for profile.

        Returns:
            Job description as string
        """
        job_file = self.profile_dir / "job.txt"
        if not job_file.exists():
            raise FileNotFoundError(
                f"No job description found for profile: {self.profile}"
            )
        return read_text_file(job_file)

    @staticmethod
    def _parse_date(date_str: str) -> date:
        """Parse date string in YYYY-MM-DD format.

        Args:
            date_str: Date string

        Returns:
            date object
        """
        parts = date_str.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))


def get_available_profiles() -> list[str]:
    """Get list of available profiles.

    Returns:
        List of profile names
    """
    profiles_dir = get_data_dir() / "profiles"
    if not profiles_dir.exists():
        return []

    return [p.name for p in profiles_dir.iterdir() if p.is_dir()]

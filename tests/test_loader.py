"""Tests for resume data loader."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from resume.loader import ResumeLoader, get_available_profiles


class TestResumeLoader:
    """Tests for ResumeLoader class."""

    @pytest.fixture
    def setup_common_data(self, temp_data_dir: Path, sample_header_data: dict, sample_experience_data: dict, sample_skills_data: dict):
        """Set up common data files."""
        common_dir = temp_data_dir / "common"

        # Header
        with open(common_dir / "header.yml", "w") as f:
            yaml.dump(sample_header_data, f)

        # Footer
        footer_data = {
            "text": "Built with Resume as Code 🚀",
            "link": "https://github.com/test/resume",
            "link_text": "View on GitHub",
        }
        with open(common_dir / "footer.yml", "w") as f:
            yaml.dump(footer_data, f)

        # Experience
        with open(common_dir / "experience.yml", "w") as f:
            yaml.dump(sample_experience_data, f)

        # Skills
        with open(common_dir / "skills.yml", "w") as f:
            yaml.dump(sample_skills_data, f)

    @pytest.fixture
    def setup_profile(self, temp_data_dir: Path, sample_summary_data: dict):
        """Set up a test profile."""
        profile_dir = temp_data_dir / "profiles" / "test-profile"
        profile_dir.mkdir(parents=True)

        # Summary (profile-specific)
        with open(profile_dir / "summary.yml", "w") as f:
            yaml.dump(sample_summary_data, f)

        # Job description
        with open(profile_dir / "job.txt", "w") as f:
            f.write("Senior Software Engineer position requiring Python and AWS experience.")

        return profile_dir

    def test_init_valid_profile(self, temp_data_dir: Path, setup_profile: Path, monkeypatch):
        """Test initializing loader with valid profile."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        assert loader.profile == "test-profile"
        assert loader.profile_dir == temp_data_dir / "profiles" / "test-profile"

    def test_init_invalid_profile(self, temp_data_dir: Path, monkeypatch):
        """Test initializing loader with non-existent profile."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        with pytest.raises(ValueError, match="Profile not found: nonexistent"):
            ResumeLoader("nonexistent")

    def test_load_header_from_common(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading header from common only."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        header = loader.load_header()

        assert header.name == "John Doe"
        assert header.title == "Software Engineer"
        assert header.contact.email == "john@example.com"

    def test_load_header_with_profile_override(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading header with profile-specific title override."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        # Create profile-specific header with title override
        profile_header = {"title": "Senior DevOps Engineer"}
        with open(setup_profile / "header.yml", "w") as f:
            yaml.dump(profile_header, f)

        loader = ResumeLoader("test-profile")
        header = loader.load_header()

        # Title should be overridden
        assert header.title == "Senior DevOps Engineer"
        # But name and contact should still come from common
        assert header.name == "John Doe"
        assert header.contact.email == "john@example.com"

    def test_load_summary(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading profile-specific summary."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        summary = loader.load_summary()

        assert "Experienced software engineer" in summary.content

    def test_load_experience_from_common(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading experience from common."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        experience = loader.load_experience()

        assert len(experience.experiences) == 2
        assert experience.experiences[0].company == "Tech Corp"
        assert experience.experiences[1].company == "Startup Inc"

    def test_load_experience_from_profile(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading experience from profile-specific file."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        # Create profile-specific experience
        profile_experience = {
            "experiences": [
                {
                    "company": "Profile Corp",
                    "title": "Lead Engineer",
                    "start_date": "2021-01-01",
                    "current": True,
                    "achievements": ["Led major initiative"],
                    "technologies": ["Kubernetes", "Python"],
                }
            ]
        }
        with open(setup_profile / "experience.yml", "w") as f:
            yaml.dump(profile_experience, f)

        loader = ResumeLoader("test-profile")
        experience = loader.load_experience()

        # Should load from profile, not common
        assert len(experience.experiences) == 1
        assert experience.experiences[0].company == "Profile Corp"

    def test_load_skills_from_common(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading skills from common."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        skills = loader.load_skills()

        assert len(skills.skills) == 4
        skill_names = [s.name for s in skills.skills]
        assert "Python" in skill_names

    def test_load_skills_from_profile(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading skills from profile-specific file."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        # Create profile-specific skills
        profile_skills = {
            "skills": [
                {"name": "Playwright", "category": "Testing", "proficiency": "Expert"},
                {"name": "Docker", "category": "Infrastructure", "proficiency": "Advanced"},
            ]
        }
        with open(setup_profile / "skills.yml", "w") as f:
            yaml.dump(profile_skills, f)

        loader = ResumeLoader("test-profile")
        skills = loader.load_skills()

        # Should load from profile, not common
        assert len(skills.skills) == 2
        skill_names = [s.name for s in skills.skills]
        assert "Playwright" in skill_names
        assert "Docker" in skill_names

    def test_load_footer(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading footer from common."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        footer = loader.load_footer()

        assert footer is not None
        assert "Built with Resume as Code" in footer.text
        assert footer.link_text == "View on GitHub"

    def test_load_footer_missing(self, temp_data_dir: Path, setup_profile: Path, monkeypatch):
        """Test loading footer when file doesn't exist."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        footer = loader.load_footer()

        assert footer is None

    def test_load_resume_complete(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading complete resume."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        resume = loader.load_resume()

        assert resume.header.name == "John Doe"
        assert resume.summary.content is not None
        assert len(resume.experience.experiences) == 2
        assert len(resume.skills.skills) == 4
        assert resume.footer is not None

    def test_load_job_description(self, temp_data_dir: Path, setup_common_data, setup_profile: Path, monkeypatch):
        """Test loading job description."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        loader = ResumeLoader("test-profile")
        job_desc = loader.load_job_description()

        assert "Senior Software Engineer" in job_desc
        assert "Python" in job_desc

    def test_load_job_description_missing(self, temp_data_dir: Path, setup_common_data, monkeypatch):
        """Test loading missing job description."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        # Create profile without job.txt
        profile_dir = temp_data_dir / "profiles" / "no-job-profile"
        profile_dir.mkdir(parents=True)

        summary_data = {"content": "Test summary"}
        with open(profile_dir / "summary.yml", "w") as f:
            yaml.dump(summary_data, f)

        loader = ResumeLoader("no-job-profile")

        with pytest.raises(FileNotFoundError, match="No job description found"):
            loader.load_job_description()

    def test_parse_date(self):
        """Test _parse_date static method."""
        date_obj = ResumeLoader._parse_date("2023-12-31")

        assert date_obj.year == 2023
        assert date_obj.month == 12
        assert date_obj.day == 31


class TestGetAvailableProfiles:
    """Tests for get_available_profiles function."""

    def test_get_available_profiles(self, temp_data_dir: Path, monkeypatch):
        """Test getting list of available profiles."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        # Create multiple profiles
        profiles_dir = temp_data_dir / "profiles"
        (profiles_dir / "sre-leadership").mkdir()
        (profiles_dir / "qe-leadership").mkdir()
        (profiles_dir / "sdet").mkdir()

        # Create a file (should be ignored)
        (profiles_dir / "readme.txt").touch()

        profiles = get_available_profiles()

        assert len(profiles) == 3
        assert "sre-leadership" in profiles
        assert "qe-leadership" in profiles
        assert "sdet" in profiles
        assert "readme.txt" not in profiles

    def test_get_available_profiles_empty(self, temp_data_dir: Path, monkeypatch):
        """Test getting profiles when directory is empty."""
        monkeypatch.setattr("resume.loader.get_data_dir", lambda: temp_data_dir)

        profiles = get_available_profiles()

        assert len(profiles) == 0

    def test_get_available_profiles_no_directory(self, tmp_path: Path, monkeypatch):
        """Test getting profiles when profiles directory doesn't exist."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        # Don't create profiles directory

        monkeypatch.setattr("resume.loader.get_data_dir", lambda: data_dir)

        profiles = get_available_profiles()

        assert len(profiles) == 0

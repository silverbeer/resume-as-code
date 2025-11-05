"""Pydantic models for resume data structures."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl


class ContactInfo(BaseModel):
    """Contact information."""

    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    location: Optional[str] = None


class Header(BaseModel):
    """Resume header with personal information."""

    name: str
    title: str
    contact: ContactInfo


class Summary(BaseModel):
    """Professional summary."""

    content: str = Field(..., description="Professional summary paragraph")


class Experience(BaseModel):
    """Single work experience entry."""

    company: str
    title: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    current: bool = False
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)

    @property
    def is_current(self) -> bool:
        """Check if this is current position."""
        return self.current or self.end_date is None


class ProfessionalExperience(BaseModel):
    """Collection of work experiences."""

    experiences: list[Experience] = Field(default_factory=list)


class Skill(BaseModel):
    """Individual skill."""

    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None  # e.g., "Expert", "Advanced", "Intermediate"


class Skills(BaseModel):
    """Collection of skills organized by category."""

    skills: list[Skill] = Field(default_factory=list)

    def get_by_category(self, category: str) -> list[Skill]:
        """Get all skills in a specific category."""
        return [s for s in self.skills if s.category == category]

    def get_skill_names(self) -> list[str]:
        """Get list of all skill names."""
        return [s.name for s in self.skills]


class Footer(BaseModel):
    """Footer information."""

    text: str = Field(..., description="Footer text with emojis")
    link: Optional[HttpUrl] = None
    link_text: Optional[str] = None


class Resume(BaseModel):
    """Complete resume data model."""

    header: Header
    summary: Summary
    experience: ProfessionalExperience
    skills: Skills
    footer: Optional[Footer] = None


class JobDescription(BaseModel):
    """Parsed job description."""

    title: str
    company: Optional[str] = None
    description: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)

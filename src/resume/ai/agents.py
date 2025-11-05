"""PydanticAI agents for job description analysis."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic_ai import Agent


class JobAnalysisResult(BaseModel):
    """Result from job description analysis."""

    required_skills: list[str] = Field(
        description="List of required/must-have skills extracted from job description"
    )
    preferred_skills: list[str] = Field(
        description="List of preferred/nice-to-have skills from job description"
    )
    key_responsibilities: list[str] = Field(
        description="Main responsibilities and duties for this role"
    )
    role_level: str = Field(
        description="Seniority level (e.g., Senior, Lead, Director, VP)"
    )
    role_type: str = Field(
        description="Primary role type (e.g., SRE, QE, SDET, Engineering Manager)"
    )


def _get_job_analysis_agent() -> Agent[None, JobAnalysisResult]:
    """Get or create the job analysis agent (lazy initialization).

    Returns:
        Configured PydanticAI agent
    """
    return Agent(
        "openai:gpt-4o",
        output_type=JobAnalysisResult,
        system_prompt="""You are an expert technical recruiter and job description analyzer.
        Your task is to carefully parse job descriptions and extract key information.

        Focus on:
        1. Required Skills: Technical skills, tools, and technologies that are mandatory
        2. Preferred Skills: Nice-to-have skills mentioned as preferred or bonus
        3. Key Responsibilities: Main duties and responsibilities (limit to 5-7 most important)
        4. Role Level: The seniority level of the position
        5. Role Type: The primary type of engineering role

        Be precise and extract actual skills/tools mentioned, not generic statements.
        For example: "Kubernetes", "Python", "AWS" are specific skills.
        Avoid: "strong communication skills", "team player" - focus on technical skills.
        """,
    )


class SkillGapAnalysis(BaseModel):
    """Analysis of skill gaps between resume and job requirements."""

    missing_required_skills: list[str] = Field(
        description="Required skills from job that are not in the resume"
    )
    missing_preferred_skills: list[str] = Field(
        description="Preferred skills from job that are not in the resume"
    )
    matching_skills: list[str] = Field(
        description="Skills that match between resume and job requirements"
    )
    skill_match_percentage: float = Field(
        description="Percentage of required skills that are matched (0-100)"
    )
    recommendations: list[str] = Field(
        description="Recommendations for improving the resume for this job"
    )


async def analyze_job_description(job_description: str) -> JobAnalysisResult:
    """Analyze a job description and extract key information.

    Args:
        job_description: The job description text

    Returns:
        JobAnalysisResult with extracted information
    """
    agent = _get_job_analysis_agent()
    result = await agent.run(job_description)
    return result.output


async def compare_skills(
    resume_skills: list[str], required_skills: list[str], preferred_skills: list[str]
) -> SkillGapAnalysis:
    """Compare resume skills against job requirements.

    Args:
        resume_skills: List of skills from resume
        required_skills: List of required skills from job
        preferred_skills: List of preferred skills from job

    Returns:
        SkillGapAnalysis with comparison results
    """
    # Normalize skills to lowercase for comparison
    resume_skills_lower = {s.lower() for s in resume_skills}
    required_lower = {s.lower() for s in required_skills}
    preferred_lower = {s.lower() for s in preferred_skills}

    # Find matching and missing skills
    matching = []
    for skill in required_skills:
        if skill.lower() in resume_skills_lower:
            matching.append(skill)

    missing_required = [s for s in required_skills if s.lower() not in resume_skills_lower]
    missing_preferred = [
        s for s in preferred_skills if s.lower() not in resume_skills_lower
    ]

    # Calculate match percentage
    match_pct = (
        (len(matching) / len(required_skills) * 100) if required_skills else 100.0
    )

    # Generate recommendations
    recommendations = []
    if missing_required:
        recommendations.append(
            f"Consider adding these {len(missing_required)} required skills to your resume"
        )
    if match_pct < 70:
        recommendations.append(
            "Your resume matches less than 70% of required skills - consider tailoring it more"
        )
    if len(matching) >= len(required_skills) * 0.8:
        recommendations.append(
            "Strong skill match! Highlight your experience with matching skills"
        )
    if missing_preferred and len(missing_preferred) <= 3:
        recommendations.append(
            "Consider highlighting any experience with the preferred skills"
        )

    return SkillGapAnalysis(
        missing_required_skills=missing_required,
        missing_preferred_skills=missing_preferred,
        matching_skills=matching,
        skill_match_percentage=round(match_pct, 1),
        recommendations=recommendations,
    )

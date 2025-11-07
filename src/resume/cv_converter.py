from __future__ import annotations

"""CV/Resume PDF to YAML converter using AI."""

from pathlib import Path

import pdfplumber
from pydantic import BaseModel
from pydantic import Field
from pydantic_ai import Agent


class CVExperience(BaseModel):
    """Extracted work experience from CV."""

    company: str = Field(description="Company name")
    title: str = Field(description="Job title")
    location: str | None = Field(default=None, description="Location (City, State/Country)")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str | None = Field(
        default=None,
        description="End date in YYYY-MM-DD format (None if current)"
    )
    current: bool = Field(default=False, description="Is this a current position?")
    achievements: list[str] = Field(
        default_factory=list,
        description="List of achievement bullets"
    )
    technologies: list[str] = Field(
        default_factory=list,
        description="Technologies, tools, and skills used"
    )


class CVData(BaseModel):
    """Complete CV data structure."""

    experiences: list[CVExperience] = Field(
        description="Work experience entries in reverse chronological order"
    )


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text content from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        RuntimeError: If PDF extraction fails
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        text_content = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)

        if not text_content:
            raise RuntimeError("No text could be extracted from PDF")

        return "\n\n".join(text_content)

    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}") from e


async def convert_cv_text_to_yaml(cv_text: str) -> CVData:
    """Convert CV text to structured YAML format using AI.

    Args:
        cv_text: Raw text extracted from CV

    Returns:
        Structured CVData with experiences

    Raises:
        RuntimeError: If AI conversion fails
    """
    agent = Agent(
        "openai:gpt-4o",
        output_type=CVData,
        system_prompt="""You are an expert at parsing resumes and CVs into structured data.

Your task is to extract work experience from the provided CV text and structure it properly.

For each job/position, extract:
1. **Company name**: Full company name
2. **Title**: Job title/position
3. **Location**: City, State/Country (if available)
4. **Start date**: In YYYY-MM-DD format (use YYYY-MM-01 if only month/year known)
5. **End date**: In YYYY-MM-DD format, or None if current position
6. **Current**: true if this is a current position, false otherwise
7. **Achievements**: List of bullet points describing accomplishments, responsibilities, and impact
   - Keep the original phrasing and metrics
   - Each bullet should be a complete sentence or phrase
   - Include quantifiable achievements (numbers, percentages, etc.)
8. **Technologies**: List of technologies, tools, programming languages, frameworks mentioned

Important:
- Extract experiences in reverse chronological order (most recent first)
- Preserve specific numbers, metrics, and percentages from the original CV
- If dates are vague (e.g., "2020"), use "2020-01-01" for start date
- For "Present" or "Current" positions, set end_date to None and current to true
- Be comprehensive - include all work experience found
- For technologies, extract specific tools/languages mentioned, not generic terms

Example date conversions:
- "January 2020" → "2020-01-01"
- "Jan 2020 - Dec 2020" → start_date: "2020-01-01", end_date: "2020-12-31"
- "2020 - Present" → start_date: "2020-01-01", end_date: None, current: true""",
    )

    try:
        result = await agent.run(cv_text)
        return result.output
    except Exception as e:
        raise RuntimeError(f"AI conversion failed: {e}") from e


async def convert_pdf_to_yaml(pdf_path: Path) -> CVData:
    """Convert PDF CV to structured YAML format.

    Args:
        pdf_path: Path to PDF CV file

    Returns:
        Structured CVData ready to be saved as YAML

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        RuntimeError: If conversion fails
    """
    # Step 1: Extract text from PDF
    cv_text = extract_text_from_pdf(pdf_path)

    # Step 2: Convert text to structured data using AI
    cv_data = await convert_cv_text_to_yaml(cv_text)

    return cv_data

from __future__ import annotations

"""CrewAI agents for multi-agent resume generation workflow.

This module defines specialized AI agents using CrewAI for collaborative
resume and cover letter generation from job descriptions.
"""

import time
from pathlib import Path
from typing import Any

from crewai import Agent
from crewai import Crew
from crewai import Process
from crewai import Task

from resume.ai.crew_models import CoverLetter
from resume.ai.crew_models import JobAnalysisResult
from resume.ai.crew_models import ProfileGenerationResult
from resume.ai.crew_models import QualityReview
from resume.ai.crew_models import ResumeContent
from resume.ai.style_rules import StyleRules


def create_job_analyzer_agent() -> Agent:
    """Create the Job Analyzer Agent.

    This agent specializes in parsing job descriptions and extracting
    key technical requirements, skills, and cultural indicators.

    Returns:
        Configured CrewAI Agent for job analysis
    """
    return Agent(
        role="Technical Recruiter and Job Analyst",
        goal="Extract precise technical requirements and skills from job descriptions",
        backstory="""You are a technical recruiter with 15 years of experience analyzing
        job descriptions for engineering roles. You have deep knowledge of technical skills,
        tools, and technologies across software development, DevOps, SRE, and QE domains.
        You excel at identifying what's truly required versus nice-to-have, and you understand
        the nuances of different seniority levels and role types.""",
        verbose=True,
        allow_delegation=False,
    )


def create_content_generator_agent(style_rules: StyleRules) -> Agent:
    """Create the Content Generator Agent.

    This agent specializes in crafting ATS-friendly, achievement-driven
    resume content tailored to specific job requirements.

    Args:
        style_rules: Style rules to follow during content generation

    Returns:
        Configured CrewAI Agent for content generation
    """
    style_guidelines = f"""
    CRITICAL STYLE RULES (MUST FOLLOW):
    - {'NEVER use em dashes (—) or en dashes (–)' if style_rules.no_em_dashes else 'Em dashes allowed'}
    - Use commas or parentheses for clauses instead of dashes
    - {'Start every bullet with strong action verb (past tense)' if style_rules.action_verb_start else ''}
    - {'NO first-person pronouns (I, my, we, our)' if style_rules.no_first_person else ''}
    - Keep bullets under {style_rules.max_bullet_length} characters
    - Quantify achievements with metrics whenever possible (numbers, percentages, time saved)
    - Avoid buzzwords: {', '.join(style_rules.no_buzzwords)}
    - Focus on IMPACT and OUTCOMES, not just tasks
    """

    return Agent(
        role="Resume Content Strategist",
        goal="Create tailored, ATS-friendly resume content that highlights relevant achievements",
        backstory=f"""You are an expert resume writer specializing in technical roles
        with 10+ years of experience. You know how to craft achievement-driven bullets that
        pass ATS systems while showcasing real impact. You understand the STAR method and
        always lead with outcomes.

        {style_guidelines}""",
        verbose=True,
        allow_delegation=False,
    )


def create_content_reviewer_agent(style_rules: StyleRules) -> Agent:
    """Create the Content Reviewer Agent.

    This agent specializes in quality assurance, ensuring resume content
    meets professional standards and style guidelines.

    Args:
        style_rules: Style rules to validate against

    Returns:
        Configured CrewAI Agent for content review
    """
    return Agent(
        role="Resume Quality Assurance Specialist",
        goal="Ensure resume content meets quality standards and style compliance",
        backstory="""You are a meticulous resume reviewer and experienced technical
        recruiter who has reviewed thousands of resumes. You know exactly what hiring
        managers and ATS systems look for. You provide constructive, specific feedback
        with examples. You are strict about style compliance but fair in your assessments.

        You check for:
        - Style guideline violations (em dashes, first person, weak verbs)
        - Achievement quantification (are there metrics?)
        - Job alignment (does experience match requirements?)
        - ATS optimization (are key job keywords present?)
        - Impact clarity (is the value proposition clear?)""",
        verbose=True,
        allow_delegation=True,  # Can ask generator to revise
    )


def create_cover_letter_agent() -> Agent:
    """Create the Cover Letter Agent.

    This agent specializes in writing compelling, personalized cover letters
    that complement the resume and demonstrate cultural fit.

    Returns:
        Configured CrewAI Agent for cover letter generation
    """
    return Agent(
        role="Cover Letter Specialist",
        goal="Write compelling cover letters that demonstrate fit and genuine interest",
        backstory="""You are a professional cover letter writer specializing in technical
        roles. You excel at storytelling, connecting a candidate's background to a specific
        role in a natural, engaging way. You know how to demonstrate cultural fit without
        using clichés. Your cover letters are conversational yet professional, specific yet
        concise (3-4 paragraphs maximum).

        You always:
        - Open with a strong hook related to the company or role
        - Highlight 2-3 most relevant achievements with brief examples
        - Show (don't tell) how skills translate to value
        - Demonstrate research and genuine interest
        - Close with clear call to action""",
        verbose=True,
        allow_delegation=False,
    )


def create_job_analysis_task(
    agent: Agent,
    job_description: str,
) -> Task:
    """Create job analysis task.

    Args:
        agent: Job analyzer agent
        job_description: Job description text

    Returns:
        Configured CrewAI Task
    """
    return Task(
        description=f"""Analyze this job description and extract key information:

{job_description}

Extract:
1. Required Skills: Technical skills explicitly required (be specific, e.g., "Kubernetes", not "containers")
2. Preferred Skills: Nice-to-have skills mentioned
3. Key Responsibilities: Top 5-7 most important duties
4. Role Level: Seniority (Junior, Mid, Senior, Staff, Principal, Director, VP)
5. Role Type: Primary role (SDET, SRE, QE Leadership, DevOps, Engineering Manager, etc.)
6. Company Culture: Any cultural indicators or values mentioned

Be precise. Focus on technical details, not soft skills.""",
        expected_output="Structured analysis of job requirements with categorized skills and clear role identification",
        agent=agent,
        output_pydantic=JobAnalysisResult,
    )


def create_content_generation_task(
    agent: Agent,
    existing_experience: list[dict[str, Any]],
    job_analysis_task: Task,
) -> Task:
    """Create content generation task.

    Args:
        agent: Content generator agent
        existing_experience: Candidate's existing work experience
        job_analysis_task: Previous job analysis task for context

    Returns:
        Configured CrewAI Task
    """
    return Task(
        description=f"""Generate tailored resume content based on the job analysis.

Using the candidate's existing experience below, reframe achievement bullets to align
with the target job requirements. Prioritize relevant skills and highlight matching
technologies.

Candidate's Experience:
{existing_experience}

Requirements:
1. Create professional title for header matching target role
2. Write 3-4 sentence professional summary emphasizing relevant experience
3. Reframe achievement bullets to highlight relevant impact (keep bullets under 120 chars)
4. Select and organize skills by relevance to target job
5. Use strong action verbs and quantify achievements with metrics

Remember: Follow ALL style rules strictly (no em dashes, no first person, action verbs, metrics).""",
        expected_output="Complete resume content in structured format with tailored header, summary, experience bullets, and prioritized skills",
        agent=agent,
        context=[job_analysis_task],  # Gets job analysis automatically
        output_pydantic=ResumeContent,
    )


def create_quality_review_task(
    agent: Agent,
    content_generation_task: Task,
    style_rules: StyleRules,
) -> Task:
    """Create quality review task with guardrails.

    Args:
        agent: Content reviewer agent
        content_generation_task: Previous content generation task
        style_rules: Style rules to validate against

    Returns:
        Configured CrewAI Task with quality guardrails
    """
    def quality_guardrail(output: str) -> str | None:
        """Validate quality standards (used by CrewAI for auto-retry).

        Args:
            output: Task output to validate

        Returns:
            None if valid, error message if invalid
        """
        # This is a simple guardrail - CrewAI will retry up to 3 times if it returns an error
        # In practice, the agent's own judgment is primary; this is a safety net
        if "passes_review: false" in output.lower():
            return "Quality review failed - content needs improvement"
        return None

    return Task(
        description=f"""Review the generated resume content for quality and compliance.

Evaluate:
1. **Style Compliance**: Check for em dashes, first person, weak verbs, bullet length
2. **Job Alignment**: Does experience clearly match job requirements? (rate 1-10)
3. **Achievement Quality**: Are accomplishments quantified with metrics?
4. **Action Verb Strength**: Strong, varied action verbs used?
5. **ATS Optimization**: Are key job keywords naturally integrated?

Style Rules to Check:
- No em dashes (—) or en dashes (–)
- No first person (I, my, we, our)
- Bullets start with action verbs
- Bullets under {style_rules.max_bullet_length} characters
- Achievements quantified with numbers/metrics
- No buzzwords: {', '.join(style_rules.no_buzzwords)}

Provide:
- passes_review: true/false
- alignment_score: 1-10 (how well it matches job)
- style_compliance_score: 1-10 (how well it follows style rules)
- issues_found: Specific problems with examples
- suggestions: Constructive improvements
- strengths: What's working well

Be thorough but fair. Only pass if alignment_score >= 7 and style_compliance_score >= 8.""",
        expected_output="Detailed quality review with scores, issues, suggestions, and pass/fail decision",
        agent=agent,
        context=[content_generation_task],
        output_pydantic=QualityReview,
        guardrails=[quality_guardrail],
    )


def create_cover_letter_task(
    agent: Agent,
    job_analysis_task: Task,
    content_generation_task: Task,
) -> Task:
    """Create cover letter generation task.

    Args:
        agent: Cover letter agent
        job_analysis_task: Job analysis task for context
        content_generation_task: Content generation task for context

    Returns:
        Configured CrewAI Task
    """
    return Task(
        description="""Generate a compelling cover letter that complements the resume.

Using the job analysis and resume content, write a cover letter that:

1. **Opening**: Strong hook related to the company or specific role aspect (show research)
2. **Body** (2-3 paragraphs):
   - Highlight 2-3 most relevant achievements from resume with brief context
   - Connect experience directly to job responsibilities
   - Demonstrate cultural fit through specific examples (not generic statements)
3. **Closing**: Express genuine interest and clear call to action

Style:
- Professional but conversational tone
- 3-4 paragraphs total (concise!)
- Specific examples over generalizat ions
- Show don't tell (e.g., "Reduced deployment time by 60%" not "I'm efficient")
- No clichés ("passionate team player", "hit the ground running")
- Demonstrate you read the job description thoroughly

Focus on why THIS candidate for THIS role at THIS company.""",
        expected_output="Well-structured cover letter with engaging opening, relevant examples, and strong closing",
        agent=agent,
        context=[job_analysis_task, content_generation_task],
        output_pydantic=CoverLetter,
    )


class ProfileGenerator:
    """Orchestrates multi-agent resume profile generation workflow."""

    def __init__(
        self,
        style_rules: StyleRules | None = None,
        model: str = "gpt-4o",
        verbose: bool = True,
    ):
        """Initialize profile generator with configuration.

        Args:
            style_rules: Style rules for content generation (defaults to standard rules)
            model: OpenAI model to use (default: gpt-4o)
            verbose: Whether to show agent progress
        """
        self.style_rules = style_rules or StyleRules()
        self.model = model
        self.verbose = verbose

        # Create specialized agents
        self.job_analyzer = create_job_analyzer_agent()
        self.content_generator = create_content_generator_agent(self.style_rules)
        self.content_reviewer = create_content_reviewer_agent(self.style_rules)
        self.cover_letter_writer = create_cover_letter_agent()

    def generate_profile(
        self,
        profile_name: str,
        job_description: str,
        existing_experience: list[dict[str, Any]],
    ) -> ProfileGenerationResult:
        """Generate complete resume profile from job description.

        This is the main orchestration method that coordinates all agents
        in a sequential workflow with quality guardrails.

        Args:
            profile_name: Name for the generated profile
            job_description: Job description text
            existing_experience: Candidate's work experience

        Returns:
            Complete profile generation result with all artifacts

        Raises:
            RuntimeError: If profile generation fails after max retries
        """
        start_time = time.time()

        # Create tasks
        analyze_task = create_job_analysis_task(
            self.job_analyzer,
            job_description,
        )

        generate_task = create_content_generation_task(
            self.content_generator,
            existing_experience,
            analyze_task,
        )

        review_task = create_quality_review_task(
            self.content_reviewer,
            generate_task,
            self.style_rules,
        )

        cover_letter_task = create_cover_letter_task(
            self.cover_letter_writer,
            analyze_task,
            generate_task,
        )

        # Create crew with sequential process
        crew = Crew(
            agents=[
                self.job_analyzer,
                self.content_generator,
                self.content_reviewer,
                self.cover_letter_writer,
            ],
            tasks=[
                analyze_task,
                generate_task,
                review_task,
                cover_letter_task,
            ],
            process=Process.sequential,
            verbose=self.verbose,
        )

        # Execute workflow
        result = crew.kickoff()

        # Extract outputs from tasks
        job_analysis = analyze_task.output.pydantic
        resume_content = generate_task.output.pydantic
        quality_review = review_task.output.pydantic
        cover_letter = cover_letter_task.output.pydantic

        duration = time.time() - start_time

        return ProfileGenerationResult(
            profile_name=profile_name,
            job_analysis=job_analysis,
            resume_content=resume_content,
            quality_review=quality_review,
            cover_letter=cover_letter,
            iterations=1,  # CrewAI handles retries internally via guardrails
            total_duration_seconds=duration,
        )

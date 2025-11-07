# Agentic Profile Generator - Design Document

## Overview

An AI-powered multi-agent system that automatically generates resume profiles and cover letters from job descriptions. The system uses PydanticAI to orchestrate multiple specialized AI agents that analyze jobs, generate content, self-review, and iterate until quality standards are met.

## Goals

1. **Automate profile creation**: Given a job description, generate all profile files (header.yml, summary.yml, experience.yml, skills.yml)
2. **Generate cover letters**: Create tailored cover letters that complement the resume
3. **Enforce style rules**: Automatically validate content against configurable style guidelines (no em dashes, action verbs, etc.)
4. **Self-review and iterate**: Agents review their own output and iterate until quality standards are met
5. **Human-in-the-loop**: User reviews and approves before files are written

## Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                    ProfileGenerator                         │
│                    (Orchestrator)                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Agent 1    │  │   Agent 2    │  │   Agent 3    │     │
│  │     Job      │→ │   Content    │→ │   Content    │     │
│  │   Analyzer   │  │  Generator   │  │   Reviewer   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                           ↓                                 │
│                    ┌──────────────┐                         │
│                    │   Agent 4    │                         │
│                    │Cover Letter  │                         │
│                    │  Generator   │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Execution Flow

```
User runs CLI
    ↓
1. Job Analysis Agent
   - Extracts required/preferred skills
   - Identifies role level (Senior, Staff, etc.)
   - Identifies role type (SDET, SRE, QE Lead)
   - Analyzes company culture and key responsibilities
    ↓
2. Content Generation Loop (with self-review)
   for iteration in 1..max_iterations:
       a. Content Generator Agent
          - Generates header title
          - Writes professional summary
          - Reframes experience bullets for target role
          - Selects and organizes relevant skills
       b. Python Style Validation
          - Checks for em dashes
          - Validates action verb usage
          - Ensures no first-person pronouns
          - Checks bullet length
       c. Content Reviewer Agent
          - Reviews job alignment
          - Checks achievement quantification
          - Validates ATS keyword optimization
       d. If passed → break, else → provide feedback for next iteration
    ↓
3. Cover Letter Generation (parallel with other content)
   - Generates compelling opening paragraph
   - Highlights relevant experience
   - Demonstrates cultural fit
   - Strong closing with call to action
    ↓
4. Display Results & Get User Approval
   - Show job analysis summary
   - Display generated content preview
   - Show style validation results
   - Ask for confirmation
    ↓
5. Write Profile Files
   - data/profiles/{profile_name}/header.yml
   - data/profiles/{profile_name}/summary.yml
   - data/profiles/{profile_name}/experience.yml
   - data/profiles/{profile_name}/skills.yml
   - data/profiles/{profile_name}/job.txt
   - data/profiles/{profile_name}/cover_letter.md
```

### Parallelization Strategy

```python
# Sequential (dependencies)
job_analysis = await analyze_job()           # Must go first
content = await generate_content()           # Needs job_analysis

# Parallel (independent)
review, cover_letter, linkedin = await asyncio.gather(
    review_content(content),                 # All three only depend on
    generate_cover_letter(job, content),     # previous results, not
    generate_linkedin_summary(content),      # each other
)
```

## Component Design

### 1. Style Rules Configuration

```python
class StyleRules(BaseModel):
    """Configurable style guidelines for resume content"""

    # Punctuation rules
    no_em_dashes: bool = True
    no_en_dashes: bool = False
    bullet_end_punctuation: str = ""  # "", ".", ";"

    # Formatting rules
    max_bullet_length: int = 120
    action_verb_start: bool = True
    no_first_person: bool = True

    # Content rules
    quantify_achievements: bool = True
    no_buzzwords: list[str] = ["synergy", "rockstar", "ninja", "guru"]

    def validate_bullet(self, bullet: str) -> list[str]:
        """Returns list of style violations"""
```

### 2. Agent Output Models

```python
class JobAnalysisResult(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    key_responsibilities: list[str]
    role_level: str          # "senior", "staff", "principal"
    role_type: str           # "SDET", "SRE", "QE Leadership"
    company_culture_notes: str

class ProfileContent(BaseModel):
    header_title: str
    summary: str
    experiences: list[dict]  # Tailored achievement bullets
    skills: list[dict]       # Categorized and prioritized
    style_violations: list[str] = Field(default_factory=list)

class ReviewResult(BaseModel):
    passes_review: bool
    issues_found: list[str]
    suggestions: list[str]
    alignment_score: int     # 1-10 rating vs job requirements

class CoverLetter(BaseModel):
    opening_paragraph: str
    body_paragraphs: list[str]
    closing_paragraph: str
    call_to_action: str

class ProfileGenerationResult(BaseModel):
    profile_name: str
    job_analysis: JobAnalysisResult
    profile_content: ProfileContent
    cover_letter: CoverLetter
    review_passed: bool
    iterations: int
```

### 3. ProfileGenerator Class

```python
class ProfileGenerator:
    """Orchestrates multi-agent resume generation"""

    def __init__(
        self,
        style_rules: StyleRules,
        max_iterations: int = 3,
        model: str = "openai:gpt-4o"
    ):
        self.style_rules = style_rules
        self.max_iterations = max_iterations

        # Initialize specialized agents
        self.job_analyzer = Agent(...)
        self.content_generator = Agent(...)
        self.content_reviewer = Agent(...)
        self.cover_letter_agent = Agent(...)

    async def generate_profile(
        self,
        profile_name: str,
        job_description: str,
        existing_experience: list[dict]
    ) -> ProfileGenerationResult:
        """Main orchestration method"""
```

## CLI Integration

### New Command: `generate-profile`

```bash
# Basic usage
uv run resume generate-profile senior-sdet --job job.txt

# With options
uv run resume generate-profile senior-sdet \
  --job job_descriptions/datadog_sdet.txt \
  --no-em-dashes \
  --max-iterations 3 \
  --output-dir data/profiles/senior-sdet \
  --auto-build  # Automatically build PDF after generation

# With custom style rules
uv run resume generate-profile staff-sre \
  --job job.txt \
  --no-em-dashes \
  --no-first-person \
  --max-bullet-length 100 \
  --require-metrics
```

### Command Options

```python
@app.command()
def generate_profile(
    profile_name: str = typer.Argument(...),
    job_file: Path = typer.Option(..., "--job", "-j"),

    # Style rules
    no_em_dashes: bool = typer.Option(True),
    no_first_person: bool = typer.Option(True),
    action_verb_start: bool = typer.Option(True),
    max_bullet_length: int = typer.Option(120),

    # Agent configuration
    max_iterations: int = typer.Option(3),
    model: str = typer.Option("openai:gpt-4o"),

    # Output options
    output_dir: Optional[Path] = typer.Option(None),
    auto_build: bool = typer.Option(False),
    skip_confirmation: bool = typer.Option(False),
):
    """Generate resume profile using AI agents"""
```

## Implementation Plan

### Phase 1: Core Infrastructure
- [ ] Create `src/resume/ai/style_rules.py` with StyleRules model and validation
- [ ] Create `src/resume/ai/profile_generator.py` with agent models
- [ ] Implement Job Analyzer Agent with system prompts
- [ ] Write unit tests for style validation

### Phase 2: Content Generation
- [ ] Implement Content Generator Agent
- [ ] Implement Content Reviewer Agent
- [ ] Build iterative review loop
- [ ] Add progress indicators with Rich

### Phase 3: Cover Letter & Additional Content
- [ ] Implement Cover Letter Agent
- [ ] Add parallel execution with asyncio.gather()
- [ ] Optional: LinkedIn summary generator
- [ ] Optional: Thank you email generator

### Phase 4: CLI Integration
- [ ] Add `generate-profile` command to cli.py
- [ ] Implement user confirmation flow
- [ ] Add YAML file writing logic
- [ ] Add auto-build option
- [ ] Rich console output with previews

### Phase 5: Testing & Documentation
- [ ] Unit tests for all agents
- [ ] Integration tests for full workflow
- [ ] Update CLAUDE.md with agent documentation
- [ ] Update README.md with usage examples
- [ ] Add example outputs to docs/

## Style Validation Rules

### Critical Rules (Must Pass)

1. **No em dashes** (`—`): Use commas or parentheses instead
2. **No en dashes** (`–`): Use hyphens (`-`) for ranges
3. **Action verb start**: All bullets start with past-tense action verbs
4. **No first person**: No "I", "my", "we", "our"
5. **Max length**: Bullets under 120 characters

### Quality Rules (AI Review)

1. **Quantification**: Prefer metrics and numbers
2. **Job alignment**: Experience matches job requirements
3. **ATS optimization**: Key job keywords present
4. **Impact focus**: Emphasize outcomes over tasks
5. **No buzzwords**: Avoid "synergy", "rockstar", "ninja"

## Agent System Prompts

### Job Analyzer Agent

```
You are an expert technical recruiter and job description analyzer.

Analyze the provided job description and extract:

1. Required Skills: Technical skills explicitly required
2. Preferred Skills: Nice-to-have skills mentioned
3. Key Responsibilities: Core duties of the role
4. Role Level: Determine seniority (Junior, Mid, Senior, Staff, Principal, etc.)
5. Role Type: Categorize (SDET, SRE, QE Leadership, DevOps, etc.)
6. Company Culture: Note any cultural indicators or values

Be precise and comprehensive. Focus on technical details.
```

### Content Generator Agent

```
You are an expert resume writer specializing in technical roles.

Generate resume content that:
1. Highlights relevant experience from the candidate's background
2. Reframes achievement bullets to align with the target job
3. Uses strong action verbs and quantified metrics
4. Follows strict style guidelines
5. Optimizes for ATS keyword matching

CRITICAL STYLE RULES:
- NEVER use em dashes (—) or en dashes (–)
- Use commas or parentheses for clauses
- Start every bullet with a strong action verb (past tense for previous roles)
- No first-person pronouns (I, my, we, our)
- Quantify achievements with metrics whenever possible
- Keep bullets under 120 characters
- No buzzwords like "rockstar", "ninja", "synergy"

Focus on impact and relevance to the target role.
```

### Content Reviewer Agent

```
You are a meticulous resume reviewer and technical recruiter.

Review the resume content for:

1. Style Compliance: Check for em dashes, first person, buzzwords, bullet length
2. Job Alignment: Does experience match the target role requirements?
3. Achievement Quality: Are accomplishments quantified and impactful?
4. Action Verb Strength: Do bullets start with strong, varied action verbs?
5. ATS Optimization: Are key job keywords present?

Provide:
- passes_review: true/false
- issues_found: Specific problems with examples
- suggestions: Constructive improvement ideas
- alignment_score: 1-10 rating vs job requirements

Be strict but constructive. Focus on specific, actionable feedback.
```

### Cover Letter Agent

```
You are an expert cover letter writer for technical roles.

Generate a compelling cover letter that:
1. Opens with a strong hook related to the company or role
2. Demonstrates deep understanding of the job requirements
3. Highlights 2-3 most relevant achievements from resume
4. Shows cultural fit and genuine interest
5. Closes with clear call to action

Style guidelines:
- Professional but conversational tone
- 3-4 paragraphs max
- No clichés or generic phrases
- Specific examples over generalizations
- Show don't tell (demonstrate skills through stories)

Focus on why this candidate is uniquely qualified for THIS role at THIS company.
```

## File Structure

```
src/resume/ai/
├── __init__.py
├── agents.py              # Existing job analysis agent
├── style_rules.py         # NEW: Style validation
├── profile_generator.py   # NEW: Multi-agent orchestrator
└── prompts.py            # NEW: System prompts library

tests/resume/ai/
├── test_style_rules.py
├── test_profile_generator.py
└── fixtures/
    ├── sample_job_description.txt
    └── sample_experience.yml

docs/
├── agentic-profile-generator-design.md  # This file
└── examples/
    ├── example_generated_profile/
    └── example_cover_letter.md
```

## Success Criteria

1. **Functional**: Generate complete, valid profile files from job description
2. **Quality**: 90%+ of bullets pass style validation on first try
3. **Performance**: Complete generation in under 30 seconds
4. **User Experience**: Clear progress indicators, helpful error messages
5. **Testable**: 80%+ code coverage with unit and integration tests

## Future Enhancements

- [ ] Multi-provider support (Anthropic Claude, Google Gemini)
- [ ] A/B testing of different prompts
- [ ] Profile version comparison and diff
- [ ] Batch generation for multiple jobs
- [ ] Web UI for non-technical users
- [ ] Integration with job board APIs (LinkedIn, Indeed)
- [ ] Resume scoring and recommendations
- [ ] Interview prep question generation

## References

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Typer CLI Documentation](https://typer.tiangolo.com/)
- [Resume Best Practices](https://www.indeed.com/career-advice/resumes-cover-letters)
- [ATS Optimization Guide](https://www.jobscan.co/blog/ats-resume/)

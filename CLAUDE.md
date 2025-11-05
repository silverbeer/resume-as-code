# Claude AI Instructions for Resume as Code (RaC)

## Project Vision
This is an AI-powered learning project exploring "Resume as Code (RaC)" - a modern approach to resume management that demonstrates DevOps expertise through:
- YAML-based structured resume data (version controlled, AI-friendly)
- Multi-format automated compilation (PDF, HTML)
- Profile-specific customization for different job types
- GitOps workflow with AI-powered job analysis
- Modern Python tooling showcasing best practices

## Technical Stack & Standards

### Core Technologies
- **Python**: uv for dependency management, pyproject.toml configuration
- **CLI Framework**: Typer with Rich for beautiful terminal interfaces
- **AI Integration**: PydanticAI with OpenAI for job description analysis
- **PDF Generation**: Playwright (headless Chromium)
- **HTML Templates**: Jinja2
- **Data Models**: Pydantic for validation

### Code Quality Requirements
- Type hints on all functions
- Ruff linting with strict configuration
- Comprehensive error handling and logging
- Rich CLI output with progress indicators

## Project Structure

```
resume-as-code/
├── CLAUDE.md                   # This file - AI instructions
├── README.md                  # Public-facing project overview
├── pyproject.toml             # Python project configuration (uv)
├── uv.lock                    # Dependency lock file
├── data/
│   ├── common/                # Shared/default resume data
│   │   ├── header.yml        # Default contact info, name
│   │   ├── footer.yml        # Footer with project branding
│   │   ├── experience.yml    # Default work history
│   │   └── skills.yml        # Default skills
│   └── profiles/             # Profile-specific data
│       ├── qe-leadership/
│       │   ├── header.yml    # QE-specific title override
│       │   ├── summary.yml   # QE-tailored summary
│       │   ├── experience.yml # QE-focused achievement bullets
│       │   ├── skills.yml    # QE-focused skills
│       │   └── job.txt       # Target job description
│       ├── sdet/
│       │   ├── header.yml
│       │   ├── summary.yml
│       │   ├── experience.yml
│       │   ├── skills.yml
│       │   └── job.txt
│       └── sre-leadership/
│           ├── header.yml
│           ├── summary.yml
│           ├── experience.yml
│           ├── skills.yml
│           └── job.txt
├── src/
│   └── resume/
│       ├── __init__.py
│       ├── cli.py            # Main Typer CLI application
│       ├── models.py         # Pydantic data models
│       ├── loader.py         # YAML data loader with profile overrides
│       ├── builder.py        # HTML builder
│       ├── pdf.py            # Playwright PDF generator
│       ├── utils.py          # Utilities
│       └── ai/
│           ├── __init__.py
│           └── agents.py     # PydanticAI agents for job analysis
├── templates/
│   └── resume.html.j2        # Jinja2 HTML template
├── output/                   # Generated resumes
└── tests/                    # Test suite
```

## CLI Commands (Typer + Rich)

### Actual Implemented Commands

```bash
# List available profiles
uv run resume list-profiles

# Analyze job description and compare skills
uv run resume analyze <profile>

# Build resume in HTML format (default)
uv run resume build <profile>

# Build resume in PDF format
uv run resume build <profile> --format pdf

# Build both formats
uv run resume build <profile> --format both

# Custom output path
uv run resume build <profile> --output ./custom-path.html
```

**Important**: All commands must be prefixed with `uv run` since the package is not installed globally.

## Profile-Specific Customization

### How It Works

The loader implements a **profile-first, fallback-to-common** strategy:

1. **Check profile directory** (`data/profiles/<profile>/`)
   - If `header.yml` exists → use it (merged with common for contact info)
   - If `skills.yml` exists → use it (completely override)
   - If `experience.yml` exists → use it (completely override)
   - `summary.yml` → always profile-specific (required)

2. **Fallback to common** (`data/common/`)
   - If profile files don't exist, use common defaults
   - `footer.yml` → always loaded from common

### Profile Override Examples

**Header Override** (`data/profiles/sdet/header.yml`):
```yaml
# Only override the title, contact info comes from common/header.yml
title: "Software Developer in Test | Quality Engineering Professional"
```

**Skills Override** (`data/profiles/sdet/skills.yml`):
```yaml
# Complete skills list specific to SDET role
skills:
  - name: "Playwright"
    category: "Testing"
    proficiency: "Expert"
  - name: "REST API Testing"
    category: "Testing"
    proficiency: "Expert"
  # ... more SDET-specific skills
```

**Experience Override** (`data/profiles/sdet/experience.yml`):
```yaml
experiences:
  - company: "Viant Technology"
    title: "Director, Cloud Reliability Engineering"
    achievements:
      - "Introduced quality engineering discipline into Cloud Reliability Engineering..."
      - "Architected observability-driven quality metrics..."
      # ... QE/Testing-focused achievement bullets
```

## AI Integration (PydanticAI + OpenAI)

### Current Implementation

The project uses **PydanticAI** with OpenAI GPT-4 for:

1. **Job Description Analysis** (`resume analyze <profile>`)
   - Extracts required and preferred skills
   - Identifies role level and type
   - Lists key responsibilities
   - Uses `JobAnalysisResult` Pydantic model

2. **Skill Gap Analysis**
   - Compares resume skills against job requirements
   - Calculates skill match percentage
   - Identifies missing required/preferred skills
   - Provides recommendations
   - Uses `SkillGapAnalysis` Pydantic model

### Agent Configuration

```python
# src/resume/ai/agents.py
from pydantic_ai import Agent

def _get_job_analysis_agent() -> Agent[None, JobAnalysisResult]:
    return Agent(
        "openai:gpt-4o",
        output_type=JobAnalysisResult,  # NOTE: PydanticAI 1.0+ uses output_type not result_type
        system_prompt="""You are an expert technical recruiter and job description analyzer...
        """
    )
```

**Important API Changes**:
- PydanticAI 1.0+: `result_type` → `output_type`
- PydanticAI 1.0+: `result.data` → `result.output`

## PDF Generation (Playwright)

### Why Playwright?

Replaced WeasyPrint due to native dependency issues on macOS (libgobject, pango, cairo). Playwright provides:
- ✅ No native dependencies
- ✅ Cross-platform (macOS, Linux, Windows)
- ✅ Consistent rendering (Chromium)
- ✅ Better CSS support

### Implementation

```python
# src/resume/pdf.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(html_content)
    page.wait_for_load_state("networkidle")
    page.pdf(
        path=str(output_file),
        format="Letter",
        print_background=True,
        margin={"top": "0.5in", "right": "0.5in", "bottom": "0.5in", "left": "0.5in"},
    )
    browser.close()
```

### Setup

```bash
# Install Playwright browsers
uv run playwright install chromium
```

## Data Models (Pydantic)

### Core Models

```python
# src/resume/models.py

class ContactInfo(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None  # Personal blog/website
    location: Optional[str] = None

class Header(BaseModel):
    name: str
    title: str
    contact: ContactInfo

class Summary(BaseModel):
    content: str

class Experience(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    current: bool = False
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)

class Skill(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None

class Skills(BaseModel):
    skills: list[Skill] = Field(default_factory=list)

    def get_by_category(self, category: str) -> list[Skill]:
        return [s for s in self.skills if s.category == category]

class Footer(BaseModel):
    text: str  # Footer text with emojis
    link: Optional[HttpUrl] = None
    link_text: Optional[str] = None

class Resume(BaseModel):
    header: Header
    summary: Summary
    experience: ProfessionalExperience
    skills: Skills
    footer: Optional[Footer] = None
```

## Footer Branding

Every resume includes a footer showcasing the project:

```yaml
# data/common/footer.yml
text: "Built with Resume as Code 🚀 | Open source on GitHub 💻"
link: "https://github.com/silverbeer/resume-as-code"
link_text: "View on GitHub"
```

The footer appears at the bottom of both HTML and PDF outputs with:
- Centered, small gray text (8pt)
- Top border separation
- Clickable GitHub link

## Development Workflow

### Running Commands

```bash
# All commands use uv run prefix
uv run resume list-profiles
uv run resume build sdet --format both
uv run resume analyze qe-leadership
```

### Adding a New Profile

1. Create profile directory: `data/profiles/new-profile/`
2. Add required files:
   - `summary.yml` (required)
   - `job.txt` (for AI analysis)
3. Optionally add overrides:
   - `header.yml` (custom title)
   - `skills.yml` (role-specific skills)
   - `experience.yml` (tailored achievements)

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src/resume
```

### Code Quality

```bash
# Lint
ruff check src/

# Format
ruff format src/

# Type check
mypy src/
```

## Key Learnings & Design Decisions

### 1. Profile-Specific Overrides
**Decision**: Check profile-specific files first, fallback to common
**Why**: Allows customization without duplication, maintains DRY for shared data

### 2. Playwright for PDF
**Decision**: Use Playwright instead of WeasyPrint
**Why**: No native dependencies, consistent cross-platform, better CSS support

### 3. PydanticAI for Job Analysis
**Decision**: Use PydanticAI instead of raw OpenAI API
**Why**: Type-safe responses, structured output, better validation

### 4. Footer Branding
**Decision**: Always include project attribution in footer
**Why**: Showcase the innovative approach, provide GitHub link for recruiters

### 5. uv for Package Management
**Decision**: Use uv instead of pip/poetry
**Why**: Faster, simpler, better dependency resolution, modern Python tooling

## Future Enhancements (Not Yet Implemented)

- [ ] Add support for more AI providers (Anthropic Claude)
- [ ] Resume version comparison and diff
- [ ] Cover letter generation from job description
- [ ] More output formats (Markdown, JSON)
- [ ] Web server with hot reload for development
- [ ] GitHub Pages deployment

## Troubleshooting

### Common Issues

**PDF Generation Fails**:
```bash
# Install Playwright browser
uv run playwright install chromium
```

**OpenAI API Errors**:
```bash
# Set API key (optional - only needed for `analyze` command)
export OPENAI_API_KEY='your-api-key'
```

**Import Errors**:
```bash
# Sync dependencies
uv sync
```

## Learning Project Context

This Resume as Code (RaC) system was created to:

### Master Modern Python Development
- Explore uv package manager
- Practice Typer + Rich for beautiful CLIs
- Use Pydantic for data validation
- Implement profile-based configuration patterns

### Explore AI Integration
- Learn PydanticAI framework
- Practice prompt engineering for job analysis
- Implement structured AI outputs
- Handle AI errors gracefully

### Demonstrate DevOps Skills
- GitOps workflow (version-controlled resume data)
- Profile-based configuration (like Kubernetes profiles)
- Automated builds (HTML + PDF generation)
- Modern tooling (uv, Playwright, Typer, Rich)

The goal is building practical AI-powered DevOps tools while creating a genuinely useful resume management system.

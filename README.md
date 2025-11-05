# Resume as Code

AI-powered resume builder that analyzes job descriptions and creates tailored ATS-friendly resumes.

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-blue)](https://github.com/astral-sh/ruff)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue)](https://github.com/python/mypy)
[![Tests: 77 passing](https://img.shields.io/badge/tests-77%20passing-brightgreen)](https://github.com/silverbeer/resume-as-code)
[![Coverage: 50%](https://img.shields.io/badge/coverage-50.29%25-yellow)](https://github.com/silverbeer/resume-as-code)

## Code Quality

| Metric | Value |
|--------|-------|
| **Test Coverage** | 50.29% (77 tests passing) |
| **Source Lines of Code** | ~1,063 lines |
| **Test Lines of Code** | ~2,563 lines |
| **Test to Code Ratio** | 2.4:1 |
| **Linting** | Ruff (zero warnings) |
| **Type Checking** | mypy (strict mode) |
| **Formatting** | black + isort |
| **Python Versions** | 3.12, 3.13 |

### Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| `builder.py` | 100% | ✅ |
| `loader.py` | 100% | ✅ |
| `pdf.py` | 100% | ✅ |
| `models.py` | 98.36% | ✅ |
| `utils.py` | 71.11% | ⚠️ |

## Overview

Resume as Code is a modern CLI tool that helps you create professional, ATS-friendly resumes tailored to specific job descriptions. It uses AI (via PydanticAI and OpenAI) to analyze job postings, identify skill gaps, and generate optimized resumes in multiple formats.

### Key Features

- **AI-Powered Job Analysis**: Automatically extract required skills and responsibilities from job descriptions
- **Skill Gap Detection**: Compare your resume against job requirements to identify missing skills
- **Multiple Resume Profiles**: Maintain different resume variations for different job types (SRE, QE, SDET, etc.)
- **ATS-Friendly Output**: Generate clean HTML and PDF resumes optimized for Applicant Tracking Systems
- **YAML-Based Data**: Version-controlled, human-readable resume data
- **Beautiful CLI**: Rich terminal interface with progress indicators and colored output

## Installation

### Prerequisites

- Python 3.12 or 3.13
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key

For PDF generation:
```bash
# Install Playwright browsers (required for PDF generation)
uv run playwright install chromium
```

**Note**: PDF generation now uses Playwright (no native dependencies required!)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-as-code.git
cd resume-as-code
```

2. Install dependencies:
```bash
uv sync
```

3. Install Playwright browsers:
```bash
uv run playwright install chromium
```

4. Set your OpenAI API key (optional - only needed for AI features):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Quick Start

### 1. List Available Profiles

```bash
uv run resume list-profiles
```

### 2. Analyze a Job Description

```bash
uv run resume analyze sre-leadership
```

This will:
- Load the job description from `data/profiles/sre-leadership/job.txt`
- Use AI to extract required and preferred skills
- Compare against your resume skills
- Show skill match percentage and recommendations

### 3. Build Your Resume

```bash
# Generate HTML resume
uv run resume build sre-leadership --format html

# Generate PDF resume
uv run resume build sre-leadership --format pdf

# Generate both
uv run resume build sre-leadership --format both
```

## Project Structure

```
resume-as-code/
├── data/
│   ├── common/                    # Shared resume data (fallbacks)
│   │   ├── header.yml            # Default contact info, name
│   │   ├── footer.yml            # Footer with project branding
│   │   ├── experience.yml        # Default work history
│   │   └── skills.yml            # Default skills
│   └── profiles/                 # Profile-specific data
│       ├── sre-leadership/
│       │   ├── header.yml        # Profile-specific title
│       │   ├── summary.yml       # Tailored summary
│       │   ├── experience.yml    # SRE-focused experience bullets
│       │   ├── skills.yml        # SRE-focused skills
│       │   └── job.txt           # Target job description
│       ├── qe-leadership/
│       │   ├── header.yml        # QE leadership title
│       │   ├── summary.yml       # QE-focused summary
│       │   ├── experience.yml    # QE-focused experience
│       │   ├── skills.yml        # QE-focused skills
│       │   └── job.txt
│       └── sdet/
│           ├── header.yml        # SDET title
│           ├── summary.yml       # SDET summary
│           ├── experience.yml    # SDET-focused experience
│           ├── skills.yml        # SDET skills
│           └── job.txt
├── templates/
│   └── resume.html.j2            # Jinja2 HTML template
├── output/                       # Generated resumes
└── src/resume/
    ├── cli.py                    # Typer CLI
    ├── models.py                 # Pydantic data models
    ├── loader.py                 # YAML data loader with profile overrides
    ├── builder.py                # HTML builder
    ├── pdf.py                    # Playwright PDF generator
    └── ai/
        └── agents.py             # PydanticAI agents
```

## CLI Commands

### `resume list-profiles`
List all available resume profiles.

### `resume analyze <profile>`
Analyze job description and compare with your resume skills.

**Example:**
```bash
uv run resume analyze sre-leadership
```

**Output:**
- Job role and level analysis
- Skills match percentage
- Missing required skills
- Missing preferred skills
- Recommendations

### `resume build <profile>`
Build resume in specified format(s).

**Options:**
- `--format, -f`: Output format (`html`, `pdf`, or `both`) [default: `html`]
- `--output, -o`: Custom output path

**Examples:**
```bash
# HTML only
uv run resume build sre-leadership --format html

# PDF only
uv run resume build sre-leadership --format pdf

# Both formats
uv run resume build sre-leadership --format both

# Custom output path
uv run resume build sre-leadership --format html --output ./my-resume.html
```

## Data Format

### Header
**Common (data/common/header.yml)** - Default contact info:
```yaml
name: "Your Name"
title: "Senior Engineering Leader"  # Default title
contact:
  email: "you@example.com"
  phone: "+1 (555) 123-4567"
  linkedin: "https://linkedin.com/in/yourname"
  github: "https://github.com/yourname"
  website: "https://yourblog.dev"  # Optional
  location: "San Francisco, CA"
```

**Profile-Specific (data/profiles/<profile>/header.yml)** - Override title per profile:
```yaml
# Only specify fields you want to override
title: "Director of Quality Engineering"
```

### Experience
**Profile-Specific (data/profiles/<profile>/experience.yml)** - Tailored achievement bullets:
```yaml
experiences:
  - company: "Company Name"
    title: "Job Title"
    location: "City, State"
    start_date: "2022-01-01"
    current: true
    achievements:
      - "Achievement tailored for this role (e.g., QE-focused or SRE-focused)"
      - "Quantifiable impact specific to the profile"
    technologies:
      - "Python"
      - "Kubernetes"
```

**Note**: Create profile-specific experience.yml to customize bullets per role type.

### Skills
**Profile-Specific (data/profiles/<profile>/skills.yml)** - Role-focused skills:
```yaml
skills:
  - name: "Playwright"
    category: "Testing"
    proficiency: "Expert"
  - name: "Kubernetes"
    category: "Infrastructure"
    proficiency: "Advanced"
```

**Note**: Each profile should have its own skills.yml with relevant skills for that role.

### Summary
**Profile-Specific (data/profiles/<profile>/summary.yml)** - Tailored summary:
```yaml
content: >
  Your tailored professional summary for this specific job type.
  This will be different for each profile (SRE vs QE vs SDET).
```

### Footer
**Common (data/common/footer.yml)** - Project branding:
```yaml
text: "Built with Resume as Code 🚀 | Open source on GitHub 💻"
link: "https://github.com/yourusername/resume-as-code"
link_text: "View on GitHub"
```

## Profile Customization

Resume as Code supports **profile-specific overrides** - each profile can have customized:

1. **Title** - Different job titles for different roles (e.g., "Director of QE" vs "Senior SDET")
2. **Skills** - Focused skill sets relevant to each role type
3. **Experience** - Tailored achievement bullets highlighting relevant accomplishments

### How It Works

The loader checks for profile-specific files first, then falls back to common defaults:

```
data/profiles/sdet/header.yml  →  Custom title for SDET profile
data/profiles/sdet/skills.yml  →  SDET-focused skills
data/profiles/sdet/experience.yml  →  QE/Testing-focused achievements

If not found, uses:
data/common/header.yml  →  Default contact info
data/common/skills.yml  →  Default skills
data/common/experience.yml  →  Default experience
```

This allows you to maintain one set of data while customizing specific aspects for each role type!

## AI Features

Resume as Code uses **PydanticAI** with OpenAI's GPT-4 to:

1. **Job Description Analysis**
   - Extract required technical skills
   - Identify preferred/nice-to-have skills
   - Determine role level and type
   - List key responsibilities

2. **Skill Gap Analysis**
   - Compare your skills against job requirements
   - Calculate skill match percentage
   - Identify missing required skills
   - Provide actionable recommendations

## Development

### Run Tests
```bash
pytest
```

### Lint Code
```bash
ruff check src/
```

### Format Code
```bash
ruff format src/
```

### Type Check
```bash
mypy src/
```

## Troubleshooting

### PDF Generation Issues

**Playwright browser not found:**
```bash
uv run playwright install chromium
```

PDF generation now uses Playwright's headless Chromium browser - no native system dependencies required! This works consistently across macOS, Linux, and Windows.

### OpenAI API Errors

Make sure your `OPENAI_API_KEY` environment variable is set:
```bash
export OPENAI_API_KEY='your-api-key'
```

You can also add it to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
echo 'export OPENAI_API_KEY="your-api-key"' >> ~/.zshrc
```

## Roadmap

- [ ] Add support for more AI providers (Anthropic Claude, Google Gemini)
- [ ] Interactive resume builder wizard
- [ ] Resume version comparison and diff
- [ ] Export to LinkedIn format
- [ ] Cover letter generation from job description
- [ ] Skills learning path recommendations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Created as a learning project to explore AI-powered DevOps tools and modern Python development practices.

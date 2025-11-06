# Resume as Code

**Because your resume shouldn't be the same document you send to Google and your local coffee shop.**

AI-powered resume builder that analyzes job descriptions and creates tailored ATS-friendly resumes. Version control your career, GitOps your job search, and let AI handle the keyword optimization so you can focus on actually having the skills listed.

**The Mission**: Beat the robots (ATS systems) to get your resume in front of actual humans who can appreciate context, nuance, and the fact that you built a deployment pipeline for your job search.

> **⚠️ Note**: This repository contains **example data** (Jane Engineer). Replace the data in `data/` with your own resume information. See [Setup](#setup) for details.

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

Think of it as Infrastructure as Code, but for your career. Because if we can manage Kubernetes clusters with YAML, why not manage resumes the same way? Plus, you get to `git commit -m "Add 5 years of Rust experience"` and pretend you're just updating documentation.

### Key Features

- **AI-Powered Job Analysis**: Automatically extract required skills and responsibilities from job descriptions *(the AI reads the 10-page JD so you don't have to)*
- **AI-Assisted Optimization**: Use structured prompts to optimize your resume for specific roles with 90%+ ATS match rates *(see [prompts/](prompts/))*
- **Skill Gap Detection**: Compare your resume against job requirements to identify missing skills *(spoiler: you're missing "Hashicorp Cloud Platform")*
- **Multiple Resume Profiles**: Maintain different resume variations for different job types (uptime-obsessive, bug-whisperer, test-ninja, etc.) *(because "Kubernetes expert" hits different depending on who's asking)*
- **ATS-Friendly Output**: Generate clean HTML and PDF resumes optimized for Applicant Tracking Systems *(robots judging your career choices since 2004)*
- **YAML-Based Data**: Version-controlled, human-readable resume data *(finally, a legitimate use for git blame)*
- **Beautiful CLI**: Rich terminal interface with progress indicators and colored output *(because if you're going to update your resume at 2am, it should at least look cool)*
- **Complete Workflow Guide**: Step-by-step documentation from job posting to submission *(see [docs/WORKFLOW.md](docs/WORKFLOW.md))*

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

4. **Replace example data with your own resume:**
```bash
# Update your personal information
edit data/common/header.yml

# Customize profile-specific data
edit data/profiles/uptime-obsessive/summary.yml
edit data/profiles/uptime-obsessive/experience.yml
edit data/profiles/uptime-obsessive/skills.yml
```

> **Important**: The repository currently contains example data for "Jane Engineer". Replace all personal information in `data/common/` and `data/profiles/` with your own resume content.

5. Set your OpenAI API key (optional - only needed for AI features):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Quick Start

### 1. List Available Profiles

```bash
uv run resume list-profiles
```

### 2. Add Your Target Job Description

**Important**: Each profile needs a `job.txt` file with your target job description.

```bash
# Navigate to your profile directory
cd data/profiles/uptime-obsessive

# Copy the example template
cp job.txt.example job.txt

# Edit job.txt and paste the full job description
# (The file is gitignored - your job search stays private)
```

**Note**: The `job.txt` file is intentionally gitignored to keep your job search private. Always create it from the `.example` template.

### 3. Analyze a Job Description

```bash
uv run resume analyze uptime-obsessive
```

This will:
- Load the job description from `data/profiles/uptime-obsessive/job.txt`
- Use AI to extract required and preferred skills
- Compare against your resume skills
- Show skill match percentage and recommendations

### 4. Build Your Resume

```bash
# Generate HTML resume
uv run resume build uptime-obsessive --format html

# Generate PDF resume
uv run resume build uptime-obsessive --format pdf

# Generate both
uv run resume build uptime-obsessive --format both
```

## Complete Workflow Guide

For a comprehensive step-by-step guide to customizing your resume for specific job applications, see:

📖 **[WORKFLOW.md](docs/WORKFLOW.md)** - Complete 8-step process from job posting to submission

This includes:
- Prerequisites and setup
- AI-assisted profile optimization
- Best practices for ATS keyword optimization
- Troubleshooting guide
- Advanced workflows
- Complete example walkthrough

### AI-Assisted Optimization

Want to optimize your profile for a specific job posting? Use the AI optimization prompt:

📝 **[Profile Optimization Prompt](prompts/optimize-profile-for-job.md)** - Reusable prompt for Claude Code or other AI assistants

This structured prompt helps you:
- Analyze job descriptions for ATS keywords
- Update header, summary, experience, and skills files
- Maximize keyword density while maintaining authenticity
- Achieve 90%+ ATS match rates

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
│       ├── uptime-obsessive/     # SRE/Platform leadership roles
│       │   ├── header.yml        # Profile-specific title
│       │   ├── summary.yml       # Tailored summary
│       │   ├── experience.yml    # SRE-focused experience bullets
│       │   ├── skills.yml        # SRE-focused skills
│       │   ├── job.txt.example   # Job description template
│       │   └── job.txt           # Your target job description (gitignored)
│       ├── bug-whisperer/        # QE/Quality leadership roles
│       │   ├── header.yml        # QE leadership title
│       │   ├── summary.yml       # QE-focused summary
│       │   ├── experience.yml    # QE-focused experience
│       │   ├── skills.yml        # QE-focused skills
│       │   ├── job.txt.example   # Job description template
│       │   └── job.txt           # Your target job description (gitignored)
│       └── test-ninja/           # SDET/Automation roles
│           ├── header.yml        # SDET title
│           ├── summary.yml       # SDET summary
│           ├── experience.yml    # SDET-focused experience
│           ├── skills.yml        # SDET skills
│           ├── job.txt.example   # Job description template
│           └── job.txt           # Your target job description (gitignored)
├── docs/
│   └── WORKFLOW.md               # Complete workflow guide
├── prompts/
│   └── optimize-profile-for-job.md  # AI optimization prompt
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
uv run resume analyze uptime-obsessive
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
uv run resume build uptime-obsessive --format html

# PDF only
uv run resume build uptime-obsessive --format pdf

# Both formats
uv run resume build uptime-obsessive --format both

# Custom output path
uv run resume build uptime-obsessive --format html --output ./my-resume.html
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
data/profiles/test-ninja/header.yml  →  Custom title for SDET profile
data/profiles/test-ninja/skills.yml  →  SDET-focused skills
data/profiles/test-ninja/experience.yml  →  QE/Testing-focused achievements

If not found, uses:
data/common/header.yml  →  Default contact info
data/common/skills.yml  →  Default skills
data/common/experience.yml  →  Default experience
```

This allows you to maintain one set of data while customizing specific aspects for each role type!

## Profile Names Explained

The profile folder names are intentionally playful (because job searching should have *some* fun):

- **uptime-obsessive** - For SRE/Platform Engineering leadership roles. You know who you are. That 99.99% isn't going to maintain itself.
- **bug-whisperer** - For QE/Quality Engineering leadership positions. You speak to bugs in ways others can't understand.
- **test-ninja** - For SDET/Test Automation roles. Stealthy, precise, and your tests always strike true.

Pick whatever makes you smile when running `uv run resume build [profile]` at 11pm on a Sunday. Or create your own with names like `kubernetes-therapist`, `pipeline-plumber`, or `chaos-coordinator`. This is your repo, have fun with it!

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

**Origin Story**: Built by someone who got tired of maintaining 47 different Word documents named `resume_final_v2_ACTUAL_final_use_this_one.docx`. Now maintains one Git repo instead. Progress? You decide.

**Real Talk**: This is what happens when an SRE applies Infrastructure as Code principles to job hunting. Is it over-engineered? Absolutely. Does it work? Also yes. Would I recommend it? Only if you enjoy explaining to recruiters why your resume is "deployed via CI/CD pipeline."

**Full Transparency**: This was heavily vibe-coded using [Claude Code](https://claude.ai/code) in a gloriously chaotic pair-programming session. The human provided the domain knowledge and job descriptions, Claude handled the Python architecture and AI integration, and together we built a tool to beat the robots... using different robots. The irony is not lost on us.

**The Real Goal**: Getting past ATS keyword filters to hopefully land this resume in front of an actual human decision maker who appreciates that someone built a CI/CD pipeline for their career. If you're that human and you're reading this—hi! 👋 Let's talk about how I can apply this same over-engineering energy to solving your infrastructure problems.

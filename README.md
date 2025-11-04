# Resume as Code

AI-powered resume builder that analyzes job descriptions and creates tailored ATS-friendly resumes.

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

For PDF generation (optional):
```bash
# macOS
brew install pango cairo

# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0

# Fedora
sudo dnf install pango cairo
```

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

3. Install the package in editable mode:
```bash
uv pip install -e .
```

4. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Quick Start

### 1. List Available Profiles

```bash
resume list-profiles
```

### 2. Analyze a Job Description

```bash
resume analyze sre-leadership
```

This will:
- Load the job description from `data/profiles/sre-leadership/job.txt`
- Use AI to extract required and preferred skills
- Compare against your resume skills
- Show skill match percentage and recommendations

### 3. Build Your Resume

```bash
# Generate HTML resume
resume build sre-leadership --format html

# Generate PDF resume (requires system libraries)
resume build sre-leadership --format pdf

# Generate both
resume build sre-leadership --format both
```

### 4. Add Missing Skills

```bash
resume add-skill sre-leadership "Terraform" --category "SRE" --proficiency "Expert"
```

## Project Structure

```
resume-as-code/
├── data/
│   ├── common/                    # Shared resume data
│   │   ├── header.yml            # Contact info, name
│   │   ├── experience.yml        # Work history
│   │   └── skills.yml            # All your skills
│   └── profiles/                 # Job-specific profiles
│       ├── sre-leadership/
│       │   ├── summary.yml       # Tailored summary
│       │   └── job.txt           # Target job description
│       ├── qe-leadership/
│       └── sdet/
├── templates/
│   └── resume.html.j2            # Jinja2 HTML template
├── output/                       # Generated resumes
└── src/resume/
    ├── cli.py                    # Typer CLI
    ├── models.py                 # Pydantic data models
    ├── loader.py                 # YAML data loader
    ├── builder.py                # HTML builder
    ├── pdf.py                    # PDF generator
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
resume analyze sre-leadership
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
resume build sre-leadership --format html

# PDF only
resume build sre-leadership --format pdf

# Both formats
resume build sre-leadership --format both

# Custom output path
resume build sre-leadership --format html --output ./my-resume.html
```

### `resume add-skill <profile> <skill-name>`
Add a new skill to your resume.

**Options:**
- `--category, -c`: Skill category [default: "General"]
- `--proficiency, -p`: Proficiency level [default: "Intermediate"]

**Example:**
```bash
resume add-skill sre-leadership "Istio" --category "SRE" --proficiency "Advanced"
```

### `resume version`
Show version information.

## Data Format

### Header (data/common/header.yml)
```yaml
name: "Your Name"
title: "Senior Engineering Leader"
contact:
  email: "you@example.com"
  phone: "+1 (555) 123-4567"
  linkedin: "https://linkedin.com/in/yourname"
  github: "https://github.com/yourname"
  location: "San Francisco, CA"
```

### Experience (data/common/experience.yml)
```yaml
experiences:
  - company: "Company Name"
    title: "Job Title"
    location: "City, State"
    start_date: "2022-01-01"
    current: true
    achievements:
      - "Achievement with quantifiable impact"
      - "Another achievement"
    technologies:
      - "Python"
      - "Kubernetes"
```

### Skills (data/common/skills.yml)
```yaml
skills:
  - name: "Kubernetes"
    category: "SRE"
    proficiency: "Expert"
  - name: "Python"
    category: "Programming"
    proficiency: "Expert"
```

### Summary (data/profiles/<profile>/summary.yml)
```yaml
content: >
  Your tailored professional summary for this specific job type.
  This will be different for each profile (SRE vs QE vs SDET).
```

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

If you see errors about missing libraries (`libgobject-2.0-0`, `libpango`, etc.), install the system dependencies:

**macOS:**
```bash
brew install pango cairo
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0

# Fedora
sudo dnf install pango cairo
```

HTML generation doesn't require these libraries and will always work.

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

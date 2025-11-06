# Resume-as-Code Workflow Guide

This guide walks through the complete process of creating a customized resume for a specific job opportunity using the Resume-as-Code (RaC) CLI.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Workflow Steps](#workflow-steps)
- [Profile Structure](#profile-structure)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Resume-as-Code workflow allows you to maintain multiple resume profiles tailored to different job types while keeping your core experience data centralized. When you find a job opportunity, you can quickly generate an optimized, ATS-friendly resume.

**Key Benefits:**
- Version-controlled resume data (Git)
- Profile-specific customization without duplication
- AI-assisted optimization for ATS matching
- Multi-format output (HTML, PDF, or both)
- Repeatable, auditable process

---

## Prerequisites

### Required Setup
1. **Python environment with uv**:
   ```bash
   # Ensure dependencies are synced
   uv sync
   ```

2. **Playwright browsers** (for PDF generation):
   ```bash
   uv run playwright install chromium
   ```

3. **OpenAI API Key** (optional, only for AI analysis):
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

### Directory Structure
```
resume-as-code/
├── data/
│   ├── common/              # Shared resume data
│   │   ├── header.yml       # Default contact info (Jane Engineer)
│   │   ├── footer.yml       # Project footer
│   │   ├── experience.yml   # Full work history
│   │   └── skills.yml       # Comprehensive skills
│   └── profiles/            # Job-specific profiles
│       └── [profile-name]/
│           ├── header.yml   # Title override
│           ├── summary.yml  # Tailored summary
│           ├── experience.yml # Customized bullets
│           ├── skills.yml   # Role-focused skills
│           ├── job.txt      # Target job description
│           └── fit.txt      # Optional fit analysis
```

---

## Workflow Steps

### Step 1: Identify or Create Profile

**Option A: Use Existing Profile**
```bash
# List available profiles
uv run resume list-profiles
```

Available profiles might include:
- `test-ninja` - Software testing and QA automation roles
- `uptime-obsessive` - SRE and reliability engineering roles
- `bug-whisperer` - Debugging and troubleshooting specialist roles

**Option B: Create New Profile**
```bash
# Create profile directory
mkdir -p data/profiles/[profile-name]

# Create required files
touch data/profiles/[profile-name]/summary.yml
touch data/profiles/[profile-name]/job.txt
```

### Step 2: Add Job Description

Copy the target job posting into `job.txt`:

```bash
# Edit job description file
vim data/profiles/[profile-name]/job.txt

# Or copy from clipboard (macOS)
pbpaste > data/profiles/[profile-name]/job.txt
```

**What to include:**
- Complete job description (responsibilities, requirements)
- Required skills and qualifications
- Preferred/nice-to-have skills
- Company information (optional but helpful)

### Step 3: Generate Fit Analysis (Optional but Recommended)

**Option A: Using Claude Code AI**

Use the optimization prompt to get AI-assisted analysis:
```
I have a new job opportunity and need to optimize my Resume-as-Code profile.

**Profile**: [profile-name]
**Files provided**:
- data/profiles/[profile-name]/job.txt

Please analyze the job description and provide:
1. ATS keyword gap analysis
2. Alignment assessment with my experience
3. Specific recommendations for optimization
```

Save the analysis to `fit.txt`:
```bash
# Save AI analysis output
vim data/profiles/[profile-name]/fit.txt
```

**Option B: Using Built-in Analysis**
```bash
# Run AI-powered job analysis (requires OpenAI API key)
uv run resume analyze [profile-name]
```

This will output:
- Required and preferred skills extraction
- Role level and type identification
- Skill gap analysis
- Match percentage estimate

### Step 4: Optimize Profile Files

Use the [Profile Optimization Prompt](../prompts/optimize-profile-for-job.md) with Claude Code to update all profile files:

```
I have a new job opportunity and need to optimize my Resume-as-Code profile.

**Profile**: [profile-name]
**Files provided**:
- data/profiles/[profile-name]/job.txt (job description)
- data/profiles/[profile-name]/fit.txt (fit analysis showing X% ATS match)

Please update header.yml, summary.yml, experience.yml, and skills.yml to maximize alignment with this role while maintaining authenticity.
```

**Files to update:**

1. **header.yml** - Update job title to match role
2. **summary.yml** - Rewrite summary with job-specific keywords
3. **experience.yml** - Reframe achievements, add missing keywords
4. **skills.yml** - Restructure skills to prioritize job requirements

### Step 5: Generate Resume

**Build HTML version:**
```bash
uv run resume build [profile-name]
# Output: output/resume_[profile-name].html
```

**Build PDF version:**
```bash
uv run resume build [profile-name] --format pdf
# Output: output/resume_[profile-name].pdf
```

**Build both formats:**
```bash
uv run resume build [profile-name] --format both
# Output: Both HTML and PDF in output/
```

**Custom output path:**
```bash
uv run resume build [profile-name] --output ./custom-resume.html
```

### Step 6: Review and Iterate

1. **Open generated resume** in browser/PDF viewer
2. **Check for:**
   - Proper formatting and layout
   - All required keywords present
   - Natural language flow (not keyword-stuffed)
   - Accurate representation of experience
   - Contact information correct
   - Footer branding present

3. **Iterate if needed:**
   - Edit profile YAML files
   - Rebuild resume
   - Review again

### Step 7: Version Control

**Commit your changes:**
```bash
# Check status
git status

# Review changes
git diff data/profiles/[profile-name]/

# Stage profile files
git add data/profiles/[profile-name]/

# Commit with descriptive message
git commit -m "Optimize [profile-name] profile for [Company] [Role]"
```

**Best practice commit message format:**
```
Optimize [profile-name] for [Company] [Role Title]

- Updated header.yml with new title
- Rewrote summary.yml for [focus area]
- Added [X] missing keywords to experience.yml
- Restructured skills.yml to prioritize [key skills]
- Estimated ATS match: X%
```

### Step 8: Submit Application

1. **Upload PDF** to application system (most compatible)
2. **Keep HTML** for web-based applications
3. **Save job posting** reference for interview prep
4. **Track application** in your system

---

## Profile Structure

### Required Files

#### `summary.yml` (required)
```yaml
content: >
  Your tailored professional summary (3-5 sentences).
  Include key achievements, years of experience, and
  role-specific keywords from the job description.
```

#### `job.txt` (recommended)
```
Complete job description text.
Paste the entire job posting including:
- Responsibilities
- Requirements
- Qualifications
- Company info
```

### Optional Override Files

#### `header.yml` (optional)
```yaml
# Only override the title, contact info comes from common/header.yml
title: "Your Job-Specific Title | Specialty Area"
```

#### `experience.yml` (optional)
```yaml
experiences:
  - company: "Acme Corporation"
    title: "Senior Software Engineer"
    location: "San Francisco, CA"
    start_date: "2020-01-15"
    end_date: "2023-06-30"
    achievements:
      - "Achievement bullet with job-specific keywords"
      - "Quantified result demonstrating relevant skill"
    technologies:
      - "Technology 1"
      - "Technology 2"
```

#### `skills.yml` (optional)
```yaml
skills:
  - name: "Skill Name"
    category: "Category"
    proficiency: "Expert"  # or "Advanced"
```

#### `fit.txt` (optional)
```
External fit analysis or notes:
- ATS keyword gaps
- Estimated match percentage
- Recommendations
- Keywords to add
```

### Fallback Behavior

If a profile file doesn't exist, the loader falls back to `data/common/` files:
- No `header.yml` → uses `common/header.yml`
- No `experience.yml` → uses `common/experience.yml`
- No `skills.yml` → uses `common/skills.yml`
- `footer.yml` → always uses `common/footer.yml`

---

## Best Practices

### 1. Start with Existing Profile
- Clone similar profile instead of starting from scratch
- Maintain consistency across profiles
- Leverage proven achievement bullets

### 2. Keep job.txt Updated
- Save complete job description (pages get deleted)
- Include posting date for reference
- Note any special application instructions

### 3. Use fit.txt for Strategy
- Document ATS keyword gaps
- Track optimization decisions
- Record estimated match percentage
- Note interview talking points

### 4. Maintain Authenticity
- Never fabricate experience or skills
- Only add keywords for actual work performed
- Adjust proficiency levels honestly
- Reframe truthfully, don't invent

### 5. Test Both Formats
- HTML for web submissions and preview
- PDF for upload systems (most reliable)
- Verify formatting in both outputs

### 6. Version Control Everything
- Commit profile changes with context
- Tag releases for major applications
- Keep job.txt in version control
- Document optimization rationale

### 7. Iterate Quickly
- Generate → Review → Edit → Regenerate
- Use AI assistance for keyword optimization
- Test ATS compatibility when possible
- Get human feedback on readability

---

## Troubleshooting

### PDF Generation Fails

**Error**: `Playwright not installed`
```bash
uv run playwright install chromium
```

**Error**: `Page.pdf: Target closed`
- Check that HTML is valid
- Try building HTML first to verify content
- Increase timeout in pdf.py if needed

### Missing Profile Files

**Error**: `Profile '[name]' not found`
```bash
# Verify profile exists
ls data/profiles/

# Create profile directory
mkdir -p data/profiles/[profile-name]
touch data/profiles/[profile-name]/summary.yml
```

### OpenAI API Errors

**Error**: `OpenAI API key not found`
```bash
export OPENAI_API_KEY='your-api-key'
```

**Note**: API key only needed for `analyze` command, not for building resumes.

### YAML Syntax Errors

**Error**: `YAML parsing failed`
- Check indentation (use spaces, not tabs)
- Verify quote matching
- Validate multiline strings use `>`
- Test with: `python -c "import yaml; yaml.safe_load(open('file.yml'))"`

### Resume Looks Wrong

**Check these common issues:**
1. **Formatting**: Review `templates/resume.html.j2`
2. **Data**: Verify YAML files have correct structure
3. **CSS**: Check print styles for PDF output
4. **Fonts**: Ensure web fonts load properly
5. **Margins**: Adjust in `pdf.py` if needed

### Git Conflicts

If multiple profiles edited simultaneously:
```bash
# Check conflict status
git status

# View conflicts
git diff

# Resolve manually, then:
git add .
git commit -m "Resolve profile merge conflicts"
```

---

## Advanced Workflows

### Creating a New Profile from Scratch

```bash
# 1. Create profile directory
mkdir -p data/profiles/cloud-ninja

# 2. Copy template files from similar profile
cp data/profiles/test-ninja/summary.yml data/profiles/cloud-ninja/
cp data/profiles/test-ninja/header.yml data/profiles/cloud-ninja/

# 3. Add job description
vim data/profiles/cloud-ninja/job.txt

# 4. Customize files
vim data/profiles/cloud-ninja/summary.yml
vim data/profiles/cloud-ninja/header.yml

# 5. Generate initial resume
uv run resume build cloud-ninja

# 6. Iterate and optimize
# ... (use optimization prompt)

# 7. Commit when ready
git add data/profiles/cloud-ninja/
git commit -m "Add cloud-ninja profile for Cloud Engineering roles"
```

### Batch Building Multiple Profiles

```bash
#!/bin/bash
# build-all-profiles.sh

PROFILES=("test-ninja" "uptime-obsessive" "bug-whisperer")

for profile in "${PROFILES[@]}"; do
  echo "Building $profile..."
  uv run resume build "$profile" --format both
done

echo "All profiles built successfully!"
```

### Pre-commit Hook for Validation

```bash
# .git/hooks/pre-commit

#!/bin/bash
# Validate YAML files before commit

echo "Validating YAML files..."

for file in $(git diff --cached --name-only | grep '\.yml$'); do
  python -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "ERROR: Invalid YAML in $file"
    exit 1
  fi
done

echo "YAML validation passed!"
```

---

## Example: Complete Workflow for CI/CD Engineer Role

Let's walk through optimizing the `test-ninja` profile for a fictional "Lead CI/CD Automation Engineer" position at TechCorp.

### Step 1: List profiles
```bash
$ uv run resume list-profiles

Available Profiles
┏━━━━━━━━━━━━━━━━━━━┓
┃ Profile Name      ┃
┡━━━━━━━━━━━━━━━━━━━┩
│ test-ninja        │
│ uptime-obsessive  │
│ bug-whisperer     │
└───────────────────┘
```

### Step 2: Add job description
```bash
# Copy job posting to job.txt
pbpaste > data/profiles/test-ninja/job.txt
```

### Step 3: Generate baseline
```bash
# Build current resume
uv run resume build test-ninja --format both

✓ Resume generated successfully!
  • output/test-ninja_resume.html
  • output/test-ninja_resume.pdf
```

### Step 4: Get AI optimization (via Claude Code)
```
I have a new job opportunity and need to optimize my Resume-as-Code profile.

**Profile**: test-ninja
**Files provided**:
- data/profiles/test-ninja/job.txt (TechCorp Lead CI/CD Automation Engineer)

Please analyze and provide fit assessment.
```

Save output to:
```bash
vim data/profiles/test-ninja/fit.txt
```

### Step 5: Optimize profile files
Use the [optimization prompt](../prompts/optimize-profile-for-job.md):

```
**Profile**: test-ninja
**Files**: job.txt, fit.txt provided

Please update header.yml, summary.yml, experience.yml, and skills.yml
to maximize alignment with this CI/CD automation role.
```

### Step 6: Rebuild optimized resume
```bash
uv run resume build test-ninja --format both

✓ Resume generated successfully!
  • output/test-ninja_resume.html
  • output/test-ninja_resume.pdf
```

### Step 7: Review changes
```bash
# Check what changed
git diff --stat data/profiles/test-ninja/

 data/profiles/test-ninja/experience.yml |  45 +++++----
 data/profiles/test-ninja/header.yml     |   2 +-
 data/profiles/test-ninja/skills.yml     | 130 +++++++++++++++--------
 data/profiles/test-ninja/summary.yml    |  15 +--
 4 files changed, 125 insertions(+), 67 deletions(-)
```

### Step 8: Commit changes
```bash
git add data/profiles/test-ninja/
git commit -m "Optimize test-ninja for TechCorp CI/CD role

- Updated header: Lead CI/CD Automation Engineer
- Rewrote summary: emphasize Jenkins, Terraform, Ansible
- Enhanced experience: added networking protocols, on-call/RCA
- Restructured skills: prioritize CI/CD, IaC, observability

Estimated ATS match: 90%+"
```

### Step 9: Submit
```bash
# Open PDF for final review
open output/test-ninja_resume.pdf

# Upload to application system
```

---

## Quick Reference

### Most Common Commands

```bash
# List profiles
uv run resume list-profiles

# Build HTML (fastest for iteration)
uv run resume build [profile]

# Build PDF (for submission)
uv run resume build [profile] --format pdf

# Analyze job fit (requires OpenAI key)
uv run resume analyze [profile]

# Check git status
git status

# Commit changes
git add data/profiles/[profile]/
git commit -m "Optimize [profile] for [Company]"
```

### File Locations

- **Profile data**: `data/profiles/[profile-name]/*.yml`
- **Job description**: `data/profiles/[profile-name]/job.txt`
- **Fit analysis**: `data/profiles/[profile-name]/fit.txt`
- **Generated output**: `output/resume_[profile-name].[html|pdf]`
- **Common defaults**: `data/common/*.yml`
- **Template**: `templates/resume.html.j2`

### Optimization Prompt Location

See [prompts/optimize-profile-for-job.md](../prompts/optimize-profile-for-job.md) for the complete AI optimization prompt.

---

## Getting Help

- **Project Documentation**: `README.md` and `CLAUDE.md`
- **CLI Help**: `uv run resume --help`
- **Command Help**: `uv run resume build --help`
- **Issues**: Check logs in console output
- **Community**: [GitHub Issues](https://github.com/yourusername/resume-as-code/issues)

---

**Last Updated**: 2025-01-06
**Version**: 1.0.0

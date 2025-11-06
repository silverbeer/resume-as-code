# Resume Profile Optimization Prompt

Use this prompt when you have a new job opportunity and need to optimize your Resume-as-Code profile to maximize ATS matching and human appeal.

## Profile Information
- **Profile name**: `[profile-name]` (e.g., `test-ninja`, `uptime-obsessive`, `bug-whisperer`)
- **Profile path**: `data/profiles/[profile-name]/`

## Input Files Provided

1. **Job Description**: `data/profiles/[profile-name]/job.txt`
   - Contains the complete job posting I'm targeting

2. **Fit Analysis** (optional but recommended): `data/profiles/[profile-name]/fit.txt`
   - External analysis of my fit for this role
   - Includes ATS keyword gaps, alignment assessment, and recommendations
   - Treat this as strategic guidance for optimization priorities

3. **Current Resume** (optional): Screenshot or PDF of current profile output
   - Shows current formatting and content presentation

## Required Actions

Please update ALL four profile files to maximize alignment with the job description:

### 1. **header.yml**
- Update `title` to mirror the job title and role focus
- Use exact keywords from job title when possible
- Signal seniority level (Lead, Senior, Staff, Director) appropriately
- Keep it concise: "Role Title | Specialty Area | Optional Third Element"

### 2. **summary.yml**
- Rewrite the `content` paragraph (3-5 sentences) to:
  - Lead with the most relevant experience for THIS role
  - Mirror job description language and requirements
  - Include 3-5 critical keywords from job requirements
  - Highlight years of experience if mentioned in JD
  - Emphasize leadership/individual contributor based on role level
  - Maintain authentic voice while maximizing keyword density

### 3. **experience.yml**
- **Reframe achievements** (not rewrite from scratch) to emphasize relevant experience:
  - Lead with bullets that directly address job responsibilities
  - Add critical missing keywords identified in fit.txt
  - Use job description language patterns (e.g., "architect and implement", "build and manage")
  - Maintain truthfulness—only add keywords for work actually performed
  - Reorder bullets to prioritize most relevant experience first

- **Update technologies lists** to include:
  - All tools/technologies explicitly mentioned in job requirements
  - Related technologies I used (even if not in original list)
  - Proper formatting for ATS (e.g., "ELK (Elasticsearch-Logstash-Kibana)")
  - Order by relevance to the job description

### 4. **skills.yml**
- **Complete restructure** organized by relevance to job:
  - Create categories that mirror job description sections
  - List most critical skills first (top 10 skills = highest ATS weight)
  - Include ALL required technologies/skills from job description
  - Include preferred/nice-to-have skills where applicable
  - Add proficiency levels appropriately (Expert/Advanced)
  - Remove or de-emphasize irrelevant skills for this role

## Optimization Principles

### ATS Keyword Strategy
1. **Exact matches**: Use exact tool names, acronyms, and phrases from JD
2. **Variations**: Include both "CI/CD" and "CI/CD Pipelines"
3. **Explicit terms**: Say "Git" not just "GitHub Actions"; "Bash" not just "shell scripting"
4. **Compound skills**: "Load Testing (Locust, JMeter)" captures multiple keywords
5. **Density without stuffing**: Natural integration in context, not lists

### Critical Keywords to Surface
Based on fit.txt analysis, prioritize adding/emphasizing:
- Missing required tools/technologies
- Methodologies explicitly mentioned (Agile/Scrum, RCA, on-call)
- Domain-specific terms (networking protocols, cloud platforms)
- Buzzwords from JD (observability, infrastructure-as-code, GitOps)

### Authenticity Requirements
- **Only add keywords for work actually performed**
- **Never fabricate experience or skills**
- **Adjust proficiency honestly** (Expert = daily use 3+ years, Advanced = regular use 1+ year)
- **Reframe truthfully**: Change emphasis and language, not facts

### Ordering Strategy
1. **Experience bullets**: Most relevant to job first, chronological second
2. **Skills**: Job requirements order, with required > preferred > bonus
3. **Technologies**: Tools mentioned in JD first, supporting tools second

## Output Format

For each file updated, please:
1. Show the complete updated file content
2. Provide a brief summary of changes made
3. Call out critical keyword additions for ATS matching
4. Estimate ATS improvement (if fit.txt provided baseline score)

## Success Criteria

After updates, the profile should:
- [ ] Mirror job title in header
- [ ] Include ALL required keywords from job description
- [ ] Surface critical skills in top 10 entries
- [ ] Reorder experience bullets by relevance
- [ ] Add missing technologies to both experience and skills
- [ ] Achieve 90%+ estimated ATS match (if fit.txt provided)
- [ ] Maintain authentic, truthful representation of experience
- [ ] Read naturally to human reviewers (not keyword-stuffed)

## Example Invocation

```
I have a new job opportunity and need to optimize my Resume-as-Code profile.

**Profile**: test-ninja
**Files provided**:
- data/profiles/test-ninja/job.txt (job description)
- data/profiles/test-ninja/fit.txt (fit analysis showing 82-87% ATS match)
- [Screenshot of current resume]

Please update header.yml, summary.yml, experience.yml, and skills.yml to maximize alignment with this role while maintaining authenticity.
```

---

## Why This Prompt Works

This prompt is effective because it:

1. **Provides complete context** - All necessary files and constraints upfront
2. **Specifies exact scope** - Four files to update, no guessing
3. **Includes strategic guidance** - fit.txt provides optimization priorities
4. **Emphasizes authenticity** - Reframe, don't fabricate
5. **Defines success metrics** - Measurable outcomes (90%+ ATS, all keywords)
6. **Respects project structure** - Follows Resume-as-Code conventions
7. **Balances ATS + human** - Keywords matter, but readability too
8. **Actionable principles** - Clear rules for keyword strategy and ordering
9. **Includes verification** - Checklist to validate completion

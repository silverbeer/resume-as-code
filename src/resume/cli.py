"""Command-line interface for Resume as Code."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from resume.ai.agents import analyze_job_description
from resume.ai.agents import compare_skills
from resume.ai.crew_agents import ProfileGenerator
from resume.ai.style_rules import StyleRules
from resume.builder import ResumeBuilder
from resume.cv_converter import convert_pdf_to_yaml
from resume.loader import ResumeLoader
from resume.loader import get_available_profiles
from resume.utils import get_data_dir
from resume.utils import load_yaml
from resume.utils import save_yaml

app = typer.Typer(
    name="resume",
    help="AI-powered resume builder that analyzes job descriptions and creates tailored ATS-friendly resumes",
    add_completion=False,
)
console = Console()


@app.command()
def list_profiles(
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Resume data directory (defaults to $RESUME_DATA_DIR or project data/)",
        envvar="RESUME_DATA_DIR",
    ),
) -> None:
    """List all available resume profiles."""
    profiles = get_available_profiles(data_dir)

    if not profiles:
        rprint("[yellow]No profiles found. Create profiles in data/profiles/[/yellow]")
        return

    table = Table(title="Available Profiles", show_header=True)
    table.add_column("Profile Name", style="cyan")

    for profile in profiles:
        table.add_row(profile)

    console.print(table)


@app.command()
def analyze(
    profile: str = typer.Argument(..., help="Profile name to analyze"),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Resume data directory (defaults to $RESUME_DATA_DIR or project data/)",
        envvar="RESUME_DATA_DIR",
    ),
) -> None:
    """Analyze job description and compare with your resume skills."""
    try:
        # Load data
        with console.status(f"[bold green]Loading profile '{profile}'..."):
            loader = ResumeLoader(profile, data_dir=data_dir)
            resume = loader.load_resume()
            job_desc = loader.load_job_description()

        # Analyze job description
        with console.status("[bold green]Analyzing job description with AI..."):
            loop = asyncio.get_event_loop()
            job_analysis = loop.run_until_complete(analyze_job_description(job_desc))

        # Compare skills
        resume_skill_names = resume.skills.get_skill_names()
        skill_gap = loop.run_until_complete(
            compare_skills(
                resume_skill_names,
                job_analysis.required_skills,
                job_analysis.preferred_skills,
            )
        )

        # Display results
        console.print()
        console.print(
            Panel(
                f"[bold]{job_analysis.role_level} {job_analysis.role_type}[/bold]",
                title="Job Analysis",
                border_style="blue",
            )
        )

        # Skills match table
        console.print()
        skills_table = Table(title="Skills Analysis", show_header=True)
        skills_table.add_column("Category", style="cyan")
        skills_table.add_column("Count", justify="right")
        skills_table.add_column("Details", style="dim")

        skills_table.add_row(
            "Matching Skills",
            str(len(skill_gap.matching_skills)),
            ", ".join(skill_gap.matching_skills[:5])
            + ("..." if len(skill_gap.matching_skills) > 5 else ""),
        )
        skills_table.add_row(
            "Missing Required",
            f"[red]{len(skill_gap.missing_required_skills)}[/red]",
            ", ".join(skill_gap.missing_required_skills[:5])
            + ("..." if len(skill_gap.missing_required_skills) > 5 else ""),
        )
        skills_table.add_row(
            "Missing Preferred",
            f"[yellow]{len(skill_gap.missing_preferred_skills)}[/yellow]",
            ", ".join(skill_gap.missing_preferred_skills[:5])
            + ("..." if len(skill_gap.missing_preferred_skills) > 5 else ""),
        )

        console.print(skills_table)

        # Match percentage
        match_color = "green" if skill_gap.skill_match_percentage >= 70 else "yellow" if skill_gap.skill_match_percentage >= 50 else "red"
        console.print()
        console.print(
            Panel(
                f"[bold {match_color}]{skill_gap.skill_match_percentage}%[/bold {match_color}]",
                title="Skill Match Percentage",
                border_style=match_color,
            )
        )

        # Recommendations
        if skill_gap.recommendations:
            console.print()
            console.print("[bold]Recommendations:[/bold]")
            for rec in skill_gap.recommendations:
                console.print(f"  • {rec}")

        # Missing skills details
        if skill_gap.missing_required_skills:
            console.print()
            console.print("[bold red]Missing Required Skills:[/bold red]")
            for skill in skill_gap.missing_required_skills:
                console.print(f"  • {skill}")

    except FileNotFoundError as e:
        rprint(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except ValueError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def build(
    profile: str = typer.Argument(..., help="Profile name to build"),
    format: str = typer.Option("html", "--format", "-f", help="Output format (html, pdf, or both)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Custom output path"),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Resume data directory (defaults to $RESUME_DATA_DIR or project data/)",
        envvar="RESUME_DATA_DIR",
    ),
) -> None:
    """Build resume in specified format(s)."""
    try:
        # Load resume data
        with console.status(f"[bold green]Loading profile '{profile}'..."):
            loader = ResumeLoader(profile, data_dir=data_dir)
            resume = loader.load_resume()

        formats = format.lower().split(",")
        generated_files = []

        with Progress() as progress:
            task = progress.add_task("[cyan]Generating resume...", total=len(formats))

            for fmt in formats:
                fmt = fmt.strip()

                if fmt == "html":
                    builder = ResumeBuilder()
                    if output:
                        html_path = Path(output)
                    else:
                        html_path = builder.build_to_file(resume, profile, "html")
                        builder.build_html(resume, html_path)

                    generated_files.append(html_path)

                elif fmt == "pdf":
                    try:
                        from resume.pdf import PDFGenerator
                        pdf_gen = PDFGenerator()
                        if output:
                            pdf_path = Path(output)
                            pdf_gen.generate_pdf(resume, pdf_path)
                        else:
                            pdf_path = pdf_gen.build_resume_pdf(resume, profile)

                        generated_files.append(pdf_path)
                    except (ImportError, OSError) as e:
                        rprint(f"[red]PDF generation failed: {e}[/red]")
                        rprint("[yellow]Install system dependencies for WeasyPrint:[/yellow]")
                        rprint("[yellow]  brew install pango cairo[/yellow]")
                        continue

                elif fmt == "both":
                    builder = ResumeBuilder()
                    html_path = builder.build_to_file(resume, profile, "html")
                    generated_files.append(html_path)

                    try:
                        from resume.pdf import PDFGenerator
                        pdf_gen = PDFGenerator()
                        pdf_path = pdf_gen.build_resume_pdf(resume, profile)
                        generated_files.append(pdf_path)
                    except (ImportError, OSError) as e:
                        rprint(f"[red]PDF generation failed: {e}[/red]")
                        rprint("[yellow]Install system dependencies for WeasyPrint:[/yellow]")
                        rprint("[yellow]  brew install pango cairo[/yellow]")

                else:
                    rprint(f"[yellow]Unknown format: {fmt}. Skipping.[/yellow]")

                progress.update(task, advance=1)

        # Display success
        console.print()
        console.print("[bold green]✓ Resume generated successfully![/bold green]")
        for file_path in generated_files:
            console.print(f"  • {file_path}")

    except ValueError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def add_skill(
    profile: str = typer.Argument(..., help="Profile to update"),
    skill_name: str = typer.Argument(..., help="Skill name to add"),
    category: str = typer.Option("General", "--category", "-c", help="Skill category"),
    proficiency: str = typer.Option("Intermediate", "--proficiency", "-p", help="Proficiency level"),
    data_dir_opt: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Resume data directory (defaults to $RESUME_DATA_DIR or project data/)",
        envvar="RESUME_DATA_DIR",
    ),
) -> None:
    """Add a new skill to your resume."""
    try:
        # Load current skills
        data_dir = get_data_dir(data_dir_opt)
        skills_file = data_dir / "common" / "skills.yml"

        from resume.utils import load_yaml

        skills_data = load_yaml(skills_file)

        # Check if skill already exists
        existing_skills = [s["name"].lower() for s in skills_data["skills"]]
        if skill_name.lower() in existing_skills:
            rprint(f"[yellow]Skill '{skill_name}' already exists in resume[/yellow]")
            return

        # Add new skill
        new_skill = {
            "name": skill_name,
            "category": category,
            "proficiency": proficiency,
        }
        skills_data["skills"].append(new_skill)

        # Save updated skills
        save_yaml(skills_data, skills_file)

        rprint(
            f"[green]✓ Added skill '{skill_name}' ({category} - {proficiency})[/green]"
        )

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def convert_cv(
    pdf_file: Path = typer.Argument(..., help="Path to PDF CV/resume file"),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output YAML file path (defaults to <pdf_name>.yml)",
    ),
) -> None:
    """Convert PDF CV/resume to YAML format using AI.

    This command extracts text from your PDF CV and uses AI to parse it into
    the structured YAML format required by the resume system.

    Examples:
        # Convert PDF to YAML (creates Tom-Drake-CV.yml)
        uv run resume convert-cv Tom-Drake-CV.pdf

        # Specify custom output path
        uv run resume convert-cv Tom-Drake-CV.pdf --output my-cv.yml

        # Then use the converted file
        uv run resume generate-profile senior-sdet --job job.txt --cv my-cv.yml
    """
    try:
        # Check if PDF exists
        if not pdf_file.exists():
            rprint(f"[red]PDF file not found: {pdf_file}[/red]")
            raise typer.Exit(1)

        # Determine output path
        if output is None:
            output = pdf_file.with_suffix(".yml")

        console.print(f"\n[bold cyan]📄 Converting PDF to YAML...[/bold cyan]")
        console.print(f"[dim]Input:  {pdf_file}[/dim]")
        console.print(f"[dim]Output: {output}[/dim]\n")

        # Extract and convert
        with console.status("[bold green]Extracting text from PDF..."):
            loop = asyncio.get_event_loop()
            cv_data = loop.run_until_complete(convert_pdf_to_yaml(pdf_file))

        # Display preview
        console.print(f"\n[bold green]✓ Conversion successful![/bold green]\n")
        console.print(f"[cyan]Extracted {len(cv_data.experiences)} work experience entries:[/cyan]\n")

        for i, exp in enumerate(cv_data.experiences, 1):
            dates = f"{exp.start_date}"
            if exp.current:
                dates += " - Present"
            elif exp.end_date:
                dates += f" - {exp.end_date}"

            console.print(f"{i}. [bold]{exp.title}[/bold] at {exp.company}")
            console.print(f"   {dates}")
            console.print(f"   {len(exp.achievements)} achievements, {len(exp.technologies)} technologies\n")

        # Save to YAML
        yaml_data = {"experiences": [exp.model_dump() for exp in cv_data.experiences]}
        save_yaml(yaml_data, output)

        console.print(f"[bold green]✓ YAML file saved:[/bold green] {output}\n")
        console.print("[dim]Review the YAML file and make any necessary edits before using it.[/dim]")
        console.print(f"\n[bold]Next step:[/bold]")
        console.print(f"  uv run resume generate-profile <profile-name> --job <job.txt> --cv {output}")

    except FileNotFoundError as e:
        rprint(f"[red]File not found: {e}[/red]")
        raise typer.Exit(1)
    except RuntimeError as e:
        rprint(f"[red]Conversion error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def generate_profile(
    profile_name: str = typer.Argument(..., help="Name for the new profile (e.g., 'senior-sdet')"),
    job_file: Path = typer.Option(..., "--job", "-j", help="Path to job description text file"),
    cv_file: Path | None = typer.Option(
        None,
        "--cv",
        "-c",
        help="Path to your CV/experience YAML file (defaults to data/common/experience.yml)",
    ),
    no_em_dashes: bool = typer.Option(True, help="Reject em dashes in content"),
    no_first_person: bool = typer.Option(True, help="Reject first-person pronouns"),
    max_bullet_length: int = typer.Option(120, help="Maximum bullet length"),
    auto_build: bool = typer.Option(False, help="Automatically build PDF after generation"),
    skip_confirmation: bool = typer.Option(False, help="Skip user confirmation before writing files"),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Resume data directory (defaults to $RESUME_DATA_DIR or project data/)",
        envvar="RESUME_DATA_DIR",
    ),
) -> None:
    """Generate resume profile using AI agents from job description.

    This command uses CrewAI multi-agent system to:
    1. Analyze the job description
    2. Generate tailored resume content
    3. Review content for quality
    4. Create a cover letter

    Examples:
        # Use default experience from data/common/experience.yml
        uv run resume generate-profile senior-sdet --job job.txt

        # Use custom CV file
        uv run resume generate-profile senior-sdet --job job.txt --cv ~/my-cv.yml
    """
    try:
        # Read job description
        if not job_file.exists():
            rprint(f"[red]Job file not found: {job_file}[/red]")
            raise typer.Exit(1)

        job_description = job_file.read_text()
        if not job_description.strip():
            rprint("[red]Job description file is empty[/red]")
            raise typer.Exit(1)

        # Load existing experience from custom CV or default location
        data_dir_path = get_data_dir(data_dir)

        if cv_file:
            # Use custom CV file provided by user
            if not cv_file.exists():
                rprint(f"[red]CV file not found: {cv_file}[/red]")
                raise typer.Exit(1)
            experience_file = cv_file
            console.print(f"[dim]Using CV from: {cv_file}[/dim]")
        else:
            # Use default common experience
            common_dir = data_dir_path / "common"
            experience_file = common_dir / "experience.yml"
            if not experience_file.exists():
                rprint(f"[red]Experience file not found: {experience_file}[/red]")
                rprint("[yellow]Create data/common/experience.yml with your work history[/yellow]")
                rprint("[yellow]Or provide a custom CV with --cv <file>[/yellow]")
                raise typer.Exit(1)
            console.print(f"[dim]Using default CV from: {experience_file}[/dim]")

        existing_experience = load_yaml(experience_file)

        # Configure style rules
        style_rules = StyleRules(
            no_em_dashes=no_em_dashes,
            no_first_person=no_first_person,
            max_bullet_length=max_bullet_length,
            action_verb_start=True,
        )

        # Initialize profile generator
        console.print("\n[bold cyan]🤖 Initializing AI agents...[/bold cyan]")
        generator = ProfileGenerator(style_rules=style_rules, verbose=False)

        # Generate profile
        console.print(f"\n[bold green]✨ Generating profile '{profile_name}'...[/bold green]\n")
        console.print("[dim]This may take 30-60 seconds...[/dim]\n")

        with console.status("[bold green]AI agents working...") as status:
            result = generator.generate_profile(
                profile_name=profile_name,
                job_description=job_description,
                existing_experience=existing_experience,
            )

        # Display results
        console.print("\n[bold green]✓ Profile generated successfully![/bold green]\n")
        console.print(f"[dim]Duration: {result.total_duration_seconds:.1f}s[/dim]\n")

        # Job Analysis Summary
        console.print(Panel(
            f"[bold]{result.job_analysis.role_level} {result.job_analysis.role_type}[/bold]\n\n"
            f"[cyan]Required Skills:[/cyan] {len(result.job_analysis.required_skills)}\n"
            f"[cyan]Preferred Skills:[/cyan] {len(result.job_analysis.preferred_skills)}\n"
            f"[cyan]Key Responsibilities:[/cyan] {len(result.job_analysis.key_responsibilities)}",
            title="📋 Job Analysis",
            border_style="blue",
        ))

        # Quality Review
        review = result.quality_review
        review_color = "green" if review.passes_review else "red"
        console.print(Panel(
            f"[bold]Passes Review:[/bold] [{review_color}]{'✓' if review.passes_review else '✗'}[/{review_color}]\n\n"
            f"[cyan]Alignment Score:[/cyan] {review.alignment_score}/10\n"
            f"[cyan]Style Compliance:[/cyan] {review.style_compliance_score}/10\n\n"
            f"[bold]Strengths:[/bold]\n" + "\n".join(f"  • {s}" for s in review.strengths[:3]),
            title="📊 Quality Review",
            border_style=review_color,
        ))

        # Preview content
        console.print("\n[bold]📝 Resume Preview:[/bold]")
        console.print(f"[cyan]Title:[/cyan] {result.resume_content.header_title}")
        console.print(f"\n[cyan]Summary:[/cyan]\n{result.resume_content.summary[:200]}...")
        console.print(f"\n[cyan]Experience Entries:[/cyan] {len(result.resume_content.experiences)}")
        console.print(f"[cyan]Total Skills:[/cyan] {len(result.resume_content.skills)}")

        # Show first achievement bullet as example
        if result.resume_content.experiences and result.resume_content.experiences[0].achievements:
            first_bullet = result.resume_content.experiences[0].achievements[0]
            console.print(f"\n[cyan]Example Bullet:[/cyan]\n  • {first_bullet}")

        console.print(f"\n[bold]📄 Cover Letter:[/bold]")
        console.print(f"{result.cover_letter.opening_paragraph[:150]}...\n")

        # User confirmation
        if not skip_confirmation:
            console.print()
            if not typer.confirm("📁 Write profile files to disk?", default=True):
                console.print("[yellow]Profile generation cancelled[/yellow]")
                return

        # Write profile files
        console.print("\n[bold green]Writing profile files...[/bold green]")
        profile_dir = data_dir_path / "profiles" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)

        # Write header.yml
        header_data = {"title": result.resume_content.header_title}
        save_yaml(header_data, profile_dir / "header.yml")
        console.print(f"  ✓ {profile_dir / 'header.yml'}")

        # Write summary.yml
        summary_data = {"content": result.resume_content.summary}
        save_yaml(summary_data, profile_dir / "summary.yml")
        console.print(f"  ✓ {profile_dir / 'summary.yml'}")

        # Write experience.yml
        experiences_data = {
            "experiences": [
                {
                    "company": exp.company,
                    "title": exp.title,
                    "location": exp.location,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "current": exp.current,
                    "achievements": exp.achievements,
                    "technologies": exp.technologies,
                }
                for exp in result.resume_content.experiences
            ]
        }
        save_yaml(experiences_data, profile_dir / "experience.yml")
        console.print(f"  ✓ {profile_dir / 'experience.yml'}")

        # Write skills.yml
        skills_data = {
            "skills": [
                {
                    "name": skill.name,
                    "category": skill.category,
                    "proficiency": skill.proficiency,
                }
                for skill in result.resume_content.skills
            ]
        }
        save_yaml(skills_data, profile_dir / "skills.yml")
        console.print(f"  ✓ {profile_dir / 'skills.yml'}")

        # Write job.txt
        (profile_dir / "job.txt").write_text(job_description)
        console.print(f"  ✓ {profile_dir / 'job.txt'}")

        # Write cover_letter.md
        cover_letter_md = result.cover_letter.to_markdown()
        (profile_dir / "cover_letter.md").write_text(cover_letter_md)
        console.print(f"  ✓ {profile_dir / 'cover_letter.md'}")

        console.print(f"\n[bold green]✓ Profile files written to:[/bold green] {profile_dir}")

        # Show any issues
        if review.issues_found:
            console.print("\n[yellow]⚠ Issues found (consider manual review):[/yellow]")
            for issue in review.issues_found[:5]:
                console.print(f"  • {issue}")

        # Auto-build PDF if requested
        if auto_build:
            console.print(f"\n[bold cyan]Building PDF for profile '{profile_name}'...[/bold cyan]")
            # Note: build() is already defined, we can call it but need to handle it differently
            # For now, just show a message
            console.print("[dim]Run: uv run resume build {profile_name} --format pdf[/dim]")

        console.print(f"\n[bold green]🎉 Profile '{profile_name}' generated successfully![/bold green]")
        console.print(f"\n[dim]Next steps:[/dim]")
        console.print(f"  1. Review files in: {profile_dir}")
        console.print(f"  2. Build resume: uv run resume build {profile_name} --format pdf")
        console.print(f"  3. Analyze quality: uv run resume analyze {profile_name}")

    except FileNotFoundError as e:
        rprint(f"[red]File not found: {e}[/red]")
        raise typer.Exit(1)
    except ValueError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    rprint("[bold]Resume as Code[/bold] - v1.0.0")
    rprint("AI-powered resume builder")


@app.callback()
def callback() -> None:
    """
    Resume as Code - AI-Powered Resume Builder

    Build ATS-friendly resumes tailored to specific job descriptions using AI.
    """
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            "[yellow]Warning: OPENAI_API_KEY not set. AI features will not work.[/yellow]"
        )
        console.print(
            "[yellow]Set it with: export OPENAI_API_KEY='your-api-key'[/yellow]\n"
        )


if __name__ == "__main__":
    app()

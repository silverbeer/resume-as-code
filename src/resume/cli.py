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
from resume.builder import ResumeBuilder
from resume.loader import ResumeLoader
from resume.loader import get_available_profiles
from resume.utils import get_data_dir
from resume.utils import save_yaml

app = typer.Typer(
    name="resume",
    help="AI-powered resume builder that analyzes job descriptions and creates tailored ATS-friendly resumes",
    add_completion=False,
)
console = Console()


@app.command()
def list_profiles() -> None:
    """List all available resume profiles."""
    profiles = get_available_profiles()

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
) -> None:
    """Analyze job description and compare with your resume skills."""
    try:
        # Load data
        with console.status(f"[bold green]Loading profile '{profile}'..."):
            loader = ResumeLoader(profile)
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
) -> None:
    """Build resume in specified format(s)."""
    try:
        # Load resume data
        with console.status(f"[bold green]Loading profile '{profile}'..."):
            loader = ResumeLoader(profile)
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
) -> None:
    """Add a new skill to your resume."""
    try:
        # Load current skills
        data_dir = get_data_dir()
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

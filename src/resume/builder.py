"""Resume builder for generating HTML from data and templates."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader

from resume.models import Resume
from resume.utils import get_output_dir
from resume.utils import get_templates_dir


class ResumeBuilder:
    """Builder for generating resume HTML from templates."""

    def __init__(self, template_name: str = "resume.html.j2") -> None:
        """Initialize the builder.

        Args:
            template_name: Name of the Jinja2 template file
        """
        self.template_name = template_name
        self.templates_dir = get_templates_dir()
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def build_html(self, resume: Resume, output_path: Path | str | None = None) -> str:
        """Build HTML resume from resume data.

        Args:
            resume: Resume data model
            output_path: Optional path to save HTML file

        Returns:
            Generated HTML string
        """
        template = self.env.get_template(self.template_name)

        # Render the template
        html = template.render(
            header=resume.header,
            summary=resume.summary,
            experience=resume.experience,
            skills=resume.skills,
        )

        # Save to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(html)

        return html

    def build_to_file(
        self, resume: Resume, profile: str, format_type: str = "html"
    ) -> Path:
        """Build resume and save to output directory.

        Args:
            resume: Resume data model
            profile: Profile name for filename
            format_type: Output format ('html' or 'pdf')

        Returns:
            Path to generated file
        """
        output_dir = get_output_dir()
        output_file = output_dir / f"{profile}_resume.{format_type}"

        if format_type == "html":
            self.build_html(resume, output_file)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        return output_file

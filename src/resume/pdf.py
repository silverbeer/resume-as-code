"""PDF generation from HTML using Playwright."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

from resume.builder import ResumeBuilder
from resume.models import Resume
from resume.utils import get_output_dir


class PDFGenerator:
    """Generator for creating PDF resumes from HTML using Playwright."""

    def __init__(self) -> None:
        """Initialize PDF generator."""
        self.builder = ResumeBuilder()

    def html_to_pdf(self, html_content: str, output_path: Path | str) -> None:
        """Convert HTML string to PDF file using Playwright.

        Args:
            html_content: HTML content as string
            output_path: Path to save PDF file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Use Playwright to generate PDF
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)
            # Wait for page to be fully rendered
            page.wait_for_load_state("networkidle")
            page.pdf(
                path=str(output_file),
                format="Letter",
                print_background=True,
                prefer_css_page_size=True,  # Use CSS @page margins
            )
            browser.close()

    def html_file_to_pdf(self, html_path: Path | str, pdf_path: Path | str) -> None:
        """Convert HTML file to PDF file using Playwright.

        Args:
            html_path: Path to HTML file
            pdf_path: Path to save PDF file
        """
        html_file = Path(html_path)
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")

        output_file = Path(pdf_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Use Playwright to generate PDF from file
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{html_file.absolute()}")
            page.pdf(
                path=str(output_file),
                format="Letter",
                print_background=True,
                prefer_css_page_size=True,  # Use CSS @page margins
            )
            browser.close()

    def generate_pdf(self, resume: Resume, output_path: Path | str) -> None:
        """Generate PDF directly from Resume model.

        Args:
            resume: Resume data model
            output_path: Path to save PDF file
        """
        # Generate HTML first
        html_content = self.builder.build_html(resume)

        # Convert to PDF
        self.html_to_pdf(html_content, output_path)

    def build_resume_pdf(self, resume: Resume, profile: str, data_dir: Path | None = None) -> Path:
        """Build resume PDF and save to output directory.

        Args:
            resume: Resume data model
            profile: Profile name for filename
            data_dir: Optional data directory path (for output location)

        Returns:
            Path to generated PDF file
        """
        output_dir = get_output_dir(data_dir)
        pdf_path = output_dir / f"{profile}_resume.pdf"

        self.generate_pdf(resume, pdf_path)

        return pdf_path

"""Tests for resume builder."""

from __future__ import annotations

from pathlib import Path

import pytest

from resume.builder import ResumeBuilder
from resume.models import Resume


class TestResumeBuilder:
    """Tests for ResumeBuilder class."""

    def test_init_default_template(self, monkeypatch, tmp_path: Path):
        """Test initializing builder with default template."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "resume.html.j2").write_text("<html>{{ header.name }}</html>")

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        assert builder.template_name == "resume.html.j2"
        assert builder.templates_dir == templates_dir

    def test_init_custom_template(self, monkeypatch, tmp_path: Path):
        """Test initializing builder with custom template."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "custom.html.j2").write_text("<html>Custom</html>")

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder(template_name="custom.html.j2")
        assert builder.template_name == "custom.html.j2"

    def test_build_html_basic(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test building basic HTML resume."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_content = """
        <html>
        <head><title>{{ header.name }} - {{ header.title }}</title></head>
        <body>
            <h1>{{ header.name }}</h1>
            <h2>{{ header.title }}</h2>
            <p>{{ summary.content }}</p>
        </body>
        </html>
        """
        (templates_dir / "resume.html.j2").write_text(template_content)

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        html = builder.build_html(sample_resume)

        assert "<h1>John Doe</h1>" in html
        assert "<h2>Software Engineer</h2>" in html
        assert "Experienced software engineer" in html

    def test_build_html_with_footer(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test building HTML with footer."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_content = """
        <html>
        <body>
            <h1>{{ header.name }}</h1>
            {% if footer %}
            <footer>{{ footer.text }}</footer>
            {% endif %}
        </body>
        </html>
        """
        (templates_dir / "resume.html.j2").write_text(template_content)

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        html = builder.build_html(sample_resume)

        assert "<footer>Built with Resume as Code 🚀</footer>" in html

    def test_build_html_without_footer(
        self, sample_header, sample_summary, sample_experience, sample_skills, monkeypatch, tmp_path: Path
    ):
        """Test building HTML without footer."""
        from resume.models import Resume

        resume = Resume(
            header=sample_header,
            summary=sample_summary,
            experience=sample_experience,
            skills=sample_skills,
            footer=None,
        )

        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_content = """
        <html>
        <body>
            <h1>{{ header.name }}</h1>
            {% if footer %}
            <footer>{{ footer.text }}</footer>
            {% else %}
            <footer>No footer</footer>
            {% endif %}
        </body>
        </html>
        """
        (templates_dir / "resume.html.j2").write_text(template_content)

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        html = builder.build_html(resume)

        assert "<footer>No footer</footer>" in html

    def test_build_html_with_experience(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test building HTML with experience section."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_content = """
        <html>
        <body>
            {% for exp in experience.experiences %}
            <div>
                <h3>{{ exp.title }} at {{ exp.company }}</h3>
                {% for achievement in exp.achievements %}
                <li>{{ achievement }}</li>
                {% endfor %}
            </div>
            {% endfor %}
        </body>
        </html>
        """
        (templates_dir / "resume.html.j2").write_text(template_content)

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        html = builder.build_html(sample_resume)

        assert "Senior Engineer at Tech Corp" in html
        assert "Software Engineer at Startup Inc" in html
        assert "Built scalable microservices architecture" in html
        assert "Developed REST APIs" in html

    def test_build_html_with_skills(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test building HTML with skills section."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_content = """
        <html>
        <body>
            {% for skill in skills.skills %}
            <span>{{ skill.name }} ({{ skill.category }})</span>
            {% endfor %}
        </body>
        </html>
        """
        (templates_dir / "resume.html.j2").write_text(template_content)

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        html = builder.build_html(sample_resume)

        assert "Python (Programming)" in html
        assert "Kubernetes (Infrastructure)" in html
        assert "pytest (Testing)" in html
        assert "AWS (Cloud)" in html

    def test_build_html_save_to_file(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test building HTML and saving to file."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "resume.html.j2").write_text("<html><h1>{{ header.name }}</h1></html>")

        output_file = tmp_path / "output" / "resume.html"

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        html = builder.build_html(sample_resume, output_path=output_file)

        # Check file was created
        assert output_file.exists()

        # Check content
        saved_html = output_file.read_text()
        assert saved_html == html
        assert "<h1>John Doe</h1>" in saved_html

    def test_build_to_file_html(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test build_to_file method with HTML format."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "resume.html.j2").write_text("<html><h1>{{ header.name }}</h1></html>")

        output_dir = tmp_path / "output"

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)
        monkeypatch.setattr("resume.builder.get_output_dir", lambda: output_dir)

        builder = ResumeBuilder()
        output_path = builder.build_to_file(sample_resume, "test-profile", "html")

        assert output_path == output_dir / "test-profile_resume.html"
        assert output_path.exists()
        assert "<h1>John Doe</h1>" in output_path.read_text()

    def test_build_to_file_unsupported_format(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test build_to_file with unsupported format."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "resume.html.j2").write_text("<html></html>")

        output_dir = tmp_path / "output"

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)
        monkeypatch.setattr("resume.builder.get_output_dir", lambda: output_dir)

        builder = ResumeBuilder()

        with pytest.raises(ValueError, match="Unsupported format: docx"):
            builder.build_to_file(sample_resume, "test-profile", "docx")

    def test_build_html_contact_info(self, sample_resume: Resume, monkeypatch, tmp_path: Path):
        """Test building HTML with complete contact info."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_content = """
        <html>
        <body>
            <div>{{ header.contact.email }}</div>
            <div>{{ header.contact.phone }}</div>
            <div>{{ header.contact.linkedin }}</div>
            <div>{{ header.contact.github }}</div>
            <div>{{ header.contact.website }}</div>
            <div>{{ header.contact.location }}</div>
        </body>
        </html>
        """
        (templates_dir / "resume.html.j2").write_text(template_content)

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        builder = ResumeBuilder()
        html = builder.build_html(sample_resume)

        assert "john@example.com" in html
        assert "+1-555-0100" in html
        assert "linkedin.com/in/johndoe" in html
        assert "github.com/johndoe" in html
        assert "johndoe.dev" in html
        assert "San Francisco, CA" in html

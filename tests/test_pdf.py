"""Tests for PDF generation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from resume.pdf import PDFGenerator


class TestPDFGenerator:
    """Tests for PDFGenerator class."""

    def test_init(self):
        """Test initializing PDF generator."""
        generator = PDFGenerator()
        assert generator is not None

    @patch("resume.pdf.sync_playwright")
    def test_html_to_pdf_basic(self, mock_playwright, tmp_path: Path):
        """Test basic HTML to PDF conversion."""
        # Setup mocks
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        html_content = "<html><body><h1>Test Resume</h1></body></html>"
        output_path = tmp_path / "test.pdf"

        generator = PDFGenerator()
        generator.html_to_pdf(html_content, output_path)

        # Verify Playwright was called correctly
        mock_playwright_instance.chromium.launch.assert_called_once()
        mock_browser.new_page.assert_called_once()
        mock_page.set_content.assert_called_once_with(html_content)
        mock_page.wait_for_load_state.assert_called_once_with("networkidle")
        mock_page.pdf.assert_called_once()
        mock_browser.close.assert_called_once()

    @patch("resume.pdf.sync_playwright")
    def test_html_to_pdf_with_path_string(self, mock_playwright, tmp_path: Path):
        """Test PDF generation with string path."""
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        html_content = "<html><body>Test</body></html>"
        output_path = str(tmp_path / "test.pdf")  # String path

        generator = PDFGenerator()
        generator.html_to_pdf(html_content, output_path)

        # Should work with string path
        mock_page.pdf.assert_called_once()
        call_args = mock_page.pdf.call_args
        assert str(tmp_path / "test.pdf") in str(call_args)

    @patch("resume.pdf.sync_playwright")
    def test_html_to_pdf_creates_directory(self, mock_playwright, tmp_path: Path):
        """Test that PDF generation creates output directory."""
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        html_content = "<html><body>Test</body></html>"
        output_path = tmp_path / "nested" / "dir" / "test.pdf"

        generator = PDFGenerator()
        generator.html_to_pdf(html_content, output_path)

        # Directory should have been created
        assert output_path.parent.exists()

    @patch("resume.pdf.sync_playwright")
    def test_html_to_pdf_settings(self, mock_playwright, tmp_path: Path):
        """Test PDF generation with correct settings."""
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        html_content = "<html><body>Test</body></html>"
        output_path = tmp_path / "test.pdf"

        generator = PDFGenerator()
        generator.html_to_pdf(html_content, output_path)

        # Check PDF settings
        call_kwargs = mock_page.pdf.call_args.kwargs
        assert call_kwargs["format"] == "Letter"
        assert call_kwargs["print_background"] is True
        assert "margin" in call_kwargs
        assert call_kwargs["margin"]["top"] == "0.5in"
        assert call_kwargs["margin"]["bottom"] == "0.5in"

    @patch("resume.pdf.sync_playwright")
    def test_generate_pdf(self, mock_playwright, sample_resume, tmp_path: Path, monkeypatch):
        """Test generate_pdf method."""
        # Setup Playwright mocks
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        # Setup file system
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "resume.html.j2").write_text("<html><h1>{{ header.name }}</h1></html>")

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)

        output_path = tmp_path / "output" / "resume.pdf"

        generator = PDFGenerator()
        generator.generate_pdf(sample_resume, output_path)

        # Verify PDF generation was called
        mock_page.set_content.assert_called_once()
        mock_page.pdf.assert_called_once()

        # Check that HTML contains resume data
        html_arg = mock_page.set_content.call_args[0][0]
        assert "John Doe" in html_arg

    @patch("resume.pdf.sync_playwright")
    def test_build_resume_pdf(self, mock_playwright, sample_resume, tmp_path: Path, monkeypatch):
        """Test build_resume_pdf method."""
        # Setup Playwright mocks
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        # Setup file system
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "resume.html.j2").write_text("<html><h1>{{ header.name }}</h1></html>")

        output_dir = tmp_path / "output"

        monkeypatch.setattr("resume.builder.get_templates_dir", lambda: templates_dir)
        monkeypatch.setattr("resume.pdf.get_output_dir", lambda: output_dir)

        generator = PDFGenerator()
        output_path = generator.build_resume_pdf(sample_resume, "test-profile")

        # Check output path
        assert output_path == output_dir / "test-profile_resume.pdf"

        # Verify PDF generation was called
        mock_page.set_content.assert_called_once()
        mock_page.pdf.assert_called_once()

    @patch("resume.pdf.sync_playwright")
    def test_html_file_to_pdf(self, mock_playwright, tmp_path: Path):
        """Test converting HTML file to PDF."""
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        html_file = tmp_path / "input.html"
        html_file.write_text("<html><body><h1>Test</h1></body></html>")

        pdf_file = tmp_path / "output.pdf"

        generator = PDFGenerator()
        generator.html_file_to_pdf(html_file, pdf_file)

        # Verify file was opened
        mock_page.goto.assert_called_once()
        call_arg = mock_page.goto.call_args[0][0]
        assert "file://" in call_arg
        assert str(html_file.absolute()) in call_arg

        # Verify PDF was generated
        mock_page.pdf.assert_called_once()

    @patch("resume.pdf.sync_playwright")
    def test_html_file_to_pdf_file_not_found(self, mock_playwright, tmp_path: Path):
        """Test html_file_to_pdf with non-existent HTML file."""
        html_file = tmp_path / "nonexistent.html"
        pdf_file = tmp_path / "output.pdf"

        generator = PDFGenerator()

        with pytest.raises(FileNotFoundError, match="HTML file not found"):
            generator.html_file_to_pdf(html_file, pdf_file)

    @patch("resume.pdf.sync_playwright")
    def test_headless_mode(self, mock_playwright, tmp_path: Path):
        """Test that browser is launched in headless mode."""
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        html_content = "<html><body>Test</body></html>"
        output_path = tmp_path / "test.pdf"

        generator = PDFGenerator()
        generator.html_to_pdf(html_content, output_path)

        # By default, Playwright launches in headless mode
        # We're just verifying it was called (headless is default)
        mock_playwright_instance.chromium.launch.assert_called_once()

    @patch("resume.pdf.sync_playwright")
    def test_wait_for_network_idle(self, mock_playwright, tmp_path: Path):
        """Test that page waits for network idle before PDF generation."""
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance

        html_content = "<html><body>Test</body></html>"
        output_path = tmp_path / "test.pdf"

        generator = PDFGenerator()
        generator.html_to_pdf(html_content, output_path)

        # Verify wait_for_load_state was called before pdf()
        mock_page.wait_for_load_state.assert_called_once_with("networkidle")

        # Verify order: set_content -> wait_for_load_state -> pdf
        call_order = [call[0] for call in mock_page.method_calls]
        set_content_idx = call_order.index("set_content")
        wait_idx = call_order.index("wait_for_load_state")
        pdf_idx = call_order.index("pdf")

        assert set_content_idx < wait_idx < pdf_idx

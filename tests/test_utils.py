"""Tests for utility functions."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from resume.utils import (
    get_data_dir,
    get_output_dir,
    get_project_root,
    get_templates_dir,
    load_yaml,
    read_text_file,
)


class TestProjectPaths:
    """Tests for project path functions."""

    def test_get_project_root(self):
        """Test getting project root directory."""
        root = get_project_root()
        assert isinstance(root, Path)
        assert root.exists()
        assert (root / "pyproject.toml").exists()

    def test_get_data_dir(self):
        """Test getting data directory."""
        data_dir = get_data_dir()
        assert isinstance(data_dir, Path)
        assert data_dir.name == "data"
        assert str(get_project_root()) in str(data_dir)

    def test_get_templates_dir(self):
        """Test getting templates directory."""
        templates_dir = get_templates_dir()
        assert isinstance(templates_dir, Path)
        assert templates_dir.name == "templates"
        assert str(get_project_root()) in str(templates_dir)

    def test_get_output_dir(self):
        """Test getting output directory."""
        output_dir = get_output_dir()
        assert isinstance(output_dir, Path)
        assert output_dir.name == "output"
        assert str(get_project_root()) in str(output_dir)


class TestFileOperations:
    """Tests for file operation functions."""

    def test_load_yaml_valid(self, tmp_path: Path):
        """Test loading valid YAML file."""
        yaml_file = tmp_path / "test.yml"
        test_data = {"name": "Test", "value": 42, "items": ["a", "b", "c"]}

        with open(yaml_file, "w") as f:
            yaml.dump(test_data, f)

        loaded_data = load_yaml(yaml_file)

        assert loaded_data == test_data
        assert loaded_data["name"] == "Test"
        assert loaded_data["value"] == 42
        assert len(loaded_data["items"]) == 3

    def test_load_yaml_nested(self, tmp_path: Path):
        """Test loading YAML with nested structures."""
        yaml_file = tmp_path / "nested.yml"
        test_data = {
            "header": {"name": "John", "title": "Engineer"},
            "contact": {"email": "john@example.com", "phone": "555-0100"},
        }

        with open(yaml_file, "w") as f:
            yaml.dump(test_data, f)

        loaded_data = load_yaml(yaml_file)

        assert loaded_data["header"]["name"] == "John"
        assert loaded_data["contact"]["email"] == "john@example.com"

    def test_load_yaml_file_not_found(self, tmp_path: Path):
        """Test loading non-existent YAML file."""
        yaml_file = tmp_path / "nonexistent.yml"

        with pytest.raises(FileNotFoundError):
            load_yaml(yaml_file)

    def test_read_text_file_basic(self, tmp_path: Path):
        """Test reading basic text file."""
        text_file = tmp_path / "test.txt"
        content = "This is a test file.\nWith multiple lines.\nAnd more content."

        text_file.write_text(content)

        read_content = read_text_file(text_file)

        assert read_content == content
        assert "This is a test file" in read_content
        assert "multiple lines" in read_content

    def test_read_text_file_empty(self, tmp_path: Path):
        """Test reading empty text file."""
        text_file = tmp_path / "empty.txt"
        text_file.write_text("")

        read_content = read_text_file(text_file)

        assert read_content == ""

    def test_read_text_file_unicode(self, tmp_path: Path):
        """Test reading text file with unicode characters."""
        text_file = tmp_path / "unicode.txt"
        content = "Hello 世界! 🚀 Testing émojis and spëcial çharacters."

        text_file.write_text(content, encoding="utf-8")

        read_content = read_text_file(text_file)

        assert read_content == content
        assert "世界" in read_content
        assert "🚀" in read_content
        assert "émojis" in read_content

    def test_read_text_file_not_found(self, tmp_path: Path):
        """Test reading non-existent text file."""
        text_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            read_text_file(text_file)

    def test_read_text_file_with_path_object(self, tmp_path: Path):
        """Test read_text_file accepts Path objects."""
        text_file = tmp_path / "test.txt"
        content = "Test content"
        text_file.write_text(content)

        # Pass Path object (not string)
        read_content = read_text_file(text_file)

        assert read_content == content

    def test_read_text_file_with_string_path(self, tmp_path: Path):
        """Test read_text_file accepts string paths."""
        text_file = tmp_path / "test.txt"
        content = "Test content"
        text_file.write_text(content)

        # Pass string path (not Path object)
        read_content = read_text_file(str(text_file))

        assert read_content == content

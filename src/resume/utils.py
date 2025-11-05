"""Utility functions for file I/O and data loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml(file_path: Path | str) -> dict[str, Any]:
    """Load YAML file and return parsed data.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r") as f:
        return yaml.safe_load(f)


def save_yaml(data: dict[str, Any], file_path: Path | str) -> None:
    """Save data to YAML file.

    Args:
        data: Data to save
        file_path: Path to output file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def read_text_file(file_path: Path | str) -> str:
    """Read text file content.

    Args:
        file_path: Path to text file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text()


def write_text_file(content: str, file_path: Path | str) -> None:
    """Write content to text file.

    Args:
        content: Content to write
        file_path: Path to output file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def get_project_root() -> Path:
    """Get project root directory.

    Returns:
        Path to project root
    """
    # Assumes this file is in src/resume/
    return Path(__file__).parent.parent.parent


def get_data_dir() -> Path:
    """Get data directory path.

    Returns:
        Path to data directory
    """
    return get_project_root() / "data"


def get_templates_dir() -> Path:
    """Get templates directory path.

    Returns:
        Path to templates directory
    """
    return get_project_root() / "templates"


def get_output_dir() -> Path:
    """Get output directory path.

    Returns:
        Path to output directory
    """
    output_dir = get_project_root() / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def list_profiles() -> list[str]:
    """List available resume profiles.

    Returns:
        List of profile names
    """
    profiles_dir = get_data_dir() / "profiles"
    if not profiles_dir.exists():
        return []

    return [p.name for p in profiles_dir.iterdir() if p.is_dir()]

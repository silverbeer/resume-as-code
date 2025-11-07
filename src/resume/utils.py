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


def get_data_dir(custom_path: Path | str | None = None) -> Path:
    """Get data directory path.

    Priority order:
    1. custom_path parameter (if provided)
    2. RESUME_DATA_DIR environment variable
    3. XDG_DATA_HOME/resume-as-code (Linux/macOS standard)
    4. ~/.local/share/resume-as-code (fallback)
    5. Project root /data (legacy fallback)

    Args:
        custom_path: Optional custom data directory path

    Returns:
        Path to data directory

    Raises:
        ValueError: If data directory is inside resume-as-code git repo (safety check)
    """
    import os

    # Priority 1: Custom path provided
    if custom_path:
        path = Path(custom_path).expanduser().resolve()
        _validate_data_dir_safety(path)
        return path

    # Priority 2: RESUME_DATA_DIR environment variable
    if env_path := os.getenv("RESUME_DATA_DIR"):
        path = Path(env_path).expanduser().resolve()
        _validate_data_dir_safety(path)
        return path

    # Priority 3: XDG_DATA_HOME
    if xdg_data_home := os.getenv("XDG_DATA_HOME"):
        path = Path(xdg_data_home) / "resume-as-code"
        if path.exists():
            _validate_data_dir_safety(path)
            return path

    # Priority 4: ~/.local/share/resume-as-code
    default_xdg_path = Path.home() / ".local" / "share" / "resume-as-code"
    if default_xdg_path.exists():
        _validate_data_dir_safety(default_xdg_path)
        return default_xdg_path

    # Priority 5: Legacy fallback
    return get_project_root() / "data"


def _validate_data_dir_safety(data_dir: Path) -> None:
    """Validate data directory is not inside resume-as-code git repo.

    Args:
        data_dir: Path to validate

    Raises:
        ValueError: If data_dir is inside a git repo named 'resume-as-code' or 'resume-as-code-private'
    """
    current = data_dir.resolve()
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists():
            if current.name in ("resume-as-code", "resume-as-code-private"):
                raise ValueError(
                    f"⚠️  SAFETY ERROR: Data directory cannot be inside git repo!\n\n"
                    f"Data directory: {data_dir}\n"
                    f"Git repository: {current}\n\n"
                    f"Move your data to a safe location:\n"
                    f"  mkdir -p ~/iCloud/resume-data\n"
                    f"  export RESUME_DATA_DIR=~/iCloud/resume-data\n"
                )
        current = current.parent


def get_templates_dir() -> Path:
    """Get templates directory path.

    Returns:
        Path to templates directory
    """
    return get_project_root() / "templates"


def get_output_dir() -> Path:
    """Get output directory path.

    If RESUME_DATA_DIR is set, output goes to $RESUME_DATA_DIR/output/
    Otherwise, output goes to project root /output

    Returns:
        Path to output directory
    """
    import os

    # Check if RESUME_DATA_DIR is set
    if env_path := os.getenv("RESUME_DATA_DIR"):
        data_dir = Path(env_path).expanduser().resolve()
        output_dir = data_dir / "output"
    else:
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

# External Data Directory Migration Plan

## Overview

Migrate from dual-repo setup (public + private) to single-repo architecture with external data directory on iCloud Drive.

## Goals

1. ✅ **Safety First**: Make it impossible to accidentally commit private resume data
2. ✅ **Single Repo**: Eliminate sync issues between public and private repos
3. ✅ **iCloud Sync**: Enable automatic sync across Mac mini and MacBook Air
4. ✅ **Clean Separation**: Code in git, data in iCloud

---

## Current Architecture (Before)

```
/Users/silverbeer/gitrepos/resume-as-code/          # Public repo
├── src/                                            # Code
├── data/                                           # Example/demo data
│   ├── common/
│   │   ├── header.yml.example
│   │   └── ...
│   └── profiles/
│       ├── test-ninja/                             # Fictional demo
│       └── bug-whisperer/                          # Fictional demo

/Users/silverbeer/gitrepos/resume-as-code-private/  # Private repo (to be deleted)
├── src/                                            # Duplicate code (sync issues)
├── data/                                           # REAL resume data
│   ├── common/
│   │   ├── header.yml                              # Real contact info
│   │   └── ...
│   └── profiles/
│       ├── sre-leadership/                         # Real profile
│       ├── qe-leadership/
│       └── sdet/
```

**Problems:**
- ❌ Must manually sync code changes between two repos
- ❌ Risk of accidentally committing private data
- ❌ .gitignore management complexity
- ❌ Code divergence risk

---

## Target Architecture (After)

```
/Users/silverbeer/gitrepos/resume-as-code/          # Single public repo
├── src/                                            # All code
├── templates/
├── prompts/
├── tests/
├── data/                                           # Example data ONLY
│   ├── common/
│   │   ├── header.yml.example
│   │   ├── experience.yml.example
│   │   └── skills.yml.example
│   └── profiles/
│       ├── test-ninja/                             # Fictional demo
│       └── bug-whisperer/                          # Fictional demo

~/Library/Mobile Documents/com~apple~CloudDocs/resume-data/  # iCloud (private)
├── common/
│   ├── header.yml                                  # Real contact info
│   ├── experience.yml                              # Real work history
│   ├── skills.yml                                  # Real skills
│   └── footer.yml                                  # Real footer
└── profiles/
    ├── sre-leadership/
    │   ├── header.yml
    │   ├── summary.yml
    │   ├── experience.yml
    │   ├── skills.yml
    │   └── job.txt
    ├── qe-leadership/
    │   └── ...
    └── sdet/
        └── ...
```

**Benefits:**
- ✅ Impossible to commit private data (not in git repo)
- ✅ Single source of truth for code
- ✅ Automatic sync across devices via iCloud
- ✅ Standard pattern (like ~/.ssh/, ~/.aws/)

---

## Implementation Steps

### Phase 1: Code Changes (in resume-as-code repo)

#### 1.1 Update `src/resume/utils.py`

Add support for external data directory with priority order:

```python
def get_data_dir(custom_path: Path | str | None = None) -> Path:
    """Get data directory path.

    Priority order:
    1. custom_path parameter (if provided)
    2. RESUME_DATA_DIR environment variable
    3. XDG_DATA_HOME/resume-as-code (Linux/macOS standard)
    4. ~/.local/share/resume-as-code (fallback)
    5. Project root /data (legacy fallback)
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
```

#### 1.2 Add Safety Guard

Add `_validate_data_dir_safety()` function to prevent data in git repos:

```python
def _validate_data_dir_safety(data_dir: Path) -> None:
    """Validate data directory is not inside resume-as-code git repo.

    Raises ValueError if inside a git repo named 'resume-as-code'.
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
                    f"Move your data to iCloud:\n"
                    f"  mkdir -p ~/Library/Mobile\\ Documents/com~apple~CloudDocs/resume-data\n"
                    f"  export RESUME_DATA_DIR=~/Library/Mobile\\ Documents/com~apple~CloudDocs/resume-data\n"
                )
        current = current.parent
```

#### 1.3 Update `src/resume/loader.py`

Update `ResumeLoader.__init__()` to accept custom data directory:

```python
class ResumeLoader:
    def __init__(self, profile: str, data_dir: Path | None = None) -> None:
        """Initialize loader with profile name.

        Args:
            profile: Profile name (e.g., 'sre-leadership')
            data_dir: Optional custom data directory path
        """
        self.profile = profile
        self.data_dir = get_data_dir(data_dir)
        self.common_dir = self.data_dir / "common"
        self.profile_dir = self.data_dir / "profiles" / profile

        if not self.profile_dir.exists():
            raise ValueError(f"Profile not found: {profile}")
```

Update `get_available_profiles()` function:

```python
def get_available_profiles(data_dir: Path | None = None) -> list[str]:
    """Get list of available profiles.

    Args:
        data_dir: Optional custom data directory path

    Returns:
        List of profile names
    """
    profiles_dir = get_data_dir(data_dir) / "profiles"
    if not profiles_dir.exists():
        return []

    return [p.name for p in profiles_dir.iterdir() if p.is_dir()]
```

#### 1.4 Update `src/resume/cli.py`

Add `--data-dir` option to all commands:

```python
@app.command()
def build(
    profile: str = typer.Argument(..., help="Profile name to build"),
    format: str = typer.Option("html", "--format", "-f", help="Output format"),
    output: str | None = typer.Option(None, "--output", "-o", help="Custom output path"),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Resume data directory (defaults to $RESUME_DATA_DIR or ~/.local/share/resume-as-code)",
        envvar="RESUME_DATA_DIR",
    ),
) -> None:
    """Build resume for a profile."""
    loader = ResumeLoader(profile, data_dir=data_dir)
    # ... rest of function
```

Apply same pattern to:
- `analyze()`
- `list_profiles()`
- `add_skill()`

#### 1.5 Add `init` Command

Create new command to help users set up their data directory:

```python
@app.command()
def init(
    data_dir: Path = typer.Option(
        Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "resume-data",
        "--data-dir",
        "-d",
        help="Data directory to initialize",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite existing directory"),
) -> None:
    """Initialize a new resume data directory with example files."""

    if data_dir.exists() and not force:
        rprint(f"[yellow]Directory already exists: {data_dir}[/yellow]")
        rprint("[yellow]Use --force to overwrite[/yellow]")
        raise typer.Exit(1)

    # Create directory structure
    (data_dir / "common").mkdir(parents=True, exist_ok=True)
    (data_dir / "profiles").mkdir(parents=True, exist_ok=True)

    # Copy example files from repo
    repo_data = get_project_root() / "data"

    # Copy example files (remove .example extension)
    for example_file in (repo_data / "common").glob("*.example"):
        target = data_dir / "common" / example_file.stem  # Removes .example
        shutil.copy(example_file, target)

    rprint(f"[green]✓ Initialized resume data directory: {data_dir}[/green]")
    rprint(f"\nNext steps:")
    rprint(f"  1. Edit your personal data: {data_dir}/common/")
    rprint(f"  2. Create a profile: mkdir -p {data_dir}/profiles/my-profile")
    rprint(f"  3. Set environment variable:")
    rprint(f"     echo 'export RESUME_DATA_DIR=\"{data_dir}\"' >> ~/.zshrc")
```

---

### Phase 2: Data Migration

#### 2.1 Create iCloud Data Directory

```bash
# Create the iCloud directory structure
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/common
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/profiles
```

#### 2.2 Copy Private Data from Private Repo

```bash
# Copy all your real resume data to iCloud
cp -r /Users/silverbeer/gitrepos/resume-as-code-private/data/common/* \
     ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/common/

cp -r /Users/silverbeer/gitrepos/resume-as-code-private/data/profiles/sre-leadership \
     ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/profiles/

cp -r /Users/silverbeer/gitrepos/resume-as-code-private/data/profiles/qe-leadership \
     ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/profiles/

cp -r /Users/silverbeer/gitrepos/resume-as-code-private/data/profiles/sdet \
     ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/profiles/
```

#### 2.3 Set Environment Variable

```bash
# Add to ~/.zshrc (macOS default shell)
echo 'export RESUME_DATA_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/resume-data"' >> ~/.zshrc

# Reload shell config
source ~/.zshrc

# Verify
echo $RESUME_DATA_DIR
```

#### 2.4 Copy Missing Files from Private Repo

```bash
# Copy prompts directory that exists in public but not private
cd /Users/silverbeer/gitrepos/resume-as-code-private
cp -r /Users/silverbeer/gitrepos/resume-as-code/prompts .
```

---

### Phase 3: Testing

#### 3.1 Test Commands with iCloud Data

```bash
cd /Users/silverbeer/gitrepos/resume-as-code

# Test list-profiles (should show your real profiles from iCloud)
uv run resume list-profiles

# Test build (should use iCloud data)
uv run resume build sre-leadership --format html

# Test analyze (should use iCloud data)
uv run resume analyze sre-leadership

# Verify output uses your real data
cat output/sre-leadership.html | grep "your-real-email@example.com"
```

#### 3.2 Test Safety Guard

```bash
# This should FAIL with safety error (data in git repo)
uv run resume build sre-leadership --data-dir ./data
# Expected: ValueError about data being in git repo
```

#### 3.3 Test on Other Device

On MacBook Air (after iCloud sync):

```bash
# Add environment variable
echo 'export RESUME_DATA_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/resume-data"' >> ~/.zshrc
source ~/.zshrc

# Clone public repo
cd ~/gitrepos
git clone https://github.com/silverbeer/resume-as-code.git
cd resume-as-code

# Install dependencies
uv sync

# Test (should work with iCloud data)
uv run resume list-profiles
uv run resume build sre-leadership
```

---

### Phase 4: Cleanup

#### 4.1 Archive Private Repo

```bash
# Rename for backup (keep for 1-2 weeks)
cd /Users/silverbeer/gitrepos
mv resume-as-code-private resume-as-code-private.backup-20250106

# After confirming everything works, delete
rm -rf resume-as-code-private.backup-20250106
```

#### 4.2 Update Public Repo README

Add section explaining external data directory setup.

---

## Usage After Migration

### Daily Workflow

```bash
# Work in single public repo
cd /Users/silverbeer/gitrepos/resume-as-code

# Edit your private data (on iCloud)
vim ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/profiles/sre-leadership/summary.yml

# Build resume (automatically uses iCloud data via $RESUME_DATA_DIR)
uv run resume build sre-leadership --format both

# Make code improvements
vim src/resume/ai/agents.py

# Commit code changes (your data is NOT in repo, safe to commit)
git add src/
git commit -m "feat: improve job analysis prompt"
git push
```

### Alternative: Explicit --data-dir

```bash
# If you don't want to use environment variable
uv run resume build sre-leadership \
  --data-dir ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data
```

---

## Rollback Plan

If something goes wrong:

```bash
# 1. Your data is safely backed up in:
#    - resume-as-code-private.backup-20250106/
#    - iCloud Drive (with version history)

# 2. Restore from private repo backup
cp -r resume-as-code-private.backup-20250106/data/* \
      ~/Library/Mobile\ Documents/com~apple~CloudDocs/resume-data/

# 3. Keep using old private repo
cd resume-as-code-private.backup-20250106
mv resume-as-code-private.backup-20250106 resume-as-code-private
```

---

## Open Questions

- [ ] Should we support `~/.resume-data` as simpler alternative to iCloud path?
- [ ] Should `init` command create a first profile for the user?
- [ ] Should we add `resume migrate` command to automate Phase 2?
- [ ] Should output directory also be configurable?

---

## References

- iCloud Drive path on macOS: `~/Library/Mobile Documents/com~apple~CloudDocs/`
- XDG Base Directory spec: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
- Similar patterns: `~/.ssh/`, `~/.aws/`, `~/.docker/`

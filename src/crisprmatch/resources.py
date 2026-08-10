"""Paths to resources shipped inside the installed package."""

from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
UI_DIR = PACKAGE_DIR / "CMlib"


def ui_path(filename: str) -> str:
    """Return an absolute path to a bundled Qt Designer file."""
    resource = UI_DIR / filename
    if not resource.is_file():
        raise FileNotFoundError(f"Bundled UI resource is missing: {resource}")
    return str(resource)

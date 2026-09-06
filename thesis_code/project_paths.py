"""Stable paths for the restored thesis directory layout.

Added in 2026 so scripts can be launched from the repository root instead of
depending on the caller's current working directory.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parent


def project_path(*parts):
    return str(ROOT.joinpath(*parts))

from __future__ import annotations
from pathlib import Path

PROJECT_MARKERS = ("pyproject.toml", "requirements.txt", ".git", ".github")

def find_project_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for parent in (p, *p.parents):
        if any((parent / m).exists() for m in PROJECT_MARKERS):
            return parent
    return p  # fallback

def resolve_data_path(rel_path: str) -> Path:
    root = find_project_root()
    return (root / rel_path).resolve()

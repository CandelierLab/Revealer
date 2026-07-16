"""Global Revealer configuration (XDG).

Stores the user's presentations *root* folder and defaults in
``$XDG_CONFIG_HOME/revealer/config.toml`` (``~/.config/revealer/config.toml``).
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

import tomli_w


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return Path(base) / "revealer"


def config_path() -> Path:
    return config_dir() / "config.toml"


def load() -> dict:
    path = config_path()
    if not path.exists():
        return {}
    with open(path, "rb") as fid:
        return tomllib.load(fid)


def save(data: dict) -> None:
    config_dir().mkdir(parents=True, exist_ok=True)
    with open(config_path(), "wb") as fid:
        tomli_w.dump(data, fid)


def get_root() -> Path | None:
    root = load().get("root")
    return Path(root) if root else None


def get_recents() -> list[Path]:
    """Recently loaded presentation folders (most recent first; existing only)."""
    out = []
    for entry in load().get("recents", []):
        path = Path(entry)
        if path.exists() and path not in out:
            out.append(path)
    return out


def add_recent(path: str | Path, limit: int = 12) -> Path:
    """Remember *path* (a presentation folder) at the top of the recents list."""
    resolved = Path(path).expanduser().resolve()
    data = load()
    recents = [str(resolved)] + [r for r in data.get("recents", []) if r != str(resolved)]
    data["recents"] = recents[:limit]
    save(data)
    return resolved


def set_root(path: str | Path) -> Path:
    root = Path(path).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    data = load()
    data["root"] = str(root)
    save(data)
    return root

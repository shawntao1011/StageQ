from __future__ import annotations

import os
from pathlib import Path

def _looks_like_stageq_root(path: Path) -> bool:
    return (path / "config").is_dir() and (path / "src" / "stageq").is_dir()

def root_dir() -> Path:
    stageq_home = os.environ.get("STAGEQ_HOME")
    if stageq_home:
        return Path(stageq_home).expanduser().resolve()

    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if _looks_like_stageq_root(candidate):
            return candidate


    return Path(__file__).resolve().parents[3]

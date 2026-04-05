from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_pid(path: Path, pid: int) -> None:
    write_text(path, f"{pid}\n")


def read_pid(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def is_pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def spawn_process(
    argv: list[str],
    cwd: Path,
    env: dict[str, str],
    log_file: Path,
) -> int:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("ab") as f:
        proc = subprocess.Popen(
            argv,
            cwd=str(cwd),
            env=env,
            stdout=f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return proc.pid


def stop_pid(pid: int) -> None:
    os.kill(pid, signal.SIGTERM)
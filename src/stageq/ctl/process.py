from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
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

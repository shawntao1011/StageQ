from __future__ import annotations

import os
import shlex
from pathlib import Path

from stageq.codec.q_config import write_config_q
from stageq.codec.q_runtime import build_q_bootstrap_argv
from stageq.ctl.fsops import ensure_dirs, read_pid, write_pid, write_text
from stageq.ctl.process import is_pid_running, spawn_process, stop_pid
from stageq.ctl.resolver import resolve_service_config
from stageq.model.runtime import QRuntimeConfig


def _runtime_home(root_dir: Path, service_name: str, env_name: str) -> Path:
    return root_dir / "var" / "runtime" / env_name / service_name


def _find_pid_file(root_dir: Path, service_name: str, env_name: str | None = None) -> Path | None:
    runtime_root = root_dir / "var" / "runtime"
    if env_name is not None:
        candidate = runtime_root / env_name / service_name / "service.pid"
        return candidate if candidate.exists() else None

    candidates = sorted(runtime_root.glob(f"*/{service_name}/service.pid"))
    if not candidates:
        return None
    if len(candidates) > 1:
        locations = ", ".join(str(p) for p in candidates)
        raise RuntimeError(f"multiple runtime homes matched for {service_name}: {locations}")
    return candidates[0]


def _service_files(root_dir: Path, service_name: str, env_name: str) -> dict[str, Path]:
    runtime_home = _runtime_home(root_dir, service_name, env_name)
    return {
        "runtime_home": runtime_home,
        "config_q": runtime_home / "config.q",
        "pid": runtime_home / "service.pid",
        "log": runtime_home / "service.log",
        "cmdline": runtime_home / "cmdline",
    }


def _build_process_env(cfg) -> dict[str, str]:
    env = dict(os.environ)
    env.update(cfg.launch.env)
    return env


def launch_service(root_dir: Path, service_name: str, env_name: str) -> int:
    cfg = resolve_service_config(root_dir, service_name, env_name)
    files = _service_files(root_dir, service_name, env_name)

    ensure_dirs(files["runtime_home"])

    existing_pid = read_pid(files["pid"])
    if existing_pid and is_pid_running(existing_pid):
        raise RuntimeError(f"service {service_name} already running with pid {existing_pid}")

    write_config_q(cfg, out=files["config_q"])

    if not isinstance(cfg.runtime, QRuntimeConfig):
        raise NotImplementedError(f"runtime {cfg.runtime.kind!r} not implemented yet")
    assert cfg.runtime.bootstrap is not None

    argv = build_q_bootstrap_argv(
        q_executable=cfg.launch.executable,
        bootstrap_file=cfg.runtime.bootstrap.entry_file,
        runtime_options=cfg.runtime.startup_options,
    )

    env = _build_process_env(cfg)
    write_text(files["cmdline"], shlex.join(argv) + "\n")

    pid = spawn_process(argv=argv, cwd=files["runtime_home"], env=env, log_file=files["log"])
    write_pid(files["pid"], pid)
    return pid


def stop_service(root_dir: Path, service_name: str, env_name: str | None = None) -> bool:
    pid_file = _find_pid_file(root_dir, service_name, env_name)
    if pid_file is None:
        return False
    pid = read_pid(pid_file)
    if pid is None or not is_pid_running(pid):
        return False

    stop_pid(pid)
    return True


def service_status(root_dir: Path, service_name: str, env_name: str | None = None) -> tuple[bool, int | None]:
    pid_file = _find_pid_file(root_dir, service_name, env_name)
    if pid_file is None:
        return False, None
    pid = read_pid(pid_file)
    if pid is None:
        return False, None
    return is_pid_running(pid), pid

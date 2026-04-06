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


def _service_files(root_dir: Path, service_name: str) -> dict[str, Path]:
    return {
        "pid": root_dir / "var" / "run" / f"{service_name}.pid",
        "log": root_dir / "var" / "log" / f"{service_name}.log",
        "cmdline": root_dir / "var" / "generated" / f"{service_name}.cmdline",
    }


def _build_process_env(cfg) -> dict[str, str]:
    env = dict(os.environ)
    env.update(cfg.launch.env)
    env["QHOME"] = str(cfg.launch.working_dir)
    env["STAGEQ_SERVICE_NAME"] = cfg.identity.name
    env["STAGEQ_SERVICE_TYPE"] = cfg.identity.service_type
    env["STAGEQ_ENV"] = cfg.identity.env_name
    if cfg.identity.instance_id:
        env["STAGEQ_INSTANCE_ID"] = cfg.identity.instance_id
    return env


def launch_service(root_dir: Path, service_name: str, env_name: str) -> int:
    cfg = resolve_service_config(root_dir, service_name, env_name)
    files = _service_files(root_dir, service_name)

    ensure_dirs(cfg.launch.log_dir, cfg.launch.run_dir, cfg.launch.generated_dir)

    existing_pid = read_pid(files["pid"])
    if existing_pid and is_pid_running(existing_pid):
        raise RuntimeError(f"service {service_name} already running with pid {existing_pid}")

    config_q_file = write_config_q(cfg)

    if not isinstance(cfg.runtime, QRuntimeConfig):
        raise NotImplementedError(f"runtime {cfg.runtime.kind!r} not implemented yet")
    assert cfg.runtime.bootstrap is not None

    bootstrap_args = ["-name", cfg.identity.name, "-env", cfg.identity.env_name, "-config", str(config_q_file)]
    argv = build_q_bootstrap_argv(
        q_executable=cfg.launch.executable,
        bootstrap_file=cfg.runtime.bootstrap.entry_file,
        runtime_options=cfg.runtime.startup_options,
        bootstrap_args=bootstrap_args,
    )

    env = _build_process_env(cfg)
    write_text(files["cmdline"], shlex.join(argv) + "\n")

    pid = spawn_process(argv=argv, cwd=cfg.launch.working_dir, env=env, log_file=files["log"])
    write_pid(files["pid"], pid)
    return pid


def stop_service(root_dir: Path, service_name: str) -> bool:
    pid_file = _service_files(root_dir, service_name)["pid"]
    pid = read_pid(pid_file)
    if pid is None or not is_pid_running(pid):
        return False

    stop_pid(pid)
    return True


def service_status(root_dir: Path, service_name: str) -> tuple[bool, int | None]:
    pid_file = _service_files(root_dir, service_name)["pid"]
    pid = read_pid(pid_file)
    if pid is None:
        return False, None
    return is_pid_running(pid), pid

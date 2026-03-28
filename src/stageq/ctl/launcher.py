from __future__ import annotations

import os
import shlex
from pathlib import Path

from stageq.ctl.process import (
    ensure_dirs,
    is_pid_running,
    read_pid,
    spawn_process,
    write_pid,
    write_text,
)
from stageq.ctl.qrender import write_config_q
from stageq.ctl.resolver import resolve_service_config


def _service_files(root_dir: Path, service_name: str) -> dict[str, Path]:
    return {
        "pid": root_dir / "var" / "run" / f"{service_name}.pid",
        "log": root_dir / "var" / "log" / f"{service_name}.log",
        "cmdline": root_dir / "var" / "generated" / f"{service_name}.cmdline",
    }


def _build_q_argv(cfg, config_q_file: Path) -> list[str]:
    argv = [
        cfg.launch.q_executable,
        str(cfg.launch.bootstrap),
    ]

    qr = cfg.q_runtime

    if qr.quiet:
        argv.append("-q")
    if qr.port is not None:
        argv += ["-p", str(qr.port)]
    if qr.secondary_threads is not None:
        argv += ["-s", str(qr.secondary_threads)]
    if qr.timer_ticks is not None:
        argv += ["-t", str(qr.timer_ticks)]
    if qr.workspace is not None:
        argv += ["-w", str(qr.workspace)]
    if qr.timeout is not None:
        argv += ["-T", str(qr.timeout)]
    if qr.utc_offset is not None:
        argv += ["-o", str(qr.utc_offset)]
    if qr.http_size is not None:
        argv += ["-C", str(qr.http_size)]
    if qr.user_password_file is not None:
        argv += ["-U", str(qr.user_password_file)]
    if qr.tls_mode:
        argv.append("-E")

    argv += [
        "--",
        "-service", cfg.identity.name,
        "-env", cfg.identity.env_name,
        "-config", str(config_q_file),
    ]
    return argv


def _build_process_env(cfg) -> dict[str, str]:
    env = dict(os.environ)
    env["QHOME"] = str(cfg.launch.q_home)
    env["STAGEQ_SERVICE_NAME"] = cfg.identity.name
    env["STAGEQ_SERVICE_TYPE"] = cfg.identity.service_type
    env["STAGEQ_ENV"] = cfg.identity.env_name
    return env


def launch_service(root_dir: Path, service_name: str, env_name: str) -> int:
    cfg = resolve_service_config(root_dir, service_name, env_name)
    files = _service_files(root_dir, service_name)

    ensure_dirs(cfg.launch.log_dir, cfg.launch.run_dir, cfg.launch.generated_dir)

    existing_pid = read_pid(files["pid"])
    if existing_pid and is_pid_running(existing_pid):
        raise RuntimeError(f"{service_name} already running with pid {existing_pid}")

    config_q_file = write_config_q(cfg)
    argv = _build_q_argv(cfg, config_q_file)
    env = _build_process_env(cfg)

    write_text(files["cmdline"], shlex.join(argv) + "\n")

    pid = spawn_process(
        argv=argv,
        cwd=cfg.launch.q_home,
        env=env,
        log_file=files["log"],
    )

    write_pid(files["pid"], pid)
    return pid
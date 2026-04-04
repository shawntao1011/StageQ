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
from stageq.ctl.runtime.q_argv import build_q_bootstrap_argv


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

    if cfg.runtime.kind == "q":
        assert cfg.runtime.bootstrap is not None

        bootstrap_args = [
            "-name", cfg.identity.name,
            "-env", cfg.identity.env_name,
            "-config", str(config_q_file),
        ]

        argv = build_q_bootstrap_argv(
            q_executable=cfg.launch.executable,
            bootstrap_file=cfg.runtime.bootstrap.entry_file,
            runtime_options=cfg.runtime.options,
            bootstrap_args=bootstrap_args,
        )
    else:
        raise NotImplementedError(f"runtime kind {cfg.runtime.kind!r} not implemented yet")

    env = _build_process_env(cfg)

    write_text(files["cmdline"], shlex.join(argv) + "\n")

    pid = spawn_process(
        argv=argv,
        cwd=cfg.launch.working_dir,
        env=env,
        log_file=files["log"],
    )
    write_pid(files["pid"], pid)
    return pid
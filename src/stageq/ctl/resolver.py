from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from stageq.model.service import (
    LaunchConfig,
    QConfig,
    QRuntimeConfig,
    ResolvedServiceConfig,
    ServiceIdentity,
)

def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def resolve_service_config(
        root_dir: Path,
        service_name: str,
        env_name: str,
) -> ResolvedServiceConfig:
    env_path = root_dir / "config" / "environments" / f"{env_name}.yaml"
    svc_path = root_dir / "config" / "services" / f"{service_name}.yaml"

    env_cfg = _read_yaml(env_path)
    svc_cfg = _read_yaml(svc_path)

    launch_defaults = env_cfg.get("launch_defaults", {})
    service = svc_cfg.get("service", {})
    paths = svc_cfg.get("paths", {})
    q_runtime = svc_cfg.get("q_runtime", {})
    q_cfg = svc_cfg.get("q", {})
    service_config = svc_cfg.get("service_config", {})

    identity = ServiceIdentity(
        name=service["name"],
        service_type=service["type"],
        runtime=service["runtime"],
        env_name=env_cfg["env_name"],
    )

    launch = LaunchConfig(
        q_executable=launch_defaults.get("q_executable", "q"),
        q_home=(root_dir / launch_defaults.get("q_home", ".")).resolve(),
        log_dir=(root_dir / launch_defaults.get("log_dir", "var/log")).resolve(),
        run_dir=(root_dir / launch_defaults.get("run_dir", "var/run")).resolve(),
        generated_dir=(root_dir / launch_defaults.get("generated_dir", "var/generated")).resolve(),
        bootstrap=(root_dir / paths["bootstrap"]).resolve(),
    )

    qrt = QRuntimeConfig(
        quiet=bool(q_runtime.get("quiet", False)),
        port=q_runtime.get("port"),
        secondary_threads=q_runtime.get("secondary_threads"),
        timer_ticks=q_runtime.get("timer_ticks"),
        workspace=q_runtime.get("workspace"),
        timeout=q_runtime.get("timeout"),
        utc_offset=q_runtime.get("utc_offset"),
        http_size=q_runtime.get("http_size"),
        user_password_file=q_runtime.get("user_password_file"),
        tls_mode=bool(q_runtime.get("tls_mode", False)),
    )

    q = QConfig(
        libraries=[(root_dir / p).resolve() for p in q_cfg.get("libraries", [])]
    )

    return ResolvedServiceConfig(
        identity=identity,
        launch=launch,
        q_runtime=qrt,
        q=q,
        service_config=service_config,
    )
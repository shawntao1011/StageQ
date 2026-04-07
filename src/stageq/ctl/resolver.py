from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from stageq.codec.q_runtime import merge_q_runtime_options, q_runtime_options_from_dict
from stageq.model.runtime import Q_RUNTIME_DEFAULTS_FOR_SERVICE, QBootstrapConfig, QRuntimeConfig
from stageq.model.service import ProcessLaunchConfig, ResolvedServiceConfig, ServiceIdentity


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolve_path(root_dir: Path, raw: str) -> Path:
    return (root_dir / raw).resolve()


def resolve_service_config(root_dir: Path, service_name: str, env_name: str) -> ResolvedServiceConfig:
    env_path = root_dir / "config" / "environments" / f"{env_name}.yaml"
    svc_path = root_dir / "config" / "services" / f"{service_name}.yaml"

    env_cfg = _read_yaml(env_path)
    svc_cfg = _read_yaml(svc_path)

    launch_defaults = env_cfg.get("launch_defaults", {})
    service = svc_cfg.get("service", {})
    runtime = svc_cfg.get("runtime", {})
    launch_cfg = svc_cfg.get("launch", {})
    q_runtime_cfg = svc_cfg.get("q_runtime", {})
    service_config = svc_cfg.get("service_config", {})

    identity = ServiceIdentity(
        name=service["name"],
        service_type=service["type"],
        env_name=env_cfg["env_name"],
        instance_id=service.get("instance_id"),
    )

    launch = ProcessLaunchConfig(
        executable=launch_cfg.get("executable", launch_defaults.get("executable", "q")),
        working_dir=_resolve_path(root_dir, launch_cfg.get("working_dir", launch_defaults.get("working_dir", "."))),
    )

    runtime_kind = runtime["kind"]
    if runtime_kind != "q":
        raise NotImplementedError(f"runtime kind {runtime_kind!r} not implemented yet")

    env_defaults = q_runtime_options_from_dict(env_cfg.get("q_runtime_defaults"))
    instance_overrides = q_runtime_options_from_dict(q_runtime_cfg.get("options"))
    resolved_q_options = merge_q_runtime_options(Q_RUNTIME_DEFAULTS_FOR_SERVICE, env_defaults, instance_overrides)

    resolved_runtime = QRuntimeConfig(
        startup_options=resolved_q_options,
        bootstrap=QBootstrapConfig(
            entry_file=_resolve_path(root_dir, q_runtime_cfg["bootstrap"]),
            libraries=[_resolve_path(root_dir, p) for p in q_runtime_cfg.get("libraries", [])],
        ),
    )

    cfg = ResolvedServiceConfig(identity=identity, launch=launch, runtime=resolved_runtime, service_config=service_config)
    cfg.validate()
    return cfg

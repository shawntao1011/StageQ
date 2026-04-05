from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from stageq.ctl.runtime.q_options import (
    merge_q_runtime_options,
    q_runtime_options_from_dict,
)
from stageq.ctl.runtime.q_profiles import SERVICE_Q_PROFILE
from stageq.model.common import (
    ProcessLaunchConfig,
    QBootstrapConfig,
    QServiceRuntimeConfig,
)
from stageq.model.service import ResolvedServiceConfig, ServiceIdentity


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolve_path(root_dir: Path, raw: str) -> Path:
    return (root_dir / raw).resolve()


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
        working_dir=_resolve_path(
            root_dir,
            launch_cfg.get("working_dir", launch_defaults.get("working_dir", "."))
        ),
        log_dir=_resolve_path(
            root_dir,
            launch_cfg.get("log_dir", launch_defaults.get("log_dir", "var/log"))
        ),
        run_dir=_resolve_path(
            root_dir,
            launch_cfg.get("run_dir", launch_defaults.get("run_dir", "var/run"))
        ),
        generated_dir=_resolve_path(
            root_dir,
            launch_cfg.get("generated_dir", launch_defaults.get("generated_dir", "var/generated"))
        ),
    )

    runtime_kind = runtime["kind"]

    if runtime_kind == "q":
        # Merge order:
        # q intrinsic defaults
        #   < workload defaults (SERVICE_Q_PROFILE)
        #   < environment defaults (env_cfg["q_runtime_defaults"])
        #   < instance overrides (svc_cfg["q_runtime"]["options"])
        #
        # q intrinsic defaults are represented implicitly:
        # if a field remains None, it is omitted from argv and q uses its native default.

        workload_defaults = SERVICE_Q_PROFILE.options
        env_defaults = q_runtime_options_from_dict(env_cfg.get("q_runtime_defaults"))
        instance_overrides = q_runtime_options_from_dict(
            q_runtime_cfg.get("options")
        )

        resolved_q_options = merge_q_runtime_options(
            workload_defaults,
            env_defaults,
            instance_overrides,
        )

        resolved_runtime = QServiceRuntimeConfig(
            startup_options=resolved_q_options,
            bootstrap=QBootstrapConfig(
                entry_file=_resolve_path(root_dir, q_runtime_cfg["bootstrap"]),
                libraries=[
                    _resolve_path(root_dir, p)
                    for p in q_runtime_cfg.get("libraries", [])
                ],
            ),
        )

        cfg = ResolvedServiceConfig(
            identity=identity,
            launch=launch,
            runtime=resolved_runtime,
            service_config=service_config,
        )
        cfg.validate()
        return cfg

    raise NotImplementedError(f"runtime kind {runtime_kind!r} not implemented yet")
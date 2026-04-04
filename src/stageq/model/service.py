from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from stageq.model.common import ProcessLaunchConfig, ServiceRuntimeConfig

@dataclass(frozen=True)
class ServiceIdentity:
    """
    Stable identity for a long-running service instance.
    """

    name: str
    # Full instance name, e.g. "hdb.hk"

    service_type: str
    # Logical role, e.g. "hdb"

    env_name: str
    # e.g. "dev", "prod"

    instance_id: str | None = None
    # e.g. "hk"


@dataclass
class ResolvedServiceConfig:
    """
    Final resolved model for a long-running service.
    """

    identity: ServiceIdentity
    launch: ProcessLaunchConfig
    runtime: ServiceRuntimeConfig
    service_config: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.runtime.kind == "q":
            if self.runtime.bootstrap is None:
                raise ValueError("q runtime requires bootstrap")
            return

        if self.runtime.kind == "python":
            if self.runtime.module is None and self.runtime.script is None:
                raise ValueError("python runtime requires module or script")
            return

        if self.runtime.kind == "cpp":
            if self.runtime.binary is None:
                raise ValueError("cpp runtime requires binary")
            return

        raise ValueError(f"unknown runtime kind: {self.runtime.kind!r}")
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from stageq.model.runtime import RuntimeConfig


@dataclass(frozen=True)
class ServiceIdentity:
    name: str
    service_type: str
    env_name: str
    instance_id: str | None = None


@dataclass
class ProcessLaunchConfig:
    executable: str
    working_dir: Path
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class ResolvedServiceConfig:
    identity: ServiceIdentity
    launch: ProcessLaunchConfig
    runtime: RuntimeConfig
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

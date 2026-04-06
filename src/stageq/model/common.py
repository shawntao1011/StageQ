from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias

from stageq.model.q_runtime_options import QRuntimeOptions

RuntimeKind = Literal["q", "python", "cpp"]

@dataclass
class ProcessLaunchConfig:
    """
    Generic OS/process-level launch settings.

    This layer is runtime-agnostic. It describes how StageQ hosts the process
    at OS level, regardless of whether the runtime is q/python/cpp.
    """

    executable: str
    working_dir: Path
    log_dir: Path
    run_dir: Path
    generated_dir: Path
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class QBootstrapConfig:
    """
    StageQ-specific q bootstrap entry definition.

    This is NOT a q executable flag. It describes the entry q script used by
    StageQ to enter q world after process startup.
    """

    entry_file: Path
    libraries: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class QServiceRuntimeConfig:
    """
    q runtime config for service-style workloads.
    """

    kind: Literal["q"] = "q"
    startup_options: QRuntimeOptions = field(default_factory=QRuntimeOptions)
    bootstrap: QBootstrapConfig | None = None


@dataclass(frozen=True)
class PythonServiceRuntimeConfig:
    """
    Placeholder for Python-hosted services.
    """

    kind: Literal["python"] = "python"
    module: str | None = None
    script: Path | None = None


@dataclass(frozen=True)
class CppServiceRuntimeConfig:
    """
    Placeholder for native-binary-hosted services.
    """

    kind: Literal["cpp"] = "cpp"
    binary: Path | None = None


ServiceRuntimeConfig: TypeAlias = (
    QServiceRuntimeConfig
    | PythonServiceRuntimeConfig
    | CppServiceRuntimeConfig
)
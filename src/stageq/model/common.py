from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias


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


@dataclass
class QRuntimeOptions:
    """
    Final q executable startup option values.

    Every field defaults to None:
      - None  : this layer does not specify a value
      - value : this layer explicitly specifies a value

    This object is used both as:
      - a partial overlay
      - a final resolved result

    IMPORTANT:
    Only q executable-level startup flags belong here.
    """

    blocked: bool | None = None                     # -b
    console_size: tuple[int, int] | None = None     # -c
    http_size: tuple[int, int] | None = None        # -C
    error_traps: int | None = None                  # -e
    tls_mode: int | None = None                     # -E
    garbage_collection: int | None = None           # -g
    log_updates: bool | None = None                 # -l
    log_sync: bool | None = None                    # -L
    memory_domain: int | None = None                # -m
    utc_offset: int | None = None                   # -o
    port: int | None = None                         # -p
    display_precision: int | None = None            # -P
    quiet: bool | None = None                       # -q
    secondary_threads: int | None = None            # -s
    random_seed: int | None = None                  # -S
    timer_ticks: int | None = None                  # -t
    timeout: int | None = None                      # -T
    disable_syscmds: bool | None = None             # -u
    user_password_file: str | None = None           # -U
    workspace: int | None = None                    # -w
    start_week: int | None = None                   # -W
    date_format: int | None = None                  # -z


@dataclass(frozen=True)
class QBootstrapSpec:
    """
    StageQ-specific q bootstrap entry definition.

    This is NOT a q executable flag. It describes the entry q script used by
    StageQ to enter q world after process startup.
    """

    entry_file: Path


@dataclass(frozen=True)
class QServiceRuntimeConfig:
    """
    q runtime config for service-style workloads.
    """

    kind: Literal["q"] = "q"
    bootstrap: QBootstrapSpec | None = None
    libraries: list[Path] = field(default_factory=list)
    options: QRuntimeOptions = field(default_factory=QRuntimeOptions)


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
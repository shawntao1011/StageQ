from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


# ============================================================================
# Runtime kind
# ============================================================================
# RuntimeKind answers:
#   "Which runtime is used to host this workload?"
#
# This is intentionally shared by both services and jobs.
#
# Examples:
#   - "q"      : q process / q script
#   - "python" : python module or script
#   - "cpp"    : native binary
#
# Keep this small and stable. Do not put workload type here.
RuntimeKind = Literal["q", "python", "cpp"]


# ============================================================================
# Generic process launch config
# ============================================================================
@dataclass
class ProcessLaunchConfig:
    """
    Generic OS/process-level launch settings.

    This is the shared launch model for both:
    - long-running services
    - short-lived jobs

    It describes how StageQ should host a process at the OS level,
    independent of runtime semantics.

    What belongs here
    -----------------
    - executable path/name
    - working directory
    - output directories (log/run/generated)
    - generic extra argv
    - generic extra env

    What does NOT belong here
    -------------------------
    Runtime-specific semantics should not be stored here, for example:
    - q -p/-s/-t flags
    - q bootstrap path / q libraries
    - python module entrypoint
    - binary-specific command protocol

    Those belong to runtime-specific spec objects.
    """

    executable: str
    # OS executable used to start the process.
    # Examples:
    #   "q"
    #   "/opt/kx/q/l64/q"
    #   "python"
    #   "/opt/stageq/bin/sorter"

    working_dir: Path
    # Process working directory (cwd).

    log_dir: Path
    # Directory for logs.

    run_dir: Path
    # Directory for runtime state files such as pid / lock / socket.

    generated_dir: Path
    # Directory for rendered artifacts such as:
    #   - config.q
    #   - cmdline snapshots
    #   - future systemd / consul payloads

    args: list[str] = field(default_factory=list)
    # Generic extra process arguments.
    # Use sparingly. Prefer typed runtime fields whenever possible.

    env: dict[str, str] = field(default_factory=dict)
    # Generic extra process environment.
    # Good for small metadata or integration hints.
    # Not recommended as the primary transport for complex config.


# ============================================================================
# q runtime options
# ============================================================================
@dataclass
class QRuntimeOptions:
    """
    Typed q executable startup flags.

    These map to:
        q [file] [-option [parameters] ...]

    These options MUST be translated into argv before q starts.

    This model is shared by:
    - q services
    - q jobs

    Why shared
    ----------
    Because the q executable startup semantics are the same regardless of
    whether the workload is a long-running daemon or a short-lived batch job.
    """

    quiet: bool = False
    # -q

    port: int | None = None
    # -p
    # Usually meaningful for q services.
    # For q jobs this is often None.

    secondary_threads: int | None = None
    # -s

    timer_ticks: int | None = None
    # -t

    workspace: str | None = None
    # -w

    timeout: int | None = None
    # -T

    utc_offset: int | None = None
    # -o

    http_size: int | None = None
    # -C

    user_password_file: str | None = None
    # -U

    tls_mode: bool = False
    # -E


# ============================================================================
# q runtime spec
# ============================================================================
@dataclass
class QRuntimeSpec:
    """
    q-specific startup spec shared by q-based workloads.

    This groups together:
    - bootstrap / entry q script
    - ordered q library list
    - q startup flags

    Shared by:
    - q services
    - q jobs

    Why this is shared
    ------------------
    The mechanism "start q -> enter bootstrap -> load libs -> call entrypoint"
    can be used for both daemon and batch styles. What differs is the workload
    model around it (service vs job), not the q runtime mechanics themselves.
    """

    bootstrap: Path
    # q-side bootstrap entry file.

    libraries: list[Path] = field(default_factory=list)
    # Ordered q libraries to load.
    # Order matters.

    options: QRuntimeOptions = field(default_factory=QRuntimeOptions)
    # q executable startup flags.


# ============================================================================
# Python runtime spec
# ============================================================================
@dataclass
class PythonRuntimeSpec:
    """
    Python-specific runtime spec.

    Can be used by both services and jobs.

    This is currently a structural placeholder so the model stays runtime-clean.
    """

    module: str | None = None
    # e.g. "stageq.agent.main"

    script: Path | None = None
    # e.g. Path("src/stageq/agent/main.py")


# ============================================================================
# C++ runtime spec
# ============================================================================
@dataclass
class CppRuntimeSpec:
    """
    Native binary runtime spec.

    Can be used by both services and jobs.
    """

    binary: Path | None = None
    # Native executable path.


# ============================================================================
# Validation helpers
# ============================================================================
def validate_runtime_binding(
    runtime_kind: RuntimeKind,
    q_runtime: QRuntimeSpec | None,
    python_runtime: PythonRuntimeSpec | None,
    cpp_runtime: CppRuntimeSpec | None,
) -> None:
    """
    Ensure that exactly one runtime spec matches the declared runtime_kind.

    Expected combinations:
      runtime_kind == "q"      -> q_runtime is set
      runtime_kind == "python" -> python_runtime is set
      runtime_kind == "cpp"    -> cpp_runtime is set
    """
    bindings = {
        "q": q_runtime is not None,
        "python": python_runtime is not None,
        "cpp": cpp_runtime is not None,
    }

    active_count = sum(1 for v in bindings.values() if v)
    if active_count != 1:
        raise ValueError(
            "Exactly one runtime spec must be set; "
            f"got q={bindings['q']}, python={bindings['python']}, cpp={bindings['cpp']}"
        )

    if not bindings[runtime_kind]:
        raise ValueError(
            f"runtime_kind={runtime_kind!r} does not match provided runtime spec bindings "
            f"{bindings}"
        )
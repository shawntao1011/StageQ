from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Any
from pathlib import Path

ConfigScope = Literal["q_executable", "bootstrap", "service_config"]

ArgKind = Literal["flag", "scalar", "multi"]

ApplyMode = Literal["requires_restart", "hot_reloadable", "runtime_mutable"]

@dataclass(frozen=True)
class QConfigSpec:
    """
    Metadata for one StageQ-managed q-related config item.

    scope:
      - q_executable : q command-line startup options
      - bootstrap    : bootstrap/load-layer config
      - service_config : service internal config

    apply_mode:
      - requires_restart : change needs process restart
      - hot_reloadable   : can be reloaded without full restart
      - runtime_mutable  : can be changed live via control path
    """
    name: str
    scope: ConfigScope
    arg_kind: ArgKind
    cli_flag: str | None
    schema: Any | None
    apply_mode: ApplyMode
    description: str


Q_CONFIG_SPECS: dict[str, QConfigSpec] = {
    # ----------------------------------------------------------------------
    # Q EXECUTABLE OPTIONS
    # ----------------------------------------------------------------------
    # q process startup flags (mapped to q CLI arguments)
    # e.g.
    #   q -b -p 9001 -e 1 -c 40 120
    #
    # Characteristics:
    # - Applied at process start
    # - Immutable after launch
    # - Direct 1:1 mapping to q CLI flags
    # ----------------------------------------------------------------------
    "blocked": QConfigSpec(
        name="blocked",
        scope="q_executable",
        arg_kind="flag",
        cli_flag="-b",
        schema=bool,
        apply_mode="requires_restart",
        description="Blocked mode",
    ),
    "console_size": QConfigSpec(
        name="console_size",
        scope="q_executable",
        arg_kind="multi",
        cli_flag="-c",
        schema=tuple[int, int],
        apply_mode="runtime_mutable",
        description="Console size (rows, cols), e.g. -c 40 120",
    ),
    "http_size": QConfigSpec(
        name="http_size",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-C",
        schema=tuple[int, int],
        apply_mode="runtime_mutable",
        description="HTTP size (rows, cols), e.g. -c 40 120",
    ),
    "error_traps": QConfigSpec(
        name="error_traps",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-e",
        schema=Literal[0, 1, 2],
        apply_mode="requires_restart",
        description="Error trapping mode (0=off, 1=some, 2=all)",
    ),
    "tls_mode": QConfigSpec(
        name="tls_mode",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-E",
        schema=Literal[0, 1, 2],
        apply_mode="requires_restart",
        description="TLS server mode (0=plain, 1=plain+TLS, 2=TLS only)",
    ),
    "garbage_collection": QConfigSpec(
        name="garbage_collection",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-g",
        schema=Literal[0, 1],
        apply_mode="requires_restart",
        description="Garbage collection mode (0=deferred, 1=immediate)",
    ),
    "log_updates": QConfigSpec(
        name="log_updates",
        scope="q_executable",
        arg_kind="flag",
        cli_flag="-l",
        schema=bool,
        apply_mode="requires_restart",
        description="Log updates to filesystem (-l)",
    ),
    "log_sync": QConfigSpec(
        name="log_sync",
        scope="q_executable",
        arg_kind="flag",
        cli_flag="-L",
        schema=bool,
        apply_mode="requires_restart",
        description="Log updates with sync (-L)",
    ),
    "memory_domain_path": QConfigSpec(
        name="memory_domain_path",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-m",
        schema=Path | str,
        apply_mode="requires_restart",
        description="Filesystem-backed memory domain path (-m path)",
    ),
    "utc_offset": QConfigSpec(
        name="utc_offset",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-o",
        schema=int,
        apply_mode="hot_reloadable",
        description="UTC offset",
    ),
    "port": QConfigSpec(
        name="port",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-p",
        schema=int,
        apply_mode="hot_reloadable",
        description="Listening port",
    ),
    "display_precision": QConfigSpec(
        name="display_precision",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-P",
        schema=int,
        apply_mode="hot_reloadable",
        description="Display precision for floating-point numbers (number of digits)",
    ),
    "quiet": QConfigSpec(
        name="quiet",
        scope="q_executable",
        arg_kind="flag",
        cli_flag="-q",
        schema=bool,
        apply_mode="requires_restart",
        description="Quiet mode",
    ),
    "secondary_threads": QConfigSpec(
        name="secondary_threads",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-s",
        schema=int,
        apply_mode="requires_restart",
        description="Secondary threads (positive N), Secondary processes (negative N)",
    ),
    "random_seed": QConfigSpec(
        name="random_seed",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-S",
        schema=int,
        apply_mode="hot_reloadable",
        description="Random seed value (-S N)",
    ),
    "timer_ticks": QConfigSpec(
        name="timer_ticks",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-t",
        schema=int,
        apply_mode="hot_reloadable",
        description="Timer ticks, in milliseconds",
    ),
    "timeout": QConfigSpec(
        name="timeout",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-T",
        schema=int,
        apply_mode="hot_reloadable",
        description="Timeout, in seconds",
    ),
    "disable_syscmds": QConfigSpec(
        name="disable_syscmds",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-u",
        schema=int | str,
        apply_mode="requires_restart",
        description="Disable syscmds or set local user/password file (-u 1 | -u file)",
    ),
    "user_password_file": QConfigSpec(
        name="user_password_file",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-U",
        schema=Path | str,
        apply_mode="requires_restart",
        description="Set user/password file and block \\x (-U file)",
    ),
    "workspace": QConfigSpec(
        name="workspace",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-w",
        schema=int,
        apply_mode="requires_restart",
        description="Workspace limit in MB (0 = no limit)",
    ),
    "start_week": QConfigSpec(
        name="start_week",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-W",
        schema=Literal[0, 1, 2, 3, 4, 5, 6],
        apply_mode="requires_restart",
        description="Start-of-week offset (0=Sat, 1=Sun, ..., 6=Fri; default=2 Mon)",
    ),
    "date_format": QConfigSpec(
        name="date_format",
        scope="q_executable",
        arg_kind="scalar",
        cli_flag="-z",
        schema=Literal[0, 1],
        apply_mode="requires_restart",
        description="Date parsing format (0=mm/dd/yyyy, 1=dd/mm/yyyy; default=0)",
    ),

    # ----------------------------------------------------------------------
    # BOOTSTRAP LAYER
    # ----------------------------------------------------------------------
    # q process initialization after startup
    # e.g.
    #   \l init.q
    #   \l lib1.q
    #   \l lib2.q
    #
    # Characteristics:
    # - Executed after q process starts
    # - Defines runtime environment (libraries, setup scripts)
    # - Not part of CLI flags
    # ----------------------------------------------------------------------
    "bootstrap_entry": QConfigSpec(
        name="bootstrap_entry",
        scope="bootstrap",
        arg_kind="scalar",
        cli_flag=None,
        schema=Path,
        apply_mode="requires_restart",
        description="Bootstrap entry .q file",
    ),
    "libraries": QConfigSpec(
        name="libraries",
        scope="bootstrap",
        arg_kind="multi",
        cli_flag=None,
        schema=list[Path],
        apply_mode="requires_restart",
        description="Ordered q library load list",
    ),

    # ----------------------------------------------------------------------
    # SERVICE CONFIG
    # ----------------------------------------------------------------------
    # Service-level configuration (application / business logic)
    #
    # Examples:
    # - ports / endpoints
    # - data paths
    # - environment settings
    #
    # Characteristics:
    # - Not q runtime flags
    # - Not bootstrap scripts
    # - Consumed by service logic (q / python / cpp)
    # ----------------------------------------------------------------------
}
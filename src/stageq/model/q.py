from dataclasses import dataclass, fields, field, asdict
from pathlib import Path
from typing import Literal, Any

@dataclass(frozen=True)
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
class QBootstrapConfig:
    entry_file: Path
    libraries: list[Path] = field(default_factory=list)

@dataclass(frozen=True)
class QServiceRuntimeConfig:
    kind: Literal["q"] = "q"
    startup_options: QRuntimeOptions = field(default_factory=QRuntimeOptions)
    bootstrap: QBootstrapConfig | None = None

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

@dataclass(frozen=True)
class QConfigSpec:
    name: str
    scope: ConfigScope
    arg_kind: ArgKind
    cli_flag: str | None
    value_type: str
    apply_mode: ApplyMode
    description: str

Q_RUNTIME_DEFAULTS_FOR_SERVICE = QRuntimeOptions(
    blocked=True,
    disable_syscmds=True,
)

Q_RUNTIME_DEFAULTS_FOR_JOB = QRuntimeOptions(
    quiet=True,
)

def merge_q_runtime_options(*layers: QRuntimeOptions) -> QRuntimeOptions:
    """
    Merge QRuntimeOptions layers from left to right.

    Later non-None values override earlier values.
    """
    result = QRuntimeOptions()

    for layer in layers:
        for f in fields(QRuntimeOptions):
            value = getattr(layer, f.name)
            if value is not None:
                setattr(result, f.name, value)

    return result


def q_runtime_options_from_dict(raw: dict[str, Any] | None) -> QRuntimeOptions:
    """
    Convert plain dict into QRuntimeOptions.

    Unknown keys raise ValueError.
    """
    if raw is None:
        return QRuntimeOptions()

    valid_fields = {f.name for f in fields(QRuntimeOptions)}
    unknown = set(raw) - valid_fields
    if unknown:
        raise ValueError(f"Unknown q runtime option keys: {sorted(unknown)}")

    return QRuntimeOptions(**raw)


def q_runtime_options_to_dict(options: QRuntimeOptions) -> dict[str, Any]:
    return asdict(options)


def compact_q_runtime_options(options: QRuntimeOptions) -> dict[str, Any]:
    raw = asdict(options)
    return {k: v for k, v in raw.items() if v is not None}

def q_runtime_options_to_argv(options: QRuntimeOptions) -> list[str]:
    """
    Render final QRuntimeOptions into q argv flags.

    Rules:
    - None -> omit
    - flag option:
        True  -> emit
        False -> omit
    - value option:
        emit '-x value'
    """
    argv: list[str] = []

    for f in fields(QRuntimeOptions):
        name = f.name
        value = getattr(options, name)
        if value is None:
            continue

        spec = Q_CONFIG_SPECS[name]

        if spec.arg_kind == "flag":
            if value is True:
                argv.append(spec.cli_flag)  # type: ignore[arg-type]
            continue

        argv.extend([str(spec.cli_flag), str(value)])

    return argv


def build_q_bootstrap_argv(
    q_executable: str,
    bootstrap_file: Path,
    runtime_options: QRuntimeOptions,
    bootstrap_args: list[str] | None = None,
) -> list[str]:
    argv = [q_executable, str(bootstrap_file)]
    argv.extend(q_runtime_options_to_argv(runtime_options))

    if bootstrap_args:
        argv.append("--")
        argv.extend(bootstrap_args)

    return argv
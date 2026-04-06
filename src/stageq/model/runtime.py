from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, TypeAlias, get_args, get_origin
import types

RuntimeKind = Literal["q", "python", "cpp"]
ConfigScope = Literal["q_executable", "bootstrap", "service_config"]
ArgKind = Literal["flag", "scalar", "multi"]
ApplyMode = Literal["requires_restart", "hot_reloadable", "runtime_mutable"]


@dataclass(frozen=True)
class QRuntimeOptions:
    blocked: bool | None = None
    console_size: tuple[int, int] | None = None
    http_size: tuple[int, int] | None = None
    error_traps: Literal[0, 1, 2] | None = None
    tls_mode: Literal[0, 1, 2] | None = None
    garbage_collection: Literal[0, 1] | None = None
    log_updates: bool | None = None
    log_sync: bool | None = None
    memory_domain_path: Path | None = None
    utc_offset: int | None = None
    port: int | None = None
    display_precision: int | None = None
    quiet: bool | None = None
    secondary_threads: int | None = None
    random_seed: int | None = None
    timer_ticks: int | None = None
    timeout: int | None = None
    disable_syscmds: int | str | None = None
    user_password_file: Path | str | None = None
    workspace: int | None = None
    start_week: Literal[0, 1, 2, 3, 4, 5, 6] | None = None
    date_format: Literal[0, 1] | None = None


@dataclass(frozen=True)
class QConfigSpec:
    name: str
    scope: ConfigScope
    arg_kind: ArgKind
    cli_flag: str | None
    schema: Any | None
    apply_mode: ApplyMode
    description: str


Q_EXECUTABLE_OPTION_SPECS: dict[str, QConfigSpec] = {
    "blocked": QConfigSpec("blocked", "q_executable", "flag", "-b", bool, "requires_restart", "Blocked mode"),
    "console_size": QConfigSpec("console_size", "q_executable", "multi", "-c", tuple[int, int], "requires_restart", "Console size"),
    "http_size": QConfigSpec("http_size", "q_executable", "multi", "-C", tuple[int, int], "requires_restart", "HTTP size"),
    "error_traps": QConfigSpec("error_traps", "q_executable", "scalar", "-e", Literal[0, 1, 2], "requires_restart", "Error trapping mode"),
    "tls_mode": QConfigSpec("tls_mode", "q_executable", "scalar", "-E", Literal[0, 1, 2], "requires_restart", "TLS server mode"),
    "garbage_collection": QConfigSpec("garbage_collection", "q_executable", "scalar", "-g", Literal[0, 1], "requires_restart", "Garbage collection mode"),
    "log_updates": QConfigSpec("log_updates", "q_executable", "flag", "-l", bool, "requires_restart", "Log updates"),
    "log_sync": QConfigSpec("log_sync", "q_executable", "flag", "-L", bool, "requires_restart", "Log updates with sync"),
    "memory_domain_path": QConfigSpec("memory_domain_path", "q_executable", "scalar", "-m", Path | str, "requires_restart", "Memory domain path"),
    "utc_offset": QConfigSpec("utc_offset", "q_executable", "scalar", "-o", int, "requires_restart", "UTC offset"),
    "port": QConfigSpec("port", "q_executable", "scalar", "-p", int, "requires_restart", "Listening port"),
    "display_precision": QConfigSpec("display_precision", "q_executable", "scalar", "-P", int, "requires_restart", "Display precision"),
    "quiet": QConfigSpec("quiet", "q_executable", "flag", "-q", bool, "requires_restart", "Quiet mode"),
    "secondary_threads": QConfigSpec("secondary_threads", "q_executable", "scalar", "-s", int, "requires_restart", "Secondary threads"),
    "random_seed": QConfigSpec("random_seed", "q_executable", "scalar", "-S", int, "requires_restart", "Random seed"),
    "timer_ticks": QConfigSpec("timer_ticks", "q_executable", "scalar", "-t", int, "requires_restart", "Timer ticks"),
    "timeout": QConfigSpec("timeout", "q_executable", "scalar", "-T", int, "requires_restart", "Timeout"),
    "disable_syscmds": QConfigSpec("disable_syscmds", "q_executable", "scalar", "-u", int | str, "requires_restart", "Disable syscmds"),
    "user_password_file": QConfigSpec("user_password_file", "q_executable", "scalar", "-U", Path | str, "requires_restart", "User/password file"),
    "workspace": QConfigSpec("workspace", "q_executable", "scalar", "-w", int, "requires_restart", "Workspace limit"),
    "start_week": QConfigSpec("start_week", "q_executable", "scalar", "-W", Literal[0, 1, 2, 3, 4, 5, 6], "requires_restart", "Start-of-week"),
    "date_format": QConfigSpec("date_format", "q_executable", "scalar", "-z", Literal[0, 1], "requires_restart", "Date format"),
}


Q_RUNTIME_DEFAULTS_FOR_SERVICE = QRuntimeOptions(blocked=True, disable_syscmds=True)
Q_RUNTIME_DEFAULTS_FOR_JOB = QRuntimeOptions(quiet=True)


@dataclass(frozen=True)
class QBootstrapConfig:
    entry_file: Path
    libraries: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class QRuntimeConfig:
    kind: Literal["q"] = "q"
    startup_options: QRuntimeOptions = field(default_factory=QRuntimeOptions)
    bootstrap: QBootstrapConfig | None = None


@dataclass(frozen=True)
class PythonRuntimeConfig:
    kind: Literal["python"] = "python"
    module: str | None = None
    script: Path | None = None


@dataclass(frozen=True)
class CppRuntimeConfig:
    kind: Literal["cpp"] = "cpp"
    binary: Path | None = None


RuntimeConfig: TypeAlias = QRuntimeConfig | PythonRuntimeConfig | CppRuntimeConfig


def validate_against_schema(value: Any, schema: Any, field_name: str) -> None:
    if schema is None:
        return

    origin = get_origin(schema)
    args = get_args(schema)

    if origin is Literal:
        if value not in args:
            raise ValueError(f"{field_name}: invalid literal value {value!r}; expected one of {args!r}")
        return

    if origin is tuple:
        if not isinstance(value, tuple):
            raise TypeError(f"{field_name}: expected tuple, got {type(value).__name__}")
        if len(args) == 2 and args[1] is Ellipsis:
            for i, item in enumerate(value):
                validate_against_schema(item, args[0], f"{field_name}[{i}]")
            return
        if len(value) != len(args):
            raise ValueError(f"{field_name}: expected tuple of length {len(args)}, got {len(value)}")
        for i, (item, item_schema) in enumerate(zip(value, args)):
            validate_against_schema(item, item_schema, f"{field_name}[{i}]")
        return

    if origin is list:
        if not isinstance(value, list):
            raise TypeError(f"{field_name}: expected list, got {type(value).__name__}")
        if len(args) == 1:
            for i, item in enumerate(value):
                validate_against_schema(item, args[0], f"{field_name}[{i}]")
        return

    if origin is types.UnionType or origin is getattr(types, "UnionType", None) or origin is getattr(__import__("typing"), "Union", None):
        last_error: Exception | None = None
        for option_schema in args:
            try:
                validate_against_schema(value, option_schema, field_name)
                return
            except (TypeError, ValueError) as e:
                last_error = e
        raise TypeError(f"{field_name}: value {value!r} does not match any allowed schema in {schema!r}") from last_error

    if schema is Path:
        if not isinstance(value, Path):
            raise TypeError(f"{field_name}: expected Path, got {type(value).__name__}")
        return

    if schema in (bool, int, str, float):
        if not isinstance(value, schema):
            raise TypeError(f"{field_name}: expected {schema.__name__}, got {type(value).__name__}")
        return

    if isinstance(schema, type):
        if not isinstance(value, schema):
            raise TypeError(f"{field_name}: expected {schema.__name__}, got {type(value).__name__}")
        return

    raise TypeError(f"{field_name}: unsupported schema declaration {schema!r}")

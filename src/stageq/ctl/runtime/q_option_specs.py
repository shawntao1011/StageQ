from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


QOptionArgKind = Literal["flag", "value"]
QOptionPhase = Literal["startup_only"]

@dataclass(frozen=True)
class QRuntimeOptionSpec:
    """
    Metadata for one q executable startup option.
    """

    name: str
    cli_flag: str
    arg_kind: QOptionArgKind
    phase: QOptionPhase
    value_type: str
    description: str


Q_RUNTIME_OPTION_SPECS: dict[str, QRuntimeOptionSpec] = {
    "blocked": QRuntimeOptionSpec("blocked", "-b", "flag", "startup_only", "bool", "Blocked mode"),
    "quiet": QRuntimeOptionSpec("quiet", "-q", "flag", "startup_only", "bool", "Quiet mode"),
    "console_size": QRuntimeOptionSpec("console_size", "-c", "value", "startup_only", "str", "Console size"),
    "http_size": QRuntimeOptionSpec("http_size", "-C", "value", "startup_only", "int", "HTTP size"),
    "error_traps": QRuntimeOptionSpec("error_traps", "-e", "value", "startup_only", "bool", "Error traps"),
    "tls_mode": QRuntimeOptionSpec("tls_mode", "-E", "flag", "startup_only", "bool", "TLS server mode"),
    "garbage_collection": QRuntimeOptionSpec("garbage_collection", "-g", "value", "startup_only", "int", "Garbage collection"),
    "log_updates": QRuntimeOptionSpec("log_updates", "-l", "value", "startup_only", "bool", "Log updates"),
    "log_sync": QRuntimeOptionSpec("log_sync", "-L", "value", "startup_only", "bool", "Log sync"),
    "memory_domain": QRuntimeOptionSpec("memory_domain", "-m", "value", "startup_only", "int", "Memory domain"),
    "utc_offset": QRuntimeOptionSpec("utc_offset", "-o", "value", "startup_only", "int", "UTC offset"),
    "port": QRuntimeOptionSpec("port", "-p", "value", "startup_only", "int", "Listening port"),
    "display_precision": QRuntimeOptionSpec("display_precision", "-P", "value", "startup_only", "int", "Display precision"),
    "secondary_threads": QRuntimeOptionSpec("secondary_threads", "-s", "value", "startup_only", "int", "Secondary threads"),
    "random_seed": QRuntimeOptionSpec("random_seed", "-S", "value", "startup_only", "int", "Random seed"),
    "timer_ticks": QRuntimeOptionSpec("timer_ticks", "-t", "value", "startup_only", "int", "Timer ticks"),
    "timeout": QRuntimeOptionSpec("timeout", "-T", "value", "startup_only", "int", "Timeout"),
    "disable_syscmds": QRuntimeOptionSpec("disable_syscmds", "-u", "flag", "startup_only", "bool", "Disable syscmds"),
    "user_password_file": QRuntimeOptionSpec("user_password_file", "-U", "value", "startup_only", "str", "User/password file"),
    "workspace": QRuntimeOptionSpec("workspace", "-w", "value", "startup_only", "str", "Workspace"),
    "start_week": QRuntimeOptionSpec("start_week", "-W", "value", "startup_only", "int", "Start week"),
    "date_format": QRuntimeOptionSpec("date_format", "-z", "value", "startup_only", "str", "Date format"),
}
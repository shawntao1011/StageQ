from __future__ import annotations

from dataclasses import fields
from pathlib import Path

from stageq.ctl.runtime.q_option_specs import Q_RUNTIME_OPTION_SPECS
from stageq.model.common import QRuntimeOptions


def q_runtime_options_to_argv(options: QRuntimeOptions) -> list[str]:
    """
    Render final QRuntimeOptions into q argv flags.

    Rules:
    - value is None: omit
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

        spec = Q_RUNTIME_OPTION_SPECS[name]

        if spec.arg_kind == "flag":
            if value is True:
                argv.append(spec.cli_flag)
            continue

        argv.extend([spec.cli_flag, str(value)])

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
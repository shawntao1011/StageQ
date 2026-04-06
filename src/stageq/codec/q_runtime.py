from __future__ import annotations

from dataclasses import asdict, fields
from pathlib import Path
from typing import Any

from stageq.model.runtime import Q_EXECUTABLE_OPTION_SPECS, QRuntimeOptions, validate_against_schema


def validate_q_runtime_option_dict(raw: dict[str, Any]) -> None:
    unknown = set(raw) - set(Q_EXECUTABLE_OPTION_SPECS)
    if unknown:
        raise ValueError(f"Unknown q runtime option keys: {sorted(unknown)}")

    for name, value in raw.items():
        validate_against_schema(value, Q_EXECUTABLE_OPTION_SPECS[name].schema, name)


def q_runtime_options_from_dict(raw: dict[str, Any] | None) -> QRuntimeOptions:
    if raw is None:
        return QRuntimeOptions()

    valid_fields = {f.name for f in fields(QRuntimeOptions)}
    unknown = set(raw) - valid_fields
    if unknown:
        raise ValueError(f"Unknown q runtime option keys: {sorted(unknown)}")

    validate_q_runtime_option_dict(raw)
    return QRuntimeOptions(**raw)


def merge_q_runtime_options(*layers: QRuntimeOptions) -> QRuntimeOptions:
    merged: dict[str, Any] = {}
    for layer in layers:
        for f in fields(QRuntimeOptions):
            value = getattr(layer, f.name)
            if value is not None:
                merged[f.name] = value
    return QRuntimeOptions(**merged)


def compact_q_runtime_options(options: QRuntimeOptions) -> dict[str, Any]:
    return {k: v for k, v in asdict(options).items() if v is not None}


def q_runtime_options_to_argv(options: QRuntimeOptions) -> list[str]:
    argv: list[str] = []

    for f in fields(QRuntimeOptions):
        name = f.name
        value = getattr(options, name)
        if value is None:
            continue

        spec = Q_EXECUTABLE_OPTION_SPECS[name]

        if spec.arg_kind == "flag":
            if value is True:
                argv.append(spec.cli_flag)  # type: ignore[arg-type]
            continue

        if spec.arg_kind == "scalar":
            argv.extend([str(spec.cli_flag), str(value)])
            continue

        if spec.arg_kind == "multi":
            if not isinstance(value, (tuple, list)):
                raise TypeError(f"{name} expects tuple/list for multi arg, got {type(value)!r}")
            argv.append(str(spec.cli_flag))
            argv.extend(str(v) for v in value)
            continue

        raise ValueError(f"unknown arg_kind={spec.arg_kind!r} for {name}")

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

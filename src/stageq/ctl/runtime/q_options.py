from __future__ import annotations

from dataclasses import asdict, fields
from typing import Any

from stageq.model.common import QRuntimeOptions


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
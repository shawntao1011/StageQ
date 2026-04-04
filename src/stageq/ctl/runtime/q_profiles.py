from __future__ import annotations

from dataclasses import dataclass

from stageq.model.common import QRuntimeOptions


@dataclass(frozen=True)
class QRuntimeProfile:
    """
    Named workload-level q runtime default profile.
    """

    name: str
    options: QRuntimeOptions


SERVICE_Q_PROFILE = QRuntimeProfile(
    name="service",
    options=QRuntimeOptions(
        blocked=True,
        quiet=True,
        disable_syscmds=True,
    ),
)

JOB_Q_PROFILE = QRuntimeProfile(
    name="job",
    options=QRuntimeOptions(
        quiet=True,
    ),
)
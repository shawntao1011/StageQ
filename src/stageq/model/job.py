from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from stageq.model.common import (
    CppRuntimeSpec,
    ProcessLaunchConfig,
    PythonRuntimeSpec,
    QRuntimeSpec,
    RuntimeKind,
    validate_runtime_binding,
)


# ============================================================================
# Job identity
# ============================================================================
@dataclass
class JobIdentity:
    """
    Identity for a run-to-completion job.

    This is specifically for workloads such as:
    - sorter
    - backfill
    - repair
    - save-down
    - housekeeping
    - one-off replay

    Why this is separate from ServiceIdentity
    -----------------------------------------
    Jobs are fundamentally different from services:

    Service:
    - long-running
    - stable endpoint/identity
    - restartable daemon semantics
    - usually monitored as "alive or not"

    Job:
    - run-to-completion
    - often tied to a specific run/execution
    - tracked by submission/result/status
    - monitored as "succeeded/failed/running"

    So jobs need a different identity model centered around execution,
    not around stable daemon presence.
    """

    job_name: str
    # Logical job type/name.
    # Example: "sorter", "eod_close", "backfill_basicqot"

    env_name: str
    # Environment/profile.
    # Example: "dev", "prod"

    run_id: str
    # Unique identifier for this specific execution.
    # Example: "20260328-hk-001", "manual-20260328-153000"

    job_type: str | None = None
    # Optional functional subtype/category if useful.
    # Example: "sorter", "backfill", "repair"

    schedule_name: str | None = None
    # Optional scheduler-origin label.
    # Example: "daily-eod", "airflow-sorter", "manual"


# ============================================================================
# Job execution policy
# ============================================================================
@dataclass
class JobExecutionPolicy:
    """
    Execution behavior for run-to-completion jobs.

    Why this exists
    ----------------
    Jobs care more about completion semantics than daemon lifecycle.
    This is the right place to describe behavior such as:
    - retry count
    - retry delay
    - max runtime
    - whether failure is fatal

    Current scope
    -------------
    Keep this intentionally small in phase 1.
    """

    max_retries: int = 0
    # How many times the controller/orchestrator may retry this job.

    retry_delay_seconds: int = 0
    # Delay between retries.

    max_runtime_seconds: int | None = None
    # Optional max runtime budget.

    fail_fast: bool = True
    # Whether the job should be treated as terminally failed immediately
    # on the first failure (unless retries are configured externally).


# ============================================================================
# Final resolved job model
# ============================================================================
@dataclass
class ResolvedJobConfig:
    """
    Final resolved model for a run-to-completion job.

    Intended flow
    -------------
        raw YAML / layered config
            -> resolver.py
            -> ResolvedJobConfig
            -> job runner / qrender / scheduler integration

    This object is for jobs only
    ----------------------------
    It is NOT intended for long-running services such as:
    - wdb
    - discovery
    - tp
    - writer daemon

    Those should use model/service.py instead.

    Typical job semantics
    ---------------------
    A job usually implies:
    - explicit submission/run
    - bounded execution
    - terminal success/failure state
    - possible retries
    - output/result collection
    - scheduler/orchestrator integration

    Structure
    ---------
    identity       -> which job execution this is
    runtime_kind   -> which runtime hosts the job
    launch         -> process-level host settings
    runtime spec   -> runtime-specific startup info
    execution      -> job execution policy
    job_config     -> business/job payload

    job_config role
    ---------------
    job_config carries the actual parameters for the run, for example:
    - trading date
    - source path
    - destination path
    - market / region
    - partition
    - replay window
    - sort mode
    """

    identity: JobIdentity
    # Identity of this specific job execution.

    runtime_kind: RuntimeKind
    # Which runtime hosts this job.

    launch: ProcessLaunchConfig
    # Generic OS/process-level launch settings.

    execution: JobExecutionPolicy = field(default_factory=JobExecutionPolicy)
    # Execution behavior / retry policy.

    q_runtime: QRuntimeSpec | None = None
    # q-specific runtime spec for q jobs.

    python_runtime: PythonRuntimeSpec | None = None
    # python-specific runtime spec for python jobs.

    cpp_runtime: CppRuntimeSpec | None = None
    # cpp-specific runtime spec for native jobs.

    job_config: dict[str, Any] = field(default_factory=dict)
    # Business/run payload for this specific job execution.

    def validate(self) -> None:
        """
        Validate internal consistency of the resolved job model.

        Current checks
        --------------
        - exactly one runtime spec is set
        - runtime_kind matches that runtime spec
        - basic execution policy sanity
        """
        validate_runtime_binding(
            runtime_kind=self.runtime_kind,
            q_runtime=self.q_runtime,
            python_runtime=self.python_runtime,
            cpp_runtime=self.cpp_runtime,
        )

        if self.execution.max_retries < 0:
            raise ValueError("execution.max_retries must be >= 0")

        if self.execution.retry_delay_seconds < 0:
            raise ValueError("execution.retry_delay_seconds must be >= 0")

        if (
            self.execution.max_runtime_seconds is not None
            and self.execution.max_runtime_seconds <= 0
        ):
            raise ValueError("execution.max_runtime_seconds must be > 0 when set")
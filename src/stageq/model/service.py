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
# Service identity
# ============================================================================
@dataclass
class ServiceIdentity:
    """
    Stable identity for a long-running service.

    This is specifically for workloads such as:
    - wdb
    - hdb query service
    - tickerplant
    - discovery
    - gateway
    - writer
    - feeder daemon

    Why a separate identity type exists
    -----------------------------------
    Services are persistent system actors. They typically have:
    - stable names
    - long-lived process presence
    - health endpoints or ports
    - monitoring labels
    - service registry identity

    This makes service identity different from job identity,
    which is usually tied to a particular execution/run.
    """

    name: str
    # Stable logical service name.
    # Example: "wdb.hk", "tp.hk", "discovery"

    service_type: str
    # Functional role/class.
    # Example: "wdb", "tp", "discovery", "writer"

    env_name: str
    # Environment/profile.
    # Example: "dev", "prod"

    instance_id: str | None = None
    # Optional instance identifier for multi-instance deployment.
    # Example: "wdb.hk.01", "writer.hk.a"
    #
    # Keep this optional because in simple local/dev scenarios the stable name
    # may already be enough.


# ============================================================================
# Final resolved service model
# ============================================================================
@dataclass
class ResolvedServiceConfig:
    """
    Final resolved model for a long-running service.

    This is the core typed contract produced by configuration resolution
    for service-style workloads.

    Intended flow
    -------------
        raw YAML / layered config
            -> resolver.py
            -> ResolvedServiceConfig
            -> launcher / qrender / registry / metrics integrations

    This object is for services only
    --------------------------------
    It is NOT intended for run-to-completion workloads such as:
    - sorter job
    - backfill
    - ad hoc repair
    - replay batch

    Those should use model/job.py instead.

    Typical service semantics
    -------------------------
    A service usually implies:
    - long-running process
    - stable identity
    - pid/status management
    - health checks
    - possible registry integration
    - possible systemd supervision

    Structure
    ---------
    identity        -> who the service is
    runtime_kind    -> which runtime hosts the service
    launch          -> how the process is hosted by the OS
    runtime spec    -> runtime-specific startup information
    service_config  -> business/application config payload

    service_config role
    -------------------
    service_config is the service-level business config payload.
    For q services, it will typically be rendered into config artifact
    and loaded into q namespace, e.g. `.stageq.cfg`.

    Example contents:
    - region
    - stream.topic
    - storage.root
    - replay.enabled
    - writer.batch_size
    """

    identity: ServiceIdentity
    # Stable identity of the long-running service.

    runtime_kind: RuntimeKind
    # Which runtime hosts this service today.

    launch: ProcessLaunchConfig
    # Generic OS/process-level launch settings.

    q_runtime: QRuntimeSpec | None = None
    # q-specific runtime spec.
    # Expected when runtime_kind == "q".

    python_runtime: PythonRuntimeSpec | None = None
    # python-specific runtime spec.
    # Expected when runtime_kind == "python".

    cpp_runtime: CppRuntimeSpec | None = None
    # cpp-specific runtime spec.
    # Expected when runtime_kind == "cpp".

    service_config: dict[str, Any] = field(default_factory=dict)
    # Business/application configuration for the service.

    def validate(self) -> None:
        """
        Validate internal consistency of the resolved service model.

        Current checks
        --------------
        - exactly one runtime spec is set
        - runtime_kind matches that runtime spec
        - instance_id is optional, no extra restriction yet

        Future extension
        ----------------
        This is the right place to add service-specific validation later, e.g.:
        - q service with port requirement
        - required health metadata
        - registry tags
        """
        validate_runtime_binding(
            runtime_kind=self.runtime_kind,
            q_runtime=self.q_runtime,
            python_runtime=self.python_runtime,
            cpp_runtime=self.cpp_runtime,
        )
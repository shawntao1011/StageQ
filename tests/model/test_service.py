from pathlib import Path

import pytest

from stageq.model.runtime import QRuntimeConfig
from stageq.model.service import ProcessLaunchConfig, ResolvedServiceConfig, ServiceIdentity


def test_service_validate_requires_q_bootstrap() -> None:
    cfg = ResolvedServiceConfig(
        identity=ServiceIdentity(name="hdb.hk", service_type="hdb", env_name="dev"),
        launch=ProcessLaunchConfig(executable="q", working_dir=Path('.')),
        runtime=QRuntimeConfig(bootstrap=None),
    )

    with pytest.raises(ValueError, match="q runtime requires bootstrap"):
        cfg.validate()

from pathlib import Path

from stageq.ctl.resolver import resolve_service_config
from stageq.model.runtime import QRuntimeConfig


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1] / 'fixtures' / 'repo'


def test_resolve_service_config_supports_canonical_q_schema() -> None:
    cfg = resolve_service_config(_repo_root(), 'hdb.hk', 'dev')

    assert isinstance(cfg.runtime, QRuntimeConfig)
    assert cfg.runtime.bootstrap is not None
    assert cfg.runtime.startup_options.port == 32120
    assert cfg.runtime.startup_options.secondary_threads == 4
    assert len(cfg.runtime.bootstrap.libraries) == 2


def test_resolve_service_config_supports_canonical_wdb_q_schema() -> None:
    cfg = resolve_service_config(_repo_root(), 'wdb.hk', 'dev')

    assert isinstance(cfg.runtime, QRuntimeConfig)
    assert cfg.runtime.bootstrap is not None
    assert cfg.runtime.startup_options.port == 32101
    assert cfg.runtime.startup_options.secondary_threads == 4
    assert cfg.runtime.startup_options.utc_offset == 0
    assert len(cfg.runtime.bootstrap.libraries) == 2

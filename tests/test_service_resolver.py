from pathlib import Path

from stageq.ctl.qrender import render_config_q
from stageq.ctl.resolver import resolve_service_config
from stageq.model.common import QServiceRuntimeConfig


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_resolve_service_config_supports_canonical_q_schema() -> None:
    cfg = resolve_service_config(_repo_root(), "hdb.hk", "dev")

    assert isinstance(cfg.runtime, QServiceRuntimeConfig)
    assert cfg.runtime.bootstrap is not None
    assert cfg.runtime.startup_options.port == 32120
    assert cfg.runtime.startup_options.secondary_threads == 4
    assert len(cfg.runtime.bootstrap.libraries) == 2


def test_resolve_service_config_supports_canonical_wdb_q_schema() -> None:
    cfg = resolve_service_config(_repo_root(), "wdb.hk", "dev")

    assert isinstance(cfg.runtime, QServiceRuntimeConfig)
    assert cfg.runtime.bootstrap is not None
    assert cfg.runtime.startup_options.port == 32101
    assert cfg.runtime.startup_options.secondary_threads == 4
    assert cfg.runtime.startup_options.utc_offset == 0
    assert len(cfg.runtime.bootstrap.libraries) == 2


def test_resolve_service_config_rejects_legacy_schema() -> None:
    root = _repo_root()
    svc_dir = root / "config" / "services"
    svc_path = svc_dir / "wdb.legacy.yaml"

    svc_path.write_text(
        "\n".join(
            [
                "service:",
                "  name: wdb.legacy",
                "  type: wdb",
                "  runtime: q",
                "paths:",
                "  bootstrap: src/stageq/q/bootstrap/bootstrap.q",
                "q_runtime:",
                "  port: 32101",
                "q:",
                "  libraries:",
                "    - src/stageq/q/common/util.q",
            ]
        ),
        encoding="utf-8",
    )

    try:
        try:
            resolve_service_config(root, "wdb.legacy", "dev")
        except KeyError as e:
            assert str(e) == "'kind'"
        else:
            raise AssertionError("expected KeyError for legacy schema without runtime.kind")
    finally:
        svc_path.unlink(missing_ok=True)


def test_render_config_q_accepts_resolved_runtime_type() -> None:
    cfg = resolve_service_config(_repo_root(), "hdb.hk", "dev")
    text = render_config_q(cfg)

    assert ".stageq.meta:" in text
    assert ".stageq.cfg:" in text
    assert ".stageq.libs:" in text
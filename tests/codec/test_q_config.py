from pathlib import Path

from stageq.codec.q_config import render_config_q
from stageq.ctl.resolver import resolve_service_config


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1] / 'fixtures' / 'repo'


def test_render_config_q_accepts_resolved_runtime_type() -> None:
    cfg = resolve_service_config(_repo_root(), 'hdb.hk', 'dev')
    text = render_config_q(cfg)

    assert '.stageq.meta:' in text
    assert '.stageq.cfg:' in text
    assert '.stageq.libs:' in text

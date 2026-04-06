from pathlib import Path

import pytest

from stageq.codec.q_runtime import q_runtime_options_from_dict, q_runtime_options_to_argv, validate_q_runtime_option_dict
from stageq.model.runtime import QRuntimeOptions


def test_q_runtime_options_to_argv_renders_flags_scalars_and_multi() -> None:
    opts = QRuntimeOptions(
        blocked=True,
        quiet=False,
        port=9010,
        console_size=(40, 120),
        memory_domain_path=Path('/tmp/mem'),
    )

    assert q_runtime_options_to_argv(opts) == [
        '-b', '-c', '40', '120', '-m', '/tmp/mem', '-p', '9010'
    ]


def test_validate_q_runtime_option_dict_accepts_valid_minimal_payload() -> None:
    validate_q_runtime_option_dict({'blocked': True, 'port': 9001, 'error_traps': 2})


def test_validate_q_runtime_option_dict_rejects_unknown_key() -> None:
    with pytest.raises(ValueError, match='Unknown q runtime option keys'):
        validate_q_runtime_option_dict({'not_exists': 1})


def test_validate_q_runtime_option_dict_rejects_wrong_type() -> None:
    with pytest.raises(TypeError, match='port: expected int'):
        validate_q_runtime_option_dict({'port': '9001'})


def test_q_runtime_options_from_dict_builds_dataclass() -> None:
    opts = q_runtime_options_from_dict({'blocked': True, 'port': 9100})
    assert opts == QRuntimeOptions(blocked=True, port=9100)


def test_q_runtime_options_from_dict_none_returns_empty_options() -> None:
    assert q_runtime_options_from_dict(None) == QRuntimeOptions()

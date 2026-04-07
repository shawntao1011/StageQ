from pathlib import Path
from typing import Literal

import pytest

from stageq.codec.q_runtime import q_runtime_options_from_dict, q_runtime_options_to_argv, validate_q_runtime_option_dict
from stageq.model.runtime import QRuntimeOptions

# ===== function: q_runtime_options_from_dict =====
# --- happy path ---
# type: none
def test_function_q_runtime_options_from_dict_none_returns_empty_options() -> None:
    assert q_runtime_options_from_dict(None) == QRuntimeOptions()

# type: combination
def test_function_q_runtime_options_from_dict_combination() -> None:
    opts = q_runtime_options_from_dict({'blocked': True, 'port': 9100})
    assert opts == QRuntimeOptions(blocked=True, port=9100)

# ===== function: q_runtime_options_to_argv =====
# --- happy path ---
# type: flag
@pytest.mark.parametrize(
    ("blocked", "expected"),
    [
        (True, ["-b"]),
        (False, []),
    ],
)
def test_function_q_runtime_options_to_argv_flag(blocked: bool, expected: list[str]) -> None:
    opts = QRuntimeOptions(blocked=blocked)
    assert q_runtime_options_to_argv(opts) == expected

# type: scalar
@pytest.mark.parametrize(
    ("error_traps", "expected"),
    [
        (1, ["-e", "1"]),
    ],
)
def test_function_q_runtime_options_to_argv_scalar(error_traps: Literal[0, 1, 2], expected: list[str]) -> None:
    opts = QRuntimeOptions(error_traps=error_traps)
    assert q_runtime_options_to_argv(opts) == expected

# type: multi
@pytest.mark.parametrize(
    ("console_size", "expected"),
    [
        ((40, 100), ["-c", "40", "100"]),
    ],
)
def test_function_q_runtime_options_to_argv_multi(console_size: tuple[int, int], expected: list[str]) -> None:
    opts = QRuntimeOptions(console_size=console_size)
    assert q_runtime_options_to_argv(opts) == expected

# type: combination
def test_function_q_runtime_options_to_argv_combination() -> None:
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

# ===== function: validate_q_runtime_option_dict =====
# --- happy path ---
# type: flag
@pytest.mark.parametrize("blocked", [True, False])
def test_validate_q_runtime_option_dict_accepts_flag(blocked: bool) -> None:
    validate_q_runtime_option_dict({"blocked": blocked})

# type: scalar
@pytest.mark.parametrize("disable_syscmds", [1, Path('/tmp/pw')])
def test_validate_q_runtime_option_dict_accepts_scalar(disable_syscmds: Literal[1] | Path) -> None:
    validate_q_runtime_option_dict({'disable_syscmds': disable_syscmds})

# type: combination
def test_validate_q_runtime_option_dict_accepts_combination() -> None:
    validate_q_runtime_option_dict({'blocked': True, 'port': 9001, 'error_traps': 2})

# --- error cases ---
# type: unknown key
def test_validate_q_runtime_option_dict_rejects_unknown_key() -> None:
    with pytest.raises(ValueError, match='Unknown q runtime option keys'):
        validate_q_runtime_option_dict({'not_exists': 1})

# type: wrong type
def test_validate_q_runtime_option_dict_rejects_wrong_type() -> None:
    with pytest.raises(TypeError, match='port: expected int'):
        validate_q_runtime_option_dict({'port': '9001'})
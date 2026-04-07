from itertools import combinations
from pathlib import Path
from typing import Any

import pytest

from stageq.codec.q_runtime import q_runtime_options_from_dict, q_runtime_options_to_argv, validate_q_runtime_option_dict
from stageq.model.runtime import Q_EXECUTABLE_OPTION_SPECS, QRuntimeOptions


REPRESENTATIVE_VALUES: dict[str, Any] = {
    "blocked": True,
    "console_size": (40, 120),
    "http_size": (10, 1000),
    "error_traps": 2,
    "tls_mode": 1,
    "garbage_collection": 1,
    "log_updates": True,
    "log_sync": True,
    "memory_domain_path": Path("/tmp/mem"),
    "utc_offset": -5,
    "port": 9001,
    "display_precision": 10,
    "quiet": True,
    "secondary_threads": 8,
    "random_seed": 12345,
    "timer_ticks": 500,
    "timeout": 120,
    "disable_syscmds": Path("/tmp/.q.pw"),
    "user_password_file": "/tmp/users.txt",
    "workspace": 256,
    "start_week": 1,
    "date_format": 1,
}

# ===== function: q_runtime_options_from_dict =====
# --- happy path ---
# type: none
def test_function_q_runtime_options_from_dict_none_returns_empty_options() -> None:
    assert q_runtime_options_from_dict(None) == QRuntimeOptions()

# type: combination
def test_function_q_runtime_options_from_dict_combination() -> None:
    opts = q_runtime_options_from_dict({'blocked': True, 'port': 9100})
    assert opts == QRuntimeOptions(blocked=True, port=9100)


def test_function_q_runtime_options_from_dict_rejects_unknown_key() -> None:
    with pytest.raises(ValueError, match='Unknown q runtime option keys'):
        q_runtime_options_from_dict({'not_exists': 1})

# ===== function: q_runtime_options_to_argv =====
# --- happy path ---
def test_function_q_runtime_options_to_argv_flag_false_is_omitted() -> None:
    opts = QRuntimeOptions(blocked=False)
    assert q_runtime_options_to_argv(opts) == []

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


@pytest.mark.parametrize("name,spec", Q_EXECUTABLE_OPTION_SPECS.items())
def test_function_q_runtime_options_to_argv_all_option_keys_are_convertible(name: str, spec: Any) -> None:
    opts = QRuntimeOptions(**{name: REPRESENTATIVE_VALUES[name]})
    argv = q_runtime_options_to_argv(opts)

    if spec.arg_kind == "flag":
        assert argv == [spec.cli_flag]
    elif spec.arg_kind == "scalar":
        assert argv == [str(spec.cli_flag), str(REPRESENTATIVE_VALUES[name])]
    else:
        assert argv == [str(spec.cli_flag), *(str(v) for v in REPRESENTATIVE_VALUES[name])]


@pytest.mark.parametrize(
    "left,right",
    [
        pair for pair in combinations(Q_EXECUTABLE_OPTION_SPECS.keys(), 2)
    ],
)
def test_function_q_runtime_options_to_argv_pairwise_combinations(left: str, right: str) -> None:
    opts = QRuntimeOptions(**{
        left: REPRESENTATIVE_VALUES[left],
        right: REPRESENTATIVE_VALUES[right],
    })

    argv = q_runtime_options_to_argv(opts)

    for name in (left, right):
        cli_flag = Q_EXECUTABLE_OPTION_SPECS[name].cli_flag
        assert cli_flag in argv

# ===== function: validate_q_runtime_option_dict =====
# --- happy path ---
@pytest.mark.parametrize("blocked", [True, False])
def test_validate_q_runtime_option_dict_accepts_flag_sample(blocked: bool) -> None:
    validate_q_runtime_option_dict({"blocked": blocked})


@pytest.mark.parametrize("error_traps", [0, 1, 2])
def test_validate_q_runtime_option_dict_accepts_scalar_literal_sample(error_traps: int) -> None:
    validate_q_runtime_option_dict({"error_traps": error_traps})


@pytest.mark.parametrize("console_size", [(10, 10), (40, 120)])
def test_validate_q_runtime_option_dict_accepts_multi_sample(console_size: tuple[int, int]) -> None:
    validate_q_runtime_option_dict({"console_size": console_size})

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

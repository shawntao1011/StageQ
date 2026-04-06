from pathlib import Path
from typing import Literal

import pytest

from stageq.model.helpers.q_runtime_options_validate import validate_against_schema


@pytest.mark.parametrize(
    ("value", "schema"),
    [
        (True, bool),
        (9001, int),
        ("user.txt", str),
        (Path("/tmp/a"), Path),
        (1, Literal[0, 1, 2]),
        ((40, 120), tuple[int, int]),
        ([1, 2, 3], list[int]),
        ("user.txt", Path | str),
    ],
)
def test_validate_against_schema_accepts_supported_forms(value, schema) -> None:
    validate_against_schema(value, schema, "field")


@pytest.mark.parametrize(
    ("value", "schema", "error_type", "message"),
    [
        ("9001", int, TypeError, "expected int"),
        (3, Literal[0, 1, 2], ValueError, "invalid literal value"),
        ([40, 120], tuple[int, int], TypeError, "expected tuple"),
        ((40,), tuple[int, int], ValueError, "expected tuple of length"),
        ("/tmp/a", Path, TypeError, "expected Path"),
    ],
)
def test_validate_against_schema_rejects_invalid_input(
    value,
    schema,
    error_type,
    message,
) -> None:
    with pytest.raises(error_type, match=message):
        validate_against_schema(value, schema, "field")
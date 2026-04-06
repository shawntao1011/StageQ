from pathlib import Path
from typing import Any, Literal, get_args, get_origin
import types


def validate_against_schema(value: Any, schema: Any, field_name: str) -> None:
    """
    Validate one value against a lightweight schema declaration.

    Supported schema forms:
    - bool / int / str / Path
    - Literal[...]
    - tuple[T1, T2, ...]
    - list[T]
    - A | B / Union[A, B]

    Raises:
        TypeError / ValueError on validation failure
    """
    if schema is None:
        return

    origin = get_origin(schema)
    args = get_args(schema)

    if origin is Literal:
        if value not in args:
            raise ValueError(
                f"{field_name}: invalid literal value {value!r}; "
                f"expected one of {args!r}"
            )
        return

    if origin is tuple:
        if not isinstance(value, tuple):
            raise TypeError(f"{field_name}: expected tuple, got {type(value).__name__}")

        if len(args) == 2 and args[1] is Ellipsis:
            item_schema = args[0]
            for i, item in enumerate(value):
                validate_against_schema(item, item_schema, f"{field_name}[{i}]")
            return

        if len(value) != len(args):
            raise ValueError(
                f"{field_name}: expected tuple of length {len(args)}, got {len(value)}"
            )

        for i, (item, item_schema) in enumerate(zip(value, args)):
            validate_against_schema(item, item_schema, f"{field_name}[{i}]")
        return

    if origin is list:
        if not isinstance(value, list):
            raise TypeError(f"{field_name}: expected list, got {type(value).__name__}")

        if len(args) == 1:
            item_schema = args[0]
            for i, item in enumerate(value):
                validate_against_schema(item, item_schema, f"{field_name}[{i}]")
        return

    if origin is types.UnionType or origin is getattr(types, "UnionType", None):
        last_error: Exception | None = None
        for option_schema in args:
            try:
                validate_against_schema(value, option_schema, field_name)
                return
            except (TypeError, ValueError) as e:
                last_error = e
        raise TypeError(
            f"{field_name}: value {value!r} does not match any allowed schema in {schema!r}"
        ) from last_error

    if origin is getattr(__import__("typing"), "Union", None):
        last_error: Exception | None = None
        for option_schema in args:
            try:
                validate_against_schema(value, option_schema, field_name)
                return
            except (TypeError, ValueError) as e:
                last_error = e
        raise TypeError(
            f"{field_name}: value {value!r} does not match any allowed schema in {schema!r}"
        ) from last_error

    if schema is Path:
        if not isinstance(value, Path):
            raise TypeError(f"{field_name}: expected Path, got {type(value).__name__}")
        return

    if schema in (bool, int, str, float):
        if not isinstance(value, schema):
            raise TypeError(
                f"{field_name}: expected {schema.__name__}, got {type(value).__name__}"
            )
        return

    if isinstance(schema, type):
        if not isinstance(value, schema):
            raise TypeError(
                f"{field_name}: expected {schema.__name__}, got {type(value).__name__}"
            )
        return

    raise TypeError(f"{field_name}: unsupported schema declaration {schema!r}")


def validate_q_runtime_option_dict(raw: dict[str, Any], specs: dict[str, Any]) -> None:
    """
    Validate runtime option payload against a spec dict.

    `specs` is expected to be a mapping from field name to object with a `schema` attribute.
    """
    unknown = set(raw) - set(specs)
    if unknown:
        raise ValueError(f"Unknown q runtime option keys: {sorted(unknown)}")

    for name, value in raw.items():
        spec = specs[name]
        validate_against_schema(value, spec.schema, name)
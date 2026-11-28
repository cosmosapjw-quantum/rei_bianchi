from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json


def _reject_constant(value: str):
    raise ValueError(f"non-finite JSON constant not allowed: {value}")


def parse_identity_z(raw_json: bytes | str) -> Decimal:
    """Parse producer IDENTITY.json z without number-vs-string ambiguity."""
    if isinstance(raw_json, bytes):
        text = raw_json.decode("utf-8")
    elif isinstance(raw_json, str):
        text = raw_json
    else:
        raise TypeError("raw_json must be bytes or str")
    obj = json.loads(text, parse_float=Decimal, parse_int=Decimal, parse_constant=_reject_constant)
    if not isinstance(obj, dict) or "z" not in obj:
        raise ValueError("IDENTITY must be an object containing z")
    value = obj["z"]
    if isinstance(value, bool) or value is None:
        raise ValueError("z must be a finite decimal number or decimal string")
    if isinstance(value, Decimal):
        z = value
    elif isinstance(value, str):
        try:
            z = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError("invalid decimal string z") from exc
    else:
        raise ValueError("z must be a JSON number or decimal string")
    if not z.is_finite():
        raise ValueError("z must be finite")
    return z


def identities_match(raw_a: bytes | str, raw_b: bytes | str, expected_decimal: str) -> bool:
    try:
        expected = Decimal(expected_decimal)
    except InvalidOperation as exc:
        raise ValueError("invalid expected_decimal") from exc
    if not expected.is_finite():
        raise ValueError("expected z must be finite")
    return parse_identity_z(raw_a) == expected == parse_identity_z(raw_b)

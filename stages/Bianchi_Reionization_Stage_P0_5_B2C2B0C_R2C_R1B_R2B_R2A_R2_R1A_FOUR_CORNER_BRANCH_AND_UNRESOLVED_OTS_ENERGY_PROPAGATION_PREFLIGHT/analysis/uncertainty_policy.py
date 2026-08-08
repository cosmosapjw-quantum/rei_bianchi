#!/usr/bin/env python3
"""Predeclared source-branch uncertainty policies.

Energy-witness endpoints are an orthogonal ledger/thermal enclosure axis.  They
are deliberately not encoded in :class:`UncertaintyPolicy`, because they do not
change the event topology or the population branch parameters ``v`` and ``f``.
"""
from __future__ import annotations

from typing import NamedTuple, Mapping
import numpy as np

V_POLICIES = (
    "CELL_LOWER_STRICT",
    "CELL_UPPER_STRICT",
    "ADAPTER_TABLE_LOW_STRICT",
    "ADAPTER_TABLE_HIGH_STRICT",
)
F_ENDPOINTS = (0.1, 1.0)
ENERGY_WITNESS_POLICIES = ("ENERGY_LOWER", "ENERGY_UPPER")

# Hummer--Seaton source nodes recovered in the prior durable stage.
LOG10_T_NODES = np.asarray((4.00, 4.25, 4.50, 4.75, 5.00), dtype=np.float64)
V_NODES = np.asarray((0.285, 0.305, 0.325, 0.350, 0.375), dtype=np.float64)


class UncertaintyPolicy(NamedTuple):
    policy_id: str
    v_policy: str
    f_value: float
    load_bearing: bool


def _immutable(values: np.ndarray) -> np.ndarray:
    out = np.ascontiguousarray(values, dtype=np.float64)
    out.setflags(write=False)
    return out


def policy_registry() -> tuple[UncertaintyPolicy, ...]:
    rows: list[UncertaintyPolicy] = []
    for v_policy in V_POLICIES:
        for f_value in F_ENDPOINTS:
            token = f'{v_policy}__F_{str(f_value).replace(".", "P")}'
            rows.append(
                UncertaintyPolicy(
                    token,
                    v_policy,
                    float(f_value),
                    v_policy in {"CELL_LOWER_STRICT", "CELL_UPPER_STRICT"},
                )
            )
    return tuple(rows)


def _array(envelope: Mapping[str, np.ndarray], key: str) -> np.ndarray:
    if key not in envelope:
        raise KeyError(key)
    value = np.asarray(envelope[key])
    if value.ndim != 1:
        raise ValueError(f"{key} must be one-dimensional")
    return value


def build_v_field(policy: str, envelope: Mapping[str, np.ndarray]) -> np.ndarray:
    if policy not in V_POLICIES:
        raise KeyError(policy)
    lower = np.asarray(_array(envelope, "v_cell_lower"), dtype=np.float64)
    upper = np.asarray(_array(envelope, "v_cell_upper"), dtype=np.float64)
    adapter = np.asarray(_array(envelope, "v_adapter_central"), dtype=np.float64)
    table = np.asarray(_array(envelope, "table_domain"), dtype=bool)
    below = np.asarray(_array(envelope, "below_table"), dtype=bool)
    above = np.asarray(_array(envelope, "above_table"), dtype=bool)
    n = len(lower)
    if any(len(x) != n for x in (upper, adapter, table, below, above)):
        raise ValueError("branch envelope arrays have inconsistent lengths")
    if np.any(above):
        raise ValueError("above-table source extrapolation is prohibited")
    domain_count = table.astype(np.int8) + below.astype(np.int8) + above.astype(np.int8)
    if np.any(domain_count != 1):
        raise ValueError("each node must have exactly one temperature-domain label")
    if policy == "CELL_LOWER_STRICT":
        out = np.where(table, lower, 0.0)
    elif policy == "CELL_UPPER_STRICT":
        out = np.where(table, upper, 1.0)
    elif policy == "ADAPTER_TABLE_LOW_STRICT":
        out = np.where(table, adapter, 0.0)
    else:
        out = np.where(table, adapter, 1.0)
    if np.any(~np.isfinite(out)) or np.any((out < 0.0) | (out > 1.0)):
        raise ValueError("v field leaves the probability domain")
    return _immutable(out)


def build_v_field_from_temperature(policy: str, temperature_K: np.ndarray) -> np.ndarray:
    """Evaluate one locked ``v`` policy at a dynamic material temperature.

    Below the source table the two strict corners are ``0`` and ``1``.  The two
    named adapter auditors inherit those respective low/high strict values.
    Inside the table, cell-corner policies use the bracketing source nodes while
    adapter policies use log-linear interpolation in ``log10(T/K)``.  Values
    above ``10^5 K`` fail closed instead of extrapolating.
    """

    if policy not in V_POLICIES:
        raise KeyError(policy)
    temperature = np.asarray(temperature_K, dtype=np.float64)
    if temperature.ndim != 1:
        raise ValueError("temperature_K must be one-dimensional")
    if np.any(~np.isfinite(temperature)) or np.any(temperature <= 0.0):
        raise ValueError("temperature_K must be finite and positive")
    if np.any(temperature > 10.0**LOG10_T_NODES[-1]):
        raise ValueError("above-table source extrapolation is prohibited")

    log_temperature = np.log10(temperature)
    below = log_temperature < LOG10_T_NODES[0]
    table = ~below

    # searchsorted(..., side='right')-1 returns the left table cell.  Clip only
    # the table index, never the physical temperature; exact last-node values
    # are treated as a degenerate source knot.
    left = np.searchsorted(LOG10_T_NODES, log_temperature, side="right") - 1
    left = np.clip(left, 0, len(LOG10_T_NODES) - 2)
    right = left + 1
    knot_match = np.isclose(
        log_temperature[:, None],
        LOG10_T_NODES[None, :],
        rtol=0.0,
        atol=8.0 * np.finfo(np.float64).eps,
    )
    exact_knot = table & np.any(knot_match, axis=1)
    knot_index = np.argmax(knot_match, axis=1)

    v_left = V_NODES[left]
    v_right = V_NODES[right]
    exact_value = V_NODES[knot_index]
    v_left = np.where(exact_knot, exact_value, v_left)
    v_right = np.where(exact_knot, exact_value, v_right)

    denominator = LOG10_T_NODES[right] - LOG10_T_NODES[left]
    fraction = (log_temperature - LOG10_T_NODES[left]) / denominator
    fraction = np.where(exact_knot, 0.0, fraction)
    adapter = v_left + fraction * (v_right - v_left)

    if policy == "CELL_LOWER_STRICT":
        out = np.where(table, v_left, 0.0)
    elif policy == "CELL_UPPER_STRICT":
        out = np.where(table, v_right, 1.0)
    elif policy == "ADAPTER_TABLE_LOW_STRICT":
        out = np.where(table, adapter, 0.0)
    else:
        out = np.where(table, adapter, 1.0)

    if np.any(~np.isfinite(out)) or np.any((out < 0.0) | (out > 1.0)):
        raise ValueError("v field leaves the probability domain")
    return _immutable(out)


def build_f_field(f_value: float, node_count: int) -> np.ndarray:
    value = float(f_value)
    if value not in F_ENDPOINTS:
        raise ValueError("f must be a predeclared endpoint")
    if int(node_count) <= 0:
        raise ValueError("node_count must be positive")
    return _immutable(np.full(int(node_count), value, dtype=np.float64))


def load_branch_envelope(path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        required = (
            "v_cell_lower",
            "v_cell_upper",
            "v_adapter_central",
            "table_domain",
            "below_table",
            "above_table",
        )
        return {key: np.array(data[key], copy=True) for key in required}

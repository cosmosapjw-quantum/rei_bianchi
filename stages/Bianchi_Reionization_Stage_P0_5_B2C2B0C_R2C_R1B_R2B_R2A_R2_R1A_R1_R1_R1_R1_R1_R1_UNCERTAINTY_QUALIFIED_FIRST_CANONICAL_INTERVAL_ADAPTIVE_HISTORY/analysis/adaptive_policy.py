#!/usr/bin/env python3
"""Pure common-grid policy and fail-closed worker-envelope validation."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Iterable

STAGE_ID = (
    "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-R1-"
    "UNCERTAINTY-QUALIFIED-FIRST-CANONICAL-INTERVAL-ADAPTIVE-HISTORY"
)
LANE_ORDER = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
TOTAL_TICKS = 131072
BASE_SEGMENT_TICKS = 64
MAXIMUM_DEPTH = 6
STATE_NODE_COUNT = 46080
PUBLIC_WIDTH_LIMIT = 0.002
LOCAL_ERROR_LIMIT = 0.0002
WIDTH_KEYS = ("x_HII", "x_HeII", "x_HeIII", "log_T")
EXPECTED_LEDGER_KEYS = (
    "H_nuclei",
    "He_nuclei",
    "stage_photon_identity",
    "stage_total_energy",
    "stage_group_0_photon",
    "stage_group_1_photon",
    "stage_group_2_photon",
    "stage_group_3_photon",
    "final_photon_identity",
    "final_total_energy",
    "final_group_0_photon",
    "final_group_1_photon",
    "final_group_2_photon",
    "final_group_3_photon",
)
POST_MAP_CLASSIFICATIONS = {
    "PASS",
    "SET_LEDGER_EXCLUDES_ZERO",
    "PUBLIC_WIDTH_GATE_FAILURE",
    "VALIDATED_LOCAL_ERROR_GATE_FAILURE",
}
EARLY_REJECTION_CLASSIFICATIONS = {
    "LOCAL_POPULATION_CERTIFICATE_FAILURE",
    "PREDICTOR_THERMAL_ROOT_FAILURE",
    "CORRECTOR_POPULATION_CERTIFICATE_FAILURE",
    "THERMAL_STAGE_ROOT_FAILURE",
    "THERMAL_FINAL_ROOT_FAILURE",
    "THERMAL_OUTER_TUBE_NOT_SELF_INCLUDED",
    "POPULATION_CONE_FAILURE",
    "IMPLICIT_CERTIFICATE_EXCEPTION",
    "INTERVAL_CERTIFICATE_INPUT_FAILURE",
    "PHYSICAL_CONE_FAILURE",
}
TABLE_EVENT_CLASSIFICATIONS = {
    "TABLE_EVENT_REQUIRES_RESTART",
    "TABLE_EVENT_ABOVE_TABLE_REQUIRES_RESTART",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _is_sha256(value: Any) -> bool:
    try:
        return isinstance(value, str) and len(value) == 64 and int(value, 16) >= 0
    except ValueError:
        return False


def _finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


@dataclass(frozen=True, order=True)
class IntervalTask:
    left_tick: int
    right_tick: int
    depth: int

    def __post_init__(self) -> None:
        if not all(
            type(value) is int
            for value in (self.left_tick, self.right_tick, self.depth)
        ):
            raise TypeError("task fields must be integers")
        if not 0 <= self.left_tick < self.right_tick <= TOTAL_TICKS:
            raise ValueError("invalid task ticks")
        if not 0 <= self.depth <= MAXIMUM_DEPTH:
            raise ValueError("invalid task depth")
        expected_width = BASE_SEGMENT_TICKS >> self.depth
        if self.width_ticks != expected_width or self.left_tick % expected_width:
            raise ValueError("task is not on the canonical dyadic grid")

    @property
    def width_ticks(self) -> int:
        return self.right_tick - self.left_tick

    def as_dict(self) -> dict[str, int]:
        return {
            "depth": self.depth,
            "left_tick": self.left_tick,
            "right_tick": self.right_tick,
        }


@dataclass(frozen=True)
class Cursor:
    accepted_index: int
    accepted_tick: int
    current: IntervalTask | None
    pending: tuple[IntervalTask, ...] = ()


@dataclass(frozen=True)
class Decision:
    action: str
    classifications: tuple[str, ...]
    left_child: IntervalTask | None = None
    right_child: IntervalTask | None = None


def validate_cursor(cursor: Cursor) -> Cursor:
    if type(cursor.accepted_index) is not int or type(cursor.accepted_tick) is not int:
        raise ValueError("cursor counters must be integers")
    if not 0 <= cursor.accepted_tick <= TOTAL_TICKS or cursor.accepted_index < 0:
        raise ValueError("invalid cursor counters")
    if cursor.accepted_tick == 0 and cursor.accepted_index != 0:
        raise ValueError("nonzero accepted index at initial tick")
    if cursor.accepted_tick:
        lower = (cursor.accepted_tick + BASE_SEGMENT_TICKS - 1) // BASE_SEGMENT_TICKS
        if not lower <= cursor.accepted_index <= cursor.accepted_tick:
            raise ValueError("accepted index is inconsistent with accepted tick")
    if cursor.current is None:
        if cursor.accepted_tick != TOTAL_TICKS or cursor.pending:
            raise ValueError("incomplete cursor lacks a current task")
        return cursor
    if not isinstance(cursor.pending, tuple) or not all(
        isinstance(task, IntervalTask) for task in cursor.pending
    ):
        raise ValueError("invalid pending task stack")
    sequence = (cursor.current,) + tuple(reversed(cursor.pending))
    tick = cursor.accepted_tick
    for task in sequence:
        if task.left_tick != tick:
            raise ValueError("cursor task sequence is not contiguous")
        tick = task.right_tick
    segment_end = min(
        ((cursor.accepted_tick // BASE_SEGMENT_TICKS) + 1) * BASE_SEGMENT_TICKS,
        TOTAL_TICKS,
    )
    if tick != segment_end:
        raise ValueError("cursor tasks do not cover the current base segment")
    return cursor


def initial_cursor() -> Cursor:
    return validate_cursor(Cursor(0, 0, IntervalTask(0, 64, 0), ()))


def job_key(
    *,
    lane: str,
    task: IntervalTask,
    accepted_index: int,
    parent_state_sha256: str,
    input_lock_sha256: str,
    predecessor_kernel_sha256: str,
    runtime_contract_sha256: str,
) -> str:
    if lane not in LANE_ORDER:
        raise ValueError("unknown lane")
    payload = {
        "accepted_index": int(accepted_index),
        "input_lock_sha256": input_lock_sha256,
        "interval": task.as_dict(),
        "lane": lane,
        "parent_state_sha256": parent_state_sha256,
        "predecessor_kernel_sha256": predecessor_kernel_sha256,
        "runtime_contract_sha256": runtime_contract_sha256,
        "stage_id": STAGE_ID,
        "worker_envelope_schema": 1,
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _validate_table_event(row: dict[str, Any], lane: str) -> bool:
    table = row.get("table_event")
    if not isinstance(table, dict) or not isinstance(table.get("any_event"), bool):
        raise ValueError(f"invalid table event for lane {lane}")
    events = table.get("events")
    if not isinstance(events, list):
        raise ValueError(f"invalid table event list for lane {lane}")
    event_flags: list[bool] = []
    node_count = 0
    for event in events:
        if not isinstance(event, dict) or not isinstance(event.get("any_event"), bool):
            raise ValueError(f"invalid table event entry for lane {lane}")
        if not _finite(event.get("minimum_distance")) or event["minimum_distance"] < 0:
            raise ValueError(f"invalid table event distance for lane {lane}")
        for name in ("node_indices", "knot_indices"):
            values = event.get(name)
            if not isinstance(values, list) or not all(
                type(value) is int and value >= 0 for value in values
            ):
                raise ValueError(f"invalid table event indices for lane {lane}")
        event_flags.append(event["any_event"])
        node_count += len(event["node_indices"])
    if table["any_event"] != any(event_flags):
        raise ValueError(f"inconsistent table event flag for lane {lane}")
    if type(table.get("node_count")) is not int or table["node_count"] != node_count:
        raise ValueError(f"inconsistent table event node count for lane {lane}")
    if not _finite(table.get("minimum_distance")) or table["minimum_distance"] < 0:
        raise ValueError(f"invalid table event summary distance for lane {lane}")
    return table["any_event"]


def _validate_post_map_metrics(row: dict[str, Any], classification: str, lane: str) -> None:
    widths = row.get("public_widths")
    ledgers = row.get("set_ledgers")
    diagnostics = row.get("diagnostics")
    if not isinstance(widths, dict) or set(widths) != set(WIDTH_KEYS):
        raise ValueError(f"invalid public width keys for lane {lane}")
    if not all(_finite(value) and value >= 0 for value in widths.values()):
        raise ValueError(f"nonfinite or negative public width for lane {lane}")
    if not isinstance(diagnostics, dict) or diagnostics.get("map_enclosed") is not True:
        raise ValueError(f"map enclosure missing for lane {lane}")
    local = diagnostics.get("validated_local_error_bounds")
    maximum = diagnostics.get("maximum_validated_local_error")
    if not isinstance(local, dict) or set(local) != set(WIDTH_KEYS):
        raise ValueError(f"invalid local-error keys for lane {lane}")
    if not all(_finite(value) and value >= 0 for value in local.values()):
        raise ValueError(f"nonfinite or negative local error for lane {lane}")
    if not _finite(maximum) or float(maximum) != max(float(v) for v in local.values()):
        raise ValueError(f"invalid maximum local error for lane {lane}")
    if not isinstance(ledgers, dict) or set(ledgers) != set(EXPECTED_LEDGER_KEYS):
        raise ValueError(f"invalid ledger keys for lane {lane}")
    include_zero = []
    for name, interval in ledgers.items():
        if (
            not isinstance(interval, list)
            or len(interval) != 2
            or not all(_finite(value) for value in interval)
            or interval[0] > interval[1]
        ):
            raise ValueError(f"invalid ledger interval {name} for lane {lane}")
        include_zero.append(interval[0] <= 0 <= interval[1])
    all_ledgers_pass = all(include_zero)
    maximum_width = max(float(value) for value in widths.values())
    maximum_local = float(maximum)
    if classification == "PASS":
        passed = (
            all_ledgers_pass
            and maximum_width < PUBLIC_WIDTH_LIMIT
            and maximum_local < LOCAL_ERROR_LIMIT
        )
    elif classification == "SET_LEDGER_EXCLUDES_ZERO":
        passed = not all_ledgers_pass
    elif classification == "PUBLIC_WIDTH_GATE_FAILURE":
        passed = all_ledgers_pass and maximum_width >= PUBLIC_WIDTH_LIMIT
    else:
        passed = (
            all_ledgers_pass
            and maximum_width < PUBLIC_WIDTH_LIMIT
            and maximum_local >= LOCAL_ERROR_LIMIT
        )
    if not passed:
        raise ValueError(f"classification/gate mismatch for lane {lane}")


def _validate_envelope(
    *,
    row: dict[str, Any],
    lane: str,
    task: IntervalTask,
    accepted_index: int,
    parent_sha: str,
    input_lock_sha256: str,
    predecessor_kernel_sha256: str,
    runtime_contract_sha256: str,
) -> tuple[str, bool]:
    expected_key = job_key(
        lane=lane,
        task=task,
        accepted_index=accepted_index,
        parent_state_sha256=parent_sha,
        input_lock_sha256=input_lock_sha256,
        predecessor_kernel_sha256=predecessor_kernel_sha256,
        runtime_contract_sha256=runtime_contract_sha256,
    )
    exact = {
        "accepted_index": accepted_index,
        "input_lock_sha256": input_lock_sha256,
        "interval": task.as_dict(),
        "job_key": expected_key,
        "lane": lane,
        "parent_state_sha256": parent_sha,
        "predecessor_kernel_sha256": predecessor_kernel_sha256,
        "runtime_contract_sha256": runtime_contract_sha256,
        "stage_id": STAGE_ID,
        "transport_status": "OK",
        "worker_envelope_schema": 1,
    }
    for name, expected in exact.items():
        if row.get(name) != expected:
            raise ValueError(f"envelope {name} mismatch for lane {lane}")
    try:
        duration = float.fromhex(row["duration_seconds_hex"])
        t0 = float.fromhex(row["time"]["t0_hex"])
        t1 = float.fromhex(row["time"]["t1_hex"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"invalid time envelope for lane {lane}") from error
    expected_t0 = duration * (task.left_tick / TOTAL_TICKS)
    expected_t1 = duration * (task.right_tick / TOTAL_TICKS)
    if (
        not all(math.isfinite(value) for value in (duration, t0, t1))
        or duration <= 0
        or row["duration_seconds_hex"] != duration.hex()
        or row["time"] != {"t0_hex": expected_t0.hex(), "t1_hex": expected_t1.hex()}
        or t0 != expected_t0
        or t1 != expected_t1
    ):
        raise ValueError(f"time/interval mismatch for lane {lane}")
    classification = row.get("classification")
    accepted = row.get("scientific_accept") is True
    if not isinstance(classification, str) or classification not in (
        POST_MAP_CLASSIFICATIONS
        | EARLY_REJECTION_CLASSIFICATIONS
        | TABLE_EVENT_CLASSIFICATIONS
    ):
        raise ValueError(f"unsupported scientific classification for lane {lane}")
    if accepted != (classification == "PASS"):
        raise ValueError(f"classification/acceptance mismatch for lane {lane}")
    event = _validate_table_event(row, lane)
    if event != (classification in TABLE_EVENT_CLASSIFICATIONS):
        raise ValueError(f"classification/table-event mismatch for lane {lane}")
    candidate = row.get("candidate_state")
    if accepted:
        if (
            not isinstance(candidate, dict)
            or candidate.get("format") != "REIADP1-deterministic-float64"
            or candidate.get("node_count") != STATE_NODE_COUNT
            or not isinstance(candidate.get("path"), str)
            or not _is_sha256(candidate.get("sha256"))
            or type(candidate.get("size_bytes")) is not int
            or candidate["size_bytes"] <= 0
        ):
            raise ValueError(f"accepted lane has invalid candidate state for lane {lane}")
    elif candidate is not None:
        raise ValueError(f"rejected lane published state for lane {lane}")
    if classification in POST_MAP_CLASSIFICATIONS:
        _validate_post_map_metrics(row, classification, lane)
    elif row.get("public_widths") != {} or row.get("set_ledgers") != {}:
        raise ValueError(f"early rejection published post-map metrics for lane {lane}")
    elif not isinstance(row.get("diagnostics"), dict):
        raise ValueError(f"early rejection lacks diagnostics for lane {lane}")
    return classification, accepted


def validate_and_decide(
    *,
    task: IntervalTask,
    accepted_index: int,
    parent_state_sha256: str | dict[str, str],
    input_lock_sha256: str,
    predecessor_kernel_sha256: str,
    runtime_contract_sha256: str,
    envelopes: Iterable[dict[str, Any]],
    maximum_depth: int = MAXIMUM_DEPTH,
) -> Decision:
    by: dict[str, dict[str, Any]] = {}
    for row in envelopes:
        if not isinstance(row, dict):
            raise ValueError("worker envelope must be an object")
        lane = row.get("lane")
        if lane in by:
            raise ValueError(f"duplicate lane envelope: {lane}")
        if lane not in LANE_ORDER:
            raise ValueError(f"unexpected lane envelope: {lane}")
        by[lane] = row
    missing = [lane for lane in LANE_ORDER if lane not in by]
    if missing:
        raise ValueError(f"missing lane envelopes: {missing}")
    classifications: list[str] = []
    duration_hexes: list[str] = []
    event = False
    all_accept = True
    for lane in LANE_ORDER:
        parent_sha = (
            parent_state_sha256[lane]
            if isinstance(parent_state_sha256, dict)
            else parent_state_sha256
        )
        classification, accepted = _validate_envelope(
            row=by[lane],
            lane=lane,
            task=task,
            accepted_index=accepted_index,
            parent_sha=parent_sha,
            input_lock_sha256=input_lock_sha256,
            predecessor_kernel_sha256=predecessor_kernel_sha256,
            runtime_contract_sha256=runtime_contract_sha256,
        )
        event |= classification in TABLE_EVENT_CLASSIFICATIONS
        all_accept &= accepted
        classifications.append(classification)
        duration_hexes.append(by[lane]["duration_seconds_hex"])
    ordered = tuple(classifications)
    if event:
        return Decision("STOP_TABLE_EVENT", ordered)
    if len(set(duration_hexes)) != 1:
        raise ValueError("cross-lane duration mismatch")
    if all_accept:
        return Decision("ACCEPT", ordered)
    if task.depth >= maximum_depth or task.width_ticks <= 1:
        return Decision("STOP_MINIMUM_STEP", ordered)
    mid = task.left_tick + task.width_ticks // 2
    return Decision(
        "BISECT",
        ordered,
        IntervalTask(task.left_tick, mid, task.depth + 1),
        IntervalTask(mid, task.right_tick, task.depth + 1),
    )


def cursor_after_bisection(
    cursor: Cursor, left: IntervalTask, right: IntervalTask
) -> Cursor:
    validate_cursor(cursor)
    if cursor.current is None:
        raise ValueError("completed cursor")
    task = cursor.current
    if (
        left.left_tick != task.left_tick
        or left.right_tick != right.left_tick
        or right.right_tick != task.right_tick
        or left.depth != task.depth + 1
        or right.depth != task.depth + 1
    ):
        raise ValueError("children do not bisect the current task")
    return validate_cursor(
        Cursor(cursor.accepted_index, cursor.accepted_tick, left, cursor.pending + (right,))
    )


def advance_after_accept(cursor: Cursor) -> Cursor:
    validate_cursor(cursor)
    if cursor.current is None:
        raise ValueError("completed cursor")
    tick = cursor.current.right_tick
    pending = cursor.pending
    if pending:
        next_task = pending[-1]
        if next_task.left_tick != tick:
            raise ValueError("pending interval mismatch")
        pending = pending[:-1]
    elif tick < TOTAL_TICKS:
        next_task = IntervalTask(tick, min(tick + BASE_SEGMENT_TICKS, TOTAL_TICKS), 0)
    else:
        next_task = None
    return validate_cursor(
        Cursor(cursor.accepted_index + 1, tick, next_task, pending)
    )

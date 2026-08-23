#!/usr/bin/env python3
"""Pure total state machine for a corrected-candidate shadow controller."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import json


class RunPhase(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    TERMINAL = "TERMINAL"


class PauseReason(str, Enum):
    ACCEPT_LIMIT = "ACCEPT_LIMIT"
    ATTEMPT_LIMIT = "ATTEMPT_LIMIT"


class TerminalOutcome(str, Enum):
    COMPLETE_CANDIDATE_UNSEALED = "COMPLETE_CANDIDATE_UNSEALED"
    BLOCKED_PROTOCOL = "BLOCKED_PROTOCOL"
    BLOCKED_TRANSPORT = "BLOCKED_TRANSPORT"
    BLOCKED_RUNTIME_IDENTITY = "BLOCKED_RUNTIME_IDENTITY"
    BLOCKED_RESOURCE = "BLOCKED_RESOURCE"
    BLOCKED_STATE_CUSTODY = "BLOCKED_STATE_CUSTODY"
    BLOCKED_NUMERICAL = "BLOCKED_NUMERICAL"
    BLOCKED_PHYSICAL = "BLOCKED_PHYSICAL"
    BLOCKED_EVENT = "BLOCKED_EVENT"
    BLOCKED_MINIMUM_STEP = "BLOCKED_MINIMUM_STEP"
    BLOCKED_INTERNAL = "BLOCKED_INTERNAL"
    ABORTED_OPERATOR = "ABORTED_OPERATOR"


class Action(str, Enum):
    START = "START"
    RECOVER = "RECOVER"
    ACCEPT = "ACCEPT"
    BISECT = "BISECT"
    EVENT_RESTART = "EVENT_RESTART"
    PAUSE_ACCEPT_LIMIT = "PAUSE_ACCEPT_LIMIT"
    PAUSE_ATTEMPT_LIMIT = "PAUSE_ATTEMPT_LIMIT"
    RESUME = "RESUME"
    COMPLETE = "COMPLETE"
    BLOCK = "BLOCK"
    ABORT = "ABORT"
    INSPECT = "INSPECT"


class TransitionCode(str, Enum):
    APPLIED = "APPLIED"
    INSPECT_NO_WRITE = "INSPECT_NO_WRITE"
    TERMINAL_NO_WRITE = "TERMINAL_NO_WRITE"
    FAIL_CLOSED_ILLEGAL = "FAIL_CLOSED_ILLEGAL"
    FAIL_CLOSED_UNKNOWN = "FAIL_CLOSED_UNKNOWN"


@dataclass(frozen=True)
class RunState:
    phase: RunPhase
    pause_reason: PauseReason | None = None
    terminal_outcome: TerminalOutcome | None = None
    transition_number: int = 0
    generation_number: int = 0
    regime_epoch: int = 0
    cursor_complete: bool = False

    def __post_init__(self) -> None:
        if type(self.phase) is not RunPhase:
            raise TypeError("phase must be a RunPhase")
        for name in ("transition_number", "generation_number", "regime_epoch"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if type(self.cursor_complete) is not bool:
            raise TypeError("cursor_complete must be boolean")
        if self.phase is RunPhase.PAUSED:
            if type(self.pause_reason) is not PauseReason or self.terminal_outcome is not None:
                raise ValueError("paused state requires only a pause reason")
        elif self.phase is RunPhase.TERMINAL:
            if type(self.terminal_outcome) is not TerminalOutcome or self.pause_reason is not None:
                raise ValueError("terminal state requires only a terminal outcome")
            if (
                self.terminal_outcome
                is TerminalOutcome.COMPLETE_CANDIDATE_UNSEALED
                and not self.cursor_complete
            ):
                raise ValueError("complete terminal requires a complete cursor")
        elif self.pause_reason is not None or self.terminal_outcome is not None:
            raise ValueError("ready/running states cannot carry pause or terminal data")


@dataclass(frozen=True)
class TransitionResult:
    state: RunState
    code: TransitionCode
    write_required: bool
    reason: str | None = None


def canonical_state_bytes(state: RunState) -> bytes:
    if type(state) is not RunState:
        raise TypeError("state must be a RunState")
    value = {
        "cursor_complete": state.cursor_complete,
        "generation_number": state.generation_number,
        "pause_reason": None if state.pause_reason is None else state.pause_reason.value,
        "phase": state.phase.value,
        "regime_epoch": state.regime_epoch,
        "terminal_outcome": (
            None if state.terminal_outcome is None else state.terminal_outcome.value
        ),
        "transition_number": state.transition_number,
    }
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _applied(state: RunState, **changes) -> TransitionResult:
    changes["transition_number"] = state.transition_number + 1
    return TransitionResult(replace(state, **changes), TransitionCode.APPLIED, True)


def _to_terminal(
    state: RunState,
    outcome: TerminalOutcome,
    code: TransitionCode,
    reason: str,
) -> TransitionResult:
    return TransitionResult(
        RunState(
            phase=RunPhase.TERMINAL,
            terminal_outcome=outcome,
            transition_number=state.transition_number + 1,
            generation_number=state.generation_number,
            regime_epoch=state.regime_epoch,
            cursor_complete=state.cursor_complete,
        ),
        code,
        True,
        reason,
    )


def _illegal(state: RunState, action: object, *, unknown: bool = False) -> TransitionResult:
    code = (
        TransitionCode.FAIL_CLOSED_UNKNOWN
        if unknown
        else TransitionCode.FAIL_CLOSED_ILLEGAL
    )
    return _to_terminal(
        state,
        TerminalOutcome.BLOCKED_PROTOCOL,
        code,
        f"unknown action: {action!r}" if unknown else f"illegal action: {action!r}",
    )


def transition(
    state: RunState,
    action: object,
    *,
    recovery_verified: bool = False,
    event_restart_verified: bool = False,
    next_cursor_complete: bool | None = None,
    closeout_passed: bool = False,
    block_outcome: TerminalOutcome | None = None,
) -> TransitionResult:
    """Evaluate every state/action pair without filesystem or process effects."""

    if type(state) is not RunState:
        raise TypeError("state must be a RunState")
    for name, value in (
        ("recovery_verified", recovery_verified),
        ("event_restart_verified", event_restart_verified),
        ("closeout_passed", closeout_passed),
    ):
        if type(value) is not bool:
            raise TypeError(f"{name} must be boolean")
    if next_cursor_complete is not None and type(next_cursor_complete) is not bool:
        raise TypeError("next_cursor_complete must be boolean or None")

    # Absorption is checked before decoding action, so even malformed input is
    # a byte-identical no-write self-loop for every terminal outcome.
    if state.phase is RunPhase.TERMINAL:
        return TransitionResult(
            state,
            TransitionCode.TERMINAL_NO_WRITE,
            False,
            "terminal state is absorbing",
        )
    if type(action) is not Action:
        return _illegal(state, action, unknown=True)
    if action is Action.INSPECT:
        return TransitionResult(state, TransitionCode.INSPECT_NO_WRITE, False)
    if action is Action.ABORT:
        return _to_terminal(
            state,
            TerminalOutcome.ABORTED_OPERATOR,
            TransitionCode.APPLIED,
            "operator abort",
        )
    if action is Action.BLOCK:
        if (
            type(block_outcome) is not TerminalOutcome
            or block_outcome is TerminalOutcome.COMPLETE_CANDIDATE_UNSEALED
        ):
            return _illegal(state, action)
        return _to_terminal(
            state, block_outcome, TransitionCode.APPLIED, "typed block"
        )

    if state.phase is RunPhase.READY:
        if action is Action.START:
            return _applied(state, phase=RunPhase.RUNNING)
        return _illegal(state, action)

    if state.phase is RunPhase.PAUSED:
        if action is Action.RESUME:
            return _applied(
                state,
                phase=RunPhase.RUNNING,
                pause_reason=None,
            )
        return _illegal(state, action)

    # The remaining nonterminal phase is RUNNING.
    if action is Action.RECOVER:
        if not recovery_verified:
            return _illegal(state, action)
        return _applied(state)
    if action is Action.ACCEPT:
        complete = (
            state.cursor_complete
            if next_cursor_complete is None
            else next_cursor_complete
        )
        return _applied(
            state,
            generation_number=state.generation_number + 1,
            cursor_complete=complete,
        )
    if action is Action.BISECT:
        return _applied(state)
    if action is Action.EVENT_RESTART:
        if not event_restart_verified:
            return _illegal(state, action)
        return _applied(
            state,
            generation_number=state.generation_number + 1,
            regime_epoch=state.regime_epoch + 1,
        )
    if action in {Action.PAUSE_ACCEPT_LIMIT, Action.PAUSE_ATTEMPT_LIMIT}:
        reason = (
            PauseReason.ACCEPT_LIMIT
            if action is Action.PAUSE_ACCEPT_LIMIT
            else PauseReason.ATTEMPT_LIMIT
        )
        return _applied(state, phase=RunPhase.PAUSED, pause_reason=reason)
    if action is Action.COMPLETE:
        if not state.cursor_complete or not closeout_passed:
            return _illegal(state, action)
        return _to_terminal(
            state,
            TerminalOutcome.COMPLETE_CANDIDATE_UNSEALED,
            TransitionCode.APPLIED,
            "cursor and closeout complete",
        )
    return _illegal(state, action)

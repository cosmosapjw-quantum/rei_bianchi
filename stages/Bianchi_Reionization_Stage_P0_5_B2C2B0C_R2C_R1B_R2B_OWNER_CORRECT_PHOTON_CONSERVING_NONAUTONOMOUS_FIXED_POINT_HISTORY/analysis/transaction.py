#!/usr/bin/env python3
"""Transactional accepted history for R1B-R2B.

An attempt runs against a detached scratch copy. It is committed only if it
completes without raising. Any failure — a fixed-point that did not converge, a
substep rejected by the positivity certificate, an event rollback — restores the
accepted state and ledger exactly.

`serialize()` gives a canonical byte image of the accepted history. Rollback is
verified against that image rather than against float comparisons, because a
rollback that restores a value one ulp away would pass `==` on the fields a
reviewer happens to check while still leaving residue in the accepted history.

Rolling back does not erase the attempt: every rejection is appended to
`failed_attempts`, matching the repository policy of preserving failed attempts.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, replace
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def _load_sibling(stem: str):
    """Load a sibling analysis module by path.

    These modules are executed via spec_from_file_location by the stage tests
    and drivers, so there is no package context for a plain import.
    """
    name = f"r2b_{stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).with_name(f"{stem}.py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LedgerSet = _load_sibling("ledgers").LedgerSet


class AttemptRejected(Exception):
    """Raised to reject an attempt and trigger rollback."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class FailedAttempt:
    reason: str
    exception_type: str
    rolled_back: bool


@dataclass
class Scratch:
    """Detached working copy handed to an attempt body."""

    state: object
    ledger: LedgerSet


class TransactionalHistory:
    def __init__(self, *, state: object, ledger: LedgerSet | None = None) -> None:
        self.state = state
        self.ledger = ledger if ledger is not None else LedgerSet()
        self.failed_attempts: list[FailedAttempt] = []

    def serialize(self) -> bytes:
        """Canonical byte image of the accepted state and ledger.

        `repr` is used for floats so the image distinguishes values that differ
        in the last bit; a rounded rendering would hide exactly the residue this
        is meant to catch.
        """
        state_fields = {
            name: repr(getattr(self.state, name))
            for name in (
                "N_HI",
                "N_HII",
                "N_HeI",
                "N_HeII",
                "N_HeIII",
                "U_resolved",
            )
        }
        ledger_fields = {k: repr(v) for k, v in sorted(self.ledger.snapshot().items())}
        return json.dumps(
            {"state": state_fields, "ledger": ledger_fields},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    @contextmanager
    def attempt(self, reason: str) -> Iterator[Scratch]:
        """Run an attempt against a detached copy; commit only on success."""
        saved_state = self.state
        saved_ledger = self.ledger.snapshot()

        scratch_ledger = LedgerSet()
        scratch_ledger.restore(saved_ledger)
        scratch = Scratch(state=replace(saved_state), ledger=scratch_ledger)

        try:
            yield scratch
        except BaseException as exc:
            # Accepted history is untouched: the attempt only ever mutated the
            # scratch copy. Restoring explicitly keeps that guarantee local
            # rather than relying on nothing else having aliased it.
            self.state = saved_state
            self.ledger.restore(saved_ledger)
            self.failed_attempts.append(
                FailedAttempt(
                    reason=reason,
                    exception_type=type(exc).__name__,
                    rolled_back=True,
                )
            )
            raise
        else:
            self.state = scratch.state
            self.ledger.restore(scratch.ledger.snapshot())

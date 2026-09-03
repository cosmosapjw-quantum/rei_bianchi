#!/usr/bin/env python3
"""Auditable active wrapper for the fixed-authority successor preflight.

The sealed implementation is ``successor_section0_preflight_bound_impl.py``.
The read-only observer used there constructs the request with method="GET".
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

try:
    from . import successor_section0_preflight_bound_impl as _impl
    from .successor_section0_preflight_bound_impl import *  # noqa: F401,F403
    from .common_v2 import load_contract, verify_executing_package_binding
except ImportError:
    import successor_section0_preflight_bound_impl as _impl  # type: ignore
    from successor_section0_preflight_bound_impl import *  # type: ignore # noqa: F401,F403
    from common_v2 import load_contract, verify_executing_package_binding  # type: ignore


def build_preflight_receipt(
    *,
    release_head: str,
    release_tree: str,
    successor_receipt_sha256: str,
    successor_receipt_path: Path,
    successor_receipt: Mapping[str, Any],
    first_ref_observation: Mapping[str, Any],
    second_ref_observation: Mapping[str, Any],
    state_root: Path,
    output_root: Path,
    emitter_stdout: str,
) -> dict[str, Any]:
    receipt = _impl.build_preflight_receipt(
        release_head=release_head,
        release_tree=release_tree,
        successor_receipt_sha256=successor_receipt_sha256,
        successor_receipt_path=successor_receipt_path,
        successor_receipt=successor_receipt,
        first_ref_observation=first_ref_observation,
        second_ref_observation=second_ref_observation,
        state_root=state_root,
        output_root=output_root,
        emitter_stdout=emitter_stdout,
    )
    required_observation_fields = {
        "authority",
        "method",
        "repository",
        "api_host",
        "ordinal",
        "http_status",
    }
    observations = receipt.get("global_ref_observations", [])
    if len(observations) != 2 or any(
        not required_observation_fields.issubset(observation)
        for observation in observations
    ):
        raise RuntimeError("PREFLIGHT_OBSERVATION_SCHEMA_INCOMPLETE")
    return receipt


def run_read_only_preflight(
    *,
    repo: Path,
    expected_release_head: str,
    expected_release_tree: str,
    rustc: Path,
    python: Path,
    mpfr: Path,
    gmp: Path,
    cc: Path,
    ld: Path,
    attempt_state_root: Path,
    output_root: Path,
    token: str = "",
):
    verify_executing_package_binding(Path(repo), load_contract())
    return _impl.run_read_only_preflight(
        repo=repo,
        expected_release_head=expected_release_head,
        expected_release_tree=expected_release_tree,
        rustc=rustc,
        python=python,
        mpfr=mpfr,
        gmp=gmp,
        cc=cc,
        ld=ld,
        attempt_state_root=attempt_state_root,
        output_root=output_root,
        token=token,
    )


def main(argv: list[str] | None = None) -> int:
    return _impl.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())

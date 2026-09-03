#!/usr/bin/env python3
"""Independent stdlib-only verifier for the read-only preflight package."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import urllib.error


PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
SUBJECT = PACKAGE / "successor_section0_preflight.py"


def load_subject():
    spec = importlib.util.spec_from_file_location(
        "rei_successor_preflight_independent", SUBJECT
    )
    if spec is None or spec.loader is None:
        raise SystemExit("PREFLIGHT_SUBJECT_IMPORT_SPEC_MISSING")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    subject = load_subject()
    subject.verify_package_index()
    contract = subject.load_contract()

    release = contract["executable_release"]
    assert release["commit"] == "eb1c05f3ea2bda910ddf85ef7f3bab08c73eca13"
    assert release["tree"] == "0aa13dd9cb8630f208307342a933a8c68abf62c8"
    assert contract["successor_section0"]["semantic_toolchain_lock_sha256"] == (
        "a3da50241ed6423212ab40c79f7810b5eaad042acdff29eb40f330aa39d2d4fa"
    )
    assert contract["attempt_state"]["remaining_before_reservation"] == 1
    assert contract["attempt_state"]["absence_is_authorization"] is False

    source = SUBJECT.read_text(encoding="utf-8")
    forbidden = (
        "acquire_global_lease(",
        "create_persistent_local_lease(",
        "reserve_then_dispatch(",
        "run_native_once(",
        'method="POST"',
        "git/refs",
    )
    for token in forbidden:
        assert token not in source, token
    assert 'method="GET"' in source
    assert "READ_ONLY_PREFLIGHT" in source

    def absent_opener(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", None, None)

    observed = subject.observe_global_ref_read_only(
        ref=contract["attempt_state"]["global_ref"],
        expected_target=release["commit"],
        opener=absent_opener,
    )
    assert observed["status"] == "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED"
    assert observed["authorization_effect"] == "NONE"
    assert observed["global_lease_acquired"] is False

    receipt = subject.build_preflight_receipt(
        release_head=release["commit"],
        release_tree=release["tree"],
        successor_receipt_sha256="1" * 64,
        first_ref_observation=observed,
        second_ref_observation=observed,
    )
    assert receipt["attempt_state"] == {
        "global_lease_acquired": False,
        "local_lease_created": False,
        "remaining_attempts": 1,
        "absence_is_authorization": False,
    }
    assert receipt["native_runtime"] == "NOT_RUN"
    assert receipt["claim_ceiling"]["first_interval"] == (
        "NO_PASS_FIRST_CANONICAL_INTERVAL"
    )

    wolfram = json.loads(
        (PACKAGE / "WOLFRAM_DAG_RECEIPT.json").read_text(encoding="utf-8")
    )
    assert wolfram["status"] == "PASS"
    assert all(wolfram["checks"].values())
    assert wolfram["authority_effect"] == "NONE"

    red = json.loads((PACKAGE / "TDD_RED_RECEIPT.json").read_text(encoding="utf-8"))
    assert red["workflow"]["tests_run"] == 12
    assert red["workflow"]["failures"] == 12
    assert red["attempt_state"]["remaining_attempts"] == 1

    render = subprocess.run(
        [sys.executable, "-I", "-S", "-B", str(PACKAGE / "render_preflight_state.py"), "--verify"],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if render.returncode != 0:
        raise SystemExit(
            "PREFLIGHT_STATE_RENDER_VERIFY_FAILED:"
            + render.stdout
            + render.stderr
        )

    print(
        json.dumps(
            {
                "status": "PASS",
                "package_entries": len(
                    json.loads((PACKAGE / "PACKAGE_INDEX.json").read_text())["entries"]
                ),
                "contract_release": release["commit"],
                "read_only_ref_observation": observed["status"],
                "remaining_attempts": 1,
                "native_runtime": "NOT_RUN",
                "wolfram_checks": len(wolfram["checks"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed validator for the REI thread-state consolidation package."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PACKAGE_REL = Path("docs/rei_thread_state_20260905")
INDEX_REL = PACKAGE_REL / "SOURCE_INDEX.json"
CONTRACT_REL = PACKAGE_REL / "AUDIT_COMPILED_WORK_UNIT.json"
STATE_REL = PACKAGE_REL / "CURRENT_STATE.json"
EVIDENCE_REL = PACKAGE_REL / "EVIDENCE_INDEX.json"
CLAIMS_REL = PACKAGE_REL / "CLAIM_LEDGER.csv"
EXPECTED_TERMINAL = "PASS_REI_THREAD_STATE_CONSOLIDATION_PACKAGE"


def fail(code: str, detail: str | None = None) -> "NoReturn":
    message = code if detail is None else f"{code}:{detail}"
    raise SystemExit(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("INVALID_JSON", f"{path}:{exc}")
    if not isinstance(value, dict):
        fail("JSON_ROOT_NOT_OBJECT", str(path))
    return value


def git(*args: str, root: Path) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        fail(
            "GIT_COMMAND_FAILED",
            f"{' '.join(args)}:rc={process.returncode}:{process.stderr.strip()}",
        )
    return process.stdout.strip()


def require_equal(actual: Any, expected: Any, name: str) -> None:
    if actual != expected:
        fail("VALUE_MISMATCH", f"{name}:expected={expected!r}:actual={actual!r}")


def validate_source_index(root: Path) -> tuple[int, set[str]]:
    index = load_json(root / INDEX_REL)
    require_equal(index.get("schema"), "rei-thread-state-source-index/v1", "index.schema")
    entries = index.get("entries")
    if not isinstance(entries, list) or not entries:
        fail("SOURCE_INDEX_ENTRIES_INVALID")

    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("SOURCE_INDEX_ENTRY_NOT_OBJECT")
        path_text = entry.get("path")
        expected_blob = entry.get("git_blob_sha")
        if not isinstance(path_text, str) or not path_text:
            fail("SOURCE_INDEX_PATH_INVALID")
        if not isinstance(expected_blob, str) or len(expected_blob) != 40:
            fail("SOURCE_INDEX_BLOB_INVALID", path_text)
        if path_text in seen:
            fail("SOURCE_INDEX_DUPLICATE_PATH", path_text)
        seen.add(path_text)
        path = root / path_text
        if not path.is_file():
            fail("SOURCE_INDEX_PATH_MISSING", path_text)
        actual_blob = git("hash-object", "--", path_text, root=root)
        require_equal(actual_blob, expected_blob, f"blob:{path_text}")

    if INDEX_REL.as_posix() in seen:
        fail("SOURCE_INDEX_SELF_CYCLE")
    return len(entries), seen


def validate_state(root: Path) -> None:
    state = load_json(root / STATE_REL)
    require_equal(state.get("schema"), "rei-thread-state-consolidation/v1", "state.schema")
    require_equal(state.get("repository"), "cosmosapjw-quantum/rei_bianchi", "state.repository")

    base = state["publication_base"]
    require_equal(base["pull_request"], 62, "state.publication_base.pull_request")
    require_equal(
        base["commit"],
        "01fd5ea775795d27758f354971ca478f90701295",
        "state.publication_base.commit",
    )
    require_equal(
        base["tree"],
        "d802eed60d98e5f2c32189ca0d358cb4f084df09",
        "state.publication_base.tree",
    )

    formula = state["formula_lane"]
    require_equal(formula["pull_request"], 62, "state.formula_lane.pull_request")
    require_equal(
        set(formula["status"]),
        {
            "PASS_REI_MATH_M1_GENERIC_SPATIAL_CURVATURE_SYMBOLIC_AUDIT",
            "PASS_REI_MATH_M1_PLOT_DRIVEN_SIGN_MUTATION_AUDIT",
        },
        "state.formula_lane.status",
    )
    require_equal(formula["native_runtime"] if "native_runtime" in formula else "NOT_RUN", "NOT_RUN", "formula.native_runtime")
    require_equal(
        formula["authority_effect_on_common_geometry_ownership"],
        "NONE",
        "formula.authority_effect",
    )

    runtime = state["runtime_lane"]
    require_equal(runtime["pull_request"], 59, "state.runtime_lane.pull_request")
    require_equal(
        runtime["commit"],
        "00d17c932eb41dbae6467e1e2fdf46818799d6db",
        "state.runtime_lane.commit",
    )
    require_equal(
        runtime["tree"],
        "4752300f2715fba6368811204d159a5d4c2f6465",
        "state.runtime_lane.tree",
    )
    require_equal(runtime["status"], "PASS_EXPECTED_RED_ONLY", "state.runtime_lane.status")

    live = state["live_server_state"]
    require_equal(live["ruleset"]["id"], 22240889, "state.ruleset.id")
    require_equal(live["ruleset"]["enforcement"], "active", "state.ruleset.enforcement")
    require_equal(live["ruleset"]["bypass_actors"], [], "state.ruleset.bypass_actors")
    require_equal(live["global_attempt_ref"]["fresh_http_status"], 404, "state.ref.http_status")
    require_equal(live["global_attempt_ref"]["state"], "ABSENT", "state.ref.state")

    auth = state["runtime_authorization"]
    exact = {
        "successor_section0": "NOT_RUN",
        "target_host_static_preflight": "NOT_RUN",
        "global_lease": "NOT_ACQUIRED",
        "persistent_local_lease": "NOT_CREATED",
        "dispatch_intent": "NOT_CREATED",
        "remaining_native_attempts": 1,
        "native_runtime": "NOT_RUN",
        "runtime_result_audit": "BLOCKED",
        "first_canonical_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
        "provider_export": "NOT_AUTHORIZED",
        "scientific_pass": "NOT_CLAIMED",
    }
    for key, expected in exact.items():
        require_equal(auth.get(key), expected, f"state.runtime_authorization.{key}")

    host = state["host_epoch"]
    require_equal(host["compiler_package"]["classification"], "PASS_LOCKED_CC_PACKAGE_IDENTIFIED_PROVENANCE_ONLY", "state.compiler.classification")
    require_equal(host["interactive_host_equal_to_locked_epoch"], False, "state.host_epoch.equal")
    require_equal(host["isolated_host_epoch"], "NOT_RECONSTRUCTED", "state.host_epoch.isolated")

    tools = state["fresh_external_tools"]
    require_equal(tools["wolfram_context"], "NO_RESULT_HTTP_502", "state.wolfram_context")
    require_equal(tools["wolfram_evaluator"], "NO_RESULT_HTTP_502", "state.wolfram_evaluator")


def validate_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root / CONTRACT_REL)
    require_equal(contract.get("schema"), "rei-audit-compiled-work-unit/v1", "contract.schema")
    require_equal(contract.get("work_unit"), "REI-THREAD-STATE-CONSOLIDATION-20260905-R1", "contract.work_unit")
    require_equal(contract["base"]["commit"], "01fd5ea775795d27758f354971ca478f90701295", "contract.base.commit")
    require_equal(contract["runtime_pin"]["commit"], "00d17c932eb41dbae6467e1e2fdf46818799d6db", "contract.runtime_pin.commit")
    require_equal(contract["required_claims"]["remaining_native_attempts"], 1, "contract.remaining_attempts")
    require_equal(contract["required_claims"]["native_runtime"], "NOT_RUN", "contract.native_runtime")
    require_equal(contract["claim_ceiling"]["publication"], "DRAFT_ONLY", "contract.publication")
    return contract


def validate_evidence(root: Path, contract: dict[str, Any]) -> int:
    evidence = load_json(root / EVIDENCE_REL)
    require_equal(evidence.get("schema"), "rei-thread-state-evidence-index/v1", "evidence.schema")
    entries = evidence.get("entries")
    if not isinstance(entries, list):
        fail("EVIDENCE_ENTRIES_INVALID")
    ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            fail("EVIDENCE_ENTRY_INVALID")
        if entry["id"] in ids:
            fail("EVIDENCE_DUPLICATE_ID", entry["id"])
        ids.add(entry["id"])
    missing = sorted(set(contract["required_evidence_ids"]) - ids)
    if missing:
        fail("REQUIRED_EVIDENCE_MISSING", ",".join(missing))
    return len(entries)


def validate_claims(root: Path, contract: dict[str, Any]) -> int:
    try:
        with (root / CLAIMS_REL).open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, UnicodeError, csv.Error) as exc:
        fail("CLAIM_LEDGER_INVALID", str(exc))
    required_columns = {
        "claim_id",
        "domain",
        "claim",
        "status",
        "evidence_class",
        "authority_effect",
        "next_gate",
    }
    if not rows or set(rows[0]) != required_columns:
        fail("CLAIM_LEDGER_COLUMNS_INVALID")
    ids: set[str] = set()
    for row in rows:
        claim_id = row["claim_id"].strip()
        if not claim_id or claim_id in ids:
            fail("CLAIM_LEDGER_DUPLICATE_OR_EMPTY", claim_id)
        ids.add(claim_id)
        for key in required_columns:
            if row[key] is None or not row[key].strip():
                fail("CLAIM_LEDGER_EMPTY_FIELD", f"{claim_id}:{key}")
    missing = sorted(set(contract["required_claim_ids"]) - ids)
    if missing:
        fail("REQUIRED_CLAIMS_MISSING", ",".join(missing))

    by_id = {row["claim_id"].strip(): row for row in rows}
    exact_status = {
        "REI-MATH-002": "PASS",
        "REI-MATH-008": "DEFERRED",
        "REI-MATH-010": "NOT_RUN",
        "REI-PHYS-004": "NO_PASS",
        "REI-PHYS-005": "NOT_AUTHORIZED",
        "REI-RUN-005": "ACTIVE",
        "REI-RUN-006": "ABSENT",
        "REI-RUN-010": "NOT_RUN",
        "REI-RUN-017": "NOT_RUN",
        "REI-RUN-018": "ONE",
        "REI-EXT-002": "NO_RESULT_HTTP_502",
        "REI-PUB-001": "NOT_AUTHORIZED",
    }
    for claim_id, expected in exact_status.items():
        actual = by_id[claim_id]["status"].strip()
        require_equal(actual, expected, f"claim:{claim_id}.status")
    return len(rows)


def validate_changed_paths(root: Path, contract: dict[str, Any]) -> list[str]:
    base = contract["base"]["commit"]
    git("merge-base", "--is-ancestor", base, "HEAD", root=root)
    changed_text = git("diff", "--name-only", f"{base}..HEAD", root=root)
    changed = [line for line in changed_text.splitlines() if line]
    if not changed:
        fail("NO_CHANGED_PATHS")
    allowed_workflow = ".github/workflows/rei-thread-state-consolidation.yml"
    prefix = PACKAGE_REL.as_posix() + "/"
    unexpected = [path for path in changed if path != allowed_workflow and not path.startswith(prefix)]
    if unexpected:
        fail("UNEXPECTED_CHANGED_PATHS", ",".join(unexpected))
    for forbidden_prefix in contract["forbidden_changed_prefixes"]:
        hits = [path for path in changed if path.startswith(forbidden_prefix)]
        if hits:
            fail("FORBIDDEN_CHANGED_PREFIX", f"{forbidden_prefix}:{','.join(hits)}")
    return changed


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    if not (root / ".git").exists():
        fail("REPOSITORY_ROOT_NOT_FOUND", str(root))

    contract = validate_contract(root)
    index_count, indexed_paths = validate_source_index(root)
    validate_state(root)
    evidence_count = validate_evidence(root, contract)
    claim_count = validate_claims(root, contract)
    changed = validate_changed_paths(root, contract)

    required_indexed = {
        (PACKAGE_REL / "README.md").as_posix(),
        STATE_REL.as_posix(),
        CONTRACT_REL.as_posix(),
        EVIDENCE_REL.as_posix(),
        CLAIMS_REL.as_posix(),
        (PACKAGE_REL / "validate_package.py").as_posix(),
        ".github/workflows/rei-thread-state-consolidation.yml",
    }
    missing_indexed = sorted(required_indexed - indexed_paths)
    if missing_indexed:
        fail("REQUIRED_SOURCE_INDEX_PATH_MISSING", ",".join(missing_indexed))

    result = {
        "status": EXPECTED_TERMINAL,
        "indexed_paths": index_count,
        "evidence_entries": evidence_count,
        "claim_rows": claim_count,
        "changed_paths": len(changed),
        "base_commit": contract["base"]["commit"],
        "runtime_pin": contract["runtime_pin"]["commit"],
        "ruleset_id": contract["required_claims"]["ruleset_id"],
        "global_attempt_ref": "ABSENT",
        "remaining_native_attempts": 1,
        "native_runtime": "NOT_RUN",
        "first_canonical_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
        "provider_export": "NOT_AUTHORIZED",
        "authority_effect": "STATE_DOCUMENTATION_AND_VALIDATION_ONLY",
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

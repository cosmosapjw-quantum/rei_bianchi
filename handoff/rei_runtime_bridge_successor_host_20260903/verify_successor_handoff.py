#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CONTRACT = json.loads((PACKAGE / "CONTRACT.json").read_text(encoding="utf-8"))
PROTOCOL = json.loads(
    (PACKAGE / "GLOBAL_ATTEMPT_LEASE_PROTOCOL_V2.json").read_text(encoding="utf-8")
)

assert CONTRACT["schema"] == "rei-runtime-successor-host-handoff/v1"
assert CONTRACT["immutable_governance_predecessor"]["commit"] == "ad4b3854cb52bc735b28fc828c09de1a3302bb0a"
assert CONTRACT["source_handoff"]["commit"] == "3169d1b0554193ababfb568406764d53df29649d"
assert CONTRACT["successor_section0"]["semantic_toolchain_lock_sha256"] == "a3da50241ed6423212ab40c79f7810b5eaad042acdff29eb40f330aa39d2d4fa"
assert CONTRACT["attempt_budget"]["remaining_native_attempts"] == 1
assert CONTRACT["attempt_budget"]["retries_after_outcome"] == 0
assert PROTOCOL["lease_target_relation"] == "EXACT_EXECUTABLE_RELEASE_HEAD"
assert PROTOCOL["mutation_policy"]["update_allowed"] is False
assert PROTOCOL["mutation_policy"]["delete_allowed"] is False

for relative, expected in {
    CONTRACT["source_handoff"]["base_runner_path"]: CONTRACT["source_handoff"]["base_runner_sha256"],
    CONTRACT["source_handoff"]["patched_input_lock_path"]: CONTRACT["source_handoff"]["patched_input_lock_sha256"],
    CONTRACT["source_handoff"]["production_bridge_path"]: CONTRACT["source_handoff"]["production_bridge_sha256"],
    f'{CONTRACT["source_handoff"]["rust_stage_path"]}/rust/source_bound_thermal.rs': CONTRACT["source_handoff"]["rust_source_sha256"],
}.items():
    path = ROOT / relative
    assert path.is_file() and not path.is_symlink(), relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative

source = (PACKAGE / "successor_runtime_runner.py").read_text(encoding="utf-8")
ast.parse(source)
assert source.index("global_acquire=global_acquire") < source.index("native_dispatch=native_dispatch")
assert "PASS_IMMUTABLE_SECTION_0" not in source
assert "PASS_EQUIVALENT_SECTION_0_SUCCESSOR" not in source
assert "REI_NATIVE_DISPATCH_FORBIDDEN" in source
assert "os.O_EXCL" in source
assert "method=\"POST\"" in source
assert "retry" not in source.lower() or "retries" in source.lower()

index = json.loads((PACKAGE / "PACKAGE_INDEX.json").read_text(encoding="utf-8"))
assert index["schema"] == "rei-runtime-successor-handoff-package-index/v1"
assert len(index["entries"]) == len({row["path"] for row in index["entries"]})
for row in index["entries"]:
    path = PACKAGE / row["path"]
    payload = path.read_bytes()
    blob = hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()
    assert blob == row["blob_sha"], row["path"]

print(json.dumps({
    "status": "PASS",
    "package_entries": len(index["entries"]),
    "source_bindings": 4,
    "remaining_native_attempts": 1,
    "native_runtime": "NOT_RUN",
}, sort_keys=True))

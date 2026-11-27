"""Read-only scope/source check before the authorized z=3.5 output exists."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

EXPECTED = {
    "engine": ("research/r31ad_five_node/unit_cell_model.py", "ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0"),
    "adaptive_policy": ("research/r31af_adaptive/adaptive_policy.py", "720b221a9e01ab7fc1bbd482b600ea785fed0b8c6b80b5834c576a75c2b70756"),
    "global_model": ("research/r31z_source_bound/source_bound.py", "4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034"),
    "six_node_manifest": ("research/r31af_adaptive/ncp_followup_20260929/SIX_NODE_INPUT_MANIFEST.json", "e444e9f1cff7d4cc9425a2f44ff45a6e87199c6bf31ca2b095010364379e7573"),
    "z35_selection": ("research/r31af_adaptive/ncp_followup_20260929/Z35_PREDICTION_SELECTION.json", "546026387ecae9952b0397fb0dd26ad0633465739d8bbb82878f0f4c532c545e"),
    "decision_rule": ("research/r31af_adaptive/ncp_followup_20260929/FROZEN_Z35_DECISION_RULE.json", "52b995b2f5516cf586cf1cbcdb681ec521f1b911a7538e3999a11d0f3bd62560"),
    "preregistration": ("research/r31af_adaptive/ncp_followup_20260929/NEXT_VALIDATION_PREREGISTRATION.json", "ec4613f5300ec38a488eae75f5c7267a2f1a166c34e45d54bb9fa8b449537447"),
    "post_z35_policy": ("research/r31ah_post_z35/POST_Z35_DECISION_POLICY.json", "b7d9928e23d1f3cd8abf0fe7be34a5868d6760bfab388ac626bab6c1c524dbc8"),
    "post_z35_policy_helper": ("research/r31ah_post_z35/post_validation_policy.py", "78af28d506edd3e7dedcb3257f10258ee1ed4477a8cabe7d78ecb1945142f6a5"),
}
PRODUCER = {
    "completion/mixed_h/od_run.py": "63c0925ff938340feceb5768aba40da348b3afe323214a9792012e9d0bbc664d",
    "completion/mixed_h/h0_backend.py": "128e13bd475ce6aeb57e3c601239318e00f6bfbfee6f99a85ba081aa97b1a9e5",
    "completion/mixed_h/h0_fused.cpp": "d019713f8a9c6e864d60cc796104a0cdef629e491e6ab8de757995aa4f3672f2",
    "completion/mixed_h/native.py": "44f784c895730d07e5a40ccc5369534f6a8e81798689a27c98a0bf5fd0a2d778",
    "completion/mixed_derivative/run.py": "d092d3e81a952d90488f25922c57ea3148b9f036d15a884f7efe51ade09de935",
    "completion/mixed_derivative/native.py": "247c9eca3c8cfa35a437f48b4ba72aac98d24dff1bc336b008058141b591a22d",
    "completion/mixed_derivative/jvp.cpp": "2ea30233fb959ec916427d672d4b7180347f4689a036ae393da6073078892cbd",
    "completion/mixed_derivative/CONTRACT.json": "f5a10ef22dd5aefade7e9d9dc079066c0b3e0781a9c997411997cb67ba0acb66",
    "cont2c/convergence/frozen_grid_n192.npz": "e1959e1bbb66b5e27410daa3d3bdb0815885919f11af3a014d86a47f15b96301",
    "inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz": "8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c",
}
SCOPE_SHA = "f43faaf5746a5fda5cd26593ee69e97c0f2be8239727a62081d49357e3c2a9b4"
ARCHIVE_SHA = "c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    for key in ("repo", "runtime", "archive", "out"):
        ap.add_argument("--" + key, required=True, type=Path)
    a = ap.parse_args()
    repo, runtime = a.repo.resolve(), a.runtime.resolve()
    gate_path = repo / "research/r31ag_z35_gate/authorization_gate.py"
    spec = importlib.util.spec_from_file_location("r31ag_gate_frozen", gate_path)
    assert spec is not None and spec.loader is not None
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    scope = json.loads((repo / "research/r31ag_z35_gate/AUTHORIZATION_SCOPE.json").read_text())
    scope_sha = gate.canonical_sha256(scope)
    envelope = {"schema": gate.SCHEMA, "authorize": True, "action": gate.ACTION, "scope_sha256": SCOPE_SHA, "one_shot": True}
    valid, reason = gate.validate_envelope(envelope)
    hashes = {key: sha(repo / rel) for key, (rel, _) in EXPECTED.items()}
    producer_hashes = {rel: sha(runtime / rel) for rel in PRODUCER}
    archive_sha = sha(a.archive)
    with zipfile.ZipFile(a.archive) as z:
        existing_archive_members = [name for name in z.namelist() if name.startswith(("completion/mixed_h/od/B192_z3.5/", "completion/mixed_derivative/B192_z3.5/"))]
    prior_dirs = [str(runtime / rel) for rel in ("completion/mixed_h/od/B192_z3.5", "completion/mixed_derivative/B192_z3.5") if (runtime / rel).exists()]
    prereg = json.loads((repo / EXPECTED["preregistration"][0]).read_text())
    rule = json.loads((repo / EXPECTED["decision_rule"][0]).read_text())
    policy = json.loads((repo / EXPECTED["post_z35_policy"][0]).read_text())
    checks = {
        "scope_canonical_sha": scope_sha == SCOPE_SHA,
        "envelope_valid_current_affirmative_directive": valid,
        "frozen_hashes": all(hashes[k] == v[1] for k, v in EXPECTED.items()),
        "producer_hashes": all(producer_hashes[k] == v for k, v in PRODUCER.items()),
        "producer_archive": archive_sha == ARCHIVE_SHA,
        "tolerance": prereg["comparison_tolerance"] == rule["comparison_tolerance"] == scope["comparison_tolerance"] == 1e-10,
        "selected_node": prereg["selected_z_a0"] == scope["selected_z_a0"] == 3.5 and prereg["radial_order"] == scope["radial_order"] == 192,
        "exact_three_verdicts": set(prereg["future_verdicts"]) == set(policy["verdicts"]) == {"PARETO_SUPPORTED_AT_Z35", "GLOBAL_SUPPORTED_AT_Z35", "TRADEOFF_UNRESOLVED"},
        "no_prior_local_or_archive_z35": not existing_archive_members and not prior_dirs,
    }
    result = {"schema": "WU088_R31AG_AUTHORIZED_Z35_PREFLIGHT_V1", "status": "AUTHORIZED_PREFLIGHT_PASSED" if all(checks.values()) else "AUTHORIZATION_SCOPE_DRIFT", "checks": checks, "envelope_validation_reason": reason, "canonical_scope_sha256": scope_sha, "frozen_hashes": hashes, "producer_hashes": producer_hashes, "archive_sha256": archive_sha, "existing_archive_z35_members": existing_archive_members, "existing_local_z35_paths": prior_dirs, "output_access_before_preflight": False, "science_commands_started": 0, "science_node_count": 0}
    if a.out.exists():
        raise FileExistsError(a.out)
    a.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()

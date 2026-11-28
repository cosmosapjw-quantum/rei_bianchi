#!/usr/bin/env python3
"""Portable, read-only byte and recorded-JSON identity checks; no science kernels."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def bits(value):
    return struct.pack(">d", value).hex()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; choose a new path")
    checks = []
    for row in read("SNAPSHOT_INDEX.json"):
        data = (ROOT / row["path"]).read_bytes()
        assert len(data) == row["bytes"], row["path"]
        assert sha256(data) == row["sha256"], row["path"]
        assert git_blob(data) == row["git_blob"], row["path"]
        checks.append({"path": row["path"], "identity": "PASS"})
    for row in read("SOURCE_LINE_BINDINGS.json"):
        data = (ROOT / row["path"]).read_bytes()
        lines = data.splitlines(keepends=True)
        first, last = row["lines"]
        segment = b"".join(lines[first - 1:last])
        assert len(b"".join(lines[:first - 1])) == row["byte_start"]
        assert len(b"".join(lines[:last])) == row["byte_end_exclusive"]
        assert sha256(segment) == row["segment_sha256"], row["id"]
        assert git_blob(data) == row["git_blob"], row["id"]
    source_identity = read("inherited/PHYS02_INPUT_IDENTITY.json")
    for original, local in [
        ("inputs/SELECTED_SOURCE.json", "history/SELECTED_SOURCE.json"),
        ("inputs/source/coupled_primary.rs", "source/coupled_primary.rs"),
    ]:
        row = next(x for x in source_identity["files"] if x["path"] == original)
        data = (ROOT / local).read_bytes()
        assert sha256(data) == row["sha256"] and len(data) == row["bytes"]
    binding = read("source/FINAL_SOURCE_BINDING_V4.json")
    for name in [
        "paired_runtime.rs", "hh_paired_extension.rs", "angular_photons.rs",
        "bianchi_i.rs", "adaptive_history.rs", "atomic_provider.rs",
        "coupled_primary.rs",
    ]:
        assert sha256((ROOT / "source" / name).read_bytes()) == binding["original_owner_sources"][name]
    assert sha256((ROOT / "source/owner_birth.rs").read_bytes()) == binding["candidate_sources"]["src/owner_birth.rs"]
    selected = read("history/SELECTED_SOURCE.json")
    records = [json.loads(line) for line in (ROOT / "history/OWNER_PREBE_FINAL_BINARY.jsonl").read_text().splitlines()]
    half1 = next(r for r in records if r["member"] == 1 and r["label"] == "half1_preBE")
    full = next(r for r in records if r["member"] == 1 and r["label"] == "full_preBE")
    half2 = next(r for r in records if r["member"] == 1 and r["label"] == "half2_birth_weights_only")
    assert half1["indices"] == list(range(25))
    selected_bits = [bits(x) for x in selected["old_point_photons"]]
    half1_bits = [bits(half1["groups"][k]) for k in half1["indices"]]
    full_bits = [bits(full["groups"][k]) for k in full["indices"]]
    assert selected_bits == half1_bits
    assert selected_bits != full_bits
    assert bits(selected["time_s"]) == bits(half1["endpoint_time"]) == bits(160625000000.0)
    assert bits(selected["dt_s"]) == bits(625000000.0)
    assert bits(half1["initial_time"]) == bits(160000000000.0)
    assert half1["source_bits"] == "3cf6849b86a12b9b"
    assert half1["birth_energy_bits"] == "402b666666666666"
    assert half1["native_roundtrip"] is True and half1["root_dispatch"] == 0
    assert half2["half2_incoming_state"] is None
    assert selected["energies_ev"][16] == 13.6 and selected["sigma_cm2"][16][0] > 0
    assert all(all(v == 0 for v in row) for row in selected["sigma_cm2"][:16])
    identity = read("latest_owner/MODEL_AND_CORNER_IDENTITY.json")
    root = read("latest_owner/ROOT_PRECONDITIONER_BINDING.json")
    birth = read("latest_owner/BIRTH_SCHEME_LEDGER.json")
    assert identity["future_corner_proposal"]["native_parameter_source_family_implemented"] is False
    assert identity["future_corner_proposal"]["actual_corner_receipts"] is None
    assert root["trusted_native_root"] is None and root["trusted_native_parameter_tube"] is None
    assert root["native_preconditioner"] is None
    assert birth["accepted_half1_receipt"] is None and birth["source_law"]["half2_state"] is None
    result = {
        "status": "PASS_RECORDED_SOURCE_IDENTITY_ONLY",
        "source_snapshot_checks": checks,
        "source_line_bindings_checked": len(read("SOURCE_LINE_BINDINGS.json")),
        "selected_linkage": {
            "member": 1, "row_1based": 5, "stage": "half1_preBE",
            "all_25_photon_binary64_values_equal": True,
            "full_preBE_not_equal": True,
            "initial_time_s": half1["initial_time"],
            "endpoint_time_s": half1["endpoint_time"],
            "dt_s": selected["dt_s"],
            "source_bits": half1["source_bits"],
            "birth_energy_bits": half1["birth_energy_bits"],
            "selected_photon_binary64_hex": selected_bits,
            "independent_seed_gas_decode_performed": False,
            "not_a_continuous_state_certificate": True,
        },
        "native_science_runs": 0, "BE_root_calls": 0, "IVP_runs": 0,
        "NCP_runs": 0, "legacy_integrations": 0, "remote_mutations": 0,
        "not_a_physics_or_final_decision_review": True,
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "snapshots": len(checks), "line_bindings": result["source_line_bindings_checked"]}))


if __name__ == "__main__":
    main()

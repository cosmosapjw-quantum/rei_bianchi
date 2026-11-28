"""Prepare three hash-bound NCP-only prefix requests; run no certifier or RHS."""
import datetime
import hashlib
import json
from pathlib import Path
import sys


BASE = Path("/workspace/scratch/61913f66989c")
SOURCE = BASE/"phys77_audit/source/export_owner.py"
EXPECTED = "7ebf5f8699d9e58dcc7c2eec4bddd99cf9c9cd1d3999aa923890ae784de5b707"
DEST = BASE/"phys77_audit/pending_requests"
CASES = [
    ("mixed_s+0_m-1", "request_mixed_s0_mminus1_4cells.json"),
    ("mixed_s+1_m+1", "request_mixed_splus1_mplus1_4cells.json"),
    ("mixed_s-1_m-1", "request_mixed_sminus1_mminus1_4cells.json"),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, content):
    with path.open("x") as stream:
        json.dump(content, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    if json.loads(path.read_text()) != content:
        raise AssertionError("PREPARATION_METADATA_READBACK_MISMATCH")


def main():
    if sha(SOURCE) != EXPECTED:
        raise ValueError("PINNED_EXPORTER_CHANGED")
    if DEST.exists():
        raise FileExistsError("REFUSE_EXISTING_PENDING_REQUEST_DIRECTORY")
    DEST.mkdir(parents=True)
    sys.path.insert(0, str(SOURCE.parent))
    import export_owner as exporter
    owner = BASE/"upstream_inputs/rei198_verified/repo_payload/research/rei_bianchi_sigma_pi_pilot_20261021"
    repo = BASE/"WU088_HH_PHYS77"
    index = BASE/"upstream_inputs/REI198_TERMINAL_STATES.json"
    prepared = []
    for case_id, filename in CASES:
        table = exporter.export_owner(repo, owner, index, case_id)
        request = exporter.prepare_request(table, owner, predictor_nodes=5)
        request["config"]["max_cells"] = 4
        receipt = exporter.write_request(DEST/filename, request)
        loaded = json.loads((DEST/filename).read_text())
        exporter.validate_table(loaded["table"])
        if (loaded != request or loaded["table"]["provenance"]["case_identity"]["case_id"] != case_id
                or loaded["config"]["max_cells"] != 4 or len(loaded["predictor"]["x"]) != 5):
            raise AssertionError("PREPARED_REQUEST_READBACK_MISMATCH")
        prepared.append({
            "case_id": case_id, "filename": filename,
            "sha256": receipt["file_sha256"], "size_bytes": (DEST/filename).stat().st_size,
            "request_content_sha256": receipt["content_sha256"],
            "table_sha256": table["table_sha256"],
            "status": "READY_NOT_RUN", "predictor_nodes": 5, "requested_prefix_cells": 4,
            "prefix_x": [request["predictor"]["x"][0], request["predictor"]["x"][-1]],
            "initial_kind": request["initial"]["kind"],
            "config": request["config"],
            "source_identity": table["provenance"], "runtime": table["runtime"],
            "model_profile": table["profile"],
            "mass_exact_decimal": table["constants"]["mass"],
            "amplitude_exact_decimal": table["constants"]["amplitude"],
            "export_readback": receipt,
        })
    if sha(SOURCE) != EXPECTED:
        raise ValueError("PINNED_EXPORTER_CHANGED_DURING_PREPARATION")
    preparation = {
        "schema": "PHYS77_NCP_PREFIX_REQUEST_PREPARATION_V1",
        "status": "READY_NOT_RUN", "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "exporter_source_sha256": EXPECTED, "preparation_script_sha256": sha(__file__),
        "method": "Pinned exporter reconstructs frozen coefficient tables and reads hash-bound original raw nodes; no interval owner, RHS, certifier or solver is invoked",
        "future_execution_target": "NCP only, within available shared resources",
        "cases": prepared,
        "new_ODE_solves": 0, "old_ODE_replays": 0, "rhs_calls": 0,
        "interval_evaluations": 0, "certification_attempts": 0, "benchmark_runs": 0, "NCP_jobs": 0,
        "full_history_certificate": False,
        "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
    }
    receipt_path = DEST/"PREPARATION_RECEIPT.json"
    write_new(receipt_path, preparation)
    payload = []
    for path in sorted(DEST.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.is_symlink():
            raise ValueError("NONREGULAR_REQUEST_PAYLOAD")
        payload.append({"filename": path.name, "sha256": sha(path), "size_bytes": path.stat().st_size})
    manifest = {
        "schema": "PHYS77_PENDING_NCP_REQUEST_MANIFEST_V1", "status": "READY_NOT_RUN",
        "purpose": "Future carry-forward finite-prefix whole-cell checks from existing saved trajectories; not new ODE solves and not a full-history promise",
        "request_count": 3, "prefix_cells_per_request": 4, "predictor_nodes_per_request": 5,
        "requests": [{key: row[key] for key in ("case_id", "filename", "sha256", "size_bytes", "request_content_sha256", "table_sha256", "requested_prefix_cells", "prefix_x", "status")} for row in prepared],
        "payload_files": payload, "payload_file_count": len(payload),
        "total_request_bytes": sum(row["size_bytes"] for row in prepared),
        "total_payload_bytes_excluding_manifest": sum(row["size_bytes"] for row in payload),
        "self_contained_inputs": True,
        "future_runner_requires_original_raw_history_or_constructor": False,
        "profile": {"source": "captured exact-real finite-L8 REI198 owner coefficients", "kinetic_cells": [24, 12], "gauss_order": 3, "packet_shape": [72, 36], "packet_count": 2592, "mass": "30", "lane": "MIXED_CANCELLATION"},
        "separate_physical_scopes": ["REI PR213 warm 729 histories", "HH74 63 controls"],
        "new_ODE_solves": 0, "rhs_calls": 0, "interval_evaluations": 0,
        "certification_attempts": 0, "benchmark_runs": 0, "NCP_jobs": 0,
        "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
    }
    manifest_path = DEST/"MANIFEST.json"
    write_new(manifest_path, manifest)
    print(json.dumps({"status": "READY_NOT_RUN", "manifest_path": str(manifest_path),
                      "manifest_sha256": sha(manifest_path),
                      "manifest_size_bytes": manifest_path.stat().st_size,
                      "total_directory_bytes": sum(path.stat().st_size for path in DEST.iterdir()),
                      "total_request_bytes": manifest["total_request_bytes"],
                      "total_payload_bytes_excluding_manifest": manifest["total_payload_bytes_excluding_manifest"],
                      "requests": manifest["requests"]}, indent=2))


if __name__ == "__main__":
    main()

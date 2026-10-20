#!/usr/bin/env python3
"""Create-only Unit B closeout from already executed evidence; no native calls."""
import argparse
import ast
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity(path, relative_to=None):
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(relative_to)) if relative_to else str(path),
        "bytes": len(data), "sha256": digest(data),
        "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
        "git_mode": "100755" if path.stat().st_mode & 0o111 else "100644",
    }


def inventory(root):
    paths = sorted(p for p in root.rglob("*") if p.is_file())
    assert all(not p.is_symlink() for p in paths)
    assert all(not ({"target", "__pycache__"} & set(p.relative_to(root).parts)) for p in paths)
    return [identity(p, root) for p in paths]


def put(path, obj):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run19-root", required=True, type=Path)
    ap.add_argument("--unit-a-snapshot", required=True, type=Path)
    ap.add_argument("--runtime-root", required=True, type=Path)
    args = ap.parse_args()
    root, old, runtime = args.run19_root.resolve(), args.unit_a_snapshot.resolve(), args.runtime_root.resolve()
    out, native = root / "execution/unit_b", root / "native"
    final_names = ["SOURCE_AFTER_MANIFEST.json", "NATIVE_DIFF_FROM_UNIT_A.patch",
                   "ORIGINAL_SOURCE_IMMUTABLE_CHECK.json", "CORE_BENCH_SUMMARY.json",
                   "BINARY_IDENTITIES.json", "REPRODUCE_COMMANDS.json", "UNIT_B_RECEIPT.json"]
    assert all(not (out / name).exists() for name in final_names), "closeout is create-only"
    assert not (runtime / "unit_b_bin").exists(), "binary preservation is create-only"
    freeze_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    base = json.loads((root / "inventory/BASE_NATIVE_MANIFEST.json").read_text())
    original = root.parent / "run13/recovered/code/rei_bass_coupled"
    original_actual = inventory(original)
    assert len(original_actual) == base["file_count"] == 91
    for row in base["files"]:
        found = identity(original / row["path"], original)
        assert all(found[key] == row[key] for key in ("bytes", "sha256", "git_blob")), row["path"]
    original_check = {"schema": "REI_RUN19_UNIT_B_ORIGINAL_IDENTITY_V1", "checked_utc": freeze_utc,
        "source_commit": base["source_commit"], "source_tree": base["source_tree"],
        "manifest": identity(root / "inventory/BASE_NATIVE_MANIFEST.json", root),
        "exact_files": 91, "extra_files": 0, "modified_files": 0,
        "status": "IMPLEMENTATION_VERIFIED", "scope": "read-only SHA256/Git-blob inventory, no tests or IVP"}
    native_rows, cubic_rows = inventory(native), inventory(root / "rate_cubic")
    old_rows = {r["path"]: r for r in inventory(old)}
    new_rows = {r["path"]: r for r in native_rows}
    changes, patches = [], []
    for name in sorted(set(old_rows) | set(new_rows)):
        before, after = old_rows.get(name), new_rows.get(name)
        if before == after:
            continue
        assert after is not None, "Unit B must not delete a Unit A source file"
        changes.append({"path": name, "kind": "ADDED" if before is None else "MODIFIED",
                        "before": before, "after": after})
        a = [] if before is None else (old / name).read_text().splitlines(keepends=True)
        b = (native / name).read_text().splitlines(keepends=True)
        patches.extend(difflib.unified_diff(a, b, fromfile="unit_a/native/" + name,
                                           tofile="unit_b/native/" + name))
    package_copy = json.loads((out / "CUBIC_PACKAGE_COPY.json").read_text())
    assert len(cubic_rows) == len(package_copy["files"]) == 6
    for row in package_copy["files"]:
        actual = identity(root / "rate_cubic" / row["path"])
        assert actual["bytes"] == row["new_bytes"] and actual["sha256"] == row["new_sha256"]
    wrapper = (native / "src/cubic_igm.rs").read_bytes()
    match = re.search(rb'const POLICY:&\[u8\]=(b"[^"\n]*");', wrapper)
    assert match is not None
    parts = [ast.literal_eval(match.group(1).decode()), (native / "owner_src/igm_rates.rs").read_bytes(),
             (native / "owner_src/rate_table.rs").read_bytes(), (root / "rate_cubic/src/lib.rs").read_bytes(), wrapper]
    bound_id = digest(b"".join(len(part).to_bytes(8, "little") + part for part in parts))
    compare = json.loads((out / "point_compare01/GAS_COMPARISON.json").read_text())
    cache = json.loads((out / "cache_probe01/CACHE_PROBE.json").read_text())
    assert bound_id == compare["metadata"]["cubic_source_id"]
    assert all(row["metadata"]["cubic_source_id"] == bound_id for row in cache["runs"])
    for row in compare["input_identities"]:
        assert identity(Path(row["path"]))["sha256"] == row["sha256"]
    for row in cache["runs"]:
        assert identity(Path(row["cache_identity"]["path"]))["sha256"] == row["cache_identity"]["sha256"]
    source_manifest = {"schema": "REI_RUN19_UNIT_B_SOURCE_MANIFEST_V1", "frozen_utc": freeze_utc,
        "source_commit": base["source_commit"], "unit_a_snapshot_native": str(old),
        "native_file_count": len(native_rows), "native_files": native_rows,
        "rate_cubic_file_count": len(cubic_rows), "rate_cubic_files": cubic_rows,
        "cubic_cache_source_id": bound_id, "changes_from_unit_a": changes,
        "source_binding_verified_against_executed_metadata": True,
        "generic_package_copy_verified": True}
    bench = json.loads((out / "core_measure01/stdout.txt").read_text())
    assert bench["unit_b"] and not bench["probe"] and bench["ivps"] == 0 and len(bench["rows"]) == 32
    compact = []
    for row in bench["rows"]:
        assert row["n"] == 4096 and len(row["seconds"]) == 5
        ns = [s / row["evaluations_per_repetition"] * 1e9 for s in row["seconds"]]
        compact.append({key: row[key] for key in ("pattern", "backend", "mode", "unique_eos_temperature_bits", "median_ns_per_rhs")} |
                       {"min_ns_per_rhs": min(ns), "max_ns_per_rhs": max(ns)})
    bench_summary = {"schema": "REI_RUN19_UNIT_B_CORE_SUMMARY_V1", "raw": identity(out / "core_measure01/stdout.txt", root),
        "command": identity(out / "core_measure01/COMMAND.json", root), "rows": compact,
        "timed_gas_evaluations": sum(r["evaluations_per_repetition"] * 5 for r in bench["rows"]),
        "untimed_warmup_gas_evaluations": sum(r["n"] for r in bench["rows"]),
        "counts_basis": "recorded row sizes and one explicit warmup loop in the frozen benchmark source",
        "table_build_seconds": bench["table_build_seconds"], "cubic_build_seconds": bench["cubic_build_seconds"],
        "table_payload_bytes": bench["table_payload_bytes"], "cubic_payload_bytes": bench["cubic_payload_bytes"],
        "method": "one bounded process; fixed mode order; same executable; affinity 0-3; 5 repetitions; preallocated outputs; thread start/join included",
        "limitations": ["shared CPU host", "no frequency lock or randomized mode order",
                        "min/max are observed ranges, not confidence intervals", "no universal or whole-trajectory speedup inferred"], "ivps": 0}
    bin_dir = runtime / "unit_b_bin"
    bin_dir.mkdir()
    binaries = []
    for name in ("gas_rhs_server", "run19_gas_bench", "run19_gas_compare"):
        producer = runtime / "target_unit_b/release/examples" / name
        dest = bin_dir / name
        data = producer.read_bytes()
        with dest.open("xb") as stream:
            stream.write(data)
        dest.chmod(0o755)
        row = identity(dest)
        row["producer_path"] = str(producer)
        row["producer_sha256"] = digest(data)
        binaries.append(row)
    assert binaries[0]["sha256"] == cache["binary_identity"]["sha256"]
    assert binaries[2]["sha256"] == compare["binary_identity"]["sha256"]
    binary_receipt = {"schema": "REI_RUN19_UNIT_B_BINARIES_V1", "frozen_utc": freeze_utc, "binaries": binaries,
        "build_receipt": identity(out / "examples_build01/COMMAND.json", root),
        "compiler_receipt": identity(root / "execution/unit_a/runtime/rustc_version.stdout.txt", root),
        "flags": "release defaults; RUSTFLAGS empty; no target-cpu override; no fast math",
        "scope": "actual produced bytes copied for archive; executable identity is separate from source and cache identity"}
    commands = []
    for path in sorted(out.glob("*/COMMAND.json")):
        receipt = json.loads(path.read_text())
        assert receipt["exit_code"] == 0 and not receipt["timed_out"], path
        commands.append({"receipt": identity(path, root), "argv": receipt["argv"],
                         "cwd": receipt["cwd"], "environment_overrides": receipt["environment_overrides"],
                         "wall_seconds": receipt["wall_seconds"]})
    safe_commands = [
        {"cwd": "{RUN19}/native", "argv": ["{PREFIX}/bin/cargo", "test", "--release", "--offline", "--locked", "--jobs", "2", "--target-dir", "{NEW_TARGET}", "--test", "run19_cubic_integration", "--example", "gas_rhs_server"]},
        {"cwd": "{RUN19}/native", "argv": ["{PREFIX}/bin/cargo", "build", "--release", "--offline", "--locked", "--jobs", "2", "--target-dir", "{NEW_TARGET}", "--example", "gas_rhs_server", "--example", "run19_gas_bench", "--example", "run19_gas_compare"]},
        {"cwd": "{RUN19}/native", "argv": ["python", "-B", "examples/run19_compare_retained.py", "--binary", "{NEW_TARGET}/release/examples/run19_gas_compare", "--inputs", "{RUN19}/execution/unit_a/evidence/unit_a_ipc_measure01/IPC_INPUTS.json.gz", "--unit-a-replies", "{RUN19}/execution/unit_a/evidence/unit_a_ipc_measure01/IPC_REPLIES.json.gz", "--output", "{NEW_OUTPUT}/point_compare"]},
        {"cwd": "{RUN19}/native", "argv": ["python", "-B", "examples/run19_cache_probe.py", "--binary", "{NEW_TARGET}/release/examples/gas_rhs_server", "--inputs", "{RUN19}/execution/unit_a/evidence/unit_a_ipc_measure01/IPC_INPUTS.json.gz", "--output", "{NEW_OUTPUT}/cache_probe"]},
        {"cwd": "{RUN19}/native", "argv": ["taskset", "-c", "0-3", "{NEW_TARGET}/release/examples/run19_gas_bench", "--unit-b", "--target-evaluations", "8192", "--repetitions", "5"], "wall_time_cap_seconds": 10},
    ]
    reproduce = {"schema": "REI_RUN19_UNIT_B_COMMANDS_V1", "producer_commands": commands,
        "portable_commands": safe_commands,
        "required_environment": {"PATH": "{PREFIX}/bin plus existing PATH", "LD_LIBRARY_PATH": "{PREFIX}/lib",
                                 "RUSTC": "{PREFIX}/bin/rustc", "RUSTDOC": "{PREFIX}/bin/rustdoc",
                                 "CARGO_HOME": "{EXPLICIT_CARGO_CACHE}", "CARGO_NET_OFFLINE": "true", "RUSTFLAGS": ""},
        "required_inputs": compare["input_identities"],
        "requirements": ["Rust 1.94.1 x86_64-unknown-linux-gnu, Linux taskset for the recorded CPU assignment",
                         "pinned Cargo.lock dependencies present in explicit Cargo cache before offline compilation",
                         "RUN13 original crate at the retained canonical relative path",
                         "new output and target directories; do not overwrite frozen evidence",
                         "wrapper script producer defaults are historical absolute paths; portable argv above supplies new paths"],
        "no_execution_by_closeout": True}
    receipt = {"schema": "REI_RUN19_UNIT_B_RECEIPT_V1", "frozen_utc": freeze_utc,
        "source_commit": base["source_commit"], "source_tree": base["source_tree"],
        "native_file_count": len(native_rows), "rate_cubic_file_count": len(cubic_rows),
        "changed_native_files": len(changes), "original_files_verified_unchanged": 91,
        "cubic_cache_source_id": bound_id, "table_domain_kelvin": [1.0, 1e6], "default_cubic_nodes": 32769,
        "implementation": ["opt-in Cubic backend reuses one bound PreparedIgmRates for HHe and D",
                           "T-only coefficient grid and exact-temperature workspace cache contain no density/source state",
                           "Direct remains default; STEP/full-network integration stays Direct",
                           "same physical source coefficients, thresholds, diagnostics, gas and energy assembly",
                           "source-byte-bound create-only cache with explicit META identity and rejection"],
        "actual_tests": {"new_native_integration_passed": 4, "existing_relevant_server_tests_passed": 2,
                         "failures": 0, "full_native_suite_run": False,
                         "test_names_evidence": "native_tests01/stdout.txt"},
        "actual_experiments": {"retained_point_inputs": compare["point_inputs"],
            "native_gas_point_evaluations": compare["native_gas_evaluations"],
            "extra_direct_d_point_evaluations": compare["extra_direct_d_evaluations_for_denominators"],
            "old_output_float_bits_equal": compare["unit_a_output_float_bits_equal"],
            "cache_point_evaluations": cache["gas_rhs_point_evaluations"],
            "core_timed_gas_evaluations": bench_summary["timed_gas_evaluations"],
            "core_warmup_gas_evaluations": bench_summary["untimed_warmup_gas_evaluations"],
            "test_internal_call_counts": "not instrumented; excluded from the explicit experiment counts",
            "ivps": 0, "full_ipc_benchmarks_repeated": 0},
        "point_results": {"maxima": {name: [r for r in values if r["channel"] in (1, 3, 10, 11, 12, 13, 27)]
                                      for name, values in compare["maxima"].items()},
                          "ledgers": compare["ledgers"],
                          "hydrogen_flux_cancellation_condition": compare["max_flux_cancellation_condition"][1],
                          "chemical_flux_cancellation_condition": compare["max_flux_cancellation_condition"][27]},
        "cache_results": {"bytes": cache["runs"][0]["cache_identity"]["bytes"],
                          "sha256": cache["runs"][0]["cache_identity"]["sha256"],
                          "cold_seconds": cache["runs"][0]["wall_seconds"], "warm_seconds": cache["runs"][1]["wall_seconds"],
                          "reply_bytes_equal": cache["warm_cold_reply_bytes_identical"],
                          "wrong_source_exit": cache["wrong_source"]["exit_code"],
                          "wrong_source_error": cache["wrong_source"]["stderr"]},
        "established_scope": ["IMPLEMENTATION_VERIFIED: the named tests, compatibility and cache controls",
                              "NUMERICALLY_CHECKED: finite manufactured-point errors, conditioning and timings"],
        "limits": ["coefficient interpolation accuracy is not a solution or spectral convergence bound",
                   "point flux conditioning does not enclose a gas Jacobian or a whole trajectory",
                   "cache SHA and source ID are integrity/compatibility checks, not producer authentication",
                   "safe Rust kernel has no newly introduced explicit SIMD or FMA; only measured behavior reported",
                   "same-temperature cache hits make interpolation choice less important",
                   "fixed-order shared-host benchmark has timing variability; no further measurements were made",
                   "generic prototype tests and broader coefficient scan are separately owned root evidence, not rerun here"],
        "known_errors": [{"kind": "EXPECTED_NEGATIVE_CONTROL", "result": "wrong source cache rejected before any RHS output", "preserved": "cache_probe01/wrong_source.*"},
                         {"kind": "MEASUREMENT_LIMIT", "result": "varying-temperature cubic batch1 and batch2 show host noise; raw ranges retained"}],
        "publication_status": "root-owned; this receipt records local frozen evidence, not a remote completion claim",
        "backup_status": "root-owned; archive/remote hashes will be in separate delivery receipt",
        "next_node": "single scoped source/math review; then root publication; continuous floating-point/table-to-trajectory error control remains separate"}
    put(out / final_names[0], source_manifest)
    with (out / final_names[1]).open("x", encoding="utf-8") as stream:
        stream.writelines(patches)
    put(out / final_names[2], original_check)
    put(out / final_names[3], bench_summary)
    put(out / final_names[4], binary_receipt)
    put(out / final_names[5], reproduce)
    put(out / final_names[6], receipt)
    print(json.dumps({"status": "FROZEN_FROM_RECORDED_EVIDENCE", "native_files": len(native_rows),
                      "cubic_files": len(cubic_rows), "changes_from_unit_a": len(changes),
                      "source_id": bound_id, "receipt": identity(out / "UNIT_B_RECEIPT.json"),
                      "binaries": binaries, "native_calls_in_closeout": 0, "ivps": 0}, indent=2))


if __name__ == "__main__":
    main()

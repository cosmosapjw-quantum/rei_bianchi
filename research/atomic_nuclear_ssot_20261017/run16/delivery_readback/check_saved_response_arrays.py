#!/usr/bin/env python3
"""RUN16 Git payload and raw-array aggregate readback; no scientific rerun.

This reader imports only NumPy for its NPZ storage format. It never imports the
RUN16 physics code, generates quadrature nodes, evaluates geometry/opacity,
calls a native RHS, or advances any IVP. Scalar libm and math.fsum reconstruct
the aggregate quantities from already-stored source weights and optical depths.
"""
from pathlib import Path, PurePosixPath
import datetime as dt
import hashlib
import json
import math
import os
import platform
import re
import stat
import struct
import subprocess
import sys
import time
import traceback
import zipfile

import numpy as np

ROOT = Path("/tmp/rei_run16_work/readback")
REPO = ROOT / "git_checkout"
RELATIVE = "research/atomic_nuclear_ssot_20261017/run16"
SOURCE = REPO / RELATIVE
EXPECTED_COMMIT = "2cc5e0862dbe9770ef83c0b2437e27627ec26524"
EXPECTED_TREE = "e27bea710a9e398311c6728fcbe22625a93e13e2"
EXPECTED_PARENT = "c875005e30d9de1ce7f426898e46fe912068412c"
EXPECTED_NPZ = "a3ded41cfd4ff7184e14b6bbaee1da865b52ada81ab3553eb2d49222fae425c6"
EXPECTED_MANIFEST_BLOB = "e9e2dc53a3bfb4e89b18911d5e2e35692b8193df"

def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")

def identity(path):
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("ordinary file required: " + str(path))
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("file changed during read: " + str(path))
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}

def safe_file(root, name):
    if not name or "\\" in name or "\0" in name or PurePosixPath(name).is_absolute():
        raise ValueError("invalid relative path")
    if any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("unsafe relative path")
    path = root.joinpath(*name.split("/"))
    if root.resolve() not in path.resolve().parents or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("path escapes root or contains a symlink")
    return path

def main():
    started = time.monotonic()
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    receipt = {"schema": "rei.run16.delivery_git_readback_check.v1", "status": "IN_PROGRESS",
               "remote_commit": EXPECTED_COMMIT, "remote_tree": EXPECTED_TREE, "remote_parent": EXPECTED_PARENT,
               "remote_commit_url": "https://github.com/cosmosapjw-quantum/rei_bianchi/commit/" + EXPECTED_COMMIT,
               "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "checkout": str(REPO), "script_identity": identity(Path(__file__)),
               "exact_command": [sys.executable, "-B", str(Path(__file__).resolve())],
               "environment": {"python": platform.python_version(), "numpy": np.__version__,
                               "platform": platform.platform(), "executable": sys.executable},
               "scope": "Git-only exact checkpoint restoration and raw saved E16/T32 array aggregates",
               "native_rhs_calls": 0, "native_IVP_runs": 0, "quadrature_generation_or_integration_runs": 0,
               "tests_rerun": 0, "old_archive_downloads": 0, "canonical_repo_modified": False,
               "new_prefix_solves_audited": False, "commands": []}
    def git(name, arguments):
        argv = ["git", *arguments]
        result = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, timeout=30)
        stdout, stderr = ROOT / (name + ".stdout.txt"), ROOT / (name + ".stderr.txt")
        with stdout.open("xb") as stream:
            stream.write(result.stdout)
        with stderr.open("xb") as stream:
            stream.write(result.stderr)
        row = {"stage": name, "argv": argv, "cwd": str(REPO), "exit_code": result.returncode,
               "environment_overrides": {"GIT_OPTIONAL_LOCKS": "0", "PYTHONDONTWRITEBYTECODE": "1"},
               "stdout": {"path": stdout.name, **identity(stdout)}, "stderr": {"path": stderr.name, **identity(stderr)}}
        receipt["commands"].append(row)
        if result.returncode:
            raise RuntimeError("read-only Git command failed: " + name)
        return result.stdout

    def source_snapshot(label):
        raw = git(label, ["ls-tree", "-r", "-z", EXPECTED_COMMIT, "--", RELATIVE])
        rows = []
        for line in raw.split(b"\0"):
            if not line:
                continue
            info, path_raw = line.split(b"\t", 1)
            mode, kind, blob = info.decode().split()
            relative = path_raw.decode()
            if kind != "blob" or mode not in ("100644", "100755"):
                raise ValueError("unexpected source Git entry")
            path = safe_file(REPO, relative)
            got = identity(path)
            got_mode = "100755" if path.stat().st_mode & 0o111 else "100644"
            if got["git_blob"] != blob or got_mode != mode:
                raise ValueError("source differs from Git: " + relative)
            rows.append({"path": relative.removeprefix(RELATIVE + "/"), "mode": mode, **got})
        save(ROOT / (label + ".json"), {"files": rows, "commit": EXPECTED_COMMIT})
        return rows

    failure = None
    before = None
    try:
        if git("READBACK_HEAD", ["rev-parse", "HEAD"]).decode().strip() != EXPECTED_COMMIT:
            raise ValueError("unexpected checkout HEAD")
        if git("READBACK_TREE", ["rev-parse", "HEAD^{tree}"]).decode().strip() != EXPECTED_TREE:
            raise ValueError("unexpected checkout tree")
        commit = git("READBACK_COMMIT", ["cat-file", "-p", EXPECTED_COMMIT]).decode()
        parents = [line[7:] for line in commit.splitlines() if line.startswith("parent ")]
        if parents != [EXPECTED_PARENT]:
            raise ValueError("checkpoint parent differs")
        receipt["git_index_before"] = identity(REPO / ".git/index")
        before = source_snapshot("SOURCE_BEFORE")
        manifest_path = SOURCE / "CHECKPOINT_MANIFEST.json"
        manifest_id = identity(manifest_path)
        if manifest_id["git_blob"] != EXPECTED_MANIFEST_BLOB:
            raise ValueError("checkpoint manifest differs from remotely read Git blob")
        manifest = json.loads(manifest_path.read_bytes())
        expected = set()
        checks = []
        for row in manifest["files"]:
            name = row["path"]
            if name in expected or name == "CHECKPOINT_MANIFEST.json":
                raise ValueError("duplicate/self manifest entry")
            expected.add(name)
            actual = identity(safe_file(SOURCE, name))
            if actual["bytes"] != row["bytes"] or actual["sha256"] != row["sha256"]:
                raise ValueError("payload manifest mismatch: " + name)
            checks.append({"path": name, **actual, "manifest_hash_and_size_match": True})
        actual_paths = {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob("*") if p.is_file()}
        if any(p.is_symlink() for p in SOURCE.rglob("*")) or actual_paths != expected | {"CHECKPOINT_MANIFEST.json"}:
            raise ValueError("restored source file inventory differs from manifest")
        if {r["path"] for r in before} != actual_paths:
            raise ValueError("scoped Git and manifest file sets differ")
        receipt["checkpoint_manifest"] = manifest_id
        receipt["payload_verification"] = {"manifest_entries": len(checks), "all_manifest_hashes_match": True,
                                           "total_files_including_manifest": len(actual_paths),
                                           "payload_bytes_excluding_manifest": sum(r["bytes"] for r in checks),
                                           "files": checks}
        result_path = SOURCE / "results/GAS_PATH_RESPONSE.json"
        result = json.loads(result_path.read_bytes())
        raw_path = SOURCE / "results/RESPONSE_NODES_E16_T32.npz"
        raw_id = identity(raw_path)
        if (raw_id["sha256"] != EXPECTED_NPZ or raw_id["bytes"] != 1824562
                or raw_id["sha256"] != result["raw_quadrature_nodes"]["sha256"]):
            raise ValueError("raw NPZ byte identity mismatch")
        with zipfile.ZipFile(raw_path) as archive:
            entries = archive.infolist()
            if len({i.filename for i in entries}) != len(entries):
                raise ValueError("duplicate NPZ members")
            for info in entries:
                name = info.filename
                if ("/" in name or "\\" in name or not name.endswith(".npy") or info.flag_bits & 1
                        or stat.S_ISLNK((info.external_attr >> 16) & 0xffff)):
                    raise ValueError("unsafe NPZ entry")
            if archive.testzip() is not None:
                raise ValueError("NPZ CRC mismatch")
        with np.load(raw_path, allow_pickle=False) as archive:
            data = {name: archive[name].copy() for name in archive.files}
        declared = result["raw_quadrature_nodes"]["arrays"]
        if set(data) != set(declared):
            raise ValueError("unexpected raw array keys")
        array_rows = {}
        for name, array in data.items():
            if list(array.shape) != declared[name]["shape"] or str(array.dtype) != declared[name]["dtype"]:
                raise ValueError("raw array shape/dtype mismatch: " + name)
            if not np.isfinite(array).all():
                raise ValueError("nonfinite saved array")
            array_rows[name] = {"shape": list(array.shape), "dtype": str(array.dtype),
                                "uncompressed_C_order_sha256": hashlib.sha256(array.tobytes(order="C")).hexdigest()}
        n = len(data["energy_eV"])
        if (n != 35088 or data["source_measure_com3"].shape != (n,) or data["baseline_tau"].shape != (n,)
                or np.any(data["source_measure_com3"] <= 0) or np.any(data["baseline_tau"] < 0)
                or np.any((data["ray"] < 0) | (data["ray"] >= 640))
                or set(data["binding_bin"].tolist()) != {0, 1}
                or np.any(np.diff(data["common_gas_knots"]) <= 0)
                or np.any(data["time_interval_sensitivity_com3"] < 0)):
            raise ValueError("saved positive-response schema invalid")
        row = result["runs"][-1]
        if (row["energy_order"], row["time_order"], row["energy_nodes"]) != (16, 32, n):
            raise ValueError("raw result is not the declared final E16/T32 run")
        measure = list(map(float, data["source_measure_com3"]))
        tau = list(map(float, data["baseline_tau"]))
        values = [m * math.exp(-t) for m, t in zip(measure, tau)]
        total = math.fsum(values)
        first = math.fsum(v * t for v, t in zip(values, tau))
        second = math.fsum(v * t * t for v, t in zip(values, tau))
        comparisons = []
        def add(name, recorded, reconstructed):
            recorded, reconstructed = float(recorded), float(reconstructed)
            delta = reconstructed - recorded
            comparisons.append({"field": name, "recorded": recorded, "reconstructed": reconstructed,
                                "absolute_difference": abs(delta), "signed_difference": delta,
                                "relative_difference_recorded_denominator": None if recorded == 0 else delta / recorded,
                                "difference_in_recorded_ULPs": abs(delta) / math.ulp(recorded),
                                "bit_identical": struct.pack(">d", recorded) == struct.pack(">d", reconstructed)})
        add("moments/S_com3", row["moments"]["S_com3"], total)
        add("moments/uniform_relative_density_elasticity_magnitude",
            row["moments"]["uniform_relative_density_elasticity_magnitude"], first / total)
        add("moments/second_relative_density_derivative_over_S",
            row["moments"]["second_relative_density_derivative_over_S"], second / total)
        add("uniform_directional_derivative_com3",
            row["directional_derivative_check"][0]["analytic_derivative_com3"], -first)
        for b in (0, 1):
            pairs = [(v, t) for v, t, label in zip(values, tau, data["binding_bin"]) if int(label) == b]
            sb = math.fsum(v for v, _ in pairs)
            ab = math.fsum(v * t for v, t in pairs)
            bb = math.fsum(v * t * t for v, t in pairs)
            for key, got in (("S_com3", sb), ("uniform_relative_density_elasticity_magnitude", ab / sb),
                             ("second_relative_density_derivative_over_S", bb / sb)):
                add(f"binding_bins/{b}/{key}", row["binding_bins"][str(b)][key], got)
        bump = math.fsum(v * float(b) for v, b in zip(values, data["delta_tau_bump"]))
        add("knot_invisible_bump/directional_elasticity_magnitude",
            row["knot_invisible_bump"]["directional_elasticity_magnitude"], bump / total)
        dstd = list(map(float, data["delta_tau_standard"]))
        linear = -math.fsum(v * d for v, d in zip(values, dstd))
        finite_delta = math.fsum(v * math.expm1(-d) for v, d in zip(values, dstd))
        add("standard_minus_tight_fixed_support/linear_delta_S_com3",
            row["standard_minus_tight_fixed_support"]["linear_delta_S_com3"], linear)
        add("standard_minus_tight_fixed_support/delta_S_com3",
            row["standard_minus_tight_fixed_support"]["delta_S_com3"], finite_delta)
        add("standard_minus_tight_fixed_support/relative_change_baseline_denominator",
            row["standard_minus_tight_fixed_support"]["relative_change_baseline_denominator"], finite_delta / total)
        intervals = list(map(float, data["time_interval_sensitivity_com3"]))
        if (len(intervals) != len(row["time_sensitivity"])
                or len(data["common_gas_knots"]) != len(intervals) + 1):
            raise ValueError("time sensitivity array shape mismatch")
        interval_record_bits = all(struct.pack(">d", v) == struct.pack(">d", float(r["minus_dS_d_relative_density_com3"]))
                                   for v, r in zip(intervals, row["time_sensitivity"]))
        interval_knots_match = all(float(data["common_gas_knots"][i]) == r["left_z"]
                                   and float(data["common_gas_knots"][i+1]) == r["right_z"]
                                   for i, r in enumerate(row["time_sensitivity"]))
        if not interval_record_bits or not interval_knots_match:
            raise ValueError("stored time sensitivities do not match published result rows")
        interval_sum = math.fsum(intervals)
        receipt["raw_NPZ"] = {**raw_id, "CRC_all_members_valid": True, "npz_members": len(entries),
                              "arrays": array_rows, "node_count": n, "allow_pickle": False}
        receipt["aggregate_reconstruction"] = {
            "method": "Independent Python scalar math.exp/expm1 and math.fsum; stored source measure and tau only",
            "producer_method": "NumPy exp, sum and BLAS dot; no producer code imported here",
            "comparison_fields": len(comparisons), "fields": comparisons,
            "maximum_relative_difference": max(abs(r["relative_difference_recorded_denominator"] or 0) for r in comparisons),
            "maximum_recorded_ULP_difference": max(r["difference_in_recorded_ULPs"] for r in comparisons),
            "diagnostic_threshold_not_imposed": True,
            "S_com3": total, "minus_uniform_density_derivative_com3": first,
            "uniform_elasticity": first / total, "second_derivative_over_S": second / total,
            "knot_invisible_bump_elasticity": bump / total,
            "time_partition": {"stored_interval_count": len(intervals), "all_28_recorded_coefficients_bit_identical": interval_record_bits,
                               "all_interval_knots_match": interval_knots_match,
                               "fsum_stored_interval_sensitivities_com3": interval_sum,
                               "per_node_uniform_sensitivity_com3": first,
                               "signed_difference_com3": interval_sum - first,
                               "relative_difference": (interval_sum - first) / first,
                               "limitation": "Per-interval coefficients are preserved aggregate arrays. Their individual optical integrals cannot be independently reconstructed without the unstored per-node interval tau matrix."},
            "scientific_scope": "Only final E16/T32 stored finite-support response; neither new quadrature nor gas/feedback/continuum accuracy certificate"}
        receipt["source_identity_history"] = {
            "canonical_source": identity(SOURCE / "gas_path_response.py"),
            "preserved_initial_source": identity(SOURCE / "history/gas_path_response_executed.py"),
            "recorded_change": json.loads((SOURCE / "history/SOURCE_IDENTITY.json").read_bytes())["change"],
            "history_and_canonical_verified_by_checkpoint_manifest": True,
            "source_versions_not_conflated": True}
        receipt["status"] = "VERIFIED_GIT_DELIVERY_AND_RAW_ARRAY_RECONSTRUCTION"
    except Exception as exc:
        failure = exc
        receipt.update(status="FAILED_OR_BLOCKED", error_type=type(exc).__name__, error=str(exc),
                       traceback=traceback.format_exc())
    finally:
        if before is not None:
            try:
                after = source_snapshot("SOURCE_AFTER")
                index = identity(REPO / ".git/index")
                receipt["source_unchanged"] = {"all_tracked_bytes_and_modes_unchanged": before == after,
                                             "tracked_files": len(after),
                                             "Git_index_unchanged": index == receipt["git_index_before"],
                                             "Git_index_after": index}
                if before != after or index != receipt["git_index_before"]:
                    raise ValueError("source or Git index changed during readback")
            except Exception as exc:
                failure = failure or exc
                receipt.update(status="FAILED_OR_BLOCKED", source_check_error=str(exc))
        receipt["wall_seconds"] = time.monotonic() - started
        save(ROOT / "DELIVERY_READBACK_CHECK.json", receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(ROOT / "DELIVERY_READBACK_CHECK.json"),
                      "manifest_entries": receipt.get("payload_verification", {}).get("manifest_entries"),
                      "raw_NPZ_sha256": receipt.get("raw_NPZ", {}).get("sha256"),
                      "aggregate": {k: receipt.get("aggregate_reconstruction", {}).get(k) for k in
                          ("S_com3", "uniform_elasticity", "second_derivative_over_S", "comparison_fields",
                           "maximum_relative_difference", "maximum_recorded_ULP_difference")},
                      "error": receipt.get("error")}, indent=2), flush=True)
    return 0 if failure is None else 1

if __name__ == "__main__":
    raise SystemExit(main())

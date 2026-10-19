#!/usr/bin/env python3
"""Reproduce only the published postloss scope from an exact fresh Git checkout.

Restores original RUN13 bytes, runs five fixed-gas quadratures, builds two
native binaries in fresh external targets, and runs three source-measure CLI
controls. No original/new native IVP or optional test suite is invoked.
The pre-loss strict117/four-case restoration protocol is deliberately unused.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import struct
import subprocess
import sys
import time
import traceback

PREFIX = "research/atomic_nuclear_ssot_20261017"
SCOPES = [PREFIX + "/run13", PREFIX + "/run15"]
EXPECTED_D = "6405bcba8ec654bf3ab98182be344cd8c3915b97"
EXPECTED_TREE = "be7a8473202b1800bc9f0dcdd3351e187fe32063"
HASHES = {
    "restore": "821591b7a7dc90f1610c6f0dbf301862fa8ed489a9367993455d4ca8bce1ebdd",
    "checksum": "ae0e9818db6a9ec5047a0b3fd72cb92bf8bd0384c5ef73de385094e5a9a05b15",
    "source_map": "7d04e35d4f77e7ee07e7e969f7a79e03623dbdbde33306dea54014202c172036",
    "diagnostic": "f95c99ce30c886f9bff26744b00d6617b3a0f39661fec97c4cec1fb285f9d968",
    "native_binary": "ec88048296f47a4683595aeddcafe2453cfef85bdada53189143913b076e8f66",
    "gas_binary": "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b",
}
ENV_KEYS = ["PYTHONDONTWRITEBYTECODE", "GIT_OPTIONAL_LOCKS", "GIT_TERMINAL_PROMPT",
            "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
            "PATH", "LD_LIBRARY_PATH", "RUSTC", "CARGO_HOME",
            "CARGO_TARGET_DIR", "CARGO_NET_OFFLINE"]

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def save(path, data):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())

def file_id(path):
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("ordinary file required: " + str(path))
    before = path.stat()
    sha = hashlib.sha256()
    blob = hashlib.sha1(b"blob " + str(before.st_size).encode("ascii") + b"\0")
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(part)
            blob.update(part)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("file changed while hashing: " + str(path))
    return {"bytes": before.st_size, "sha256": sha.hexdigest(), "git_blob": blob.hexdigest()}

def safe_path(root, name):
    if not isinstance(name, str) or not name or "\\" in name or "\0" in name:
        raise ValueError("invalid relative manifest path")
    if PurePosixPath(name).is_absolute() or any(x in ("", ".", "..") for x in name.split("/")):
        raise ValueError("unsafe manifest path: " + name)
    path = root.joinpath(*name.split("/"))
    if root.resolve() not in path.resolve().parents:
        raise ValueError("path escaped root")
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("symlink in manifest path")
    return path

def numeric_fields(value, prefix=""):
    result = {}
    if isinstance(value, bool):
        return result
    if isinstance(value, (float, int)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("nonfinite number: " + prefix)
        result[prefix] = value
    elif isinstance(value, dict):
        for key in sorted(value):
            if key not in ("wall_seconds",):
                result.update(numeric_fields(value[key], prefix + "/" + key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.update(numeric_fields(item, prefix + "/" + str(index)))
    return result

def compare_numeric(expected, actual):
    left, right = numeric_fields(expected), numeric_fields(actual)
    rows = []
    for key in sorted(set(left) | set(right)):
        a, b = left.get(key), right.get(key)
        match = key in left and key in right and type(a) is type(b) and a == b
        if match and isinstance(a, float):
            match = struct.pack(">d", a) == struct.pack(">d", b)
        row = {"field": key, "published": a, "reproduced": b, "exact_numeric_match": match}
        if a is not None and b is not None:
            row["difference"] = b - a
        rows.append(row)
    return {"fields": len(rows), "exact_matches": sum(r["exact_numeric_match"] for r in rows),
            "missing_fields": sorted(set(left) - set(right)), "extra_fields": sorted(set(right) - set(left)),
            "all_numeric_fields_match_exactly": bool(rows) and all(r["exact_numeric_match"] for r in rows),
            "float_comparison": "identical IEEE754 binary64 representation, including sign of zero",
            "excluded_numeric_keys": ["wall_seconds"], "comparisons": rows}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--toolchain-prefix", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--stage-root", required=True, type=Path)
    parser.add_argument("--stage-manifest", required=True, type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    prefix = args.toolchain_prefix.resolve(strict=True)
    output = args.output_root.absolute()
    stage = args.stage_root.resolve(strict=True)
    stage_manifest = args.stage_manifest.resolve(strict=True)
    if output.exists() or output.is_symlink() or output == repo or repo in output.parents:
        raise ValueError("new external output root required")
    output.mkdir(parents=True)
    (output / "logs").mkdir()
    env = dict(os.environ)
    env.update(PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0",
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    run13 = repo / PREFIX / "run13"
    source = run13 / "recovered"
    run15 = repo / PREFIX / "run15"
    native = run15 / "postloss_native"
    diagnostic = run15 / "postloss_diagnostic"
    owner = source / "code/rei_bass_coupled"
    receipt = {"schema": "rei.run15.postloss.scoped_clean_reproduction.v1", "status": "IN_PROGRESS",
               "started_at_utc": now(), "science_commit": EXPECTED_D, "science_tree": EXPECTED_TREE,
               "repo": str(repo), "output_root": str(output), "script": file_id(Path(__file__)),
               "command_argv": [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:]],
               "environment": {"python": platform.python_version(), "executable": sys.executable,
                               "platform": platform.platform(),
                               "controlled_values": {k: env[k] for k in ENV_KEYS if k in env}},
               "scope": "Fresh exact-D Git checkout, original333 Git restoration, five published fixed-gas settings, fresh offline native builds, three source-measure controls",
               "not_established": ["preloss strict117/four-case archive restoration",
                                   "lost RUN15 raw 342-case-file recovery",
                                   "coupled spectral continuum error bound",
                                   "true gas history between archived checkpoints"],
               "old_and_new_native_IVP_runs": 0, "optional_or_full_test_suite_runs": 0,
               "preloss_strict_verifier_used": False, "commands": []}
    def run(name, argv, cwd=repo, timeout=120, custom_env=None):
        actual_env = env if custom_env is None else custom_env
        argv = [str(x) for x in argv]
        stdout = output / "logs" / (name + ".stdout.txt")
        stderr = output / "logs" / (name + ".stderr.txt")
        row = {"stage": name, "argv": argv, "cwd": str(cwd), "started_at_utc": now(),
               "environment": {k: actual_env[k] for k in ENV_KEYS if k in actual_env}}
        save(output / "logs" / (name + ".request.json"), row)
        print(json.dumps({"stage": name, "status": "STARTED"}), flush=True)
        start = time.monotonic()
        try:
            with stdout.open("xb") as out, stderr.open("xb") as err:
                process = subprocess.run(argv, cwd=cwd, env=actual_env, stdin=subprocess.DEVNULL,
                                         stdout=out, stderr=err, timeout=timeout)
            row["exit_code"] = process.returncode
        except Exception as exc:
            row.update(exit_code=None, error_type=type(exc).__name__, error=str(exc))
        row.update(seconds=time.monotonic() - start,
                   stdout={"path": str(stdout.relative_to(output)), **file_id(stdout)},
                   stderr={"path": str(stderr.relative_to(output)), **file_id(stderr)})
        receipt["commands"].append(row)
        save(output / "logs" / (name + ".command.json"), row)
        print(json.dumps({"stage": name, "exit_code": row["exit_code"], "seconds": row["seconds"]}), flush=True)
        if row["exit_code"] != 0:
            raise RuntimeError("command failed or timed out: " + name)
        return stdout.read_bytes()

    def scoped_snapshot(label):
        raw = run(label, ["git", "ls-tree", "-r", "-z", EXPECTED_D, "--", *SCOPES])
        rows = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            metadata, path_raw = record.split(b"\t", 1)
            mode, kind, git_blob = metadata.decode().split()
            rel = path_raw.decode()
            if kind != "blob" or mode not in ("100644", "100755"):
                raise ValueError("unexpected Git object type")
            path = safe_path(repo, rel)
            actual = file_id(path)
            actual_mode = "100755" if path.stat().st_mode & 0o111 else "100644"
            if git_blob != actual["git_blob"] or actual_mode != mode:
                raise ValueError("tracked file differs from selected Git commit: " + rel)
            rows.append({"path": rel, "mode": mode, **actual})
        if not rows:
            raise ValueError("empty tracked source scope")
        save(output / (label + ".json"), {"commit": EXPECTED_D, "files": rows})
        return rows

    before = None
    failure = None
    try:
        head = run("01_head", ["git", "rev-parse", "HEAD"]).decode().strip()
        tree = run("02_tree", ["git", "rev-parse", "HEAD^{tree}"]).decode().strip()
        if head != EXPECTED_D or tree != EXPECTED_TREE:
            raise ValueError("exact published D checkout required")
        receipt["git_head_verified"] = head
        receipt["git_tree_verified"] = tree
        receipt["index_before"] = file_id(repo / ".git/index")
        before = scoped_snapshot("03_git_source_before")

        staged = json.loads(stage_manifest.read_bytes())
        if staged["science_commit"] != EXPECTED_D or len(staged["files"]) != 159:
            raise ValueError("expected exact-D 159-file stage manifest")
        stage_rows = []
        seen = set()
        for row in staged["files"]:
            name = row["path"]
            if name in seen:
                raise ValueError("duplicate stage path")
            seen.add(name)
            actual = file_id(safe_path(run15, name))
            staged_id = file_id(safe_path(stage, name))
            for key in ("bytes", "sha256", "git_blob"):
                if actual[key] != row[key] or staged_id[key] != row[key]:
                    raise ValueError("stage/Git/manifest mismatch: " + name)
            stage_rows.append({"path": name, **actual, "stage_equals_Git_bytes": True})
        tracked_run15 = {r["path"].split("/run15/", 1)[1] for r in before if "/run15/" in r["path"]}
        if tracked_run15 != seen:
            raise ValueError("stage159 inventory does not equal published run15 file inventory")
        stage_report = {"schema": "rei.run15.science_stage_clean_git_match.v1", "science_commit": EXPECTED_D,
                        "manifest": file_id(stage_manifest), "stage_root": str(stage),
                        "published_files_verified": len(stage_rows),
                        "total_bytes": sum(r["bytes"] for r in stage_rows),
                        "all_159_exact_Git_stage_manifest_matches": True, "files": stage_rows}
        save(output / "D_STAGE_159_BYTE_COMPARISON.json", stage_report)
        receipt["D_stage_159"] = {"status": "EXACT_BYTES_VERIFIED", "files": len(stage_rows),
                                  "total_bytes": stage_report["total_bytes"],
                                  "receipt": "D_STAGE_159_BYTE_COMPARISON.json"}
        print(json.dumps({"stage": "D_STAGE_159", "status": "EXACT_BYTES_VERIFIED",
                          "files": len(stage_rows), "bytes": stage_report["total_bytes"]}), flush=True)

        helper = run13 / "git_transport/restore.py"
        checksum = source / "SHA256SUMS.txt"
        source_map = source / "evidence/run13/UNCHANGED_INPUT_CODE.json"
        for key, path in (("restore", helper), ("checksum", checksum), ("source_map", source_map)):
            if file_id(path)["sha256"] != HASHES[key]:
                raise ValueError("original source contract changed: " + key)
        restored = json.loads(run("04_original_transport", [sys.executable, "-B", helper,
                                  "--manifest", helper.with_name("MANIFEST.json"), "--destination-root", source]))
        if not restored["all_parts_and_full_files_verified"] or restored["overwritten_files"] != 0:
            raise ValueError("original transport identity not established")
        expected_names = set()
        payload_rows = []
        for line in checksum.read_text().splitlines():
            if not re.fullmatch(r"[0-9a-f]{64}  .+", line):
                raise ValueError("invalid original checksum entry")
            digest, name = line[:64], line[66:]
            if name in expected_names:
                raise ValueError("duplicate original checksum entry")
            expected_names.add(name)
            actual = file_id(safe_path(source, name))
            if actual["sha256"] != digest:
                raise ValueError("original payload checksum mismatch: " + name)
            payload_rows.append({"path": name, **actual, "matches": True})
        actual_names = {p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file()}
        if len(payload_rows) != 332 or actual_names != expected_names | {"SHA256SUMS.txt"}:
            raise ValueError("restored original333 inventory mismatch")
        mapping = json.loads(source_map.read_bytes())
        if len(mapping) != 113:
            raise ValueError("original113 source map count changed")
        source_rows = []
        for name, digest in sorted(mapping.items()):
            actual = file_id(safe_path(source, name))
            if actual["sha256"] != digest:
                raise ValueError("original source/input mismatch: " + name)
            source_rows.append({"path": name, **actual, "matches": True})
        original_report = {"status": "EXACT_GIT_PAYLOAD_RESTORED", "payload_files": 333,
                           "manifest_entries": 332, "source_input_entries": 113,
                           "transport": restored, "payload": payload_rows, "source_inputs": source_rows}
        save(output / "ORIGINAL_333_113_RESTORATION.json", original_report)
        receipt["original_run13"] = {"status": original_report["status"], "files": 333,
                                    "manifest_entries": 332, "source_input_entries": 113,
                                    "receipt": "ORIGINAL_333_113_RESTORATION.json"}

        program = diagnostic / "postloss_fixed_gas_optical_response.py"
        if file_id(program)["sha256"] != HASHES["diagnostic"]:
            raise ValueError("published diagnostic source hash changed")
        reproduced_path = output / "FIXED_GAS_OPTICAL_RESPONSE_REPRODUCED.json"
        run("05_fixed_gas_five_settings", [sys.executable, "-B", program,
                                         "--source-root", source, "--output", reproduced_path])
        expected = json.loads((diagnostic / "FIXED_GAS_OPTICAL_RESPONSE.json").read_bytes())
        actual = json.loads(reproduced_path.read_bytes())
        settings = lambda d: [(r["gas_profile"], r["energy_GL_order"], r["time_GL_order"]) for r in d["results"]]
        required = [("tight", 6, 16), ("tight", 8, 16), ("tight", 12, 16), ("tight", 12, 24), ("standard", 12, 24)]
        if settings(expected) != required or settings(actual) != required or actual["execution_environment"]["native_IVP_runs"] != 0:
            raise ValueError("unexpected fixed-gas scope")
        sections = ["inputs", "implementation_checks", "results", "comparisons"]
        comparison = compare_numeric({k: expected[k] for k in sections}, {k: actual[k] for k in sections})
        comparison.update(schema="rei.run15.fixed_gas_clean_reproduction_comparison.v1",
                          published_result=file_id(diagnostic / "FIXED_GAS_OPTICAL_RESPONSE.json"),
                          reproduced_result=file_id(reproduced_path), settings=required,
                          scope_metadata_unchanged=actual["scope"] == expected["scope"],
                          source_sha256_unchanged=actual["script_sha256"] == expected["script_sha256"])
        save(output / "FIXED_GAS_NUMERIC_COMPARISON.json", comparison)
        receipt["fixed_gas_reproduction"] = {k: comparison[k] for k in
            ("fields", "exact_matches", "all_numeric_fields_match_exactly", "scope_metadata_unchanged", "source_sha256_unchanged")}
        if not all(receipt["fixed_gas_reproduction"][k] for k in
                   ("all_numeric_fields_match_exactly", "scope_metadata_unchanged", "source_sha256_unchanged")):
            raise ValueError("fixed-gas reproduction differs from published numeric fields")

        new_crate = output / "postloss_native_crate"
        native_output = output / "postloss_native_build"
        run("06_native_materialize", [sys.executable, "-B", native / "materialize.py",
                                      "--source-root", owner, "--output-root", new_crate])
        run("07_native_build_three_controls", [sys.executable, "-B", native / "build_and_check.py",
                                               "--crate-root", new_crate, "--toolchain-prefix", prefix,
                                               "--output-root", native_output], timeout=240)
        native_receipt = json.loads((native_output / "POSTLOSS_NATIVE_BUILD_RECEIPT.json").read_bytes())
        binary = native_output / "target/release/positive_planck_panel_postloss"
        native_id = file_id(binary)
        if native_id["sha256"] != HASHES["native_binary"] or native_id["bytes"] != 569800:
            raise ValueError("new native binary SHA/size differs from published execution")
        old_controls = json.loads((native / "evidence/controls/THREE_CLI_CONTROLS.json").read_bytes())
        new_controls = json.loads((native_output / "controls/THREE_CLI_CONTROLS.json").read_bytes())
        if new_controls["status"] != "NUMERICALLY_CHECKED" or len(new_controls["cases"]) != 3 or new_controls["new_native_ivps"] != 0:
            raise ValueError("native control scope/acceptance differs")
        native_comparison = compare_numeric(old_controls["cases"], new_controls["cases"])
        native_comparison.update(schema="rei.run15.native_control_clean_reproduction_comparison.v1",
                                 published_binary_sha256=HASHES["native_binary"], rebuilt_binary=native_id,
                                 stdout_bytes_equal=(native / "evidence/controls/STDOUT.jsonl").read_bytes()
                                     == (native_output / "controls/STDOUT.jsonl").read_bytes())
        save(output / "NATIVE_CONTROL_NUMERIC_COMPARISON.json", native_comparison)
        receipt["postloss_native"] = {"binary": native_id, "fresh_target": str(native_output / "target"),
                                     "native_CLI_processes": 1, "controls": 3,
                                     "numeric_fields": native_comparison["fields"],
                                     "numeric_matches": native_comparison["exact_matches"],
                                     "stdout_bytes_equal": native_comparison["stdout_bytes_equal"],
                                     "all_numeric_fields_match_exactly": native_comparison["all_numeric_fields_match_exactly"],
                                     "build_status": native_receipt["status"]}
        if not native_comparison["all_numeric_fields_match_exactly"] or not native_comparison["stdout_bytes_equal"]:
            raise ValueError("native controls differ from published execution")

        gas_output = output / "original_gas_build"
        gas_output.mkdir()
        (gas_output / "cargo_home").mkdir()
        (gas_output / "target").mkdir()
        gas_env = dict(env)
        for key in list(gas_env):
            if key.startswith("CARGO_") or key.startswith("RUSTFLAGS") or key in {
                "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "RUSTDOC", "RUSTDOCFLAGS"}:
                gas_env.pop(key)
        gas_env.update(PATH=str(prefix / "bin") + os.pathsep + env.get("PATH", ""),
                       LD_LIBRARY_PATH=str(prefix / "lib"), RUSTC=str(prefix / "bin/rustc"),
                       CARGO_HOME=str(gas_output / "cargo_home"),
                       CARGO_TARGET_DIR=str(gas_output / "target"), CARGO_NET_OFFLINE="true")
        run("08_original_gas_fresh_build", [prefix / "bin/cargo", "build", "--release", "--offline", "--locked",
                                          "--example", "gas_rhs_server", "--jobs", "2"],
            cwd=owner, timeout=180, custom_env=gas_env)
        gas_id = file_id(gas_output / "target/release/examples/gas_rhs_server")
        if gas_id["sha256"] != HASHES["gas_binary"] or gas_id["bytes"] != 571904:
            raise ValueError("original gas binary SHA/size differs from historical identity")
        receipt["original_gas"] = {"binary": gas_id, "matches_historical_binary_sha256": True,
                                   "fresh_target": str(gas_output / "target"), "binary_process_executions": 0}
        receipt["status"] = "IMPLEMENTATION_VERIFIED_SCOPED_CLEAN_REPRODUCTION"
    except Exception as exc:
        failure = exc
        receipt.update(status="FAILED_OR_BLOCKED", error_type=type(exc).__name__, error=str(exc),
                       traceback=traceback.format_exc())
    finally:
        if before is not None:
            try:
                after = scoped_snapshot("09_git_source_after")
                receipt["scoped_tracked_files"] = len(after)
                receipt["all_scoped_tracked_source_bytes_and_modes_unchanged"] = before == after
                receipt["index_after"] = file_id(repo / ".git/index")
                receipt["git_index_bytes_unchanged"] = receipt["index_before"] == receipt["index_after"]
                receipt["final_head"] = run("10_final_head", ["git", "rev-parse", "HEAD"]).decode().strip()
                if not all((before == after, receipt["git_index_bytes_unchanged"], receipt["final_head"] == EXPECTED_D)):
                    raise ValueError("source/index/head changed during reproduction")
            except Exception as exc:
                failure = failure or exc
                receipt.update(status="FAILED_OR_BLOCKED", immutability_error=type(exc).__name__ + ": " + str(exc))
        receipt["completed_at_utc"] = now()
        save(output / "SCOPED_CLEAN_REPRODUCTION_RECEIPT.json", receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(output / "SCOPED_CLEAN_REPRODUCTION_RECEIPT.json"),
                      "fixed_gas": receipt.get("fixed_gas_reproduction"),
                      "native": receipt.get("postloss_native"), "gas": receipt.get("original_gas"),
                      "error": receipt.get("error")}, indent=2), flush=True)
    return 0 if failure is None else 1

if __name__ == "__main__":
    raise SystemExit(main())

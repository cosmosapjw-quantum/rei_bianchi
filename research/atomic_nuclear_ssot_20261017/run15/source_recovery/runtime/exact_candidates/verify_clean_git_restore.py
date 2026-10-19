#!/usr/bin/env python3
"""Verify RUN13/RUN15 restoration from an explicitly selected clean Git checkout.

Required: --checkout-root REPO --expected-head SHA --toolchain-root RUST_PREFIX
          --native-target-root NEW_TARGET --output-root NEW_OUTPUT
Optional: --python-executable PYTHON --jobs 2 --command-timeout-s 300

This script performs no clone, fetch, install, scientific IVP, or test suite.
It restores the two original Git-transport ZIPs and the three gzip packets,
checks all 333 original files and the 117-file source checkpoint, rebuilds the
two native executables offline in a NEW external target, compares their bytes
with the recorded executables, joins the three transported RUN15 case ZIPs,
and safely restores/validates all four COMPLETE cases using frozen code.

The selected Python must satisfy the exact numeric_runtime locked in the case
manifests. A binary mismatch or runtime mismatch is reported as a failure; no
saved identity or validation rule is rewritten. Every command writes separate
logs and a receipt. The final CLEAN_RESTORE.json records scoped results even if
a later stage fails. Existing output/target directories are never reused.

Run this file from the published checkout. Repository paths are derived from
--checkout-root; no producer's absolute setup path is used as an executable,
source, input, archive, or output location.
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
import subprocess
import sys
import time
import traceback

RUNS = Path("research/atomic_nuclear_ssot_20261017")
RUN15_REL = RUNS / "run15"
SOURCE_REL = RUNS / "run13/recovered"
CASES = {"optical_n4_standard", "optical_n6_standard", "optical_n8_standard", "optical_n8_tight"}
THREADS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
SEALED_SOURCE_MAP_SHA = "7d04e35d4f77e7ee07e7e969f7a79e03623dbdbde33306dea54014202c172036"
BLOCK = 1024 * 1024


class RestoreError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise RestoreError(message)


def unique_json(data):
    def pairs(items):
        answer = {}
        for key, value in items:
            require(key not in answer, "duplicate JSON key: " + key)
            answer[key] = value
        return answer
    return json.loads(data, object_pairs_hook=pairs)


def clean_path(value: Path) -> Path:
    value = value.absolute()
    require(not any(p.is_symlink() for p in (value, *value.parents)), "symlink in selected path: " + str(value))
    return value.resolve()


def relative_file(root: Path, name: str) -> Path:
    require(isinstance(name, str) and name and "\\" not in name and "\0" not in name,
            "nonempty canonical POSIX path required")
    require(not PurePosixPath(name).is_absolute() and all(p not in ("", ".", "..") for p in name.split("/")),
            "unsafe relative path: " + name)
    path = clean_path(root.joinpath(*PurePosixPath(name).parts))
    require(root in path.parents, "path outside declared root")
    return path


def file_identity(path: Path) -> dict:
    path = clean_path(path)
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode), "ordinary file required: " + str(path))
    before = path.stat()
    digest = hashlib.sha256()
    git = hashlib.sha1(b"blob " + str(before.st_size).encode() + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(BLOCK), b""):
            digest.update(block)
            git.update(block)
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            "file changed while hashing: " + str(path))
    return {"bytes": before.st_size, "sha256": digest.hexdigest(), "git_blob_sha1": git.hexdigest(),
            "mode": "100755" if before.st_mode & 0o111 else "100644"}


def write_json_new(path: Path, data) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


class Commands:
    def __init__(self, root: Path, timeout_s: float):
        self.root, self.timeout_s, self.records = root, timeout_s, []

    def run(self, name: str, argv, cwd: Path, env: dict, *, as_json=False):
        number = len(self.records) + 1
        label = f"{number:02d}_{name}"
        stdout, stderr = self.root / (label + ".stdout.log"), self.root / (label + ".stderr.log")
        entry = {"stage": label, "argv": [str(a) for a in argv], "cwd": str(cwd),
                 "started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                 "stdout": stdout.name, "stderr": stderr.name,
                 "effective_controls": {k: env[k] for k in (*THREADS, "PYTHONDONTWRITEBYTECODE",
                      "CARGO_HOME", "CARGO_TARGET_DIR", "CARGO_NET_OFFLINE", "RUSTC") if k in env}}
        print(json.dumps({"stage": label, "status": "STARTED"}), flush=True)
        started, failure = time.perf_counter(), None
        try:
            with stdout.open("xb") as out, stderr.open("xb") as err:
                result = subprocess.run(entry["argv"], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                        stdout=out, stderr=err, timeout=self.timeout_s, check=False)
            entry["returncode"] = result.returncode
        except Exception as exc:
            failure = exc
            entry.update(returncode=None, error_type=type(exc).__name__, error=str(exc))
        entry["wall_s"] = time.perf_counter() - started
        for path, key in ((stdout, "stdout"), (stderr, "stderr")):
            if path.exists():
                entry[key + "_identity"] = file_identity(path)
        self.records.append(entry)
        write_json_new(self.root / (label + ".receipt.json"), entry)
        print(json.dumps({"stage": label, "returncode": entry["returncode"], "wall_s": entry["wall_s"]}), flush=True)
        if failure is not None:
            raise RestoreError(f"{label}: {type(failure).__name__}; see command receipt") from failure
        require(entry["returncode"] == 0, f"{label} exited {entry['returncode']}; see {stderr}")
        data = stdout.read_bytes()
        return unique_json(data) if as_json else data


def process_environment(toolchain: Path) -> dict:
    env = dict(os.environ)
    # These affect child processes only. User/system configuration is untouched.
    for key in list(env):
        if key.startswith("CARGO_") or key in {"RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTDOCFLAGS",
                "RUSTC", "RUSTDOC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "PYTHONPATH", "PYTHONHOME"}:
            del env[key]
    env.update({key: "1" for key in THREADS})
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["PATH"] = str(toolchain / "bin") + os.pathsep + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = str(toolchain / "lib") + (os.pathsep + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    return env


def tree_entries(data: bytes) -> dict:
    result = {}
    for row in data.split(b"\0"):
        if not row:
            continue
        meta, name = row.split(b"\t", 1)
        mode, kind, digest = meta.decode("ascii").split()
        require(kind == "blob", "non-blob entry in restoration source scope")
        result[name.decode("utf-8")] = {"git_blob_sha1": digest, "mode": mode}
    return result


def anchored_file(repo: Path, relative: str, tree: dict) -> dict:
    require(relative in tree, "required file is absent from selected Git commit: " + relative)
    actual = file_identity(relative_file(repo, relative))
    require(all(actual[k] == tree[relative][k] for k in ("git_blob_sha1", "mode")),
            "working bytes/mode differ from Git object: " + relative)
    return actual


def checkpoint_identity(repo: Path, run15: Path, tree: dict) -> dict:
    manifest_path = run15 / "SOURCE_CHECKPOINT.json"
    own = anchored_file(repo, manifest_path.relative_to(repo).as_posix(), tree)
    manifest = unique_json(manifest_path.read_bytes())
    require(manifest.get("schema") == "rei.run15.source_checkpoint.v1", "unknown source checkpoint schema")
    entries = manifest["covered_files"]
    require(len(entries) == 116 and manifest["covered_file_count_excluding_this_manifest"] == 116,
            "expected the original 117-file source checkpoint")
    require([e["path"] for e in entries] == sorted({e["path"] for e in entries}), "checkpoint path order/uniqueness")
    canonical = (json.dumps(entries, sort_keys=True, separators=(",", ":")) + "\n").encode()
    require(hashlib.sha256(canonical).hexdigest() == manifest["canonical_covered_entries_sha256"],
            "checkpoint inventory digest mismatch")
    for entry in entries:
        require(entry["path"].startswith(RUN15_REL.as_posix() + "/"), "checkpoint scope escape")
        actual = anchored_file(repo, entry["path"], tree)
        require(all(actual[k] == entry[k] for k in ("bytes", "sha256", "git_blob_sha1", "mode")),
                "source checkpoint file differs: " + entry["path"])
    require(sum(e["bytes"] for e in entries) == manifest["covered_total_bytes_excluding_this_manifest"],
            "checkpoint total size differs")
    return {"status": "VERIFIED", "files": 117, "manifest_identity": own,
            "canonical_covered_entries_sha256": manifest["canonical_covered_entries_sha256"]}


def original_identity(source: Path) -> dict:
    checksum = source / "SHA256SUMS.txt"
    rows = {}
    for line in checksum.read_text(encoding="utf-8").splitlines():
        require(re.fullmatch(r"[0-9a-f]{64}  .+", line) is not None, "invalid original checksum line")
        digest, name = line[:64], line[66:]
        require(name not in rows, "duplicate original manifest path")
        path = relative_file(source, name)
        require(file_identity(path)["sha256"] == digest, "original file SHA mismatch: " + name)
        rows[name] = digest
    require(len(rows) == 332, "original archive manifest must contain 332 entries")
    actual_files = set()
    for path in source.rglob("*"):
        require(not path.is_symlink(), "link inside restored original source")
        if path.is_file():
            actual_files.add(path.relative_to(source).as_posix())
    require(actual_files == set(rows) | {"SHA256SUMS.txt"}, "restored original inventory is not exactly 333 files")
    mapfile = source / "evidence/run13/UNCHANGED_INPUT_CODE.json"
    require(file_identity(mapfile)["sha256"] == SEALED_SOURCE_MAP_SHA, "sealed original source/input map differs")
    mapping = unique_json(mapfile.read_bytes())
    require(len(mapping) == 113, "sealed source/input count differs")
    for name, digest in mapping.items():
        require(file_identity(relative_file(source, name))["sha256"] == digest, "sealed dependency differs: " + name)
    return {"status": "VERIFIED", "original_files": 333, "manifest_entries": 332,
            "manifest_sha256": file_identity(checksum)["sha256"], "sealed_source_input_files": 113,
            "sealed_source_map_sha256": SEALED_SOURCE_MAP_SHA}


def perform(args, state: dict, commands: Commands) -> None:
    repo, out, target, toolchain = args.checkout_root, args.output_root, args.native_target_root, args.toolchain_root
    run15, source = repo / RUN15_REL, repo / SOURCE_REL
    scripts, env = run15 / "scripts", process_environment(toolchain)
    python = str(args.python_executable)

    def run(name, argv, cwd=repo, *, child_env=None, as_json=False):
        return commands.run(name, argv, cwd, child_env or env, as_json=as_json)

    top = run("git_toplevel", ["git", "rev-parse", "--show-toplevel"]).decode().strip()
    require(Path(top).resolve() == repo, "checkout-root is not the Git repository root")
    head = run("git_head", ["git", "rev-parse", "HEAD"]).decode().strip()
    require(head == args.expected_head, "selected Git HEAD differs from --expected-head")
    dirty = run("git_initial_status", ["git", "status", "--porcelain=v1", "--untracked-files=all"])
    require(not dirty.strip(), "a clean checkout with no untracked files is required")
    state["git"] = {"head": head, "initial_status_clean": True, "explicit_ref_or_index_mutation_commands": 0}
    tree = tree_entries(run("git_source_tree", ["git", "ls-tree", "-r", "-z", "HEAD", "--",
        str(SOURCE_REL), str(RUNS / "run13/git_transport"), str(RUN15_REL)]))
    script_relative = (RUN15_REL / "scripts/verify_clean_git_restore.py").as_posix()
    script_identity = anchored_file(repo, script_relative, tree)
    require(file_identity(Path(__file__))["sha256"] == script_identity["sha256"], "invoked verifier differs from checkout copy")
    state["verifier_identity"] = script_identity
    state["source_checkpoint"] = checkpoint_identity(repo, run15, tree)
    anchored_file(repo, (SOURCE_REL / "SHA256SUMS.txt").as_posix(), tree)
    # A fresh Git restore may not silently reuse already materialized dependencies.
    for relative in ("provenance/RUN09.zip", "provenance/RUN11.zip"):
        require(not (source / relative).exists(), "original transport target already exists; select a fresh checkout")
    for order in (4, 6, 8):
        require(not (run15 / f"inputs/optical_n{order}.json").exists(), "raw packet already exists; select a fresh checkout")
    require(not (run15 / "outputs").exists(), "RUN15 output directory already exists; select a fresh checkout")

    index_path = run15 / "evidence/CASE_ARCHIVE_INDEX.json"
    state["case_archive_index_identity"] = anchored_file(repo, index_path.relative_to(repo).as_posix(), tree)
    index = unique_json(index_path.read_bytes())
    require(index.get("schema") == "rei.run15.case_archive_index.v1" and index.get("case_count") == 4,
            "unexpected completed-case archive index")
    require(len(index["cases"]) == 4 and {r["case"] for r in index["cases"]} == CASES, "four named complete cases required")
    for name, digest in index["source_scripts_sha256"].items():
        path = relative_file(scripts, name)
        require(anchored_file(repo, path.relative_to(repo).as_posix(), tree)["sha256"] == digest,
                "archive/frozen driver identity changed: " + name)
    helper_info = index["original_transport_helper"]
    helper = relative_file(repo, helper_info["repo_path"])
    require(anchored_file(repo, helper_info["repo_path"], tree)["sha256"] == helper_info["sha256"],
            "original transport helper changed")
    anchored_file(repo, helper.with_name("MANIFEST.json").relative_to(repo).as_posix(), tree)

    manifests, expected_runtime = {}, None
    for row in index["cases"]:
        path = relative_file(run15, row["internal_manifest_path"])
        require(anchored_file(repo, path.relative_to(repo).as_posix(), tree)["sha256"] == row["internal_manifest_sha256"],
                "case manifest identity differs")
        manifest = unique_json(path.read_bytes())
        locked = manifest["locked_inputs"]
        require(manifest["file_count"] == row["case_files"] and locked["packet_sha256"] == row["packet_sha256"]
                and locked["requested_rtol"] == row["rtol"] and locked["native_binary_sha256"] == index["native_binary_sha256"],
                "case index and original locked inputs differ")
        runtime = locked["numeric_runtime"]
        require(expected_runtime is None or runtime == expected_runtime, "case numeric runtimes disagree")
        expected_runtime, manifests[row["case"]] = runtime, manifest
    runtime_code = ("import json,platform,numpy,scipy; print(json.dumps({'python':platform.python_version(),"
                    "'numpy':numpy.__version__,'scipy':scipy.__version__,'float64_bytes':numpy.dtype('<f8').itemsize}))")
    actual_runtime = run("numeric_runtime", [python, "-B", "-c", runtime_code], as_json=True)
    state["numeric_runtime"] = {"actual": actual_runtime, "expected": expected_runtime, "matches": actual_runtime == expected_runtime}
    require(actual_runtime == expected_runtime, "numeric runtime differs from frozen case profile; no profile is rewritten")

    original_transport = run("restore_original_transport", [python, "-B", str(helper),
        "--manifest", str(helper.with_name("MANIFEST.json")), "--destination-root", str(source)], as_json=True)
    require(original_transport["all_parts_and_full_files_verified"] and original_transport["overwritten_files"] == 0,
            "original transport restoration failed")
    state["original_transport"] = original_transport
    state["original_identity_before_build"] = original_identity(source)
    state["gzip_inputs"] = run("restore_gzip_inputs", [python, "-B", str(scripts / "restore_inputs.py")], as_json=True)
    require(len(state["gzip_inputs"]) == 3, "three restored optical packets required")
    for row in index["cases"]:
        packet = relative_file(run15, row["packet_path"])
        require(file_identity(packet)["sha256"] == row["packet_sha256"], "restored case packet SHA differs")

    cargo, rustc = toolchain / "bin/cargo", toolchain / "bin/rustc"
    for binary in (cargo, rustc):
        file_identity(binary)
        require(os.access(binary, os.X_OK), "toolchain executable is not executable")
    versions = {"rustc": run("rustc_version", [str(rustc), "-Vv"]).decode(),
                "cargo": run("cargo_version", [str(cargo), "-Vv"]).decode()}
    state["toolchain"] = {"root": str(toolchain), "versions": versions,
                          "rustc_identity": file_identity(rustc), "cargo_identity": file_identity(cargo)}
    require("commit-hash: e408947bfd200af42db322daf0fadfe7e26d3bd1" in versions["rustc"]
            and "host: x86_64-unknown-linux-gnu" in versions["rustc"]
            and "commit-hash: 29ea6fb6a5db279426f4cc4e17aa385f05a0cfbc" in versions["cargo"],
            "exact recorded Rust 1.94.1 x86_64 toolchain is required")
    target.mkdir(parents=True, exist_ok=False)
    cargo_home = out / "cargo_home"
    cargo_home.mkdir()
    build_env = dict(env, CARGO_HOME=str(cargo_home), CARGO_NET_OFFLINE="true", RUSTC=str(rustc))
    binaries = [
        ("gas_rhs_server", source / "code/rei_bass_coupled", target / "gas",
         ["--example", "gas_rhs_server"], "release/examples/gas_rhs_server",
         run15 / "recovery/runtime/native_validation_receipt.json"),
        ("positive_planck_panel", run15 / "native", target / "quadrature", [], "release/positive_planck_panel",
         run15 / "validation/native_quadrature/run15_native_execution_initial.json"),
    ]
    state["rebuilt_binaries"] = {}
    for name, crate, build_target, extra, relative, old_receipt in binaries:
        current_env = dict(build_env, CARGO_TARGET_DIR=str(build_target))
        run("build_" + name, [str(cargo), "build", "--release", "--offline", "--locked", *extra,
            "--jobs", str(args.jobs)], cwd=crate, child_env=current_env)
        expected = unique_json(old_receipt.read_bytes())["binary"]
        binary = build_target / relative
        actual = file_identity(binary)
        matches = all(actual[k] == expected[k] for k in ("bytes", "sha256"))
        state["rebuilt_binaries"][name] = {"path": str(binary), "actual": actual,
                                          "expected": {k: expected[k] for k in ("bytes", "sha256")}, "matches": matches}
    require(all(v["matches"] for v in state["rebuilt_binaries"].values()),
            "rebuilt executable byte identity differs; frozen validation is blocked, not bypassed")
    gas_binary = Path(state["rebuilt_binaries"]["gas_rhs_server"]["path"])
    require(file_identity(gas_binary)["sha256"] == index["native_binary_sha256"], "rebuilt gas binary differs from case index")

    state["cases"] = []
    for row in index["cases"]:
        case, transport = row["case"], row["git_transport"]
        packet = relative_file(run15, row["packet_path"])
        if transport["kind"] == "DIRECT_ZIP":
            archive = relative_file(run15, row["archive_path"])
            anchored_file(repo, archive.relative_to(repo).as_posix(), tree)
            joined = None
        else:
            require(transport["kind"] == "RAW_8_MIB_CHUNKS", "unknown case transport kind")
            manifest_path = relative_file(run15, transport["manifest_path"])
            require(anchored_file(repo, manifest_path.relative_to(repo).as_posix(), tree)["sha256"] == transport["manifest_sha256"],
                    "transport manifest differs")
            for part in transport["parts"]:
                path = relative_file(run15, part["path"])
                actual = anchored_file(repo, path.relative_to(repo).as_posix(), tree)
                require(all(actual[k] == part[k] for k in ("bytes", "sha256", "git_blob_sha1")), "transport part differs")
            joined = run("join_" + case, [python, "-B", str(scripts / "transport_archives.py"), "join",
                "--manifest", str(manifest_path), "--destination-root", str(out / "archives")], as_json=True)
            require(joined["all_parts_and_full_files_verified"] and joined["overwritten_files"] == 0, "case transport join failed")
            archive = out / "archives" / Path(row["archive_path"]).name
        archive_identity = file_identity(archive)
        require(archive_identity["bytes"] == row["archive_bytes"] and archive_identity["sha256"] == row["archive_sha256"],
                "complete case archive differs from index")
        destination = out / "cases" / case
        restored = run("restore_" + case, [python, "-B", str(scripts / "archive_runs.py"), "restore",
            "--archive", str(archive), "--destination", str(destination), "--expected-sha256", row["archive_sha256"],
            "--packet", str(packet), "--native-binary", str(gas_binary), "--source-root", str(source),
            "--require-validation"], as_json=True)
        require(restored["status"] == "RESTORED_EXACT" and restored["crc_and_all_manifest_hashes_verified"]
                and restored["manifest_sha256"] == row["internal_manifest_sha256"] and restored["case_files"] == row["case_files"]
                and restored["validation"]["status"] == "COMPLETE_VALIDATED"
                and restored["validation"]["new_event_intervals_this_command"] == 0, "staged restore admission differs")
        # The archive helper validates the stage; this checks its published path.
        final = run("validate_" + case, [python, "-B", str(scripts / "run_joint.py"), "validate",
            "--packet", str(packet), "--native-binary", str(gas_binary), "--out", str(destination),
            "--source-root", str(source), "--rtol", str(row["rtol"])], as_json=True)
        require(final["status"] == "COMPLETE" and final["new_event_intervals_this_command"] == 0
                and final["next_segment"] == row["event_intervals"] and final["total_segments"] == row["event_intervals"]
                and final["dimension"] == row["dimension"] and final["gas_event_points"] == row["gas_event_points"]
                and final["observable"] == row["observables_reconstructed"], "published frozen endpoint validation differs")
        for member in manifests[case]["files"]:
            actual = file_identity(relative_file(destination, member["path"]))
            require(actual["bytes"] == member["bytes"] and actual["sha256"] == member["sha256"], "published case member differs")
        published_paths = {p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file() or p.is_symlink()}
        require(published_paths == {m["path"] for m in manifests[case]["files"]}, "published case inventory differs")
        state["cases"].append({"case": case, "archive_identity": archive_identity, "join": joined,
                               "restore": restored, "published_validation": final, "restored_files": row["case_files"]})
    require(sum(r["restored_files"] for r in state["cases"]) == index["case_file_total"], "case file total differs")
    state["original_identity_after_all_commands"] = original_identity(source)
    state["source_checkpoint_after_all_commands"] = checkpoint_identity(repo, run15, tree)
    run("git_tracked_unchanged", ["git", "diff", "--exit-code", "HEAD", "--"])
    run("git_index_unchanged", ["git", "diff", "--cached", "--exit-code", "HEAD", "--"])
    state["git"]["final_head"] = run("git_final_head", ["git", "rev-parse", "HEAD"]).decode().strip()
    require(state["git"]["final_head"] == head, "Git HEAD changed during restoration")
    state.update(status="IMPLEMENTATION_VERIFIED", original_files_verified=333, source_snapshot_files_verified=117,
                 completed_cases_validated=4, restored_case_files=index["case_file_total"],
                 both_native_binaries_byte_identical=True, new_event_intervals=0, fresh_IVP_runs=0,
                 scope="Git source/archive restoration and frozen endpoint validation; no continuum error bound")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkout-root", type=Path, required=True)
    parser.add_argument("--expected-head", required=True, help="Exact 40-character commit SHA supplied by the caller")
    parser.add_argument("--toolchain-root", type=Path, required=True, help="Installed Rust prefix containing bin/cargo and bin/rustc")
    parser.add_argument("--native-target-root", type=Path, required=True, help="NEW directory outside the checkout")
    parser.add_argument("--output-root", type=Path, required=True, help="NEW directory for logs, restored cases, and the final receipt")
    parser.add_argument("--python-executable", type=Path, default=Path(sys.executable))
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--command-timeout-s", type=float, default=300.0)
    args = parser.parse_args()
    try:
        require(re.fullmatch(r"[0-9a-f]{40}", args.expected_head) is not None, "exact lowercase Git SHA required")
        require(1 <= args.jobs <= 8 and math.isfinite(args.command_timeout_s) and args.command_timeout_s > 0,
                "bounded jobs and positive finite command timeout required")
        for name in ("checkout_root", "toolchain_root", "native_target_root", "output_root"):
            setattr(args, name, clean_path(getattr(args, name)))
        args.python_executable = args.python_executable.resolve(strict=True)
        require(args.checkout_root.is_dir() and args.toolchain_root.is_dir(), "checkout/toolchain directories must exist")
        require(not args.output_root.exists() and not args.native_target_root.exists(), "output and target must both be NEW")
        for path in (args.output_root, args.native_target_root):
            require(path != args.checkout_root and args.checkout_root not in path.parents
                    and path not in args.checkout_root.parents, "output/target must not overlap the checkout")
            require(path != args.toolchain_root and args.toolchain_root not in path.parents
                    and path not in args.toolchain_root.parents, "output/target must not overlap the toolchain")
        require(args.native_target_root != args.output_root and args.native_target_root not in args.output_root.parents,
                "target must be separate from or below output-root")
        args.output_root.mkdir(parents=True, exist_ok=False)
    except Exception as exc:
        print(json.dumps({"status": "PREFLIGHT_FAILED", "error_type": type(exc).__name__, "error": str(exc)}), file=sys.stderr)
        return 1
    state = {"schema": "rei.run15.clean_git_restore.v1", "status": "IN_PROGRESS",
             "started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
             "invocation": [sys.executable, *sys.argv], "checkout_root": str(args.checkout_root),
             "output_root": str(args.output_root), "native_target_root": str(args.native_target_root),
             "orchestrator_python": platform.python_version(), "fresh_IVP_runs": 0, "new_test_suite_runs": 0}
    commands = Commands(args.output_root, args.command_timeout_s)
    try:
        perform(args, state, commands)
    except Exception as exc:
        state.update(status="FAILED_OR_BLOCKED", error_type=type(exc).__name__, error=str(exc),
                     traceback=traceback.format_exc(), full_clean_restore_admitted=False)
    finally:
        state["completed_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        state["commands"] = commands.records
        write_json_new(args.output_root / "CLEAN_RESTORE.json", state)
    print(json.dumps({"status": state["status"], "receipt": str(args.output_root / "CLEAN_RESTORE.json"),
                      "completed_cases_validated": state.get("completed_cases_validated", 0),
                      "error": state.get("error")}, allow_nan=False), flush=True)
    return 0 if state["status"] == "IMPLEMENTATION_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

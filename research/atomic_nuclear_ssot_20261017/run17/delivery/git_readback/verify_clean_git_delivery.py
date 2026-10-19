#!/usr/bin/env python3
"""RUN17 Git-only byte delivery readback. No numerical modules are imported."""
from __future__ import annotations
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import sys
import time

COMMIT = "589ffbaff7b74a6cf1dbaf797285f15a58131dbd"
TREE = "b2c5d15e8f4baf0fc12d03ac40a86110c187a37e"
BASE = "45ee7192b9d405214ec2650185aeaaa635e0fa13"
PREFIX = "research/atomic_nuclear_ssot_20261017"
MANIFEST_SHA = "256b084717e1039da6cdc1ac53d44d726c0f0a85f06a02387639a0db53dfaae7"

def digest(raw: bytes) -> dict:
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}

def path_safe(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("invalid relative path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ("", ".", "..") for x in value.split("/")):
        raise ValueError("unsafe relative path")
    return value

def write_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(raw)

def ordinary(path: Path) -> bytes:
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"not ordinary: {path}")
    return path.read_bytes()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    repo, out = args.repo.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "rei.run17.clean-git-delivery-readback.v1",
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repository": "cosmosapjw-quantum/rei_bianchi",
        "remote": "https://github.com/cosmosapjw-quantum/rei_bianchi.git",
        "commit": COMMIT, "tree": TREE, "base": BASE,
        "checkout": str(repo), "commands": [],
        "environment": {"python": sys.version, "python_executable": sys.executable,
                        "platform": platform.platform(), "git_optional_locks": "0"},
        "invocation": [sys.executable, "-B", *sys.argv],
        "counts": {"tests": 0, "native_builds": 0, "RHS": 0, "quadrature": 0,
                   "IVPs": 0, "certificate_reruns": 0, "old_M2_reruns": 0},
        "scope": "Exact Git/source/result restoration and stored identity checks only.",
    }
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"

    def command(argv: list[str], label: str) -> bytes:
        start = time.monotonic()
        p = subprocess.run(argv, cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        so, se = out / f"{label}.stdout", out / f"{label}.stderr"
        write_new(so, p.stdout)
        write_new(se, p.stderr)
        report["commands"].append({
            "argv": argv, "cwd": str(repo), "exit_code": p.returncode,
            "wall_seconds": time.monotonic() - start,
            "stdout": so.name, "stderr": se.name,
            "stdout_identity": digest(p.stdout), "stderr_identity": digest(p.stderr)})
        if p.returncode:
            raise RuntimeError(f"command failed: {label}, exit {p.returncode}")
        return p.stdout

    def git(label: str, *parts: str) -> bytes:
        return command(["git", "-C", str(repo), *parts], label)

    try:
        head = git("head_before", "rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines()
        if head != [COMMIT, TREE]:
            raise ValueError("fresh checkout HEAD/tree mismatch")
        report["environment"]["git_version"] = git("git_version", "--version").decode().strip()
        index_path = Path(git("index_location", "rev-parse", "--git-path", "index").decode().strip())
        if not index_path.is_absolute():
            index_path = repo / index_path
        index_before = digest(ordinary(index_path))
        run17 = repo / PREFIX / "run17"
        manifest_path = run17 / "SCIENCE_MANIFEST.json"
        raw_manifest = ordinary(manifest_path)
        if digest(raw_manifest)["sha256"] != MANIFEST_SHA:
            raise ValueError("science manifest byte mismatch")
        manifest = json.loads(raw_manifest)
        if manifest.get("schema") != "rei.run17.complete-science-manifest.v1" or not manifest.get("excludes_itself"):
            raise ValueError("science manifest schema/self-reference")
        if manifest["base_commit"] != BASE or manifest["file_count_excluding_this_manifest"] != 110:
            raise ValueError("science manifest baseline/count mismatch")

        raw_tree = git("run17_tree", "ls-tree", "-r", "-z", "--full-tree", COMMIT, "--", PREFIX + "/run17")
        entries = {}
        for row in raw_tree.split(b"\0"):
            if not row:
                continue
            meta, path = row.split(b"\t", 1)
            mode, kind, blob = meta.decode().split()
            name = path.decode()
            if not name.startswith(PREFIX + "/run17/"):
                raise ValueError("unexpected tree prefix")
            rel = path_safe(name[len(PREFIX + "/run17/"):])
            entries[rel] = {"mode": mode, "type": kind, "blob": blob}
        names = [path_safe(row["path"]) for row in manifest["files"]]
        if len(set(names)) != len(names) or set(names) | {"SCIENCE_MANIFEST.json"} != set(entries):
            raise ValueError("exact Git science membership mismatch")
        if len(entries) != 111:
            raise ValueError("Git science count mismatch")
        sci = []
        for row in [*manifest["files"], {"path": "SCIENCE_MANIFEST.json", **digest(raw_manifest), "git_mode": "100644"}]:
            rel = row["path"]
            target = run17 / rel
            actual = digest(ordinary(target))
            expected_mode = row["git_mode"]
            g = entries[rel]
            if g != {"mode": expected_mode, "type": "blob", "blob": actual["git_blob"]}:
                raise ValueError(f"Git mode/blob mismatch: {rel}")
            if expected_mode not in ("100644", "100755"):
                raise ValueError("nonordinary science mode")
            if stat.S_IMODE(target.stat().st_mode) != (0o755 if expected_mode == "100755" else 0o644):
                raise ValueError(f"filesystem mode mismatch: {rel}")
            for key in ("bytes", "sha256", "git_blob"):
                if actual[key] != row[key]:
                    raise ValueError(f"manifest {key} mismatch: {rel}")
            sci.append({"path": rel, **actual, "git_mode": expected_mode, "match": True})
        if sum(r["bytes"] for r in sci if r["path"] != "SCIENCE_MANIFEST.json") != manifest["payload_bytes_excluding_this_manifest"]:
            raise ValueError("science payload total mismatch")
        report["science_payload"] = {"manifest": digest(raw_manifest), "files": sci,
                                     "file_count": len(sci), "bytes": sum(x["bytes"] for x in sci),
                                     "manifest_excluded_files": 110, "all_hashes_modes_git_blobs_match": True}

        raw_diff = git("base_to_science_diff", "diff-tree", "--no-commit-id", "--raw", "-r", "-z", BASE, COMMIT)
        tokens = raw_diff.split(b"\0")
        changed = []
        pos = 0
        while pos < len(tokens) and tokens[pos]:
            meta = tokens[pos].decode()
            path = tokens[pos + 1].decode()
            pos += 2
            mode0, mode1, old, new, status = meta.lstrip(":").split()
            if status != "A" or mode0 != "000000" or old != "0" * 40:
                raise ValueError(f"base diff is not add-only: {path}")
            if not path.startswith(PREFIX + "/run17/"):
                raise ValueError(f"addition outside run17: {path}")
            rel = path[len(PREFIX + "/run17/"):]
            if rel not in entries or entries[rel]["mode"] != mode1 or entries[rel]["blob"] != new:
                raise ValueError("diff vs tree mismatch")
            changed.append({"path": path, "status": status, "git_mode": mode1, "git_blob": new})
        if len(changed) != 111 or {x["path"][len(PREFIX + "/run17/"):] for x in changed} != set(entries):
            raise ValueError("base diff count/membership mismatch")
        report["add_only_base_diff"] = {"count": len(changed), "only_run17_additions": True, "files": changed}

        transport_dir = repo / PREFIX / "run13/git_transport"
        transport_script = transport_dir / "restore.py"
        transport_manifest = transport_dir / "MANIFEST.json"
        old = repo / PREFIX / "run13/recovered"
        transport_before = {"script": digest(ordinary(transport_script)), "manifest": digest(ordinary(transport_manifest))}
        transport = json.loads(command([
            sys.executable, "-B", str(transport_script),
            "--manifest", str(transport_manifest), "--destination-root", str(old)
        ], "original_byte_transport"))
        if not transport["all_parts_and_full_files_verified"] or transport["overwritten_files"] or transport["scientific_recalculations"]:
            raise ValueError("byte restoration contract failed")
        if len(transport["files"]) != 2:
            raise ValueError("expected two chunked historical payload files")
        for name, path in [("script", transport_script), ("manifest", transport_manifest)]:
            if digest(ordinary(path)) != transport_before[name]:
                raise ValueError("original transport source changed")
        report["original_transport"] = {"source_identity": transport_before, "result": transport,
                                        "original_chunked_payloads": 2, "raw_chunks": 5}

        sums = old / "SHA256SUMS.txt"
        internal = []
        for line in ordinary(sums).decode().splitlines():
            expected, rel = line.split("  ", 1)
            path_safe(rel)
            actual = digest(ordinary(old / rel))
            if actual["sha256"] != expected:
                raise ValueError(f"original manifest mismatch: {rel}")
            internal.append({"path": rel, **actual, "match": True})
        if len(internal) != 332:
            raise ValueError("original manifest should list332payload files")
        write_new(out / "ORIGINAL332_MANIFEST_READBACK.json", (json.dumps({
            "schema": "rei.run17.original-manifest-byte-readback.v1",
            "manifest": digest(ordinary(sums)), "payload_files": internal,
            "payload_files_checked": 332, "files_including_manifest": 333,
            "comparison_scope": "Git-restored payload vs original internal SHA256SUMS; no full archive redownload."
        }, indent=2) + "\n").encode())
        report["original_payload"] = {"manifest": digest(ordinary(sums)), "payload_entries_checked": 332,
                                      "files_including_manifest": 333, "all_internal_hashes_match": True}

        stored = json.loads(ordinary(run17 / "residual/analysis_execution01/FIRST_BIRTH_RESIDUAL.json"))
        used = stored["source"]["verified_source_input_files"]
        if len(used) != 112:
            raise ValueError("RUN17 recorded used source/input count is not112")
        used_checks = []
        for rel, expected in used.items():
            path_safe(rel)
            actual = digest(ordinary(old / rel))
            if actual["bytes"] != expected["bytes"] or actual["sha256"] != expected["sha256"]:
                raise ValueError(f"used source/input mismatch: {rel}")
            used_checks.append({"path": rel, **actual, "match": True})
        report["run17_used112_readback"] = {
            "map_source": "run17/residual/analysis_execution01/FIRST_BIRTH_RESIDUAL.json#/source/verified_source_input_files",
            "map_source_identity": digest(ordinary(run17 / "residual/analysis_execution01/FIRST_BIRTH_RESIDUAL.json")),
            "files_checked": 112, "all_match": True,
            "category_counts": dict(collections.Counter(x["path"].split("/")[0] for x in used_checks)),
            "files": used_checks}

        ident = json.loads(ordinary(run17 / "SOURCE_IDENTITY.json"))
        input_paths = {
            "packet": old / "inputs/spectral11/m2.json",
            "events": old / "inputs/spectral11/m2_events.json",
            "run16_point": repo / PREFIX / "run16/feedback/execution01/RECORDED_STATE_FEEDBACK.json",
            "run16_prefix_C": repo / PREFIX / "run16/feedback/prefix_stephalf_execution01/PREFIX_STEP_HALVING.json",
            "source_manifest": sums,
            "context_code": run17 / "native/native_context.py"}
        raw_input_checks = []
        for key, path in input_paths.items():
            expected = ident["raw_inputs"][key]
            actual = digest(ordinary(path))
            if actual["bytes"] != expected["bytes"] or actual["sha256"] != expected["sha256"]:
                raise ValueError(f"explicit raw input mapping mismatch: {key}")
            raw_input_checks.append({"key": key, "producer_path": expected["path"],
                                     "restored_path": str(path.relative_to(repo)), **actual, "match": True})
        report["raw_input_path_overrides"] = raw_input_checks
        binding = ident["execution_to_publication_binding"]
        for path_key, id_key in [("executed_old_comparison_code", "executed_old_identity"),
                                 ("published_comparison_code", "published_identity")]:
            actual = digest(ordinary(run17 / path_safe(binding[path_key])))
            if any(actual[k] != binding[id_key][k] for k in ("bytes", "sha256")):
                raise ValueError("executed vs published comparison source binding mismatch")
        report["recorded_docstring_only_execution_binding_bytes_match"] = True
        git("tracked_diff_after", "diff", "--exit-code")
        git("cached_diff_after", "diff", "--cached", "--exit-code")
        final_head = git("head_after", "rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines()
        index_after = digest(ordinary(index_path))
        if final_head != [COMMIT, TREE] or index_before != index_after:
            raise ValueError("HEAD/index changed during readback")
        for row in sci:
            if digest(ordinary(run17 / row["path"])) != {k: row[k] for k in ("bytes", "sha256", "git_blob")}:
                raise ValueError("frozen science bytes changed during readback")
        report["unchanged_source"] = {"HEAD_tree_unchanged": True, "index_before": index_before,
                                      "index_after": index_after, "index_unchanged": True,
                                      "tracked_diff_empty": True, "cached_diff_empty": True,
                                      "all111_science_bytes_unchanged_after": True,
                                      "add_only_restored_untracked_files": [f["target"] for f in transport["files"]],
                                      "previous_worktree_writes": 0}
        report["status"] = "VERIFIED_SCOPED_CLEAN_GIT_BYTE_DELIVERY"
        report["scope_limits"] = [
            "No numerical recomputation, certificate replay, native binary build, or trajectory integration.",
            "Original gas executable was separately backed up by the parent; no Git-only executable restoration is claimed here.",
            "Original internal hashes are checked from Git; archive cross-source comparison is not repeated."]
        exit_code = 0
    except Exception as exc:
        report["status"] = "BLOCKED_READBACK_GUARD"
        report["error"] = {"type": type(exc).__name__, "message": str(exc)}
        exit_code = 1
    report["ended_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    raw = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
    write_new(out / "CLEAN_GIT_READBACK_RECEIPT.json", raw)
    print(json.dumps({"status": report["status"], "receipt": str(out / "CLEAN_GIT_READBACK_RECEIPT.json"),
                      **digest(raw), "scientific_execution_counts": report["counts"]}))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""Build delivery artifacts from an explicitly frozen publication payload.

This creates an independent source-artifact Git history, never rei_bianchi's
history. All Git worktrees stay under brperf01/git_delivery/. No baseline source,
license, external reference, or binary archive is added beyond the selected
publication payload. Run only after PACKAGE.py git has been finally frozen:

    python BUILD_SOURCE_DELIVERY.py --frozen

Output: brperf01/delivery/{source ZIP, add-only patch, Git bundle,
SOURCE_DELIVERY.json}. The FULL archive can include these artifacts afterwards;
do not regenerate the Git payload from that later FULL-archive state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
PREFIX = PurePosixPath("research/dossier_ssot_sandbox_20261016/bass_reactive_performance01_20261020")
PAYLOAD = HERE / "publication_payload"
DELIVERY = HERE / "delivery"
GIT_AREA = HERE / "git_delivery"
BRANCH = "brperf01-source-artifact"
AUTHOR_NAME = "REI source artifact builder"
AUTHOR_EMAIL = "artifact@local.invalid"
FIXED_DATE = "2026-10-20T00:00:00+00:00"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def checked_path(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name or "\x00" in name:
        raise ValueError(f"Unsafe payload path: {name!r}")
    if not p.is_relative_to(PREFIX):
        raise ValueError(f"Path outside the declared add-only prefix: {name}")
    return p


def collect() -> tuple[dict[str, bytes], list[dict], str]:
    contract_name = str(PREFIX / "GIT_RESTORE_CONTRACT.json")
    contract_data = (PAYLOAD / contract_name).read_bytes()
    contract = json.loads(contract_data)
    if contract.get("schema") != "rei.brperf01.git_payload.v1":
        raise ValueError("Unexpected publication restore-contract schema")
    files, rows = {}, []
    for row in contract["files"]:
        p = checked_path(row["path"])
        name = str(p)
        if name in files:
            raise ValueError(f"Duplicate payload path: {name}")
        source = PAYLOAD / name
        if source.is_symlink():
            raise ValueError(f"Symlink is not a regular publication payload: {name}")
        data = source.read_bytes()
        if len(data) != row["bytes"] or sha(data) != row["sha256"] or blob_sha(data) != row["git_blob_sha1"]:
            raise ValueError(f"Frozen publication payload hash mismatch: {name}")
        files[name] = data
        rows.append({"publication_path": name, "git_path": name,
                     "fresh_workspace_path": str(p.relative_to(PREFIX)),
                     "bytes": len(data), "sha256": sha(data),
                     "git_blob_sha1": blob_sha(data), "git_mode": "100644"})
    files[contract_name] = contract_data
    rows.append({"publication_path": contract_name, "git_path": contract_name,
                 "fresh_workspace_path": None, "mapping_role": "restore-contract metadata",
                 "bytes": len(contract_data), "sha256": sha(contract_data),
                 "git_blob_sha1": blob_sha(contract_data), "git_mode": "100644"})
    actual = {p.relative_to(PAYLOAD).as_posix() for p in PAYLOAD.rglob("*") if p.is_file()}
    if actual != set(files):
        raise ValueError(f"Publication inventory differs from contract: extra={sorted(actual-set(files))}, missing={sorted(set(files)-actual)}")
    return files, sorted(rows, key=lambda x: x["git_path"]), sha(contract_data)


def git(directory: Path, *args: str, input_data: bytes | None = None) -> bytes:
    if not directory.resolve().is_relative_to(GIT_AREA.resolve()):
        raise ValueError("Git operation requested outside the dedicated artifact area")
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(key, None)  # Never inherit paths into the original repository.
    env.update({"GIT_AUTHOR_NAME": AUTHOR_NAME, "GIT_AUTHOR_EMAIL": AUTHOR_EMAIL,
                "GIT_COMMITTER_NAME": AUTHOR_NAME, "GIT_COMMITTER_EMAIL": AUTHOR_EMAIL,
                "GIT_AUTHOR_DATE": FIXED_DATE, "GIT_COMMITTER_DATE": FIXED_DATE})
    command = ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
               "-c", "core.autocrlf=false", "-C", str(directory), *args]
    return subprocess.run(command, input=input_data, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=env, check=True).stdout


def verify_tree(root: Path, files: dict[str, bytes]) -> None:
    for name, data in files.items():
        if (root / name).read_bytes() != data:
            raise ValueError(f"Readback mismatch: {name}")


def artifact(path: Path) -> dict:
    data = path.read_bytes()
    return {"file": path.name, "path": str(path), "bytes": len(data), "sha256": sha(data)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", action="store_true", help="The parent has explicitly frozen publication_payload.")
    args = parser.parse_args()
    if not args.frozen:
        parser.error("Wait for the parent publication-payload freeze, then use --frozen.")
    files, rows, contract_sha = collect()
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    payload_sha = sha(canonical)
    if GIT_AREA.is_symlink():
        raise ValueError("Dedicated Git artifact area must not be a symlink")
    run = GIT_AREA / payload_sha[:16]
    if run.exists():
        raise FileExistsError(f"Artifact work area already exists; inspect its recovery inventory before rebuilding: {run}")
    run.mkdir(parents=True)
    history, clone, patch_tree = (run / name for name in ("source_history", "bundle_readback", "patch_readback"))
    history.mkdir()
    git(history, "init", "--quiet", "--initial-branch=" + BRANCH, "--object-format=sha1")
    git(history, "commit", "--quiet", "--allow-empty", "-m",
        "Initialize independent REI BRPERF01 source artifact history\n\nNo original rei_bianchi Git history is included.")
    initial = git(history, "rev-parse", "HEAD").decode().strip()
    for name, data in files.items():
        target = history / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o644)
    git(history, "add", "--all", "--", str(PREFIX))
    message = ("Add frozen BRPERF01 publication payload\n\n"
               f"Payload mapping SHA-256: {payload_sha}\n"
               f"Restore contract SHA-256: {contract_sha}\n"
               "Independent source-artifact commit; no original repository history or production branch update.\n")
    git(history, "commit", "--quiet", "-m", message)
    head = git(history, "rev-parse", "HEAD").decode().strip()
    tree = git(history, "rev-parse", "HEAD^{tree}").decode().strip()
    if git(history, "rev-list", "--count", "HEAD").strip() != b"2":
        raise ValueError("Source artifact history must contain exactly two commits")
    changes = git(history, "diff", "--name-status", "--no-renames", initial, head).decode().splitlines()
    expected = ["A\t" + path for path in sorted(files)]
    if sorted(changes) != expected or git(history, "status", "--porcelain"):
        raise ValueError("Artifact commit is not exactly the clean add-only payload")
    DELIVERY.mkdir(exist_ok=True)
    stem = "REI_BRPERF01_SOURCE_ARTIFACT_20261020_" + payload_sha[:12]
    patch = DELIVERY / (stem + ".patch")
    bundle = DELIVERY / (stem + ".bundle")
    source_zip = DELIVERY / (stem + ".zip")
    patch.write_bytes(git(history, "diff", "--binary", "--full-index", "--no-renames",
                          "--no-ext-diff", "--no-textconv", "--src-prefix=a/", "--dst-prefix=b/",
                          initial, head, "--"))
    git(history, "bundle", "create", str(bundle), "--all")
    git(history, "bundle", "verify", str(bundle))
    bundle_header = bundle.read_bytes().split(b"\n\n", 1)[0].decode("utf-8").splitlines()
    if any(line.startswith("-") for line in bundle_header):
        raise ValueError("The source bundle unexpectedly requires external commits")
    git(history, "archive", "--format=zip", "--output=" + str(source_zip), head)
    # Read back the self-contained bundle and patch in separate generated trees.
    git(run, "clone", "--quiet", "--no-hardlinks", str(bundle), str(clone))
    if git(clone, "rev-parse", "HEAD").decode().strip() != head:
        raise ValueError("Bundle clone HEAD differs from the source snapshot")
    verify_tree(clone, files)
    patch_tree.mkdir()
    git(patch_tree, "init", "--quiet", "--initial-branch=patch-readback", "--object-format=sha1")
    git(patch_tree, "apply", "--check", str(patch))
    git(patch_tree, "apply", "--whitespace=nowarn", str(patch))
    verify_tree(patch_tree, files)
    with zipfile.ZipFile(source_zip) as archive:
        members = {name for name in archive.namelist() if not name.endswith("/")}
        if members != set(files) or any(archive.read(name) != data for name, data in files.items()):
            raise ValueError("Source ZIP readback differs from the frozen payload")
    # Detect any late mutation of the publisher's frozen input.
    current_files, current_rows, current_contract_sha = collect()
    if current_files != files or current_rows != rows or current_contract_sha != contract_sha:
        raise ValueError("Publication payload changed during artifact creation")
    receipt = {
        "schema": "rei.brperf01.source_delivery.v1", "status": "COMPLETE_VERIFIED_ARTIFACT",
        "history_kind": "INDEPENDENT_SOURCE_ARTIFACT_HISTORY_NOT_REI_REPOSITORY_HISTORY",
        "original_rei_history_included": False, "original_repo_modified": False,
        "publication_payload_root": str(PAYLOAD), "publication_prefix": str(PREFIX),
        "source_scope": "Exact frozen publication text/bounded-evidence payload; full baseline/science archive remains a separate dependency.",
        "source_selection_rule": "GIT_RESTORE_CONTRACT.files plus the restore contract itself; no additional license or external source is introduced.",
        "restore_contract_sha256": contract_sha, "payload_mapping_sha256": payload_sha,
        "selected_files": len(files), "selected_bytes": sum(len(x) for x in files.values()),
        "git": {"branch": BRANCH, "initial_empty_commit": initial, "snapshot_commit": head,
                "tree": tree, "commit_count": 2, "author_name": AUTHOR_NAME,
                "author_email": AUTHOR_EMAIL, "fixed_commit_date": FIXED_DATE,
                "worktree": str(history), "bundle_prerequisites": []},
        "artifacts": {"source_zip": artifact(source_zip), "add_only_patch": artifact(patch), "git_bundle": artifact(bundle)},
        "verification": {"all_changes_add_only": True, "git_status_clean": True,
                         "bundle_verify": "PASS", "bundle_clone_byte_readback": "PASS",
                         "patch_apply_check": "PASS", "patch_apply_byte_readback": "PASS",
                         "zip_byte_readback": "PASS", "frozen_payload_unchanged": True,
                         "new_science_tests_or_benchmarks": False},
        "apply_contract": {"patch": "From a repository root whose new publication paths do not already exist: git apply --check ARTIFACT.patch; git apply ARTIFACT.patch",
                           "bundle": "git clone ARTIFACT.bundle NEW_DIRECTORY creates the independent artifact history, not a restored rei_bianchi Git repository.",
                           "workspace": "Use the included MATERIALIZE_GIT.py and pinned BR06 archive as declared by GIT_RESTORE_CONTRACT.json."},
        "selected_paths": rows,
    }
    receipt_path = DELIVERY / "SOURCE_DELIVERY.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "history_kind", "selected_files", "selected_bytes", "payload_mapping_sha256", "git", "artifacts")}, indent=2))


if __name__ == "__main__":
    main()

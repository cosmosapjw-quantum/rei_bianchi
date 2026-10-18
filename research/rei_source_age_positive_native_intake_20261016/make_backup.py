#!/usr/bin/env python3
"""Package exact Git research/native source objects and their byte manifest."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

RESEARCH = "research/rei_source_age_positive_native_intake_20261016"
PARENT_SOURCE = "research/rei_source_age_native_owner_bind_20261016"
NATIVE_SHA = "35d9747a0bbedcafdb568467ce7c1e7a25f965b6"
NATIVE_EMBEDDED_INPUTS = (
    "docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json",
    "research/flrw_jacobian_columns_20261016/CONTRACT.json",
    "research/bass_source008_20261016/CONTRACT.json",
    "research/bass_source007_20261016/CONTRACT.json",
    "research/bass_source009_20261016/CONTRACT.json",
    "research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json",
    "research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md",
    "research/flrw_covariant_transport_20261015/NATIVE_CONTRACT.md",
    "research/flrw_covariant_transport_20261015/INACTIVE_POOL_CONTRACT.md",
    "research/flrw_covariant_transport_20261015/HPC_CONTRACT.md",
    "research/flrw_covariant_transport_20261015/BACKGROUND_CACHE_CONTRACT.md",
    "research/flrw_covariant_transport_20261015/OUTPUT_ALLOCATION_005_CONTRACT.md",
)


def git(*args):
    return subprocess.check_output(["git", *args])


def paths(commit, prefix):
    return git("ls-tree", "-r", "--name-only", commit, "--", prefix).decode().splitlines()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("commit")
    p.add_argument("output", type=Path)
    args = p.parse_args()
    payload = {}
    for path in paths(args.commit, RESEARCH):
        payload[path] = git("show", f"{args.commit}:{path}")
    for name in ("native_owner.rs", "prepared_node_accessor.rs"):
        path = f"{PARENT_SOURCE}/{name}"
        payload[path] = git("show", f"{args.commit}:{path}")
    for path in paths(NATIVE_SHA, "rust/rei_microphysics"):
        payload[f"native_source/{path}"] = git("show", f"{NATIVE_SHA}:{path}")
    for path in NATIVE_EMBEDDED_INPUTS:
        payload[f"native_source/{path}"] = git("show", f"{NATIVE_SHA}:{path}")
    for name in ("RESTORE_VERIFY.sh", "make_backup.py"):
        path = f"{RESEARCH}/{name}"
        payload[path] = (Path(__file__).parent / name).read_bytes()
    manifest = {
        "research_commit": args.commit,
        "original_native_sha": NATIVE_SHA,
        "payload": {k: {"size": len(v), "sha256": hashlib.sha256(v).hexdigest()}
                    for k, v in sorted(payload.items())},
    }
    payload["PAYLOAD_MANIFEST.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(payload.items()):
            info = zipfile.ZipInfo(path, date_time=(2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(json.dumps({"archive": str(args.output), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "payload_files": len(manifest["payload"])}, sort_keys=True))


if __name__ == "__main__":
    main()

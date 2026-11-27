#!/usr/bin/env python3
"""Create an immutable capsule from this committed PHYS72 source subtree.

The result is explicitly a source/evidence ZIP, not a full Git clone.
It uses committed tracked bytes only and never includes a binary/cache or
the original numerical campaigns. All output paths are create-only.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(git(Path(__file__).resolve().parent, "rev-parse", "--show-toplevel").decode().strip())
    scope = "research/hh_phys72_20261020"
    if git(repo, "status", "--porcelain", "--untracked-files=all", "--", scope).strip():
        raise SystemExit("Commit the complete PHYS72 subtree before freezing a capsule")
    if args.out.exists() or args.receipt.exists():
        raise SystemExit("Create-only output already exists")
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    tree = git(repo, "rev-parse", "HEAD^{tree}").decode().strip()
    names = git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", scope).decode().splitlines()
    payload = {name: git(repo, "show", f"HEAD:{name}") for name in names}
    files = [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
             for name, data in payload.items()]
    manifest = {"schema": "PHYS72_COMMITTED_SOURCE_CAPSULE_V1", "source_commit": head,
                "source_tree": tree, "repository": "cosmosapjw-quantum/WU088_HH",
                "base_commit": "7060b2390caa931a74b3a377150731b98c2431a9",
                "is_full_git_clone": False, "contains_old_panel_campaign": False,
                "contains_native_binaries": False, "HH_R10": "OFF", "files": files}
    prefix = args.out.stem
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in payload.items():
            info = zipfile.ZipInfo(prefix + "/" + name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
        archive.writestr(prefix + "/CAPSULE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    receipt = {"schema": "PHYS72_CAPSULE_BUILD_RECEIPT_V1",
               "built_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "source_commit": head, "source_tree": tree, "file_count": len(files),
               "path": str(args.out.resolve()), "bytes": args.out.stat().st_size,
               "sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
               "is_full_git_clone": False, "status": "BUILT_LOCAL_BYTES"}
    with args.receipt.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

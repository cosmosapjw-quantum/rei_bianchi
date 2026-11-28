#!/usr/bin/env python3
"""Build a restore-oriented capsule and member SHA256SUMS for this supplement."""
from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "evidence" / "REI_UNIFIED_FINAL_20261021.tar.gz"


def main() -> None:
    repo = ROOT.parents[1]
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"], text=True).strip()
    files = [
        ROOT / "REPORT_KO.md",
        ROOT / "DAG_OVERLAY.json",
        ROOT / "D8_RESULT.json",
        ROOT / "source" / "analyze_d8.py",
        ROOT / "source" / "test_analyze_d8.py",
        ROOT / "source" / "package_capsule.py",
        ROOT / "delivery" / "PHYS76_REI199_D8_RUN_RECORD.json",
        ROOT / "delivery" / "PUBLICATION_BACKUP_STATUS.json",
        ROOT / "delivery" / "PROVIDER_BACKUP_RESTORE_RECEIPT.json",
        ARCHIVE,
    ]
    missing = [str(p) for p in files if not p.is_file()]
    if missing:
        raise FileNotFoundError("missing capsule payload: " + ", ".join(missing))
    name = f"PHYS76_REI199_D8_CAPSULE_{commit[:12]}.zip"
    out = repo / "archives" / name
    sums = repo / "archives" / f"{name}.SHA256SUMS"
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "PHYS76_REI199_D8_CAPSULE_V1",
        "commit": commit,
        "tree": tree,
        "payload_root": "research/hh_phys76_rei199_d8_20261021",
        "members": [],
    }
    for p in files:
        rel = p.relative_to(repo).as_posix()
        data = p.read_bytes()
        manifest["members"].append({"path": rel, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in files:
            zf.write(p, p.relative_to(repo).as_posix())
        zf.writestr("CAPSULE_MANIFEST.json", manifest_bytes)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    sums.write_text(f"{digest}  {out.name}\n")
    print(json.dumps({"archive": str(out), "bytes": out.stat().st_size, "sha256": digest, "manifest": str(sums), "commit": commit, "tree": tree}))


if __name__ == "__main__":
    main()

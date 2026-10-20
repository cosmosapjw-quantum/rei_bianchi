#!/usr/bin/env python3
"""Snapshot this numerical unit plus the exact original parent crate, then restore.

Cargo uses the separately pinned offline registry in the shared runtime; a clean
target tests restored source bytes. No original source is edited by this script.
"""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

unit = Path(__file__).resolve().parent
workspace = unit.parent.parent
parent = workspace / "repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019/parent/crate"
source_paths = [unit / p for p in ["Cargo.toml", "Cargo.lock", "src/lib.rs", "examples/measure_rates.rs", "validate_pchip.py", "summarize_bench.py", "prepare_restore.py", "RUN_STAGE.sh", "SOURCE_CONTRACT.json"]]
source_paths += [Path(p) for p in subprocess.check_output(["rg", "--files", str(parent)], text=True).splitlines() if "target" not in Path(p).parts]
snapshot = unit / "evidence/RATES_SOURCE_SNAPSHOT.zip"
payload = []
with zipfile.ZipFile(snapshot, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(source_paths):
        data = path.read_bytes()
        name = str(path.relative_to(workspace))
        archive.writestr(name, data)
        payload.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
restore = unit / "fresh_restore"
restore.mkdir(exist_ok=True)
with zipfile.ZipFile(snapshot) as archive:
    archive.extractall(restore)
for entry in payload:
    assert hashlib.sha256((restore / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
manifest = {"zip_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(), "zip_bytes": snapshot.stat().st_size, "payload_count": len(payload), "all_payload_hashes_restored": True, "sources": payload, "dependency_restore_scope": "Original parent crate payload restored; pinned offline registry and Rust toolchain reused from shared runtime, empty CARGO_TARGET_DIR used for validation."}
(unit / "evidence/FRESH_SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: v for k, v in manifest.items() if k != "sources"}, indent=2))

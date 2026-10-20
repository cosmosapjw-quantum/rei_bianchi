#!/usr/bin/env python3
"""Build deterministic research checkpoints and an add-only Git payload.

All science code is copied byte-for-byte. Build caches and regenerated restore
trees are omitted. External reference program/text downloads without an explicit
redistribution grant are represented by their URL/hash fetch contract; numerical
fit parameters, our implementation, and verification receipts remain included.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
PREFIX = "research/dossier_ssot_sandbox_20261016/bass_reactive_performance01_20261020"
BASE = WORKSPACE / "repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019"
SKIP_PARTS = {"target", "fresh_target", "fresh_restore", "fresh_restore_work", "empty_target", "restore_tree", "cargo_home", "__pycache__", "mpl_cache", "runtime", "outputs", "git_delivery", "publication_payload", "private"}
EXTERNAL_REFERENCES = {
    "atomic_theory/data/phfit2.f", "atomic_theory/data/cfit.f",
    "atomic_theory/data/photo.txt", "atomic_theory/data/cfit.txt",
    "atomic_theory/data/rec_table.txt", "atomic_theory/data/author_info.html",
    "atomic_theory/ATOMIC_SOURCE_SNAPSHOT.zip",
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def collect() -> tuple[dict[str, bytes], list[dict]]:
    files, omitted = {}, []
    for p in sorted(HERE.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(HERE)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        name = rel.as_posix()
        # Research search responses can contain full third-party abstracts/pages.
        raw_search = name.startswith("atomic_theory/evidence/") and any(
            token in p.name for token in ("_TOOL_", "SCISPACE_TARGETED")
        )
        if name in EXTERNAL_REFERENCES or raw_search:
            b = p.read_bytes()
            omitted.append({"path": "brperf01/" + name, "bytes": len(b), "sha256": sha(b), "reason": "EXTERNAL_REFERENCE_FETCH_CONTRACT_OR_METADATA_RECEIPT"})
            continue
        files["brperf01/" + name] = p.read_bytes()
    return files, omitted

def archive(name: str, payload: dict[str, bytes], omitted: list[dict], *, baseline: bool) -> dict:
    if baseline:
        # Use the original BR06 declared payload list, not incidental build trees.
        base_manifest = json.loads((BASE / "MANIFEST_SHA256.json").read_text()) if (BASE / "MANIFEST_SHA256.json").exists() else None
        if base_manifest is None:
            old_zip = WORKSPACE / "br06_recovery/outputs/REI_BASS_REACTIVE06_VIGILODE_REFERENCE_RECOVERY_20261020_3137ad89_FULL.zip"
            with zipfile.ZipFile(old_zip) as z:
                base_manifest = json.loads(z.read("MANIFEST_SHA256.json"))
        for entry in base_manifest["files"]:
            path = BASE / entry["path"]
            if not path.is_file():
                # Archive metadata outside the materialized scientific tree is not a dependency.
                continue
            data = path.read_bytes()
            if sha(data) != entry["sha256"]:
                raise ValueError(f"Frozen source/input mismatch: {entry['path']}")
            payload[path.relative_to(WORKSPACE).as_posix()] = data
    manifest = {"schema": "rei.brperf01.archive.v1", "baseline_commit": "54948439be7039c9b2b1f9580bee69bebeb80129", "baseline_included": baseline,
        "files": [{"path": p, "bytes": len(b), "sha256": sha(b)} for p, b in sorted(payload.items())], "reference_omissions": omitted}
    path = HERE / "outputs" / name
    path.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p, b in sorted(payload.items()):
            info = zipfile.ZipInfo(p, (2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, b)
        info = zipfile.ZipInfo("MANIFEST_SHA256.json", (2026, 10, 20, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    data = path.read_bytes()
    content_hash = sha(b"".join(hashlib.sha256(data[i:i+4194304]).digest() for i in range(0, len(data), 4194304)))
    result = {"path": str(path), "file": name, "bytes": len(data), "sha256": sha(data), "md5": hashlib.md5(data).hexdigest(), "dropbox_content_hash": content_hash,
        "payload_files": len(payload), "entries": len(payload)+1, "baseline_included": baseline, "reference_omission_count": len(omitted)}
    (path.with_suffix(".identity.json")).write_text(json.dumps(result, indent=2)+"\n")
    return result

def git_payload(files: dict[str, bytes], omitted: list[dict]) -> dict:
    root = HERE / "publication_payload"
    if root.exists():
        shutil.rmtree(root)  # Only this script's disposable, generated payload.
    root.mkdir(exist_ok=True)
    selected, large = [], []
    for name, data in sorted(files.items()):
        path = Path(name)
        try:
            data.decode("utf-8")
            text = True
        except UnicodeError:
            text = False
        if not text or len(data) > 100_000:
            large.append({"path": name, "bytes": len(data), "sha256": sha(data), "location": "FULL_ARCHIVE"})
            continue
        target = root / PREFIX / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        selected.append({"path": f"{PREFIX}/{name}", "bytes": len(data), "sha256": sha(data), "git_blob_sha1": hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()})
    contract = {"schema":"rei.brperf01.git_payload.v1","workspace_mapping":"Git subtree brperf01/ -> fresh workspace brperf01/; restore pinned BR06 archive at workspace repo/research/.../bass_reactive06_vigilode_reference_20261019/","files": selected,"archive_only":large,"external_reference_omissions":omitted}
    p = root / PREFIX / "GIT_RESTORE_CONTRACT.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(contract, indent=2)+"\n")
    return {"selected_files":len(selected)+1,"archive_only":len(large),"root":str(root)}

def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("mode",choices=("stages","full","git"));args=parser.parse_args()
    files, omitted=collect()
    if args.mode=="stages":
        for stage, groups in [("01_T_TABLE_NATIVE",("rates/","native_rates/","integration/")),("02_PHOTON",("photon/",)),("03_ATOMIC",("atomic_theory/",))]:
            chosen={k:v for k,v in files.items() if k.startswith(tuple("brperf01/"+g for g in groups)) or k.startswith("brperf01/contracts/")}
            print(json.dumps(archive("REI_BRPERF01_STAGE"+stage+"_20261020.zip",chosen,[x for x in omitted if x["path"].startswith(tuple("brperf01/"+g for g in groups))],baseline=False)))
    elif args.mode=="full":
        print(json.dumps(archive("REI_BRPERF01_OPTIMIZATION_20261020_FULL.zip",files,omitted,baseline=True)))
    else:
        print(json.dumps(git_payload(files,omitted)))

if __name__=="__main__":
    main()

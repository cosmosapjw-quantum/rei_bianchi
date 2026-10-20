#!/usr/bin/env python3
"""Read-only byte/entry verification of the three freshly packaged stage ZIPs."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import zipfile

here = Path(__file__).resolve().parent
root = here.parent
verifier = root / "VERIFY_ARCHIVE.py"
names = [
    "REI_BRPERF01_STAGE01_T_TABLE_NATIVE_20261020.zip",
    "REI_BRPERF01_STAGE02_PHOTON_20261020.zip",
    "REI_BRPERF01_STAGE03_ATOMIC_20261020.zip",
]
records = []
for name in names:
    archive = root / "outputs" / name
    identity_path = archive.with_suffix(".identity.json")
    identity_bytes = identity_path.read_bytes()
    identity = json.loads(identity_bytes)
    initial_stat = archive.stat()
    data = archive.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    block_hashes = b"".join(hashlib.sha256(data[start:start + 4 * 1024 * 1024]).digest() for start in range(0, len(data), 4 * 1024 * 1024))
    provider_hash = hashlib.sha256(block_hashes).hexdigest()
    assert len(data) == identity["bytes"] and digest == identity["sha256"]
    assert hashlib.md5(data).hexdigest() == identity["md5"]
    assert provider_hash == identity["dropbox_content_hash"]
    log = here / (archive.stem + ".log")
    argv = ["python3", str(verifier), str(archive)]
    with log.open("w") as stream:
        completed = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT)
    assert completed.returncode == 0, name
    verified = json.loads(log.read_text())
    assert verified["status"] == "PASS" and verified["archive_sha256"] == digest
    assert verified["payloads"] == identity["payload_files"]
    with zipfile.ZipFile(archive) as stream:
        entries = stream.namelist()
        assert len(entries) == len(set(entries)) == identity["entries"]
        manifest_bytes = stream.read("MANIFEST_SHA256.json")
        manifest = json.loads(manifest_bytes)
        assert len(manifest["files"]) == identity["payload_files"]
    final_stat = archive.stat()
    assert initial_stat.st_size == final_stat.st_size and initial_stat.st_mtime_ns == final_stat.st_mtime_ns
    assert identity_path.read_bytes() == identity_bytes
    records.append({
        "file": name, "status": "PASS", "bytes": len(data), "sha256": digest,
        "entries": len(entries), "verified_payloads": verified["payloads"],
        "zip_entry_duplicates": 0, "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "identity_sha256": hashlib.sha256(identity_bytes).hexdigest(),
        "zip_mtime_utc": datetime.datetime.fromtimestamp(initial_stat.st_mtime, datetime.timezone.utc).isoformat(),
        "identity_mtime_utc": datetime.datetime.fromtimestamp(identity_path.stat().st_mtime, datetime.timezone.utc).isoformat(),
        "fresh_identity_matches_current_archive": True, "identity_and_archive_unchanged_during_check": True,
        "md5_and_dropbox_content_hash_recomputed": True,
        "baseline_included": identity["baseline_included"], "reference_omission_count": identity["reference_omission_count"],
        "command": argv, "returncode": completed.returncode, "log": log.name,
    })
result = {
    "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "PASS", "scope": "STAGE_ARCHIVE_ENTRY_AND_BYTE_HASH_READBACK_ONLY",
    "verifier": str(verifier), "verifier_sha256": hashlib.sha256(verifier.read_bytes()).hexdigest(),
    "archives": records, "total_verified_payloads": sum(row["verified_payloads"] for row in records),
    "source_tests_run": 0, "benchmarks_run": 0, "science_recomputations_or_reviews": 0,
    "extractions": 0, "original_source_or_evidence_modified": False,
}
(here / "STAGE_ARCHIVE_CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": "PASS", "archives": len(records), "verified_payloads": result["total_verified_payloads"], "source_tests": 0, "benchmarks": 0, "science_runs": 0}))

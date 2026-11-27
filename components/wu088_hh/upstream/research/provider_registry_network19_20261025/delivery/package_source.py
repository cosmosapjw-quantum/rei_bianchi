#!/usr/bin/env python3
"""Create a reproducible source ZIP from an exact published commit, without runs."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATHS = [
    "AGENTS.md",
    "research/program_expansion_20261025",
    "research/provider_registry_20261025",
    "research/provider_registry_network19_20261025",
    "research/rei_chem_ledger_20261025",
]


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--expected-tree", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    commit = git("rev-parse", args.commit + "^{commit}").decode().strip()
    tree = git("rev-parse", commit + "^{tree}").decode().strip()
    if commit != args.commit or tree != args.expected_tree:
        raise SystemExit("Commit/tree identity mismatch")
    if args.output.exists() or args.receipt.exists():
        raise SystemExit("Refusing to overwrite an existing archive or receipt")
    names = git("ls-tree", "-r", "--name-only", commit, "--", *PATHS).decode().splitlines()
    if not names or "research/provider_registry_20261025/SCIENTIFIC_ADMISSION.json" not in names:
        raise SystemExit("Missing accepted source-registry payload")
    names.sort()
    objects = {}
    for name in names:
        objects[name] = git("show", f"{commit}:{name}")
    admission = json.loads(objects["research/provider_registry_20261025/SCIENTIFIC_ADMISSION.json"])
    if admission["decision"] != "ACCEPT_SCOPED_SOURCE_ROWS_AND_INTEGER_PROJECTIONS":
        raise SystemExit("Unexpected source admission")
    r2 = json.loads(objects["research/provider_registry_network19_20261025/SCIENTIFIC_ADMISSION.json"])
    if r2["decision"] != "ACCEPT_SCOPED_TARGET19_SOURCE_BINDINGS_AND_NUMBER_PROJECTIONS":
        raise SystemExit("Unexpected R2 admission")
    records = [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
               for name, data in objects.items()]
    manifest = {
        "schema": "WU_PROVIDER_REGISTRY_TARGET19_SOURCE_ARCHIVE_V2",
        "repository": "cosmosapjw-quantum/WU088_HH",
        "source_commit": commit,
        "source_tree": tree,
        "source_base": "34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad",
        "previous_R1_source": "18a6804d7cbe4879701e83631f7e908bbb84cef1",
        "previous_R1_ZIP_sha256": "c1ced1cdeb7382064e64d11abd38d52466802a699edf99bd78aa355c0ce17863",
        "previous_R1_dropbox_id": "id:BSpOijBcT10AAAAAAEAb2w",
        "previous_R1_drive_id": "10N1VsPIPPSVzw7qXMQfZ9G1a0hkDZRV5",
        "scope": PATHS,
        "dependency": "unchanged finite compiler, stored prior admission/results and fixed expansion handoff",
        "complete_historical_repository_snapshot": False,
        "prior_PHYS91_archive": {
            "bytes": 37419031,
            "sha256": "b12f946dabe2f15e242e489977102abebdd58d3ce8acf336ec0753c25c74f2b7",
            "dropbox_id": "id:BSpOijBcT10AAAAAAD_-EQ",
            "drive_id": "1SE8UhYbm3k6TAYAVOyGwrGYKOHnaQ5z7",
        },
        "source_files": records,
        "current_unit_postpublication_receipts_included": False,
        "prior_R1_postpublication_receipts_included": True,
    }
    objects["SOURCE_ARCHIVE_MANIFEST.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in objects.items():
            item = zipfile.ZipInfo("WU088_HH/" + name, (2026, 10, 25, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            archive.writestr(item, data)
    # Read actual archive bytes back and verify every member against its source.
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise SystemExit("ZIP CRC verification failed")
        for name, data in objects.items():
            if archive.read("WU088_HH/" + name) != data:
                raise SystemExit("Source ZIP member mismatch: " + name)
    blob = args.output.read_bytes()
    block_hashes = b"".join(hashlib.sha256(blob[i:i + 4 * 1024 * 1024]).digest()
                           for i in range(0, len(blob), 4 * 1024 * 1024))
    receipt = {
        "schema": "WU_PROVIDER_REGISTRY_TARGET19_SOURCE_ZIP_RECEIPT_V2",
        "source_commit": commit,
        "source_tree": tree,
        "archive": args.output.name,
        "bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "dropbox_content_hash_locally_computed": hashlib.sha256(block_hashes).hexdigest(),
        "source_files": len(records),
        "archive_members": len(objects),
        "scope": PATHS,
        "manifest_member": "WU088_HH/SOURCE_ARCHIVE_MANIFEST.json",
        "all_member_bytes_match_published_commit": True,
        "zip_crc_readback": "PASS",
        "physical_calculations": 0,
        "backup_provider_ACKs": "SEPARATE_PENDING",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()

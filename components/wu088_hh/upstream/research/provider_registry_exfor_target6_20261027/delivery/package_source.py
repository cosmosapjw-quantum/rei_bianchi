#!/usr/bin/env python3
"""Archive exact published R3 source and inherited registry evidence; no runs."""
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
    "research/provider_registry_exfor_target6_20261027",
    "research/rei_chem_ledger_20261025",
]
R3 = "research/provider_registry_exfor_target6_20261027"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def main():
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
        raise SystemExit("Preserve prior archive and receipt")
    names = sorted(git("ls-tree", "-r", "--name-only", commit, "--", *PATHS).decode().splitlines())
    objects = {name: git("show", f"{commit}:{name}") for name in names}
    admission = json.loads(objects[R3 + "/SCIENTIFIC_ADMISSION.json"])
    if admission["decision"] != "ACCEPT_SCOPED_EXFOR_TARGET6_SOURCE_REFERENCE_CLOSURE":
        raise SystemExit("R3 source intake has not been accepted")
    if json.loads(objects[R3 + "/registry/coverage.json"])["directions_with_any_primary_source_record_reference"] != 28:
        raise SystemExit("Unexpected source-reference coverage")
    records = [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} for name, data in objects.items()]
    manifest = {
        "schema": "WU_PROVIDER_REGISTRY_EXFOR_R3_SOURCE_ARCHIVE_V1",
        "repository": "cosmosapjw-quantum/WU088_HH", "source_commit": commit, "source_tree": tree,
        "fixed_handoff_commit": "34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad",
        "previous_R1_source": "18a6804d7cbe4879701e83631f7e908bbb84cef1",
        "previous_R2_source": "71019bb469c92d1ea665155ed98c472b362d6706",
        "previous_R2_metadata": "87933da5654bb2e4d93f7de4341df5e0fa0f8716",
        "previous_R2_ZIP_sha256": "43845ea085797a6d628b722d58197a64a0af6f0a34a708f3dc981a5274faa906",
        "previous_R2_dropbox_id": "id:BSpOijBcT10AAAAAAEAfFg",
        "previous_R2_drive_id": "1C4NE14swNXTL4GXb-ol8HE8cm57sHaIe",
        "scope": PATHS, "source_files": records,
        "complete_historical_repository_snapshot": False,
        "current_unit_postpublication_receipts_included": False,
        "prior_R1_R2_postpublication_receipts_included": True,
        "source_license": "EXFOR data CC-BY-4.0; supplier attribution and license bundled",
        "dependency": "Unchanged compiler, saved R1/R2 checks and fixed expansion handoff; no science replay",
        "physical_rate_Q_consumer_admission": False,
    }
    objects["SOURCE_ARCHIVE_MANIFEST.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in objects.items():
            item = zipfile.ZipInfo("WU088_HH/" + name, (2026, 10, 27, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            archive.writestr(item, data)
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise SystemExit("ZIP CRC failure")
        for name, data in objects.items():
            if archive.read("WU088_HH/" + name) != data:
                raise SystemExit("Source member mismatch: " + name)
    blob = args.output.read_bytes()
    block_hashes = b"".join(hashlib.sha256(blob[i:i + 4 * 1024 * 1024]).digest()
                           for i in range(0, len(blob), 4 * 1024 * 1024))
    receipt = {
        "schema": "WU_PROVIDER_REGISTRY_EXFOR_R3_ZIP_RECEIPT_V1",
        "source_commit": commit, "source_tree": tree, "archive": args.output.name,
        "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(),
        "dropbox_content_hash_locally_computed": hashlib.sha256(block_hashes).hexdigest(),
        "source_files": len(records), "archive_members": len(objects), "scope": PATHS,
        "manifest_member": "WU088_HH/SOURCE_ARCHIVE_MANIFEST.json",
        "all_member_bytes_match_published_commit": True, "zip_crc_readback": "PASS",
        "physical_calculations": 0, "backup_provider_ACKs": "SEPARATE_PENDING",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()

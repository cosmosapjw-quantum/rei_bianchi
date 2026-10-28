"""One full private backup ZIP and separate public Git payloads, once.

Call only after final report/review. Private archive streams each unit source
file once, calculates its SHA and ZIP CRC, verifies every CRC in one pass, then
hashes the completed ZIP once. Public payloads exclude private inventories.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import resource
import time
import zipfile


PUBLIC_DIRS = ("theory/", "implementation/", "review/", "reused_native_review/",
               "inputs/", "execution/", "delivery/")
PUBLIC_FILES = {
    "REPORT_KO.md", "ADMISSION.json", "BUDGET_STATUS.json", "HANDOFF_KO.md",
    "STAGE_LEDGER.json", "intake/synthesis.md", "intake/DAG_CURRENT_COMPARISON.json",
    "intake/WORK_THREAD_PROMPT_KO.md",
}
PRIVATE_EXCLUDES = {"__pycache__", ".git", ".DS_Store"}


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(262144):
            digest.update(block)
    return digest.hexdigest()


def is_public(relative: str) -> bool:
    return relative in PUBLIC_FILES or relative.startswith(PUBLIC_DIRS)


def write_json_exclusive(path: Path, document: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(document, stream, ensure_ascii=False, separators=(",", ":"))
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--private-zip", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--public-text-payload", type=Path, required=True)
    parser.add_argument("--png-blob-payload", type=Path, required=True)
    args = parser.parse_args()
    start_wall, start_cpu = time.monotonic(), cpu()
    root = args.unit.resolve(strict=True)
    private, receipt, public_text, png_blob = (
        path.resolve() for path in (args.private_zip, args.receipt,
                                     args.public_text_payload, args.png_blob_payload))
    targets = {private, receipt, public_text, png_blob}
    if len(targets) != 4:
        raise ValueError("Delivery targets must differ")
    if any(p.exists() for p in targets):
        raise FileExistsError("One-pass delivery output already exists; preserve and diagnose")
    files = sorted((p for p in root.rglob("*") if p.is_file() and
                    not any(part in PRIVATE_EXCLUDES for part in p.relative_to(root).parts)
                    and p.resolve() not in targets and
                    not p.name.endswith((".tmp", ".pyc", ".zip"))),
                   key=lambda p: p.relative_to(root).as_posix())
    rels = {p.relative_to(root).as_posix() for p in files}
    required = {"REPORT_KO.md", "ADMISSION.json", "BUDGET_STATUS.json",
                "STAGE_LEDGER.json", "delivery/eos_branch_four_panel.png",
                "delivery/eos_branch_four_panel.svg",
                "execution/attempt01/saved_source_result.json",
                "execution/attempt01/RESULT.json"}
    if not required <= rels:
        raise ValueError(f"Finalized evidence missing: {sorted(required-rels)}")
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
    temp = private.with_name(private.name + ".tmp")
    if temp.exists():
        raise FileExistsError("Unfinished private ZIP exists; preserve and diagnose")
    entries, text_entries, png_entry = [], [], None
    with zipfile.ZipFile(temp, "x", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as archive:
        for source in files:
            relative = source.relative_to(root).as_posix()
            included = is_public(relative)
            digest = hashlib.sha256()
            size = 0
            content = bytearray() if included else None
            with source.open("rb") as inp, archive.open(root.name + "/" + relative, "w") as out:
                while block := inp.read(262144):
                    digest.update(block)
                    size += len(block)
                    out.write(block)
                    if content is not None:
                        content.extend(block)
            entries.append({"path": relative, "bytes": size, "sha256": digest.hexdigest(),
                            "public": included})
            if content is not None:
                if relative.endswith(".png"):
                    if png_entry is not None:
                        raise ValueError("Only one final PNG can be published")
                    png_entry = {"path": relative, "encoding": "base64",
                                 "content": base64.b64encode(content).decode("ascii")}
                else:
                    text_entries.append({"path": relative, "encoding": "utf-8",
                                         "content": content.decode("utf-8")})
        crcs = {z.filename.removeprefix(root.name + "/"): z.CRC for z in archive.infolist()}
    if png_entry is None:
        raise ValueError("Final PNG missing")
    for entry in entries:
        entry["crc32"] = f"{crcs[entry['path']]:08x}"
    # One independent decompression/CRC pass after the writer has closed.
    with zipfile.ZipFile(temp, "r") as verify:
        failed = verify.testzip()
        if failed is not None:
            raise ValueError(f"ZIP CRC verification failed at {failed}; no retry")
        if len(verify.infolist()) != len(entries):
            raise ValueError("ZIP inventory count mismatch")
    temp.rename(private)
    archive_sha = sha256(private)
    write_json_exclusive(public_text, {"schema": "REI_EOS_PUBLIC_TEXT_PAYLOAD_V1",
                                       "scope": "Public Git evidence; no private inventory",
                                       "entries": text_entries})
    write_json_exclusive(png_blob, {"schema": "REI_EOS_PUBLIC_PNG_BLOB_V1", "entry": png_entry})
    document = {
        "schema": "REI_EOS_DELIVERY_ARCHIVE_RECEIPT_V1",
        "scope": "Full private new-unit backup; separate public Git payloads; physical claim null",
        "private_zip": {"path": str(private), "bytes": private.stat().st_size,
                        "sha256": archive_sha, "entries": len(entries),
                        "crc_verification": "PASS_ONE_FULL_DECOMPRESSION_PASS"},
        "public_text_payload": {"path": str(public_text), "bytes": public_text.stat().st_size,
                                "entries": len(text_entries)},
        "png_blob_payload": {"path": str(png_blob), "bytes": png_blob.stat().st_size,
                             "path_in_repo": png_entry["path"]},
        "entries": entries,
        "cpu_pre_receipt_s": cpu() - start_cpu,
        "wall_pre_receipt_s": time.monotonic() - start_wall,
        "receipt_write_and_outer_command_costs": "UNKNOWN_NOT_ZERO",
    }
    write_json_exclusive(receipt, document)
    print(json.dumps({key: document[key] for key in ("private_zip", "public_text_payload",
          "png_blob_payload", "cpu_pre_receipt_s", "wall_pre_receipt_s")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

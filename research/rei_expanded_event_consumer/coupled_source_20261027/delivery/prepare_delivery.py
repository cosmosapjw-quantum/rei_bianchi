"""Build a portable four-unit REI ZIP and narrow new-unit Git handoff.

Run after the root's admission, report, canonical staging and raw-only plot.
This script makes local artifacts; it neither commits nor uploads anything.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import zipfile


UNIT = Path(__file__).resolve().parents[1]
ROOT = UNIT.parents[2]
FAMILY = UNIT.parent
DELIVERY = UNIT / "delivery"
PREFIX = Path("research/rei_expanded_event_consumer")
CANONICAL = Path("research/orchestration_expansion_20261025")
OLD_UNITS = ("lumina_20261027", "blocker_closure_20261026", "lumina_resume_20261026")
SKIP = {"GIT_TREE_PAYLOAD.json", "BINARY_BLOBS.json", "PACKAGE_RECEIPT.json", "__pycache__", ".DS_Store"}
BINARY = {".pdf", ".png"}


def files(path: Path):
    return sorted(p for p in path.rglob("*") if p.is_file()
                  and not any(part in SKIP for part in p.parts)
                  and p.suffix not in (".pyc", ".zip"))


def items():
    """Yield (source, ZIP name, Git path or None) with stable relative names."""
    for unit_name in (UNIT.name, *OLD_UNITS):
        unit = FAMILY / unit_name
        if not unit.is_dir():
            raise ValueError(f"Required portable sibling missing: {unit}")
        for source in files(unit):
            relative = source.relative_to(unit)
            if relative.parts[:1] == ("canonical_updates",):
                continue
            destination = PREFIX / unit_name / relative
            git_path = destination if unit_name == UNIT.name and relative.parts[:2] != ("intake", "canonical_base") else None
            yield source, destination, git_path
    staged = UNIT / "canonical_updates" / CANONICAL
    expected = {"DAG.json", "status/CURRENT_STATUS.json", "contracts/REC-COUPLED.json",
                "node_plans/REC-COUPLED.md", "returns/REI_COUPLED_SOURCE_20261027.json"}
    found = {p.relative_to(staged).as_posix() for p in files(staged)}
    if found != expected:
        raise ValueError(f"Root canonical staging must contain exactly {sorted(expected)}; found {sorted(found)}")
    for source in files(staged):
        destination = CANONICAL / source.relative_to(staged)
        yield source, destination, destination


def main():
    for name in ("ADMISSION.json", "REPORT_KO.md", "HANDOFF_KO.md", "GLOBAL_DAG_STATUS.json",
                 "review/VALIDATION.json", "delivery/RENDER_RECEIPT.json"):
        if not (UNIT / name).is_file():
            raise ValueError(f"Root decision/delivery incomplete: {name}")
    for name in ("implementation/attempt01/RESOURCE_RECEIPT.json",
                 "implementation/attempt02/RESOURCE_RECEIPT.json",
                 "implementation/attempt03/stdout.json",
                 "implementation/attempt03/RESOURCE_RECEIPT.json"):
        if not (UNIT / name).is_file():
            raise ValueError(f"Preserved attempt record missing: {name}")
    entries = list(items())
    names = [z.as_posix() for _, z, _ in entries]
    git_names = [g.as_posix() for _, _, g in entries if g is not None]
    if len(names) != len(set(names)) or len(git_names) != len(set(git_names)):
        raise ValueError("Duplicate archive or Git destination")

    archive_path = DELIVERY / "REI_COUPLED_SOURCE_20261027.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for source, destination, _ in entries:
            info = zipfile.ZipInfo(destination.as_posix(), (2026, 10, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    with zipfile.ZipFile(archive_path) as archive:
        if archive.namelist() != names or archive.testzip() is not None:
            raise ValueError("Archive round-trip check failed")

    text_entries, binary_entries = [], []
    for source, _, git_path in entries:
        if git_path is None:
            continue
        raw = source.read_bytes()
        metadata = {"path": git_path.as_posix(), "mode": "100644", "type": "blob"}
        if source.suffix.lower() in BINARY:
            binary_entries.append({**metadata, "base64": base64.b64encode(raw).decode("ascii"),
                                   "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        else:
            text_entries.append({**metadata, "content": raw.decode("utf-8")})
    (DELIVERY / "GIT_TREE_PAYLOAD.json").write_text(json.dumps({"unit": "REI-COUPLED-SOURCE-20261027",
        "entries": text_entries}, ensure_ascii=False, separators=(",", ":")))
    (DELIVERY / "BINARY_BLOBS.json").write_text(json.dumps({"unit": "REI-COUPLED-SOURCE-20261027",
        "entries": binary_entries}, separators=(",", ":")))
    payload = archive_path.read_bytes()
    receipt = {"unit": "REI-COUPLED-SOURCE-20261027", "archive": archive_path.name,
               "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
               "archive_entries": names, "git_paths": git_names,
               "git_text_entries": len(text_entries), "git_binary_entries": len(binary_entries),
               "prior_units_complete_except_archives_and_recursive_payloads": True,
               "original_canonical_source_fields_preserved": True,
               "new_scientific_executions": 0, "publication_status": "PREPARED_NOT_PUBLISHED"}
    (DELIVERY / "PACKAGE_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k not in ("archive_entries", "git_paths")}, indent=2))


if __name__ == "__main__":
    main()

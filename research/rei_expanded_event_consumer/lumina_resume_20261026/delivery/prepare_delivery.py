"""Assemble one portable continuation ZIP and a Git tree handoff payload.

Run only after the root report and handoff are complete. This does not publish
or upload anything. The old published ZIP remains byte-for-byte unchanged.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import zipfile


UNIT = Path(__file__).resolve().parents[1]
PILOT = UNIT.parent
DELIVERY = UNIT / "delivery"
NEW_PREFIX = Path("research/rei_expanded_event_consumer/lumina_resume_20261026")
OLD_PREFIX = Path("research/rei_expanded_event_consumer/lumina_20261027")
CANONICAL = Path("research/orchestration_expansion_20261025")
BINARY_SUFFIXES = {".png", ".pdf"}
SKIP_NAMES = {"GIT_TREE_PAYLOAD.json", "BINARY_BLOBS.json", "PACKAGE_RECEIPT.json"}


def files_under(path: Path):
    return sorted(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")


def items():
    """Yield (physical path, portable ZIP path, Git path or None)."""
    for physical in files_under(UNIT):
        relative = physical.relative_to(UNIT)
        if physical.name in SKIP_NAMES or physical.suffix == ".zip":
            continue
        if relative.parts[:1] == ("canonical_updates",):
            continue  # staged files below map to their original repository paths
        zip_path = NEW_PREFIX / relative
        if relative.parts[:2] == ("intake", "canonical_base"):
            git_path = None  # recovery snapshot in the ZIP only
        elif relative == Path("policy/AGENTS.md"):
            git_path = Path("AGENTS.md")
        else:
            git_path = zip_path
        yield physical, zip_path, git_path

    old = PILOT / "lumina_20261027"
    for physical in files_under(old):
        if physical.suffix == ".zip" or physical.name in SKIP_NAMES:
            continue
        relative = physical.relative_to(old)
        publish_recovery = (relative == Path("implementation/RESUME_AUTHORIZATION.json") or
                            relative.parts[:2] == ("implementation", "attempt02"))
        yield physical, OLD_PREFIX / relative, OLD_PREFIX / relative if publish_recovery else None

    staged = UNIT / "canonical_updates" / CANONICAL
    expected = {"DAG.json", "contracts/REC-EXP-EXTERNAL.json",
                "node_plans/REC-EXP-EXTERNAL.md", "status/CURRENT_STATUS.json",
                "returns/REI_LUMINA_RESUME_20261026.json"}
    found = {p.relative_to(staged).as_posix() for p in files_under(staged)}
    if found != expected:
        raise ValueError(f"Canonical staging incomplete or expanded: {found ^ expected}")
    for physical in files_under(staged):
        repo_path = CANONICAL / physical.relative_to(staged)
        yield physical, repo_path, repo_path


def main():
    for name in ("REPORT_KO.md", "HANDOFF_KO.md", "ADMISSION.json", "GLOBAL_DAG_STATUS.json"):
        if not (UNIT / name).is_file():
            raise ValueError("Required final unit document missing: " + name)
    if not (UNIT / "implementation/run01/MOMENTS.json").is_file():
        raise ValueError("Actual raw native result missing")
    entries = list(items())
    zip_names = [z.as_posix() for _, z, _ in entries]
    git_names = [g.as_posix() for _, _, g in entries if g is not None]
    if len(zip_names) != len(set(zip_names)) or len(git_names) != len(set(git_names)):
        raise ValueError("Duplicate destination in portable package or Git payload")
    if not all(p.is_file() for p, _, _ in entries):
        raise ValueError("A selected delivery source is missing")

    zip_path = DELIVERY / "REI_LUMINA_RESUME_20261026.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for physical, dest, _ in entries:
            info = zipfile.ZipInfo(dest.as_posix(), (2026, 10, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, physical.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.namelist() == zip_names
        assert archive.testzip() is None

    text_entries, binary_entries = [], []
    for physical, _, git_path in entries:
        if git_path is None:
            continue
        raw = physical.read_bytes()
        if physical.suffix.lower() in BINARY_SUFFIXES:
            binary_entries.append({"path": git_path.as_posix(), "mode": "100644", "type": "blob",
                                   "base64": base64.b64encode(raw).decode("ascii"),
                                   "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        else:
            text_entries.append({"path": git_path.as_posix(), "mode": "100644", "type": "blob",
                                 "content": raw.decode("utf-8")})
    (DELIVERY / "GIT_TREE_PAYLOAD.json").write_text(json.dumps({"unit": "REI-LUMINA-RESUME-20261026",
        "entries": text_entries}, ensure_ascii=False, separators=(",", ":")))
    (DELIVERY / "BINARY_BLOBS.json").write_text(json.dumps({"unit": "REI-LUMINA-RESUME-20261026",
        "entries": binary_entries}, separators=(",", ":")))
    payload = zip_path.read_bytes()
    receipt = {"unit": "REI-LUMINA-RESUME-20261026", "archive": zip_path.name,
               "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
               "archive_entries": zip_names, "git_text_entries": len(text_entries),
               "git_binary_entries": len(binary_entries),
               "old_unit_source_complete_except_recursive_archives": True,
               "old_published_zip_record_preserved": True, "new_scientific_executions": 0,
               "publication_status": "PREPARED_NOT_PUBLISHED"}
    (DELIVERY / "PACKAGE_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "archive_entries"}, indent=2))


if __name__ == "__main__":
    main()

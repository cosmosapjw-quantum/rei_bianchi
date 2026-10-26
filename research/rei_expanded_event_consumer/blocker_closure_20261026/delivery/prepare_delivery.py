"""Prepare a portable source ZIP and Git blob payload; never publish or upload.

Run after the final report, handoff, and scenario review are frozen. Prior-unit
sources stay in their sibling repository paths so relative imports work.
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
NEW_PREFIX = Path("research/rei_expanded_event_consumer/blocker_closure_20261026")
PRIOR_UNITS = ("lumina_20261027", "lumina_resume_20261026")
CANONICAL = Path("research/orchestration_expansion_20261025")
SCENARIO = Path("research/rei_expanded_scenario/pw19_snapshot_20261026")
SCENARIO_FILES = {"SCENARIO.json", "SOURCE_ABSORBER_MATRIX.json", "COVERAGE_DELTA.json"}
BINARY_SUFFIXES = {".png", ".pdf", ".npz"}
GENERATED = {"GIT_TREE_PAYLOAD.json", "BINARY_BLOBS.json", "PACKAGE_RECEIPT.json",
             "PACKAGING_COST.json", "GIT_READBACK_RAW.json", "GIT_READBACK.json"}


def files_under(path: Path):
    return sorted(p for p in path.rglob("*") if p.is_file() and
                  "__pycache__" not in p.parts and p.suffix not in {".pyc", ".zip"} and
                  p.name not in GENERATED)


def entries():
    """Yield physical source, archive path, optional Git path."""
    for physical in files_under(UNIT):
        rel = physical.relative_to(UNIT)
        if rel.parts[:1] == ("canonical_updates",):
            continue
        git = None if rel.parts[:2] == ("intake", "canonical_base") else NEW_PREFIX / rel
        if rel.parts[:1] == ("scenario",):
            git = SCENARIO / rel.name
        yield physical, NEW_PREFIX / rel, git

    for name in PRIOR_UNITS:
        root = PILOT / name
        prefix = Path("research/rei_expanded_event_consumer") / name
        for physical in files_under(root):
            yield physical, prefix / physical.relative_to(root), None

    stage = UNIT / "canonical_updates" / CANONICAL
    expected = {"DAG.json", "status/CURRENT_STATUS.json",
                "contracts/REC-FIELD.json", "contracts/REC-EXP-SPECTRAL.json",
                "node_plans/REC-FIELD.md", "node_plans/REC-EXP-SPECTRAL.md",
                "returns/REI_NATIVE_PW19_CALLBACK_20261026.json"}
    found = {p.relative_to(stage).as_posix() for p in files_under(stage)}
    if found != expected:
        raise ValueError(f"Canonical staging differs from two-node decision: {found ^ expected}")
    for physical in files_under(stage):
        path = CANONICAL / physical.relative_to(stage)
        yield physical, path, path
    # The scenario is intentionally additive and has no canonical count effect.
    found_scenario = {p.name for p in files_under(UNIT / "scenario")}
    if found_scenario != SCENARIO_FILES:
        raise ValueError(f"Scenario staging differs from approved three-file variant: {found_scenario ^ SCENARIO_FILES}")
    for physical in files_under(UNIT / "scenario"):
        path = SCENARIO / physical.name
        yield physical, path, None  # Git entry already mapped above


def main():
    for name in ("REPORT_KO.md", "HANDOFF_KO.md", "ADMISSION.json", "GLOBAL_DAG_STATUS.json"):
        if not (UNIT / name).is_file():
            raise ValueError("Final report/handoff/admission is missing: " + name)
    selected = list(entries())
    archive_names = [a.as_posix() for _, a, _ in selected]
    git_names = [g.as_posix() for _, _, g in selected if g is not None]
    if len(archive_names) != len(set(archive_names)) or len(git_names) != len(set(git_names)):
        raise ValueError("Repeated portable or Git destination")

    zip_path = DELIVERY / "REI_BLOCKER_CLOSURE_20261026.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for physical, path, _ in selected:
            info = zipfile.ZipInfo(path.as_posix(), (2026, 10, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, physical.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    with zipfile.ZipFile(zip_path) as z:
        assert z.namelist() == archive_names and z.testzip() is None

    text_entries, binary_entries = [], []
    for physical, _, git_path in selected:
        if git_path is None:
            continue
        raw = physical.read_bytes()
        identity = {"path": git_path.as_posix(), "mode": "100644", "type": "blob"}
        if physical.suffix.lower() in BINARY_SUFFIXES:
            binary_entries.append({**identity, "base64": base64.b64encode(raw).decode("ascii"),
                                   "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        else:
            text_entries.append({**identity, "content": raw.decode("utf-8")})
    (DELIVERY / "GIT_TREE_PAYLOAD.json").write_text(json.dumps({"unit":"REI-BLOCKER-CLOSURE-20261026",
        "entries":text_entries},ensure_ascii=False,separators=(",",":")))
    (DELIVERY / "BINARY_BLOBS.json").write_text(json.dumps({"unit":"REI-BLOCKER-CLOSURE-20261026",
        "entries":binary_entries},separators=(",",":")))
    raw_zip = zip_path.read_bytes()
    receipt = {"unit":"REI-BLOCKER-CLOSURE-20261026", "archive":zip_path.name,
               "bytes":len(raw_zip), "sha256":hashlib.sha256(raw_zip).hexdigest(),
               "archive_entries":archive_names, "git_text_entries":len(text_entries),
               "git_binary_entries":len(binary_entries), "publication_status":"PREPARED_NOT_PUBLISHED",
               "new_scientific_executions":0}
    (DELIVERY / "PACKAGE_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:v for k,v in receipt.items() if k!="archive_entries"},indent=2))


if __name__ == "__main__":
    main()

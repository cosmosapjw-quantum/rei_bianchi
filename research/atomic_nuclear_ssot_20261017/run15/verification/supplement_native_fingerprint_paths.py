#!/usr/bin/env python3
"""Add-only correction of one read-only fingerprint path selector."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import sys

BASE = Path("/tmp/rei_run15_salvage/verification")
OLD = Path("/tmp/rei_run15_salvage/recovery/postloss_native_build/execution/target")
NEW = BASE / "reproduction_D/postloss_native_build/target"

def identity(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}

def rows(target):
    out = []
    for path in sorted((target / "release/.fingerprint").glob("*/*.json")):
        if path.name in ("lib-rei_iso_couple_reference.json", "lib-rei_run15_positive_planck.json",
                         "bin-positive_planck_panel_postloss.json"):
            out.append({"file_name": path.name, "relative_path": path.relative_to(target).as_posix(),
                        **identity(path), "metadata": json.loads(path.read_bytes())})
    return out

def main():
    published, reproduced = rows(OLD), rows(NEW)
    if len(published) != 3 or len(reproduced) != 3:
        raise ValueError("expected three existing Cargo fingerprint records for each build")
    differences = []
    for name in sorted({r["file_name"] for r in published}):
        left = next(r for r in published if r["file_name"] == name)["metadata"]
        right = next(r for r in reproduced if r["file_name"] == name)["metadata"]
        differences.append({"file_name": name, "different_metadata_fields":
            {k: {"published": left.get(k), "reproduced": right.get(k)}
             for k in sorted(set(left) | set(right)) if left.get(k) != right.get(k)}})
    result = {"schema": "rei.run15.scoped_verification.fingerprint_path_correction.v1",
              "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": identity(Path(__file__)), "argv": [sys.executable, "-B", str(Path(__file__).resolve())],
              "corrects": "NATIVE_BINARY_BYTE_MISMATCH_OBSERVATIONS.json published_local_package_fingerprint_metadata",
              "prior_selector_error": "reference_binary.parents[2] selected execution, one level above target; this gave an empty published list. The binary and ELF comparisons were unaffected.",
              "corrected_target": str(OLD), "new_target": str(NEW),
              "published_metadata": published, "reproduced_metadata": reproduced,
              "observed_field_differences": differences,
              "causality_or_instruction_equivalence": "NOT_ESTABLISHED",
              "source_owners_modified": 0, "native_builds": 0, "native_CLI_executions": 0, "IVP_runs": 0}
    path = BASE / "completion_D/NATIVE_FINGERPRINT_PATH_CORRECTION.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"path": str(path), "published_records": len(published),
                      "reproduced_records": len(reproduced),
                      "differing_fields": {r["file_name"]: list(r["different_metadata_fields"]) for r in differences},
                      **identity(path)}, indent=2))

if __name__ == "__main__":
    main()

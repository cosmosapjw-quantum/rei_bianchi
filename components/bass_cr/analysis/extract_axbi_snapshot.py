"""Extract five matched fixed-a abundance rows from the admitted owner table."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess

OWNER = "56dc609ea9b801c88d3364aed3eee140b3a20d46"
TABLE = "research/rei_igm_sync_20261116/approximation_validity/incremental_fifth/results_five/five_case_abundances.csv.gz"
BLOB = "ce22a6b6d94aabf1bffcc3b5c472316cac1983d4"
REPO = Path(__file__).resolve().parents[3]
DESTINATION = REPO / "src/rei_bianchi/microphysics/cr_sources/axbi_rows.json"


def main():
    path = REPO/TABLE
    raw = path.read_bytes() if path.exists() else subprocess.check_output(
        ["git", "show", f"{OWNER}:{TABLE}"], cwd=REPO)
    if hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() != BLOB:
        raise ValueError("owner abundance table checksum changed")
    source = csv.DictReader(io.StringIO(gzip.decompress(raw).decode()))
    rows = {}
    for row in source:
        z = float(row["zbar"])
        case = row["case"]
        if z <= 8 and (case not in rows or z > float(rows[case]["zbar"])):
            rows[case] = row
    if len(rows) != 5 or len(set(float(r['a']) for r in rows.values())) != 1:
        raise ValueError("expected all five cases at the common first z<=8")
    document = {"selection":"largest saved zbar<=8 per case, fixed-a published abundance sample",
                "repo":"cosmosapjw-quantum/rei_bianchi", "commit":OWNER, "table":TABLE,
                "git_blob":BLOB,"gzip_sha256":hashlib.sha256(raw).hexdigest(),
                "geometry_sources":["rust/rei_microphysics/src/axbi_background.rs", "rust/rei_microphysics/src/axbi_driver.rs"],
                "rows":rows}
    DESTINATION.write_text(json.dumps(document,indent=2,sort_keys=True)+"\n")
    print({case:(row['a'],row['zbar']) for case,row in rows.items()})


if __name__ == "__main__":
    main()

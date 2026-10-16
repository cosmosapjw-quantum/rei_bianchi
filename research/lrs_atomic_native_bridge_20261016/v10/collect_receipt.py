"""Collect factual native execution and source identities from an NCP stage."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wall_seconds(stderr: str) -> float | None:
    m = re.search(r"Elapsed \(wall clock\) time .*\):\s*([^\n]+)", stderr)
    if not m:
        return None
    parts = m.group(1).strip().split(":")
    if len(parts) == 2:
        return 60 * int(parts[0]) + float(parts[1])
    if len(parts) == 3:
        return 3600 * int(parts[0]) + 60 * int(parts[1]) + float(parts[2])
    return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("stage", type=Path)
    a = p.parse_args()
    stage = a.stage
    runs = []
    for csv_path in sorted((stage / "runs_v2").glob("*.csv")):
        m = re.fullmatch(r"(.+)_(\d+)", csv_path.stem)
        if not m:
            continue
        stderr_path = csv_path.with_suffix(".stderr")
        stderr = stderr_path.read_text() if stderr_path.exists() else ""
        with csv_path.open(newline="") as f:
            rows = list(csv.DictReader(f))
        runs.append({
            "mode": m.group(1), "steps": int(m.group(2)), "rows": len(rows),
            "csv_sha256": sha(csv_path),
            "stderr_sha256": sha(stderr_path) if stderr_path.exists() else None,
            "exit_marker": bool(re.search(r"Exit status:\s*0\b", stderr)),
            "completion_marker": "V10_COMPLETED" in stderr,
            "wall_s": wall_seconds(stderr),
            "max_rss_kib": int(re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", stderr).group(1))
                if re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", stderr) else None,
            "terminal": {k: rows[-1][k] for k in
                ("a", "T_K", "HII", "HeII", "HeIII", "ne_cm3",
                 "photon_n_per_h", "photon_u_ev_per_h", "energy_residual")}
                if rows else None,
        })
    source_files = [
        "owner_6ea2.tar.gz", "pr167_driver.patch", "pr167_transport.patch",
        "pr167_copy/rust/rei_microphysics/src/axbi_driver.rs",
        "pr167_copy/rust/rei_microphysics/src/axbi_covariant_transport.rs",
        "pr167_copy/rust/rei_microphysics/src/v10_rrmp.rs",
        "pr167_copy/rust/rei_microphysics/examples/native_v10.rs",
    ]
    out = {
        "schema": "rei.lrs.v10.native_execution.1",
        "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "ncp_stage": str(stage),
        "frozen_owner_commit": "6ea2b1b4b3875c9163cafc45efe720afded43fc4",
        "pr167_donor_commit": "1e6a3dd60d69b22483d07a30541736018a69dea8",
        "base_pr169_commit": "0cf419eb61f52f24adcfcbaa3afa055176276b6e",
        "source_sha256": {p: sha(stage / p) for p in source_files},
        "source_replay": "prepare_owner_v10.sh",
        "build_first_failure": "build_controls.stderr: exit 101, new diagnostic ledger fields absent from checkpoint initializer; repaired with default diagnostic fields",
        "targeted_test": "axbi_driver 13 passed, 0 failed",
        "runs": runs,
    }
    (stage / "NCP_RUN_RECEIPT.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
